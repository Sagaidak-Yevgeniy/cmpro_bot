"""
Упрощенные модели SQLAlchemy для совместимости с Vercel.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DirectionCode(PyEnum):
    """Available programming directions."""
    PYTHON = "python"
    JAVASCRIPT = "js"
    GO = "go"
    DATA_ANALYTICS = "da"


class EnrollmentStatus(PyEnum):
    """Enrollment status options."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentReminderStatus(PyEnum):
    """Payment reminder status options."""
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"


class LanguageCode(PyEnum):
    """Supported languages."""
    RUSSIAN = "ru"
    KAZAKH = "kk"


class Student(Base):
    """Student model representing bot users."""
    
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    lang = Column(
        Enum(LanguageCode), 
        default=LanguageCode.RUSSIAN,
        nullable=False
    )
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    enrollments = relationship(
        "Enrollment", 
        back_populates="student",
        cascade="all, delete-orphan"
    )
    payment_reminders = relationship(
        "PaymentReminder", 
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Direction(Base):
    """Programming direction model."""
    
    __tablename__ = "directions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(
        Enum(DirectionCode), 
        unique=True, 
        nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    enrollments = relationship(
        "Enrollment", 
        back_populates="direction"
    )
    groups = relationship(
        "Group", 
        back_populates="direction",
        cascade="all, delete-orphan"
    )


class Group(Base):
    """Study group model."""
    
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    direction_id = Column(
        ForeignKey("directions.id"), 
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    direction = relationship("Direction", back_populates="groups")
    lessons = relationship(
        "Lesson", 
        back_populates="group",
        cascade="all, delete-orphan"
    )


class Lesson(Base):
    """Lesson model for schedule."""
    
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    group = relationship("Group", back_populates="lessons")


class Enrollment(Base):
    """Student enrollment model."""
    
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        ForeignKey("students.id"), 
        nullable=False
    )
    direction_id = Column(
        ForeignKey("directions.id"), 
        nullable=False
    )
    status = Column(
        Enum(EnrollmentStatus), 
        default=EnrollmentStatus.PENDING,
        nullable=False
    )
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    direction = relationship("Direction", back_populates="enrollments")


class PaymentReminder(Base):
    """Payment reminder model."""
    
    __tablename__ = "payment_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        ForeignKey("students.id"), 
        nullable=False
    )
    due_at = Column(DateTime, nullable=False)
    status = Column(
        Enum(PaymentReminderStatus), 
        default=PaymentReminderStatus.PENDING,
        nullable=False
    )
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    student = relationship("Student", back_populates="payment_reminders")
