"""
Database repository layer.
Provides data access methods for all models.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[Student]:
        """Get student by Telegram ID."""
        result = await session.execute(
            select(Student).where(Student.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        session: AsyncSession,
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
        await session.commit()
        await session.refresh(student)
        
        logger.info("Student created", student_id=student.id, telegram_id=telegram_id)
        return student
    
    @staticmethod
    async def update_language(session: AsyncSession, student: Student, lang: LanguageCode) -> Student:
        """Update student language preference."""
        student.lang = lang
        await session.commit()
        await session.refresh(student)
        
        logger.info("Student language updated", student_id=student.id, lang=lang.value)
        return student
    
    @staticmethod
    async def update_profile(
        session: AsyncSession,
        student: Student,
        full_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Student:
        """Update student profile information."""
        if full_name is not None:
            student.full_name = full_name
        if phone is not None:
            student.phone = phone
        
        await session.commit()
        await session.refresh(student)
        
        logger.info("Student profile updated", student_id=student.id)
        return student


class DirectionRepository:
    """Repository for Direction model operations."""
    
    @staticmethod
    async def get_all_active(session: AsyncSession) -> List[Direction]:
        """Get all active directions."""
        result = await session.execute(
            select(Direction).where(Direction.is_active == True).order_by(Direction.id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_code(session: AsyncSession, code: DirectionCode) -> Optional[Direction]:
        """Get direction by code."""
        result = await session.execute(
            select(Direction).where(
                and_(Direction.code == code, Direction.is_active == True)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, direction_id: int) -> Optional[Direction]:
        """Get direction by ID."""
        result = await session.execute(
            select(Direction).where(Direction.id == direction_id)
        )
        return result.scalar_one_or_none()


class EnrollmentRepository:
    """Repository for Enrollment model operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
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
        await session.commit()
        await session.refresh(enrollment)
        
        logger.info("Enrollment created", enrollment_id=enrollment.id, student_id=student_id)
        return enrollment
    
    @staticmethod
    async def get_pending_enrollments(
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Enrollment]:
        """Get pending enrollments with pagination."""
        result = await session.execute(
            select(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.direction)
            )
            .where(Enrollment.status == EnrollmentStatus.PENDING)
            .order_by(desc(Enrollment.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_student_and_direction(
        session: AsyncSession,
        student_id: int,
        direction_id: int
    ) -> Optional[Enrollment]:
        """Get enrollment by student and direction."""
        result = await session.execute(
            select(Enrollment).where(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.direction_id == direction_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_status(
        session: AsyncSession,
        enrollment: Enrollment,
        status: EnrollmentStatus
    ) -> Enrollment:
        """Update enrollment status."""
        enrollment.status = status
        await session.commit()
        await session.refresh(enrollment)
        
        logger.info("Enrollment status updated", enrollment_id=enrollment.id, status=status.value)
        return enrollment
    
    @staticmethod
    async def count_pending(session: AsyncSession) -> int:
        """Count pending enrollments."""
        result = await session.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.status == EnrollmentStatus.PENDING
            )
        )
        return result.scalar() or 0


class GroupRepository:
    """Repository for Group model operations."""
    
    @staticmethod
    async def get_by_direction(session: AsyncSession, direction_id: int) -> List[Group]:
        """Get groups by direction."""
        result = await session.execute(
            select(Group)
            .where(and_(Group.direction_id == direction_id, Group.is_active == True))
            .order_by(Group.id)
        )
        return list(result.scalars().all())


class LessonRepository:
    """Repository for Lesson model operations."""
    
    @staticmethod
    async def get_upcoming_lessons(
        session: AsyncSession,
        limit: int = 5
    ) -> List[Lesson]:
        """Get upcoming lessons."""
        now = datetime.utcnow()
        result = await session.execute(
            select(Lesson)
            .options(selectinload(Lesson.group).selectinload(Group.direction))
            .where(Lesson.starts_at > now)
            .order_by(Lesson.starts_at)
            .limit(limit)
        )
        return list(result.scalars().all())


class PaymentReminderRepository:
    """Repository for PaymentReminder model operations."""
    
    @staticmethod
    async def get_pending_reminders(session: AsyncSession) -> List[PaymentReminder]:
        """Get pending payment reminders that are due."""
        now = datetime.utcnow()
        result = await session.execute(
            select(PaymentReminder)
            .options(selectinload(PaymentReminder.student))
            .where(
                and_(
                    PaymentReminder.status == PaymentReminderStatus.PENDING,
                    PaymentReminder.due_at <= now
                )
            )
            .order_by(PaymentReminder.due_at)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(
        session: AsyncSession,
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
        await session.commit()
        await session.refresh(reminder)
        
        logger.info("Payment reminder created", reminder_id=reminder.id, student_id=student_id)
        return reminder
    
    @staticmethod
    async def update_status(
        session: AsyncSession,
        reminder: PaymentReminder,
        status: PaymentReminderStatus
    ) -> PaymentReminder:
        """Update payment reminder status."""
        reminder.status = status
        await session.commit()
        await session.refresh(reminder)
        
        logger.info("Payment reminder status updated", reminder_id=reminder.id, status=status.value)
        return reminder
