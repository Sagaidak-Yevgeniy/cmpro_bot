"""
Database repository layer (synchronous version for Windows compatibility).
Provides data access methods for all models.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, selectinload

from app.logging import get_logger
from app.models import (
    Direction,
    DirectionCode,
    Enrollment,
    EnrollmentStatus,
    Group,
    LanguageCode,
    Lesson,
    PaymentReminder,
    PaymentReminderStatus,
    Student,
)

logger = get_logger(__name__)


class StudentRepository:
    """Repository for Student model operations."""
    
    @staticmethod
    def get_by_telegram_id(session: Session, telegram_id: int) -> Optional[Student]:
        """Get student by Telegram ID."""
        return session.query(Student).filter(Student.telegram_id == telegram_id).first()
    
    @staticmethod
    def create(
        session: Session,
        telegram_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        lang: LanguageCode = LanguageCode.RUSSIAN
    ) -> Student:
        """Create a new student."""
        student = Student(
            telegram_id=telegram_id,
            full_name=full_name,
            phone=phone,
            lang=lang
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        
        logger.info("Student created", student_id=student.id, telegram_id=telegram_id)
        return student
    
    @staticmethod
    def update_language(session: Session, student: Student, lang: LanguageCode) -> Student:
        """Update student language preference."""
        student.lang = lang
        session.commit()
        session.refresh(student)
        
        logger.info("Student language updated", student_id=student.id, lang=lang.value)
        return student
    
    @staticmethod
    def update_profile(
        session: Session,
        student: Student,
        full_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Student:
        """Update student profile information."""
        if full_name is not None:
            student.full_name = full_name
        if phone is not None:
            student.phone = phone
        
        session.commit()
        session.refresh(student)
        
        logger.info("Student profile updated", student_id=student.id)
        return student


class DirectionRepository:
    """Repository for Direction model operations."""
    
    @staticmethod
    def get_all_active(session: Session) -> List[Direction]:
        """Get all active directions."""
        return session.query(Direction).filter(Direction.is_active == True).order_by(Direction.id).all()
    
    @staticmethod
    def get_by_code(session: Session, code: DirectionCode) -> Optional[Direction]:
        """Get direction by code."""
        return session.query(Direction).filter(
            and_(Direction.code == code, Direction.is_active == True)
        ).first()
    
    @staticmethod
    def get_by_id(session: Session, direction_id: int) -> Optional[Direction]:
        """Get direction by ID."""
        return session.query(Direction).filter(Direction.id == direction_id).first()


class EnrollmentRepository:
    """Repository for Enrollment model operations."""
    
    @staticmethod
    def create(
        session: Session,
        student_id: int,
        direction_id: int,
        status: EnrollmentStatus = EnrollmentStatus.PENDING
    ) -> Enrollment:
        """Create a new enrollment."""
        enrollment = Enrollment(
            student_id=student_id,
            direction_id=direction_id,
            status=status
        )
        session.add(enrollment)
        session.commit()
        session.refresh(enrollment)
        
        logger.info("Enrollment created", enrollment_id=enrollment.id, student_id=student_id)
        return enrollment
    
    @staticmethod
    def get_pending_enrollments(
        session: Session,
        limit: int = 10,
        offset: int = 0
    ) -> List[Enrollment]:
        """Get pending enrollments with pagination."""
        return session.query(Enrollment)\
            .options(selectinload(Enrollment.student), selectinload(Enrollment.direction))\
            .filter(Enrollment.status == EnrollmentStatus.PENDING)\
            .order_by(desc(Enrollment.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def get_by_student_and_direction(
        session: Session,
        student_id: int,
        direction_id: int
    ) -> Optional[Enrollment]:
        """Get enrollment by student and direction."""
        return session.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.direction_id == direction_id
            )
        ).first()
    
    @staticmethod
    def update_status(
        session: Session,
        enrollment: Enrollment,
        status: EnrollmentStatus
    ) -> Enrollment:
        """Update enrollment status."""
        enrollment.status = status
        session.commit()
        session.refresh(enrollment)
        
        logger.info("Enrollment status updated", enrollment_id=enrollment.id, status=status.value)
        return enrollment
    
    @staticmethod
    def count_pending(session: Session) -> int:
        """Count pending enrollments."""
        return session.query(Enrollment).filter(
            Enrollment.status == EnrollmentStatus.PENDING
        ).count()


class GroupRepository:
    """Repository for Group model operations."""
    
    @staticmethod
    def get_by_direction(session: Session, direction_id: int) -> List[Group]:
        """Get groups by direction."""
        return session.query(Group)\
            .filter(and_(Group.direction_id == direction_id, Group.is_active == True))\
            .order_by(Group.id)\
            .all()


class LessonRepository:
    """Repository for Lesson model operations."""
    
    @staticmethod
    def get_upcoming_lessons(
        session: Session,
        limit: int = 5
    ) -> List[Lesson]:
        """Get upcoming lessons."""
        now = datetime.utcnow()
        return session.query(Lesson)\
            .options(selectinload(Lesson.group).selectinload(Group.direction))\
            .filter(Lesson.starts_at > now)\
            .order_by(Lesson.starts_at)\
            .limit(limit)\
            .all()


class PaymentReminderRepository:
    """Repository for PaymentReminder model operations."""
    
    @staticmethod
    def get_pending_reminders(session: Session) -> List[PaymentReminder]:
        """Get pending payment reminders that are due."""
        now = datetime.utcnow()
        return session.query(PaymentReminder)\
            .options(selectinload(PaymentReminder.student))\
            .filter(
                and_(
                    PaymentReminder.status == PaymentReminderStatus.PENDING,
                    PaymentReminder.due_at <= now
                )
            )\
            .order_by(PaymentReminder.due_at)\
            .all()
    
    @staticmethod
    def create(
        session: Session,
        student_id: int,
        due_at: datetime,
        status: PaymentReminderStatus = PaymentReminderStatus.PENDING
    ) -> PaymentReminder:
        """Create a new payment reminder."""
        reminder = PaymentReminder(
            student_id=student_id,
            due_at=due_at,
            status=status
        )
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        
        logger.info("Payment reminder created", reminder_id=reminder.id, student_id=student_id)
        return reminder
    
    @staticmethod
    def update_status(
        session: Session,
        reminder: PaymentReminder,
        status: PaymentReminderStatus
    ) -> PaymentReminder:
        """Update payment reminder status."""
        reminder.status = status
        session.commit()
        session.refresh(reminder)
        
        logger.info("Payment reminder status updated", reminder_id=reminder.id, status=status.value)
        return reminder
