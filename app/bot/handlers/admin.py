"""
Admin handlers for managing enrollments and bot administration.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.config import settings
from app.logging import get_logger
from app.models import EnrollmentStatus, LanguageCode
from app.utils.i18n import get_translation
from app.utils.telegram import get_user_id, safe_reply_text
from app.bot.keyboards import (
    get_admin_menu_keyboard,
    get_enrollment_actions_keyboard,
    get_pagination_keyboard,
    get_main_menu_keyboard
)
from app.bot.services.repo import EnrollmentRepository, StudentRepository
from app.models import Enrollment
from app.db import get_async_db

logger = get_logger(__name__)

# Conversation states
WAITING_FOR_ADMIN_TOKEN = 1


async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start admin command.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Next conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    # Check if already authenticated
    if context.user_data.get("admin_authenticated"):
        await show_admin_menu(update, context)
        return ConversationHandler.END
    
    admin_text = get_translation("admin.access_required", lang=lang)
    
    await safe_reply_text(update, admin_text)
    
    return WAITING_FOR_ADMIN_TOKEN


async def receive_admin_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive and validate admin token.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Next conversation state
    """
    lang = context.user_data.get("lang", "ru")
    token = update.message.text.strip()
    
    if token == settings.admin_access_token:
        context.user_data["admin_authenticated"] = True
        
        await safe_reply_text(
            update,
            get_translation("admin.access_granted", lang=lang)
        )
        
        await show_admin_menu(update, context)
        
        logger.info("Admin access granted", user_id=get_user_id(update))
        
    else:
        await safe_reply_text(
            update,
            get_translation("admin.access_denied", lang=lang)
        )
    
    return ConversationHandler.END


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show admin menu.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    if not context.user_data.get("admin_authenticated"):
        await start_admin(update, context)
        return ConversationHandler.END
    
    admin_text = get_translation("admin.menu", lang=lang)
    admin_keyboard = get_admin_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        admin_text,
        reply_markup=admin_keyboard
    )
    
    return ConversationHandler.END


async def show_enrollments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show pending enrollments for admin review.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    if not context.user_data.get("admin_authenticated"):
        await start_admin(update, context)
        return ConversationHandler.END
    
    try:
        async with get_async_db() as session:
            # Get page from callback data or default to 0
            page = 0
            if update.callback_query and "page_" in update.callback_query.data:
                try:
                    page = int(update.callback_query.data.split("_")[-1])
                except (ValueError, IndexError):
                    page = 0
            
            limit = 5
            offset = page * limit
            
            enrollments = await EnrollmentRepository.get_pending_enrollments(
                session, limit=limit, offset=offset
            )
            
            if not enrollments:
                enrollments_text = get_translation("admin.no_enrollments", lang=lang)
                admin_keyboard = get_admin_menu_keyboard(lang)
                
                await safe_reply_text(
                    update,
                    enrollments_text,
                    reply_markup=admin_keyboard
                )
                return ConversationHandler.END
            
            # Format enrollments
            enrollments_text = get_translation("admin.enrollments_list", lang=lang) + "\n\n"
            
            for enrollment in enrollments:
                enrollment_text = get_translation("admin.enrollment_item", lang=lang).format(
                    name=enrollment.student.full_name or "Не указано",
                    phone=enrollment.student.phone or "Не указано",
                    direction=enrollment.direction.title,
                    date=enrollment.created_at.strftime("%d.%m.%Y %H:%M")
                )
                enrollments_text += f"{enrollment_text}\n\n"
            
            # Create pagination
            total_count = await EnrollmentRepository.count_pending(session)
            total_pages = (total_count + limit - 1) // limit
            
            if total_pages > 1:
                pagination_keyboard = get_pagination_keyboard(
                    current_page=page,
                    total_pages=total_pages,
                    base_action="admin_enrollments",
                    lang=lang
                )
            else:
                pagination_keyboard = [[{
                    "text": get_translation("buttons.back", lang=lang),
                    "callback_data": "admin_menu"
                }]]
            
            await safe_reply_text(
                update,
                enrollments_text,
                reply_markup=pagination_keyboard
            )
            
    except Exception as e:
        logger.error("Failed to show enrollments", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def handle_enrollment_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle enrollment approval/rejection.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    if not context.user_data.get("admin_authenticated"):
        await start_admin(update, context)
        return ConversationHandler.END
    
    if not update.callback_query:
        return ConversationHandler.END
    
    callback_data = update.callback_query.data
    
    try:
        # Parse action and enrollment ID
        if callback_data.startswith("approve_enrollment_"):
            enrollment_id = int(callback_data.replace("approve_enrollment_", ""))
            new_status = EnrollmentStatus.APPROVED
            action_text = "одобрена"
        elif callback_data.startswith("reject_enrollment_"):
            enrollment_id = int(callback_data.replace("reject_enrollment_", ""))
            new_status = EnrollmentStatus.REJECTED
            action_text = "отклонена"
        else:
            return ConversationHandler.END
        
        async with get_async_db() as session:
            # Get enrollment
            result = await session.execute(
                select(Enrollment).where(Enrollment.id == enrollment_id)
            )
            enrollment = result.scalar_one_or_none()
            
            if not enrollment:
                await safe_reply_text(
                    update,
                    get_translation("errors.general", lang=lang)
                )
                return ConversationHandler.END
            
            # Update status
            await EnrollmentRepository.update_status(session, enrollment, new_status)
            
            # Send confirmation
            confirmation_text = f"Заявка {action_text}!"
            await safe_reply_text(update, confirmation_text)
            
            logger.info(
                "Enrollment status updated",
                enrollment_id=enrollment_id,
                new_status=new_status.value,
                admin_user_id=get_user_id(update)
            )
            
            # Show enrollments again
            await show_enrollments(update, context)
            
    except Exception as e:
        logger.error("Failed to handle enrollment action", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def admin_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle back to admin menu.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    await show_admin_menu(update, context)
    return ConversationHandler.END


async def admin_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Logout from admin mode.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    context.user_data["admin_authenticated"] = False
    
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        "Выход из админ-панели",
        reply_markup=keyboard
    )
    
    logger.info("Admin logout", user_id=get_user_id(update))
    
    return ConversationHandler.END
