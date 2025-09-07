"""
Database configuration and session management.
Uses SQLAlchemy 2.x with synchronous operations for Windows compatibility.
"""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.logging import get_logger
from app.models import Base

logger = get_logger(__name__)

# Create engines
engine = create_engine(settings.database_url, echo=False)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


def get_sync_db():
    """
    Get synchronous database session.
    Used for all operations (simplified for Windows compatibility).
    
    Returns:
        Database session
    """
    return SessionLocal()


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
