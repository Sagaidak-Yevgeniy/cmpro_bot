"""
Enrollment service for handling student enrollment logic.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models import DirectionCode, EnrollmentStatus, LanguageCode, Student
from app.utils.i18n import get_translation
from app.bot.services.repo import (
    DirectionRepository,
    EnrollmentRepository,
    StudentRepository,
)

logger = get_logger(__name__)


class EnrollmentService:
    """Service for handling enrollment operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_student(
        self,
        telegram_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        lang: LanguageCode = LanguageCode.RUSSIAN
    ) -> Student:
        """
        Get existing student or create new one.
        
        Args:
            telegram_id: Telegram user ID
            full_name: Student's full name
            phone: Student's phone number
            lang: Student's language preference
            
        Returns:
            Student instance
        """
        student = await StudentRepository.get_by_telegram_id(self.session, telegram_id)
        
        if not student:
            student = await StudentRepository.create(
                self.session,
                telegram_id=telegram_id,
                full_name=full_name,
                phone=phone,
                lang=lang
            )
        else:
            # Update existing student if new data provided
            if full_name or phone:
                await StudentRepository.update_profile(
                    self.session,
                    student,
                    full_name=full_name,
                    phone=phone
                )
        
        return student
    
    async def enroll_student(
        self,
        student: Student,
        direction_code: DirectionCode
    ) -> tuple[bool, str]:
        """
        Enroll student in a direction.
        
        Args:
            student: Student instance
            direction_code: Direction code to enroll in
            
        Returns:
            Tuple of (success, message)
        """
        # Get direction
        direction = await DirectionRepository.get_by_code(self.session, direction_code)
        if not direction:
            message = get_translation("errors.general", lang=student.lang.value)
            return False, message
        
        # Check if already enrolled
        existing_enrollment = await EnrollmentRepository.get_by_student_and_direction(
            self.session,
            student.id,
            direction.id
        )
        
        if existing_enrollment:
            if existing_enrollment.status == EnrollmentStatus.PENDING:
                message = get_translation("enroll.already_enrolled", lang=student.lang.value)
                return False, message
            elif existing_enrollment.status == EnrollmentStatus.APPROVED:
                message = get_translation("enroll.already_enrolled", lang=student.lang.value)
                return False, message
        
        # Create new enrollment
        await EnrollmentRepository.create(
            self.session,
            student_id=student.id,
            direction_id=direction.id,
            status=EnrollmentStatus.PENDING
        )
        
        message = get_translation("enroll.direction_received", lang=student.lang.value)
        return True, message
    
    async def get_available_directions(self) -> list:
        """
        Get all available directions.
        
        Returns:
            List of Direction objects
        """
        return await DirectionRepository.get_all_active(self.session)
    
    async def get_direction_by_code(self, code: DirectionCode):
        """
        Get direction by code.
        
        Args:
            code: Direction code
            
        Returns:
            Direction object or None
        """
        return await DirectionRepository.get_by_code(self.session, code)
