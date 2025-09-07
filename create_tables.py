"""
Простой скрипт для создания таблиц без Alembic.
"""

from app.config import settings
from app.logging import configure_logging, get_logger
from app.db import engine
from app.models_simple import Base

# Настройка логирования
configure_logging(settings.environment)
logger = get_logger(__name__)

def create_tables():
    """Создание всех таблиц в базе данных."""
    print("🗄️  Создание таблиц в базе данных...")
    
    try:
        # Создание всех таблиц
        Base.metadata.create_all(bind=engine)
        print("✅ Все таблицы созданы успешно!")
        
        # Показ созданных таблиц
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Созданные таблицы ({len(tables)}):")
        for table in tables:
            print(f"   ✅ {table}")
        
        print("\n🎉 База данных готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        logger.error("Table creation failed", error=str(e))
        raise

if __name__ == "__main__":
    create_tables()
