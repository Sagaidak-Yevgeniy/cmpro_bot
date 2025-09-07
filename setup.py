"""
Setup script for CodeMastersPRO Telegram Bot.
Helps with initial database setup and configuration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.logging import configure_logging, get_logger
from app.db import async_engine
from app.seed import seed_database

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)


async def check_database_connection():
    """Check if database connection is working."""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def setup_database():
    """Set up database with initial data."""
    logger.info("Setting up database...")
    
    # Check connection
    if not await check_database_connection():
        logger.error("Cannot proceed without database connection")
        return False
    
    try:
        # Seed database
        await seed_database()
        logger.info("Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_WEBHOOK_SECRET", 
        "APP_BASE_URL",
        "DATABASE_URL",
        "ADMIN_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please copy env.example to .env and fill in the required values")
        return False
    
    logger.info("All required environment variables are set")
    return True


async def main():
    """Main setup function."""
    logger.info("Starting CodeMastersPRO Bot setup...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Setup database
    if not await setup_database():
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info("You can now start the bot or deploy to Vercel")


if __name__ == "__main__":
    asyncio.run(main())
