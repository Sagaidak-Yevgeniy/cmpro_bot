"""
Database configuration and session management.
Uses SQLAlchemy 2.x with async support for PostgreSQL.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

# Convert sync database URL to async
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
engine = create_engine(settings.database_url, echo=False)
async_engine = create_async_engine(async_database_url, echo=False)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


def get_db() -> Generator:
    """
    Dependency to get database session.
    Used for sync operations (Flask endpoints).
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager to get database session.
    Used for async operations (Telegram bot handlers).
    
    Yields:
        Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Async database session error", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()


# Add connection event listeners for logging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection parameters for PostgreSQL."""
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout."""
    logger.debug("Database connection checked out")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin."""
    logger.debug("Database connection checked in")
