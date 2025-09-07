"""
Enrollment conversation handler.
Handles the student enrollment flow.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.models import DirectionCode, LanguageCode
from app.utils.i18n import get_translation
from app.utils.telegram import get_user_id, safe_reply_text, is_phone_valid
from app.bot.keyboards import get_directions_keyboard, get_cancel_keyboard
from app.bot.services.enroll_service import EnrollmentService
from app.db import get_async_db

logger = get_logger(__name__)

# Conversation states
WAITING_FOR_NAME, WAITING_FOR_PHONE, WAITING_FOR_DIRECTION = range(3)


async def start_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start enrollment conversation.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Next conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    enroll_text = get_translation("enroll.start", lang=lang)
    cancel_keyboard = get_cancel_keyboard(lang)
    
    await safe_reply_text(
        update,
        enroll_text,
        reply_markup=cancel_keyboard
    )
    
    return WAITING_FOR_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive and validate student name.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Next conversation state
    """
    lang = context.user_data.get("lang", "ru")
    name = update.message.text.strip()
    
    if len(name) < 2:
        await safe_reply_text(
            update,
            get_translation("errors.invalid_input", lang=lang)
        )
        return WAITING_FOR_NAME
    
    # Store name in context
    context.user_data["enroll_name"] = name
    
    # Ask for phone
    phone_text = get_translation("enroll.name_received", lang=lang, name=name)
    cancel_keyboard = get_cancel_keyboard(lang)
    
    await safe_reply_text(
        update,
        phone_text,
        reply_markup=cancel_keyboard
    )
    
    return WAITING_FOR_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive and validate student phone.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Next conversation state
    """
    lang = context.user_data.get("lang", "ru")
    phone = update.message.text.strip()
    
    if not is_phone_valid(phone):
        await safe_reply_text(
            update,
            get_translation("enroll.invalid_phone", lang=lang)
        )
        return WAITING_FOR_PHONE
    
    # Store phone in context
    context.user_data["enroll_phone"] = phone
    
    # Show directions
    try:
        async with get_async_db() as session:
            enroll_service = EnrollmentService(session)
            directions = await enroll_service.get_available_directions()
            
            if not directions:
                await safe_reply_text(
                    update,
                    get_translation("errors.general", lang=lang)
                )
                return ConversationHandler.END
            
            directions_text = get_translation("enroll.phone_received", lang=lang)
            directions_keyboard = get_directions_keyboard(directions, lang)
            
            await safe_reply_text(
                update,
                directions_text,
                reply_markup=directions_keyboard
            )
            
    except Exception as e:
        logger.error("Failed to get directions", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
        return ConversationHandler.END
    
    return WAITING_FOR_DIRECTION


async def receive_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive direction selection and complete enrollment.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation end state
    """
    user_id = get_user_id(update)
    lang = context.user_data.get("lang", "ru")
    
    if not update.callback_query:
        return WAITING_FOR_DIRECTION
    
    callback_data = update.callback_query.data
    
    # Parse direction from callback data
    if not callback_data.startswith("direction_"):
        return WAITING_FOR_DIRECTION
    
    direction_code_str = callback_data.replace("direction_", "")
    
    try:
        direction_code = DirectionCode(direction_code_str)
    except ValueError:
        await safe_reply_text(
            update,
            get_translation("errors.invalid_input", lang=lang)
        )
        return WAITING_FOR_DIRECTION
    
    try:
        async with get_async_db() as session:
            enroll_service = EnrollmentService(session)
            
            # Get or create student
            student = await enroll_service.get_or_create_student(
                telegram_id=user_id,
                full_name=context.user_data.get("enroll_name"),
                phone=context.user_data.get("enroll_phone"),
                lang=LanguageCode(lang)
            )
            
            # Enroll student
            success, message = await enroll_service.enroll_student(student, direction_code)
            
            if success:
                # Clear enrollment data from context
                context.user_data.pop("enroll_name", None)
                context.user_data.pop("enroll_phone", None)
                
                # Show main menu
                from app.bot.keyboards import get_main_menu_keyboard
                keyboard = get_main_menu_keyboard(lang)
                
                await safe_reply_text(
                    update,
                    message,
                    reply_markup=keyboard
                )
                
                logger.info(
                    "Enrollment completed",
                    user_id=user_id,
                    student_id=student.id,
                    direction=direction_code.value
                )
            else:
                await safe_reply_text(update, message)
                
    except Exception as e:
        logger.error("Enrollment failed", user_id=user_id, error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def cancel_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel enrollment conversation.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation end state
    """
    lang = context.user_data.get("lang", "ru")
    
    # Clear enrollment data from context
    context.user_data.pop("enroll_name", None)
    context.user_data.pop("enroll_phone", None)
    
    # Show main menu
    from app.bot.keyboards import get_main_menu_keyboard
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        get_translation("buttons.cancel", lang=lang),
        reply_markup=keyboard
    )
    
    return ConversationHandler.END
