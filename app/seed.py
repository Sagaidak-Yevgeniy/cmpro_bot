"""
Database seed script.
Populates the database with initial data for directions, groups, and lessons.
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.logging import configure_logging, get_logger
from app.models import (
    Direction,
    DirectionCode,
    Group,
    Lesson,
)
from app.db import async_engine, AsyncSessionLocal

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)


async def create_directions(session: AsyncSession) -> None:
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
        from sqlalchemy import select
        existing = await session.execute(
            select(Direction).where(Direction.code == direction_data["code"])
        )
        if existing.scalar_one_or_none():
            logger.info(f"Direction {direction_data['code'].value} already exists, skipping")
            continue
        
        direction = Direction(**direction_data)
        session.add(direction)
        logger.info(f"Created direction: {direction_data['title']}")
    
    await session.commit()


async def create_groups(session: AsyncSession) -> None:
    """Create initial groups for each direction."""
    # Get all directions
    directions_result = await session.execute(
        select(Direction).where(Direction.is_active == True)
    )
    directions = directions_result.scalars().all()
    
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
                existing = await session.execute(
                    select(Group).where(
                        Group.direction_id == direction.id,
                        Group.title == group_title
                    )
                )
                if existing.scalar_one_or_none():
                    logger.info(f"Group {group_title} already exists, skipping")
                    continue
                
                group = Group(
                    title=group_title,
                    direction_id=direction.id
                )
                session.add(group)
                logger.info(f"Created group: {group_title} for {direction.title}")
    
    await session.commit()


async def create_lessons(session: AsyncSession) -> None:
    """Create sample lessons for the next 30 days."""
    # Get all groups
    groups_result = await session.execute(
        select(Group).where(Group.is_active == True)
    )
    groups = groups_result.scalars().all()
    
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
    
    await session.commit()
    logger.info(f"Created {lesson_count} lessons")


async def seed_database() -> None:
    """Main seed function."""
    logger.info("Starting database seeding...")
    
    try:
        async with AsyncSessionLocal() as session:
            await create_directions(session)
            await create_groups(session)
            await create_lessons(session)
        
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error("Database seeding failed", error=str(e))
        raise


async def main() -> None:
    """Main entry point for seeding."""
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
