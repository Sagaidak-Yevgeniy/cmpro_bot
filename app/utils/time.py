"""
Time utility functions for handling timezone and date formatting.
"""

from datetime import datetime, timezone
from typing import Optional

import pytz
from dateutil import parser

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

# Application timezone
APP_TIMEZONE = pytz.timezone(settings.timezone)


def get_current_time() -> datetime:
    """
    Get current time in application timezone.
    
    Returns:
        Current datetime in app timezone
    """
    return datetime.now(APP_TIMEZONE)


def utc_to_app_time(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to application timezone.
    
    Args:
        utc_dt: UTC datetime
        
    Returns:
        Datetime in application timezone
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    return utc_dt.astimezone(APP_TIMEZONE)


def app_time_to_utc(app_dt: datetime) -> datetime:
    """
    Convert application timezone datetime to UTC.
    
    Args:
        app_dt: Datetime in application timezone
        
    Returns:
        UTC datetime
    """
    if app_dt.tzinfo is None:
        app_dt = APP_TIMEZONE.localize(app_dt)
    
    return app_dt.astimezone(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    if dt.tzinfo is None:
        dt = APP_TIMEZONE.localize(dt)
    elif dt.tzinfo != APP_TIMEZONE:
        dt = dt.astimezone(APP_TIMEZONE)
    
    return dt.strftime(format_str)


def format_date(dt: datetime) -> str:
    """
    Format date for display.
    
    Args:
        dt: Datetime to format
        
    Returns:
        Formatted date string
    """
    return format_datetime(dt, "%d.%m.%Y")


def format_time(dt: datetime) -> str:
    """
    Format time for display.
    
    Args:
        dt: Datetime to format
        
    Returns:
        Formatted time string
    """
    return format_datetime(dt, "%H:%M")


def parse_datetime_string(dt_str: str) -> Optional[datetime]:
    """
    Parse datetime string with timezone handling.
    
    Args:
        dt_str: Datetime string to parse
        
    Returns:
        Parsed datetime or None if invalid
    """
    try:
        dt = parser.parse(dt_str)
        if dt.tzinfo is None:
            dt = APP_TIMEZONE.localize(dt)
        return dt
    except (ValueError, TypeError) as e:
        logger.error("Failed to parse datetime string", dt_str=dt_str, error=str(e))
        return None


def is_future_datetime(dt: datetime) -> bool:
    """
    Check if datetime is in the future.
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if datetime is in the future
    """
    current = get_current_time()
    if dt.tzinfo is None:
        dt = APP_TIMEZONE.localize(dt)
    elif dt.tzinfo != APP_TIMEZONE:
        dt = dt.astimezone(APP_TIMEZONE)
    
    return dt > current


def get_time_until(dt: datetime) -> str:
    """
    Get human-readable time until datetime.
    
    Args:
        dt: Target datetime
        
    Returns:
        Human-readable time string
    """
    current = get_current_time()
    if dt.tzinfo is None:
        dt = APP_TIMEZONE.localize(dt)
    elif dt.tzinfo != APP_TIMEZONE:
        dt = dt.astimezone(APP_TIMEZONE)
    
    delta = dt - current
    
    if delta.total_seconds() < 0:
        return "Прошло"
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    
    if not parts:
        return "Сейчас"
    
    return " ".join(parts)
