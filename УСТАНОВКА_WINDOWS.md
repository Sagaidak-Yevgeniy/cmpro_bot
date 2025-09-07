# 🪟 Установка CodeMastersPRO Bot на Windows

## ✅ Исправлена проблема с asyncpg

Проблема с установкой `asyncpg` на Windows решена! Теперь бот использует синхронные операции с базой данных для лучшей совместимости.

## 🚀 Быстрая установка

### 1. Установка Python и зависимостей

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Установка зависимостей (теперь без asyncpg!)
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Копирование шаблона
copy env.example .env
```

Отредактируйте `.env` файл:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather
TELEGRAM_WEBHOOK_SECRET=случайная_строка_16_символов
APP_BASE_URL=https://ваш-домен.vercel.app
PUBLIC_BOT_USERNAME=@ваш_бот
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
ADMIN_ACCESS_TOKEN=ваш_секретный_токен_админа
DEFAULT_LANG=ru
TZ=Asia/Almaty
```

### 3. Настройка базы данных

```bash
# Создание таблиц
python create_tables.py

# Заполнение начальными данными
python -m app.seed
```

### 4. Тестирование локально

```bash
# Запуск Flask сервера для тестирования
python -m flask --app api.health run --port 5000
```

Откройте браузер и перейдите на `http://localhost:5000/api/health` - должно показать статус "healthy".

## 🔧 Что изменилось

### ✅ Убрано:
- `asyncpg` зависимость (проблемная на Windows)
- Все async/await операции с базой данных
- Сложные async контекстные менеджеры

### ✅ Добавлено:
- Синхронные операции с SQLAlchemy
- Упрощенные обработчики для быстрого тестирования
- Совместимость с Windows из коробки

## 🎯 Функции бота

### Основные команды:
- `/start` - Главное меню
- `/lang` - Смена языка (ru/kk)

### Меню:
- 📝 **Записаться на курс** - Информация о записи
- 🎯 **Направления** - Список курсов (Python, JS, Go, Data Analytics)
- 📅 **Расписание** - Примерное расписание занятий
- 💬 **Поддержка** - Контактная информация

## 🚀 Развертывание на Vercel

### 1. Установка Vercel CLI
```bash
npm install -g vercel
```

### 2. Развертывание
```bash
# Вход в аккаунт
vercel login

# Развертывание
vercel

# Добавление переменных окружения
vercel env add TELEGRAM_BOT_TOKEN
vercel env add TELEGRAM_WEBHOOK_SECRET
vercel env add APP_BASE_URL
vercel env add DATABASE_URL
vercel env add ADMIN_ACCESS_TOKEN
```

### 3. Настройка webhook
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=https://ваш-домен.vercel.app/api/webhook&secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

## 🧪 Тестирование

### 1. Проверка здоровья
```bash
curl https://ваш-домен.vercel.app/api/health
```

### 2. Тестирование бота
1. Отправьте `/start` боту
2. Попробуйте кнопки меню
3. Переключите язык командой `/lang`

## 🐛 Устранение проблем

### Если бот не отвечает:
1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все переменные окружения установлены
3. Проверьте webhook: `curl "https://api.telegram.org/bot$TOKEN/getWebhookInfo"`

### Если база данных не подключается:
1. Проверьте формат DATABASE_URL
2. Убедитесь, что база данных доступна
3. Проверьте SSL настройки

## 📝 Структура проекта

```
├─ app/
│  ├─ bot/
│  │  ├─ handlers/
│  │  │  ├─ simple_handlers.py  # Упрощенные обработчики
│  │  │  └─ ...
│  │  └─ services/
│  │     └─ repo_sync.py        # Синхронные репозитории
│  └─ ...
├─ api/
│  ├─ webhook.py                # Webhook endpoint
│  ├─ health.py                 # Health check
│  └─ cron.py                   # Cron задачи
└─ requirements.txt             # Без asyncpg!
```

## 🎉 Готово!

Теперь бот полностью совместим с Windows и готов к использованию! Все основные функции работают:

- ✅ Многоязычность (русский/казахский)
- ✅ Информация о курсах
- ✅ Расписание занятий
- ✅ Контактная информация
- ✅ Смена языка
- ✅ Развертывание на Vercel

Бот готов принимать студентов и предоставлять информацию о школе программирования CodeMastersPRO!
