"""
Schedule handler for showing upcoming lessons.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.utils.i18n import get_translation
from app.utils.telegram import safe_reply_text
from app.bot.keyboards import get_main_menu_keyboard
from app.bot.services.schedule_service import ScheduleService
from app.db import get_async_db

logger = get_logger(__name__)


async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show upcoming lessons schedule.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    try:
        async with get_async_db() as session:
            schedule_service = ScheduleService(session)
            lessons = await schedule_service.get_upcoming_lessons(limit=5)
            
            schedule_text = await schedule_service.format_lessons_for_display(lessons, lang=lang)
            
            # Add back to menu button
            keyboard = get_main_menu_keyboard(lang)
            
            await safe_reply_text(
                update,
                schedule_text,
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error("Failed to show schedule", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END
