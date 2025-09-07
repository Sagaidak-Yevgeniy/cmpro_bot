"""
Database seed script.
Populates the database with initial data for directions, groups, and lessons.
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.logging import configure_logging, get_logger
from app.models import (
    Direction,
    DirectionCode,
    Group,
    Lesson,
)
from app.db import engine, SessionLocal

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)


def create_directions(session: Session) -> None:
    """Create initial directions."""
    directions_data = [
        {
            "code": DirectionCode.PYTHON,
            "title": "Python",
            "description": "Изучите один из самых популярных языков программирования. От веб-разработки до машинного обучения."
        },
        {
            "code": DirectionCode.JAVASCRIPT,
            "title": "JavaScript",
            "description": "Освойте современную веб-разработку с React, Node.js и другими популярными технологиями."
        },
        {
            "code": DirectionCode.GO,
            "title": "Go",
            "description": "Изучите высокопроизводительный язык программирования от Google для создания масштабируемых приложений."
        },
        {
            "code": DirectionCode.DATA_ANALYTICS,
            "title": "Data Analytics",
            "description": "Научитесь анализировать данные с помощью Python, SQL и современных инструментов аналитики."
        }
    ]
    
    for direction_data in directions_data:
        # Check if direction already exists
        existing = session.query(Direction).filter(Direction.code == direction_data["code"]).first()
        if existing:
            logger.info(f"Direction {direction_data['code'].value} already exists, skipping")
            continue
        
        direction = Direction(**direction_data)
        session.add(direction)
        logger.info(f"Created direction: {direction_data['title']}")
    
    session.commit()


def create_groups(session: Session) -> None:
    """Create initial groups for each direction."""
    # Get all directions
    directions = session.query(Direction).filter(Direction.is_active == True).all()
    
    groups_data = {
        DirectionCode.PYTHON: [
            "Python для начинающих",
            "Python Advanced"
        ],
        DirectionCode.JAVASCRIPT: [
            "JavaScript Fundamentals",
            "React & Node.js"
        ],
        DirectionCode.GO: [
            "Go Basics",
            "Go Microservices"
        ],
        DirectionCode.DATA_ANALYTICS: [
            "Data Analysis с Python",
            "Machine Learning"
        ]
    }
    
    for direction in directions:
        if direction.code in groups_data:
            for group_title in groups_data[direction.code]:
                # Check if group already exists
                existing = session.query(Group).filter(
                    Group.direction_id == direction.id,
                    Group.title == group_title
                ).first()
                if existing:
                    logger.info(f"Group {group_title} already exists, skipping")
                    continue
                
                group = Group(
                    title=group_title,
                    direction_id=direction.id
                )
                session.add(group)
                logger.info(f"Created group: {group_title} for {direction.title}")
    
    session.commit()


def create_lessons(session: Session) -> None:
    """Create sample lessons for the next 30 days."""
    # Get all groups
    groups = session.query(Group).filter(Group.is_active == True).all()
    
    if not groups:
        logger.warning("No groups found, skipping lesson creation")
        return
    
    # Create lessons for the next 30 days
    start_date = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    lesson_topics = [
        "Введение в программирование",
        "Основы синтаксиса",
        "Переменные и типы данных",
        "Условные операторы",
        "Циклы и итерации",
        "Функции и методы",
        "Работа с файлами",
        "Обработка ошибок",
        "Объектно-ориентированное программирование",
        "Работа с базами данных",
        "Веб-разработка",
        "API и интеграции",
        "Тестирование кода",
        "Деплой и DevOps",
        "Проектная работа"
    ]
    
    lesson_count = 0
    current_date = start_date
    
    for day in range(30):  # Next 30 days
        for group in groups:
            # Create 2-3 lessons per week per group
            if day % 3 == 0:  # Every 3rd day
                topic = lesson_topics[lesson_count % len(lesson_topics)]
                
                lesson = Lesson(
                    group_id=group.id,
                    topic=topic,
                    starts_at=current_date,
                    ends_at=current_date + timedelta(hours=2)
                )
                session.add(lesson)
                lesson_count += 1
                logger.info(f"Created lesson: {topic} for {group.title} on {current_date.strftime('%Y-%m-%d')}")
        
        current_date += timedelta(days=1)
    
    session.commit()
    logger.info(f"Created {lesson_count} lessons")


def seed_database() -> None:
    """Main seed function."""
    logger.info("Starting database seeding...")
    
    try:
        session = SessionLocal()
        try:
            create_directions(session)
            create_groups(session)
            create_lessons(session)
        finally:
            session.close()
        
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error("Database seeding failed", error=str(e))
        raise


def main() -> None:
    """Main entry point for seeding."""
    seed_database()


if __name__ == "__main__":
    main()
