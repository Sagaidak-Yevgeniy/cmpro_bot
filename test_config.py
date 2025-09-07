"""
Тестовый скрипт для проверки конфигурации.
"""

import os
from app.config import settings
from app.logging import configure_logging

def test_config():
    """Тестирование конфигурации."""
    print("🔧 Тестирование конфигурации...")
    
    # Настройка логирования
    configure_logging(settings.environment)
    
    print(f"✅ Environment: {settings.environment}")
    print(f"✅ Default language: {settings.default_lang}")
    print(f"✅ Timezone: {settings.timezone}")
    print(f"✅ Rate limit: {settings.rate_limit_per_minute}")
    print(f"✅ Admin token: {settings.admin_access_token}")
    print(f"✅ App URL: {settings.app_base_url}")
    print(f"✅ Bot username: {settings.public_bot_username}")
    
    # Проверка токена бота
    if settings.telegram_bot_token:
        print(f"✅ Bot token: {settings.telegram_bot_token[:10]}...")
    else:
        print("⚠️  Bot token не установлен (можно установить в .env)")
    
    # Проверка webhook секрета
    if settings.telegram_webhook_secret:
        print(f"✅ Webhook secret: {settings.telegram_webhook_secret[:10]}...")
    else:
        print("⚠️  Webhook secret не установлен (можно установить в .env)")
    
    # Проверка базы данных
    print(f"✅ Database URL: {settings.database_url}")
    
    print("\n🎉 Конфигурация загружена успешно!")
    print("\n📝 Для полной настройки создайте .env файл:")
    print("TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather")
    print("TELEGRAM_WEBHOOK_SECRET=случайная_строка_16_символов")
    print("DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db")

if __name__ == "__main__":
    test_config()
