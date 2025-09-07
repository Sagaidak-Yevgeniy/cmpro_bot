"""
Keyboard helpers for Telegram bot.
Provides pre-built keyboards for different bot states.
"""

from typing import List, Optional

from app.models import Direction, DirectionCode, LanguageCode
from app.utils.i18n import get_translation
from app.utils.telegram import create_inline_keyboard, create_reply_keyboard


def get_main_menu_keyboard(lang: str = "ru") -> List[List[str]]:
    """
    Get main menu reply keyboard.
    
    Args:
        lang: Language code
        
    Returns:
        Keyboard layout
    """
    return [
        [
            get_translation("menu.enroll", lang=lang),
            get_translation("menu.directions", lang=lang)
        ],
        [
            get_translation("menu.schedule", lang=lang),
            get_translation("menu.support", lang=lang)
        ]
    ]


def get_directions_keyboard(directions: List[Direction], lang: str = "ru") -> List[List[dict]]:
    """
    Get directions inline keyboard.
    
    Args:
        directions: List of Direction objects
        lang: Language code
        
    Returns:
        Inline keyboard layout
    """
    keyboard = []
    
    for direction in directions:
        direction_key = f"directions.{direction.code.value}"
        title = get_translation(f"{direction_key}.title", lang=lang)
        
        keyboard.append([{
            "text": title,
            "callback_data": f"direction_{direction.code.value}"
        }])
    
    # Add back button
    keyboard.append([{
        "text": get_translation("buttons.back", lang=lang),
        "callback_data": "back_to_menu"
    }])
    
    return keyboard


def get_direction_enroll_keyboard(direction_code: DirectionCode, lang: str = "ru") -> List[List[dict]]:
    """
    Get direction enrollment keyboard.
    
    Args:
        direction_code: Direction code
        lang: Language code
        
    Returns:
        Inline keyboard layout
    """
    direction_key = f"directions.{direction_code.value}"
    enroll_text = get_translation("directions.enroll_button", lang=lang, direction=get_translation(f"{direction_key}.title", lang=lang))
    
    return [
        [{
            "text": enroll_text,
            "callback_data": f"enroll_{direction_code.value}"
        }],
        [{
            "text": get_translation("buttons.back", lang=lang),
            "callback_data": "back_to_directions"
        }]
    ]


def get_language_keyboard(lang: str = "ru") -> List[List[dict]]:
    """
    Get language selection keyboard.
    
    Args:
        lang: Current language
        
    Returns:
        Inline keyboard layout
    """
    return [
        [
            {
                "text": get_translation("lang.ru", lang=lang),
                "callback_data": "lang_ru"
            },
            {
                "text": get_translation("lang.kk", lang=lang),
                "callback_data": "lang_kk"
            }
        ],
        [{
            "text": get_translation("buttons.back", lang=lang),
            "callback_data": "back_to_menu"
        }]
    ]


def get_admin_menu_keyboard(lang: str = "ru") -> List[List[dict]]:
    """
    Get admin menu keyboard.
    
    Args:
        lang: Language code
        
    Returns:
        Inline keyboard layout
    """
    return [
        [{
            "text": get_translation("admin.enrollments", lang=lang),
            "callback_data": "admin_enrollments"
        }],
        [
            {
                "text": get_translation("admin.students", lang=lang),
                "callback_data": "admin_students"
            },
            {
                "text": get_translation("admin.groups", lang=lang),
                "callback_data": "admin_groups"
            }
        ],
        [
            {
                "text": get_translation("admin.schedule", lang=lang),
                "callback_data": "admin_schedule"
            },
            {
                "text": get_translation("admin.reminders", lang=lang),
                "callback_data": "admin_reminders"
            }
        ],
        [{
            "text": get_translation("buttons.back", lang=lang),
            "callback_data": "back_to_menu"
        }]
    ]


def get_enrollment_actions_keyboard(enrollment_id: int, lang: str = "ru") -> List[List[dict]]:
    """
    Get enrollment action keyboard for admin.
    
    Args:
        enrollment_id: Enrollment ID
        lang: Language code
        
    Returns:
        Inline keyboard layout
    """
    return [
        [
            {
                "text": get_translation("admin.approve", lang=lang),
                "callback_data": f"approve_enrollment_{enrollment_id}"
            },
            {
                "text": get_translation("admin.reject", lang=lang),
                "callback_data": f"reject_enrollment_{enrollment_id}"
            }
        ],
        [{
            "text": get_translation("buttons.back", lang=lang),
            "callback_data": "admin_enrollments"
        }]
    ]


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    base_action: str,
    lang: str = "ru",
    extra_data: Optional[dict] = None
) -> List[List[dict]]:
    """
    Get pagination keyboard.
    
    Args:
        current_page: Current page number (0-based)
        total_pages: Total number of pages
        base_action: Base action for pagination
        lang: Language code
        extra_data: Additional data for callback
        
    Returns:
        Inline keyboard layout
    """
    keyboard = []
    
    # Previous button
    if current_page > 0:
        prev_data = f"{base_action}_page_{current_page - 1}"
        if extra_data:
            prev_data += f"_{extra_data}"
        keyboard.append([{
            "text": get_translation("buttons.prev", lang=lang),
            "callback_data": prev_data
        }])
    
    # Page info
    page_info = f"{current_page + 1}/{total_pages}"
    keyboard.append([{
        "text": page_info,
        "callback_data": "page_info"
    }])
    
    # Next button
    if current_page < total_pages - 1:
        next_data = f"{base_action}_page_{current_page + 1}"
        if extra_data:
            next_data += f"_{extra_data}"
        keyboard.append([{
            "text": get_translation("buttons.next", lang=lang),
            "callback_data": next_data
        }])
    
    # Close button
    keyboard.append([{
        "text": get_translation("buttons.close", lang=lang),
        "callback_data": "close"
    }])
    
    return keyboard


def get_cancel_keyboard(lang: str = "ru") -> List[List[dict]]:
    """
    Get cancel keyboard for conversations.
    
    Args:
        lang: Language code
        
    Returns:
        Inline keyboard layout
    """
    return [
        [{
            "text": get_translation("buttons.cancel", lang=lang),
            "callback_data": "cancel"
        }]
    ]
