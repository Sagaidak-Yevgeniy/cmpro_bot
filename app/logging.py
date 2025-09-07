"""
Structured logging configuration using structlog.
Provides consistent logging across the application.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory


def configure_logging(environment: str = "production") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        environment: Environment name (development/production)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if environment == "production" else logging.DEBUG,
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if environment == "development":
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_telegram_update(update_id: int, user_id: int, message_type: str, **kwargs: Any) -> None:
    """
    Log Telegram update with structured data.
    
    Args:
        update_id: Telegram update ID
        user_id: Telegram user ID
        message_type: Type of message (text, callback_query, etc.)
        **kwargs: Additional context data
    """
    logger = get_logger("telegram.update")
    logger.info(
        "Telegram update received",
        update_id=update_id,
        user_id=user_id,
        message_type=message_type,
        **kwargs
    )


def log_database_operation(operation: str, table: str, **kwargs: Any) -> None:
    """
    Log database operations with structured data.
    
    Args:
        operation: Database operation (create, read, update, delete)
        table: Database table name
        **kwargs: Additional context data
    """
    logger = get_logger("database.operation")
    logger.info(
        "Database operation",
        operation=operation,
        table=table,
        **kwargs
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log errors with structured context.
    
    Args:
        error: Exception instance
        context: Additional context data
    """
    logger = get_logger("error")
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {})
    )
