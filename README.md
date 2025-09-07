# 🤖 CodeMastersPRO Telegram Bot

Профессиональный Telegram бот для школы программирования CodeMastersPRO с полным функционалом управления студентами и админ-панелью.

## 🚀 Возможности

### Для студентов:
- 📝 **Запись на курсы** - Python, JavaScript, Go, Data Science
- 👤 **Личный кабинет** - после подтверждения записи
- 📅 **Расписание занятий**
- 💰 **Информация о платежах**
- 👥 **Данные о группе**
- 📚 **Учебные материалы**
- 📞 **Поддержка**

### Для администраторов:
- 🔧 **Админ-панель** - полное управление школой
- 📋 **Управление записями** - подтверждение/отклонение заявок
- 👥 **Управление группами** - создание и редактирование
- 📅 **Управление расписанием**
- 💰 **Контроль платежей**
- 📢 **Система рассылок**
- ✏️ **Редактирование текстов бота**
- 📊 **Статистика и аналитика**

## 🛠 Технологии

- **Python 3.9+**
- **python-telegram-bot** - для работы с Telegram API
- **Vercel** - для деплоя (Serverless Functions)
- **In-memory storage** - для хранения данных

## 📦 Установка

### Локальная разработка:

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/your-username/codemasterspro-bot.git
cd codemasterspro-bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив ваш BOT_TOKEN
```

5. **Запустите бота:**
```bash
python bot_polling.py
```

## 🌐 Деплой на Vercel

1. **Установите Vercel CLI:**
```bash
npm i -g vercel
```

2. **Войдите в аккаунт:**
```bash
vercel login
```

3. **Добавьте переменные окружения:**
```bash
vercel env add BOT_TOKEN
# Введите токен вашего бота
```

4. **Деплой:**
```bash
vercel --prod
```

5. **Настройте webhook:**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-vercel-app.vercel.app/api/webhook"}'
```

## ⚙️ Конфигурация

### Переменные окружения:
- `BOT_TOKEN` - токен вашего Telegram бота (получить у @BotFather)

### Админ-доступ:
- **Логин:** `Saga`
- **Пароль:** `Saga190989$`

## 📁 Структура проекта

```
├── api/
│   └── webhook.py          # Vercel webhook endpoint
├── app/
│   ├── i18n/               # Локализация (ru, kk)
│   └── utils/              # Утилиты
├── bot_polling.py          # Основной файл бота (локальная разработка)
├── requirements.txt        # Python зависимости
├── vercel.json            # Конфигурация Vercel
└── .env.example           # Пример переменных окружения
```

## 🎯 Использование

### Для студентов:
1. Отправьте `/start` боту
2. Нажмите "📝 Записаться на курс"
3. Выберите направление
4. Поделитесь контактом
5. Ждите подтверждения от администратора

### Для администраторов:
1. Отправьте `/admin` боту
2. Введите логин и пароль
3. Используйте админ-панель для управления

## 🔧 Разработка

### Добавление новых функций:
1. Отредактируйте `bot_polling.py`
2. Добавьте новые обработчики в `process_message()` или `process_callback_query()`
3. Создайте новые клавиатуры при необходимости

### Локализация:
- Файлы переводов находятся в `app/i18n/`
- Поддерживаются русский (ru) и казахский (kk) языки

## 📄 Лицензия

MIT License

## 🤝 Поддержка

- **Telegram:** @CodeMastersPRO_bot
- **Email:** info@codemasterspro.dev
- **Website:** https://www.codemasterspro.dev/

---

**CodeMastersPRO** - Ваш путь в мир программирования! 🚀
