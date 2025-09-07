"""
Telegram bot middlewares for rate limiting and i18n.
"""

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.logging import get_logger
from app.models import LanguageCode
from app.utils.i18n import get_translation
from app.bot.services.repo import StudentRepository
from app.db import get_async_db

logger = get_logger(__name__)

# In-memory rate limiting storage (for serverless, consider Redis in production)
_rate_limit_storage: Dict[int, Dict[str, float]] = defaultdict(dict)


class RateLimitMiddleware:
    """Rate limiting middleware for Telegram updates."""
    
    def __init__(self, max_requests_per_minute: int = None):
        self.max_requests = max_requests_per_minute or settings.rate_limit_per_minute
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]]
    ) -> Any:
        """Apply rate limiting to the update."""
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_id:
            return await next_handler(update, context)
        
        current_time = time.time()
        user_requests = _rate_limit_storage[user_id]
        
        # Clean old requests (older than 1 minute)
        minute_ago = current_time - 60
        user_requests = {
            timestamp: timestamp for timestamp in user_requests.values()
            if timestamp > minute_ago
        }
        _rate_limit_storage[user_id] = user_requests
        
        # Check rate limit
        if len(user_requests) >= self.max_requests:
            logger.warning(
                "Rate limit exceeded",
                user_id=user_id,
                requests_count=len(user_requests),
                limit=self.max_requests
            )
            
            # Send rate limit message
            if update.message:
                await update.message.reply_text(
                    get_translation("errors.general", lang="ru")
                )
            return
        
        # Record this request
        _rate_limit_storage[user_id][current_time] = current_time
        
        # Continue to next handler
        return await next_handler(update, context)


class I18nMiddleware:
    """Internationalization middleware for setting user language context."""
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]]
    ) -> Any:
        """Set user language context."""
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_id:
            context.user_data["lang"] = settings.default_lang
            return await next_handler(update, context)
        
        # Try to get user language from database
        try:
            async with get_async_db() as session:
                student = await StudentRepository.get_by_telegram_id(session, user_id)
                if student:
                    context.user_data["lang"] = student.lang.value
                else:
                    context.user_data["lang"] = settings.default_lang
        except Exception as e:
            logger.error("Failed to get user language", user_id=user_id, error=str(e))
            context.user_data["lang"] = settings.default_lang
        
        return await next_handler(update, context)


class LoggingMiddleware:
    """Logging middleware for tracking updates."""
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]]
    ) -> Any:
        """Log update information."""
        user_id = update.effective_user.id if update.effective_user else None
        chat_id = update.effective_chat.id if update.effective_chat else None
        
        # Determine message type
        message_type = "unknown"
        if update.message:
            if update.message.text:
                message_type = "text"
            elif update.message.photo:
                message_type = "photo"
            elif update.message.document:
                message_type = "document"
        elif update.callback_query:
            message_type = "callback_query"
        elif update.inline_query:
            message_type = "inline_query"
        
        logger.info(
            "Telegram update received",
            update_id=update.update_id,
            user_id=user_id,
            chat_id=chat_id,
            message_type=message_type
        )
        
        try:
            result = await next_handler(update, context)
            logger.info(
                "Update processed successfully",
                update_id=update.update_id,
                user_id=user_id
            )
            return result
        except Exception as e:
            logger.error(
                "Update processing failed",
                update_id=update.update_id,
                user_id=user_id,
                error=str(e)
            )
            raise


# Global middleware instances
rate_limit_middleware = RateLimitMiddleware()
i18n_middleware = I18nMiddleware()
logging_middleware = LoggingMiddleware()


def get_user_language(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get user language from context.
    
    Args:
        context: Bot context
        
    Returns:
        Language code
    """
    return context.user_data.get("lang", settings.default_lang)


def get_translation_for_user(key: str, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> str:
    """
    Get translation for user's language.
    
    Args:
        key: Translation key
        context: Bot context
        **kwargs: Format variables
        
    Returns:
        Translated string
    """
    lang = get_user_language(context)
    return get_translation(key, lang=lang, **kwargs)
