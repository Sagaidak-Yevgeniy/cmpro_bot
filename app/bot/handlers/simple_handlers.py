"""
Упрощенные обработчики для быстрого тестирования без async операций.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.logging import get_logger
from app.utils.i18n import get_translation
from app.utils.telegram import safe_reply_text
from app.bot.keyboards import get_main_menu_keyboard

logger = get_logger(__name__)


async def simple_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная команда /start для тестирования.
    """
    lang = context.user_data.get("lang", "ru")
    
    welcome_text = get_translation("welcome.title", lang=lang)
    welcome_text += "\n\n" + get_translation("welcome.description", lang=lang)
    welcome_text += "\n\n" + get_translation("welcome.menu", lang=lang)
    
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        welcome_text,
        reply_markup=keyboard
    )
    
    logger.info("Simple start command processed", user_id=update.effective_user.id)
    return ConversationHandler.END


async def simple_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная команда поддержки.
    """
    lang = context.user_data.get("lang", "ru")
    
    support_text = get_translation("support.message", lang=lang)
    
    await safe_reply_text(update, support_text)
    
    return ConversationHandler.END


async def simple_directions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная команда направлений.
    """
    lang = context.user_data.get("lang", "ru")
    
    directions_text = get_translation("directions.title", lang=lang) + "\n\n"
    directions_text += "🐍 **Python**\n"
    directions_text += get_translation("directions.python.description", lang=lang) + "\n\n"
    directions_text += "⚡ **JavaScript**\n"
    directions_text += get_translation("directions.js.description", lang=lang) + "\n\n"
    directions_text += "🚀 **Go**\n"
    directions_text += get_translation("directions.go.description", lang=lang) + "\n\n"
    directions_text += "📊 **Data Analytics**\n"
    directions_text += get_translation("directions.da.description", lang=lang)
    
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        directions_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def simple_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная команда расписания.
    """
    lang = context.user_data.get("lang", "ru")
    
    schedule_text = get_translation("schedule.title", lang=lang) + "\n\n"
    schedule_text += "📚 Введение в Python\n"
    schedule_text += "👥 Группа: Python для начинающих\n"
    schedule_text += "🕐 18:00 - 20:00\n"
    schedule_text += "📅 15.01.2024\n\n"
    schedule_text += "📚 Основы JavaScript\n"
    schedule_text += "👥 Группа: JavaScript Fundamentals\n"
    schedule_text += "🕐 18:00 - 20:00\n"
    schedule_text += "📅 16.01.2024"
    
    keyboard = get_main_menu_keyboard(lang)
    
    await safe_reply_text(
        update,
        schedule_text,
        reply_markup=keyboard
    )
    
    return ConversationHandler.END


async def simple_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная команда смены языка.
    """
    lang = context.user_data.get("lang", "ru")
    
    lang_text = get_translation("lang.current", lang=lang, lang=lang.upper())
    lang_text += "\n\n" + get_translation("lang.select", lang=lang)
    
    from app.bot.keyboards import get_language_keyboard
    lang_keyboard = get_language_keyboard(lang)
    
    await safe_reply_text(
        update,
        lang_text,
        reply_markup=lang_keyboard
    )
    
    return ConversationHandler.END


async def simple_change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Упрощенная смена языка.
    """
    if not update.callback_query:
        return ConversationHandler.END
    
    callback_data = update.callback_query.data
    
    if callback_data == "lang_ru":
        new_lang = "ru"
        lang_name = "Русский"
    elif callback_data == "lang_kk":
        new_lang = "kk"
        lang_name = "Қазақша"
    else:
        return ConversationHandler.END
    
    # Update context
    context.user_data["lang"] = new_lang
    
    # Send confirmation
    confirmation_text = get_translation("lang.changed", lang=new_lang, lang=lang_name)
    
    # Show main menu with new language
    keyboard = get_main_menu_keyboard(new_lang)
    
    await safe_reply_text(
        update,
        confirmation_text,
        reply_markup=keyboard
    )
    
    return ConversationHandler.END
