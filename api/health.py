"""
Health check endpoint for monitoring.
"""

from typing import Dict, Any

from flask import Flask, jsonify

from app.config import settings
from app.logging import configure_logging, get_logger

# Configure logging
configure_logging(settings.environment)
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route("/api/health", methods=["GET"])
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    try:
        # Basic health check
        health_data = {
            "status": "healthy",
            "service": "cmpro-bot",
            "version": "1.0.0",
            "environment": settings.environment,
            "timezone": settings.timezone,
            "default_language": settings.default_lang
        }
        
        logger.debug("Health check requested")
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route("/", methods=["GET"])
def root() -> Dict[str, Any]:
    """
    Root endpoint.
    
    Returns:
        Basic service information
    """
    return jsonify({
        "service": "CodeMastersPRO Telegram Bot",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "/api/webhook",
            "health": "/api/health",
            "cron": "/api/cron"
        }
    })


# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request.environ, lambda *args: None)
