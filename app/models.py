"""
SQLAlchemy ORM models for the CodeMastersPRO bot.
Defines all database tables and relationships.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lang: Mapped[LanguageCode] = mapped_column(
        Enum(LanguageCode), 
        default=LanguageCode.RUSSIAN,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", 
        back_populates="student",
        cascade="all, delete-orphan"
    )
    payment_reminders: Mapped[List["PaymentReminder"]] = relationship(
        "PaymentReminder", 
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Direction(Base):
    """Programming direction model."""
    
    __tablename__ = "directions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[DirectionCode] = mapped_column(
        Enum(DirectionCode), 
        unique=True, 
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", 
        back_populates="direction"
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group", 
        back_populates="direction",
        cascade="all, delete-orphan"
    )


class Group(Base):
    """Study group model."""
    
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id"), 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    direction: Mapped["Direction"] = relationship("Direction", back_populates="groups")
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", 
        back_populates="group",
        cascade="all, delete-orphan"
    )


class Lesson(Base):
    """Lesson model for schedule."""
    
    __tablename__ = "lessons"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="lessons")


class Enrollment(Base):
    """Student enrollment model."""
    
    __tablename__ = "enrollments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), 
        nullable=False
    )
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id"), 
        nullable=False
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus), 
        default=EnrollmentStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    direction: Mapped["Direction"] = relationship("Direction", back_populates="enrollments")


class PaymentReminder(Base):
    """Payment reminder model."""
    
    __tablename__ = "payment_reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), 
        nullable=False
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[PaymentReminderStatus] = mapped_column(
        Enum(PaymentReminderStatus), 
        default=PaymentReminderStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="payment_reminders")
