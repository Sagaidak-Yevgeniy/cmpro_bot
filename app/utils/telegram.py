"""
Telegram bot utility functions.
Provides helpers for common Telegram operations.
"""

import json
from typing import Any, Dict, List, Optional, Union

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from app.logging import get_logger

logger = get_logger(__name__)


def get_user_id(update: Update) -> Optional[int]:
    """
    Extract user ID from Telegram update.
    
    Args:
        update: Telegram update object
        
    Returns:
        User ID or None if not found
    """
    if update.effective_user:
        return update.effective_user.id
    return None


def get_chat_id(update: Update) -> Optional[int]:
    """
    Extract chat ID from Telegram update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Chat ID or None if not found
    """
    if update.effective_chat:
        return update.effective_chat.id
    return None


def get_message_text(update: Update) -> Optional[str]:
    """
    Extract message text from Telegram update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Message text or None if not found
    """
    if update.message and update.message.text:
        return update.message.text
    if update.callback_query and update.callback_query.data:
        return update.callback_query.data
    return None


def create_reply_keyboard(buttons: List[List[str]], resize_keyboard: bool = True) -> ReplyKeyboardMarkup:
    """
    Create a reply keyboard markup.
    
    Args:
        buttons: List of button rows
        resize_keyboard: Whether to resize keyboard
        
    Returns:
        ReplyKeyboardMarkup object
    """
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )


def create_inline_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard markup.
    
    Args:
        buttons: List of button rows, each containing dicts with 'text' and 'callback_data'
        
    Returns:
        InlineKeyboardMarkup object
    """
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append(
                InlineKeyboardButton(
                    text=button["text"],
                    callback_data=button["callback_data"]
                )
            )
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)


def create_pagination_keyboard(
    current_page: int,
    total_pages: int,
    base_callback: str,
    extra_data: Optional[Dict[str, Any]] = None
) -> InlineKeyboardMarkup:
    """
    Create pagination keyboard.
    
    Args:
        current_page: Current page number (0-based)
        total_pages: Total number of pages
        base_callback: Base callback data
        extra_data: Additional data to include in callback
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    buttons = []
    
    # Previous button
    if current_page > 0:
        prev_data = {
            "action": base_callback,
            "page": current_page - 1,
            **(extra_data or {})
        }
        buttons.append([{
            "text": "⬅️ Предыдущая",
            "callback_data": json.dumps(prev_data)
        }])
    
    # Page info
    page_info = f"Страница {current_page + 1} из {total_pages}"
    buttons.append([{"text": page_info, "callback_data": "page_info"}])
    
    # Next button
    if current_page < total_pages - 1:
        next_data = {
            "action": base_callback,
            "page": current_page + 1,
            **(extra_data or {})
        }
        buttons.append([{
            "text": "➡️ Следующая",
            "callback_data": json.dumps(next_data)
        }])
    
    # Close button
    buttons.append([{"text": "❌ Закрыть", "callback_data": "close"}])
    
    return create_inline_keyboard(buttons)


async def safe_reply_text(
    update: Update,
    text: str,
    reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]] = None,
    parse_mode: Optional[str] = None
) -> Optional[Message]:
    """
    Safely send a text message with error handling.
    
    Args:
        update: Telegram update object
        text: Message text
        reply_markup: Optional keyboard markup
        parse_mode: Optional parse mode
        
    Returns:
        Sent message or None if failed
    """
    try:
        if update.callback_query:
            await update.callback_query.answer()
            return await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            return await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except Exception as e:
        logger.error("Failed to send message", error=str(e), user_id=get_user_id(update))
        return None


async def safe_edit_message(
    update: Update,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None
) -> Optional[Message]:
    """
    Safely edit a message with error handling.
    
    Args:
        update: Telegram update object
        text: New message text
        reply_markup: Optional keyboard markup
        parse_mode: Optional parse mode
        
    Returns:
        Edited message or None if failed
    """
    try:
        if update.callback_query:
            await update.callback_query.answer()
            return await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            return await update.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except Exception as e:
        logger.error("Failed to edit message", error=str(e), user_id=get_user_id(update))
        return None


def parse_callback_data(callback_data: str) -> Dict[str, Any]:
    """
    Parse callback data JSON.
    
    Args:
        callback_data: Callback data string
        
    Returns:
        Parsed data dictionary
    """
    try:
        return json.loads(callback_data)
    except (json.JSONDecodeError, TypeError):
        return {"action": callback_data}


def format_user_info(user) -> str:
    """
    Format user information for display.
    
    Args:
        user: Telegram user object
        
    Returns:
        Formatted user info string
    """
    if not user:
        return "Неизвестный пользователь"
    
    name_parts = []
    if user.first_name:
        name_parts.append(user.first_name)
    if user.last_name:
        name_parts.append(user.last_name)
    
    name = " ".join(name_parts) if name_parts else "Без имени"
    username = f"@{user.username}" if user.username else "Без username"
    
    return f"{name} ({username})"


def is_phone_valid(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid, False otherwise
    """
    import re
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it starts with + and has 10-15 digits
    if not cleaned.startswith('+'):
        return False
    
    digits = cleaned[1:]  # Remove +
    if not digits.isdigit():
        return False
    
    return 10 <= len(digits) <= 15
