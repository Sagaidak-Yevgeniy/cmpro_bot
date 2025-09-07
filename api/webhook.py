"""
Flask webhook endpoint for Telegram bot.
Handles incoming webhook requests from Telegram.
"""

import json
from typing import Dict, Any

from flask import Flask, request, jsonify
from telegram import Update

from app.config import settings
from app.logging import configure_logging, get_logger
from app.bot.app import get_application

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route("/api/webhook", methods=["POST"])
def webhook() -> Dict[str, Any]:
    """
    Handle incoming webhook from Telegram.
    
    Returns:
        JSON response
    """
    try:
        # Verify webhook secret
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.telegram_webhook_secret:
            logger.warning("Invalid webhook secret token")
            return jsonify({"error": "Unauthorized"}), 401
        
        # Parse update
        update_data = request.get_json()
        if not update_data:
            logger.warning("Empty webhook payload")
            return jsonify({"error": "Empty payload"}), 400
        
        # Create Update object
        update = Update.de_json(update_data, None)
        if not update:
            logger.warning("Invalid update data")
            return jsonify({"error": "Invalid update"}), 400
        
        # Process update
        import asyncio
        application = get_application()
        asyncio.run(application.process_update(update))
        
        logger.info(
            "Webhook processed successfully",
            update_id=update.update_id,
            user_id=update.effective_user.id if update.effective_user else None
        )
        
        return jsonify({"ok": True})
        
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/webhook", methods=["GET"])
def webhook_info() -> Dict[str, Any]:
    """
    Provide webhook information.
    
    Returns:
        Webhook status information
    """
    return jsonify({
        "status": "active",
        "bot_username": settings.public_bot_username,
        "webhook_url": f"{settings.app_base_url}/api/webhook"
    })


# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request.environ, lambda *args: None)
