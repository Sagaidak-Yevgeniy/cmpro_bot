"""
Cron endpoint for scheduled tasks.
Handles payment reminders and other periodic tasks.
"""

from typing import Dict, Any

from flask import Flask, jsonify

from app.config import settings
from app.logging import configure_logging, get_logger
from app.bot.services.reminders_service import RemindersService
from app.db import get_async_db

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route("/api/cron", methods=["POST", "GET"])
def cron_handler() -> Dict[str, Any]:
    """
    Handle cron tasks.
    
    Returns:
        Task execution results
    """
    try:
        logger.info("Cron job started")
        
        # Process payment reminders
        import asyncio
        async def process_reminders():
            async with get_async_db() as session:
                reminders_service = RemindersService(session)
                return await reminders_service.process_due_reminders()
        
        reminder_stats = asyncio.run(process_reminders())
        
        # TODO: Add other scheduled tasks here
        # - Send course reminders
        # - Update lesson schedules
        # - Clean up old data
        
        result = {
            "status": "success",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be replaced with actual timestamp
            "tasks": {
                "payment_reminders": reminder_stats
            }
        }
        
        logger.info(
            "Cron job completed",
            reminder_stats=reminder_stats
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error("Cron job failed", error=str(e), exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request.environ, lambda *args: None)
