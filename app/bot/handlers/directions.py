"""
Directions handler for showing available courses.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.models import DirectionCode
from app.utils.i18n import get_translation
from app.utils.telegram import safe_reply_text
from app.bot.keyboards import get_directions_keyboard, get_direction_enroll_keyboard
from app.bot.services.enroll_service import EnrollmentService
from app.db import get_async_db

logger = get_logger(__name__)


async def show_directions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show available directions.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
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
            
            # Format directions text
            directions_text = get_translation("directions.title", lang=lang) + "\n\n"
            
            for direction in directions:
                direction_key = f"directions.{direction.code.value}"
                title = get_translation(f"{direction_key}.title", lang=lang)
                description = get_translation(f"{direction_key}.description", lang=lang)
                directions_text += f"**{title}**\n{description}\n\n"
            
            directions_keyboard = get_directions_keyboard(directions, lang)
            
            await safe_reply_text(
                update,
                directions_text,
                reply_markup=directions_keyboard,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error("Failed to show directions", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def show_direction_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show direction details and enrollment option.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    if not update.callback_query:
        return ConversationHandler.END
    
    callback_data = update.callback_query.data
    
    # Parse direction from callback data
    if not callback_data.startswith("direction_"):
        return ConversationHandler.END
    
    direction_code_str = callback_data.replace("direction_", "")
    
    try:
        direction_code = DirectionCode(direction_code_str)
    except ValueError:
        await safe_reply_text(
            update,
            get_translation("errors.invalid_input", lang=lang)
        )
        return ConversationHandler.END
    
    try:
        async with get_async_db() as session:
            enroll_service = EnrollmentService(session)
            direction = await enroll_service.get_direction_by_code(direction_code)
            
            if not direction:
                await safe_reply_text(
                    update,
                    get_translation("errors.general", lang=lang)
                )
                return ConversationHandler.END
            
            # Format direction details
            direction_key = f"directions.{direction.code.value}"
            title = get_translation(f"{direction_key}.title", lang=lang)
            description = get_translation(f"{direction_key}.description", lang=lang)
            
            details_text = f"**{title}**\n\n{description}"
            
            enroll_keyboard = get_direction_enroll_keyboard(direction_code, lang)
            
            await safe_reply_text(
                update,
                details_text,
                reply_markup=enroll_keyboard,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error("Failed to show direction details", error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=lang)
        )
    
    return ConversationHandler.END


async def start_direction_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start enrollment for specific direction.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    if not update.callback_query:
        return ConversationHandler.END
    
    callback_data = update.callback_query.data
    
    # Parse direction from callback data
    if not callback_data.startswith("enroll_"):
        return ConversationHandler.END
    
    direction_code_str = callback_data.replace("enroll_", "")
    
    try:
        direction_code = DirectionCode(direction_code_str)
    except ValueError:
        await safe_reply_text(
            update,
            get_translation("errors.invalid_input", lang=lang)
        )
        return ConversationHandler.END
    
    # Store direction in context for enrollment
    context.user_data["selected_direction"] = direction_code.value
    
    # Start enrollment flow
    from app.bot.handlers.enroll import start_enrollment
    return await start_enrollment(update, context)
