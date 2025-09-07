"""
Main Telegram bot application.
Creates and configures the PTB Application singleton.
"""

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.logging import configure_logging, get_logger
from app.bot.handlers import (
    admin,
    directions,
    enroll,
    lang,
    schedule,
    start,
)
from app.bot.middlewares import (
    i18n_middleware,
    logging_middleware,
    rate_limit_middleware,
)

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)

# Global application instance
_application: Application | None = None


def create_application() -> Application:
    """
    Create and configure the Telegram bot application.
    
    Returns:
        Configured PTB Application instance
    """
    global _application
    
    if _application is not None:
        return _application
    
    # Create application
    _application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add middlewares
    _application.add_handler(logging_middleware, group=-1)
    _application.add_handler(rate_limit_middleware, group=-1)
    _application.add_handler(i18n_middleware, group=-1)
    
    # Add command handlers
    _application.add_handler(CommandHandler("start", start.start_command))
    _application.add_handler(CommandHandler("lang", lang.show_language_menu))
    _application.add_handler(CommandHandler("admin", admin.start_admin))
    
    # Add conversation handlers
    _application.add_handler(create_enrollment_conversation())
    _application.add_handler(create_admin_conversation())
    _application.add_handler(create_language_conversation())
    
    # Add callback query handlers
    _application.add_handler(CallbackQueryHandler(
        directions.show_direction_details,
        pattern=r"^direction_"
    ))
    _application.add_handler(CallbackQueryHandler(
        directions.start_direction_enrollment,
        pattern=r"^enroll_"
    ))
    _application.add_handler(CallbackQueryHandler(
        admin.handle_enrollment_action,
        pattern=r"^(approve_enrollment_|reject_enrollment_)"
    ))
    _application.add_handler(CallbackQueryHandler(
        admin.show_enrollments,
        pattern=r"^admin_enrollments"
    ))
    _application.add_handler(CallbackQueryHandler(
        admin.show_admin_menu,
        pattern=r"^admin_menu"
    ))
    _application.add_handler(CallbackQueryHandler(
        lang.change_language,
        pattern=r"^lang_"
    ))
    _application.add_handler(CallbackQueryHandler(
        start.back_to_menu,
        pattern=r"^back_to_menu"
    ))
    
    # Add message handlers for menu items
    _application.add_handler(MessageHandler(
        filters.Regex(r"^📝 Записаться на курс$|^📝 Курсқа жазылу$"),
        enroll.start_enrollment
    ))
    _application.add_handler(MessageHandler(
        filters.Regex(r"^🎯 Направления$|^🎯 Бағыттар$"),
        directions.show_directions
    ))
    _application.add_handler(MessageHandler(
        filters.Regex(r"^📅 Расписание$|^📅 Кесте$"),
        schedule.show_schedule
    ))
    _application.add_handler(MessageHandler(
        filters.Regex(r"^💬 Поддержка$|^💬 Қолдау$"),
        start.support_command
    ))
    
    # Add error handler
    _application.add_error_handler(error_handler)
    
    logger.info("Telegram bot application created and configured")
    
    return _application


def create_enrollment_conversation() -> ConversationHandler:
    """Create enrollment conversation handler."""
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^📝 Записаться на курс$|^📝 Курсқа жазылу$"),
                enroll.start_enrollment
            ),
            CallbackQueryHandler(
                directions.start_direction_enrollment,
                pattern=r"^enroll_"
            )
        ],
        states={
            enroll.WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enroll.receive_name),
                CallbackQueryHandler(enroll.cancel_enrollment, pattern=r"^cancel$")
            ],
            enroll.WAITING_FOR_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enroll.receive_phone),
                CallbackQueryHandler(enroll.cancel_enrollment, pattern=r"^cancel$")
            ],
            enroll.WAITING_FOR_DIRECTION: [
                CallbackQueryHandler(enroll.receive_direction, pattern=r"^direction_"),
                CallbackQueryHandler(enroll.cancel_enrollment, pattern=r"^cancel$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(enroll.cancel_enrollment, pattern=r"^cancel$"),
            CommandHandler("start", start.start_command)
        ],
        name="enrollment_conversation",
        persistent=False
    )


def create_admin_conversation() -> ConversationHandler:
    """Create admin conversation handler."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin.start_admin)
        ],
        states={
            admin.WAITING_FOR_ADMIN_TOKEN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.receive_admin_token)
            ]
        },
        fallbacks=[
            CommandHandler("start", start.start_command)
        ],
        name="admin_conversation",
        persistent=False
    )


def create_language_conversation() -> ConversationHandler:
    """Create language selection conversation handler."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("lang", lang.show_language_menu)
        ],
        states={},
        fallbacks=[
            CallbackQueryHandler(lang.change_language, pattern=r"^lang_"),
            CallbackQueryHandler(start.back_to_menu, pattern=r"^back_to_menu$"),
            CommandHandler("start", start.start_command)
        ],
        name="language_conversation",
        persistent=False
    )


async def error_handler(update, context) -> None:
    """
    Handle errors in the bot.
    
    Args:
        update: Telegram update
        context: Bot context
    """
    logger.error(
        "Bot error occurred",
        update=update,
        error=context.error,
        exc_info=context.error
    )


def get_application() -> Application:
    """
    Get the global application instance.
    
    Returns:
        PTB Application instance
    """
    if _application is None:
        return create_application()
    return _application
