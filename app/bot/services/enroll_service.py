"""
Enrollment service for handling student enrollment logic.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.logging import get_logger
from app.models_simple import DirectionCode, EnrollmentStatus, LanguageCode, Student
from app.utils.i18n import get_translation
from app.bot.services.repo_sync import (
    DirectionRepository,
    EnrollmentRepository,
    StudentRepository,
)

logger = get_logger(__name__)


class EnrollmentService:
    """Service for handling enrollment operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_or_create_student(
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
        student = StudentRepository.get_by_telegram_id(self.session, telegram_id)
        
        if not student:
            student = StudentRepository.create(
                self.session,
                telegram_id=telegram_id,
                full_name=full_name,
                phone=phone,
                lang=lang
            )
        else:
            # Update existing student if new data provided
            if full_name or phone:
                StudentRepository.update_profile(
                    self.session,
                    student,
                    full_name=full_name,
                    phone=phone
                )
        
        return student
    
    def enroll_student(
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
        direction = DirectionRepository.get_by_code(self.session, direction_code)
        if not direction:
            message = get_translation("errors.general", lang=student.lang.value)
            return False, message
        
        # Check if already enrolled
        existing_enrollment = EnrollmentRepository.get_by_student_and_direction(
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
        EnrollmentRepository.create(
            self.session,
            student_id=student.id,
            direction_id=direction.id,
            status=EnrollmentStatus.PENDING
        )
        
        message = get_translation("enroll.direction_received", lang=student.lang.value)
        return True, message
    
    def get_available_directions(self) -> list:
        """
        Get all available directions.
        
        Returns:
            List of Direction objects
        """
        return DirectionRepository.get_all_active(self.session)
    
    def get_direction_by_code(self, code: DirectionCode):
        """
        Get direction by code.
        
        Args:
            code: Direction code
            
        Returns:
            Direction object or None
        """
        return DirectionRepository.get_by_code(self.session, code)
