"""
Start command handler and main menu.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.models import LanguageCode
from app.utils.i18n import get_translation
from app.utils.telegram import get_user_id, safe_reply_text
from app.bot.keyboards import get_main_menu_keyboard
from app.bot.services.enroll_service import EnrollmentService
from app.db import get_async_db

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    user_id = get_user_id(update)
    if not user_id:
        return ConversationHandler.END
    
    lang = context.user_data.get("lang", "ru")
    
    try:
        # Get or create student
        from app.db import get_sync_db
        session = get_sync_db()
        try:
            enroll_service = EnrollmentService(session)
            student = enroll_service.get_or_create_student(
                telegram_id=user_id,
                lang=LanguageCode(lang)
            )
        finally:
            # Update context with student info
            context.user_data["student_id"] = student.id
            session.close()
        
        # Send welcome message
        welcome_text = get_translation("welcome.title", lang=lang)
        welcome_text += "\n\n" + get_translation("welcome.description", lang=lang)
        welcome_text += "\n\n" + get_translation("welcome.menu", lang=lang)
        
        keyboard = get_main_menu_keyboard(lang)
        
        await safe_reply_text(
            update,
            welcome_text,
            reply_markup=keyboard
        )
        
        logger.info("Start command processed", user_id=user_id, student_id=student.id)
        
    except Exception as e:
        logger.error("Start command failed", user_id=user_id, error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle support menu item.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    support_text = get_translation("support.message", lang=lang)
    
    await safe_reply_text(update, support_text)
    
    return ConversationHandler.END


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle back to menu callback.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    menu_text = get_translation("welcome.menu", lang=lang)
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        menu_text,
        reply_markup=keyboard
    )
    
    return ConversationHandler.END
