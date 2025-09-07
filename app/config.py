"""
Configuration management using Pydantic Settings.
Validates environment variables and provides type-safe configuration.
"""

import os
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(default="", description="Telegram bot token from @BotFather")
    telegram_webhook_secret: str = Field(default="", description="Secret token for webhook verification")
    app_base_url: str = Field(default="http://localhost:5000", description="Base URL for the application (Vercel domain)")
    public_bot_username: str = Field(default="@cmpro_bot", description="Public bot username (e.g., @cmpro_bot)")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./cmpro_bot.db", description="PostgreSQL database URL")
    
    # Security Configuration
    admin_access_token: str = Field(default="admin123", description="Token for admin access")
    rate_limit_per_minute: int = Field(default=20, description="Rate limit per minute per user")
    
    # Internationalization
    default_lang: Literal["ru", "kk"] = Field(default="ru", description="Default language")
    timezone: str = Field(default="Asia/Almaty", description="Application timezone")
    
    # Environment
    environment: str = Field(default="development", description="Environment (development/production)")
    
    @validator("telegram_bot_token")
    def validate_bot_token(cls, v: str) -> str:
        """Validate Telegram bot token format."""
        if v and len(v) < 10:
            raise ValueError("Invalid Telegram bot token")
        return v
    
    @validator("telegram_webhook_secret")
    def validate_webhook_secret(cls, v: str) -> str:
        """Validate webhook secret length."""
        if v and len(v) < 16:
            raise ValueError("Webhook secret must be at least 16 characters")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if v and not v.startswith(("postgresql://", "postgresql+psycopg://", "sqlite:///")):
            raise ValueError("Database URL must be a valid connection string")
        return v
    
    @validator("app_base_url")
    def validate_app_base_url(cls, v: str) -> str:
        """Validate app base URL format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("App base URL must start with http:// or https://")
        return v.rstrip("/")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
