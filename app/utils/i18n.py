"""
Internationalization utility functions.
Handles loading and accessing translations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

# Cache for loaded translations
_translations_cache: Dict[str, Dict[str, Any]] = {}


def load_translations() -> None:
    """Load all translation files into cache."""
    i18n_dir = Path(__file__).parent.parent / "i18n"
    
    for lang_file in i18n_dir.glob("*.json"):
        lang_code = lang_file.stem
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations_cache[lang_code] = json.load(f)
            logger.info("Loaded translations", language=lang_code)
        except Exception as e:
            logger.error("Failed to load translations", language=lang_code, error=str(e))


def get_translation(key: str, lang: str = None, **kwargs: Any) -> str:
    """
    Get translation for a key.
    
    Args:
        key: Translation key (dot-separated path)
        lang: Language code (defaults to settings default)
        **kwargs: Variables to format into the translation
        
    Returns:
        Translated string
    """
    if not _translations_cache:
        load_translations()
    
    if lang is None:
        lang = settings.default_lang
    
    # Get translation data
    translations = _translations_cache.get(lang, {})
    if not translations:
        # Fallback to default language
        translations = _translations_cache.get(settings.default_lang, {})
    
    # Navigate through nested keys
    value = translations
    for part in key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            # Key not found, return the key itself
            logger.warning("Translation key not found", key=key, language=lang)
            return key
    
    # Format with provided variables
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.error("Failed to format translation", key=key, error=str(e))
            return value
    
    return str(value)


def get_available_languages() -> list[str]:
    """
    Get list of available language codes.
    
    Returns:
        List of language codes
    """
    if not _translations_cache:
        load_translations()
    
    return list(_translations_cache.keys())


def is_language_supported(lang: str) -> bool:
    """
    Check if language is supported.
    
    Args:
        lang: Language code to check
        
    Returns:
        True if language is supported
    """
    return lang in get_available_languages()


# Initialize translations on import
load_translations()
