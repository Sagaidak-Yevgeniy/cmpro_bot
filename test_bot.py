"""
Тестовый скрипт для проверки бота.
"""

from app.config import settings
from app.logging import configure_logging, get_logger
from app.bot.app import get_application

# Настройка логирования
configure_logging(settings.environment)
logger = get_logger(__name__)

def test_bot():
    """Тестирование создания бота."""
    print("🤖 Тестирование бота...")
    
    try:
        # Проверка токена
        if not settings.telegram_bot_token:
            print("⚠️  TELEGRAM_BOT_TOKEN не установлен")
            print("   Бот не может быть создан без токена")
            return False
        
        # Создание приложения
        print("🔧 Создание приложения бота...")
        application = get_application()
        print("✅ Приложение бота создано успешно")
        
        # Проверка обработчиков
        handlers = application.handlers[0]
        print(f"✅ Загружено обработчиков: {len(handlers)}")
        
        print("\n🎉 Бот готов к работе!")
        print("\n📝 Для запуска бота:")
        print("1. Установите webhook: curl 'https://api.telegram.org/bot$TOKEN/setWebhook?url=$URL/api/webhook'")
        print("2. Или запустите локально с ngrok")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        logger.error("Bot test failed", error=str(e))
        return False

if __name__ == "__main__":
    test_bot()
