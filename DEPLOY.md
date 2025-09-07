# 🚀 Деплой CodeMastersPRO Bot на Vercel

## 📋 Быстрый старт

### 1. Подготовка
```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/codemasterspro-bot.git
cd codemasterspro-bot

# Установите Vercel CLI
npm i -g vercel
```

### 2. Настройка переменных окружения
```bash
# Войдите в Vercel
vercel login

# Добавьте токен бота
vercel env add BOT_TOKEN
# Введите токен вашего бота (получить у @BotFather)
```

### 3. Деплой
```bash
# Деплой на Vercel
vercel --prod
```

### 4. Настройка webhook
```bash
# Замените YOUR_BOT_TOKEN и YOUR_VERCEL_URL на ваши значения
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://YOUR_VERCEL_URL.vercel.app/api/webhook"}'
```

## 🔧 Локальная разработка

### Запуск бота локально:
```bash
# Создайте виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
# или
source .venv/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp env.example .env
# Отредактируйте .env, добавив BOT_TOKEN

# Запустите бота
python bot_polling.py
```

## 📁 Структура проекта

```
├── api/
│   └── webhook.py          # Vercel webhook endpoint
├── bot_polling.py          # Локальная разработка
├── requirements.txt        # Python зависимости
├── vercel.json            # Конфигурация Vercel
├── env.example            # Пример переменных окружения
└── README.md              # Документация
```

## ⚙️ Конфигурация

### Vercel (vercel.json):
```json
{
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/$1"
    }
  ]
}
```

### Переменные окружения:
- `BOT_TOKEN` - токен Telegram бота

## 🎯 Функционал

### Для студентов:
- Запись на курсы (Python, JavaScript, Go, Data Science)
- Личный кабинет после подтверждения
- Расписание, платежи, группа, материалы

### Для администраторов:
- Админ-панель (логин: Saga, пароль: Saga190989$)
- Управление записями, группами, расписанием
- Редактирование текстов бота
- Статистика и аналитика

## 🔍 Проверка работы

1. **Проверьте webhook:**
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

2. **Отправьте /start боту** - должно прийти приветствие

3. **Проверьте админ-панель:**
   - Отправьте `/admin`
   - Введите `Saga Saga190989$`

## 🛠 Обновление

```bash
# Обновите код
git pull origin main

# Передеплойте
vercel --prod
```

## 📞 Поддержка

- **Telegram:** @CodeMastersPRO_bot
- **Email:** info@codemasterspro.dev
- **Website:** https://www.codemasterspro.dev/
