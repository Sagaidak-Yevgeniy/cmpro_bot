"""
Тестовый скрипт для проверки подключения к базе данных.
"""

from app.config import settings
from app.logging import configure_logging, get_logger
from app.db import engine, SessionLocal
from app.models import Base

# Настройка логирования
configure_logging(settings.environment)
logger = get_logger(__name__)

def test_database():
    """Тестирование подключения к базе данных."""
    print("🗄️  Тестирование базы данных...")
    
    try:
        # Создание таблиц
        print("📋 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы успешно")
        
        # Тестирование подключения
        print("🔗 Тестирование подключения...")
        session = SessionLocal()
        try:
            # Простой запрос
            result = session.execute("SELECT 1").scalar()
            print(f"✅ Подключение работает: {result}")
            
            # Проверка таблиц
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"✅ Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
                
        finally:
            session.close()
        
        print("\n🎉 База данных работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        logger.error("Database test failed", error=str(e))

if __name__ == "__main__":
    test_database()
