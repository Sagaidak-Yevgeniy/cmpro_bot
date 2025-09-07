"""
Language switching handler.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.models import LanguageCode
from app.utils.i18n import get_translation
from app.utils.telegram import get_user_id, safe_reply_text
from app.bot.keyboards import get_language_keyboard, get_main_menu_keyboard
from app.bot.services.repo import StudentRepository
from app.db import get_async_db

logger = get_logger(__name__)


async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show language selection menu.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    lang = context.user_data.get("lang", "ru")
    
    lang_text = get_translation("lang.current", lang=lang, lang=lang.upper())
    lang_text += "\n\n" + get_translation("lang.select", lang=lang)
    
    lang_keyboard = get_language_keyboard(lang)
    
    await safe_reply_text(
        update,
        lang_text,
        reply_markup=lang_keyboard
    )
    
    return ConversationHandler.END


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Change user language.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        Conversation state
    """
    user_id = get_user_id(update)
    
    if not update.callback_query:
        return ConversationHandler.END
    
    callback_data = update.callback_query.data
    
    # Parse language from callback data
    if callback_data == "lang_ru":
        new_lang = LanguageCode.RUSSIAN
        lang_name = "Русский"
    elif callback_data == "lang_kk":
        new_lang = LanguageCode.KAZAKH
        lang_name = "Қазақша"
    else:
        return ConversationHandler.END
    
    try:
        # Update user language in database
        async with get_async_db() as session:
            student = await StudentRepository.get_by_telegram_id(session, user_id)
            
            if student:
                await StudentRepository.update_language(session, student, new_lang)
                logger.info("User language updated", user_id=user_id, new_lang=new_lang.value)
            else:
                # Create student if not exists
                student = await StudentRepository.create(
                    session,
                    telegram_id=user_id,
                    lang=new_lang
                )
                logger.info("Student created with language", user_id=user_id, lang=new_lang.value)
        
        # Update context
        context.user_data["lang"] = new_lang.value
        
        # Send confirmation
        confirmation_text = get_translation("lang.changed", lang=new_lang.value, lang=lang_name)
        
        # Show main menu with new language
        keyboard = get_main_menu_keyboard(new_lang.value)
        
        await safe_reply_text(
            update,
            confirmation_text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error("Failed to change language", user_id=user_id, error=str(e))
        await safe_reply_text(
            update,
            get_translation("errors.general", lang=context.user_data.get("lang", "ru"))
        )
    
    return ConversationHandler.END
