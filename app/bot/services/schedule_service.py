"""
Schedule service for handling lesson and schedule operations.
"""

from typing import List

from sqlalchemy.orm import Session

from app.logging import get_logger
from app.models import LanguageCode
from app.utils.i18n import get_translation
from app.utils.time import format_date, format_time
from app.bot.services.repo_sync import LessonRepository

logger = get_logger(__name__)


class ScheduleService:
    """Service for handling schedule operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_upcoming_lessons(self, limit: int = 5) -> List:
        """
        Get upcoming lessons.
        
        Args:
            limit: Maximum number of lessons to return
            
        Returns:
            List of Lesson objects
        """
        return LessonRepository.get_upcoming_lessons(self.session, limit)
    
    def format_lessons_for_display(self, lessons: List, lang: LanguageCode = LanguageCode.RUSSIAN) -> str:
        """
        Format lessons for display in Telegram.
        
        Args:
            lessons: List of Lesson objects
            lang: Language for translations
            
        Returns:
            Formatted string with lessons
        """
        if not lessons:
            return get_translation("schedule.no_lessons", lang=lang.value)
        
        title = get_translation("schedule.title", lang=lang.value)
        lesson_format = get_translation("schedule.lesson_format", lang=lang.value)
        
        formatted_lessons = []
        for lesson in lessons:
            formatted_lesson = lesson_format.format(
                topic=lesson.topic,
                group=lesson.group.title,
                start_time=format_time(lesson.starts_at),
                end_time=format_time(lesson.ends_at),
                date=format_date(lesson.starts_at)
            )
            formatted_lessons.append(formatted_lesson)
        
        return f"{title}\n\n" + "\n\n".join(formatted_lessons)
