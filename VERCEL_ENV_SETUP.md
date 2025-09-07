# 🔧 Настройка переменных окружения в Vercel

## ❌ Проблема с именем переменной

**Ошибка:** `The name contains invalid characters. Only letters, digits, and underscores are allowed. Furthermore, the name should not start with a digit.`

**Причина:** Токен бота начинается с цифры `7172072404:...`, что недопустимо для имени переменной.

## ✅ Правильная настройка

### 1. Создайте файл .env.local
```bash
# Создайте файл с переменными
cat > .env.local << EOF
TELEGRAM_BOT_TOKEN=7172072404:AAG4Kw6GfyXJnm_jG0Fvo8j61jGb6JNgJqs
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_here
DATABASE_URL=postgresql://user:pass@host:5432/db
APP_BASE_URL=https://your-domain.vercel.app
PUBLIC_BOT_USERNAME=@cmpro_bot
ADMIN_ACCESS_TOKEN=your_admin_token
DEFAULT_LANG=ru
TZ=Asia/Almaty
EOF
```

### 2. Загрузите переменные в Vercel
```bash
# Загрузите все переменные из файла
vercel env push .env.local
```

### 3. Или добавьте по одной
```bash
# Добавьте каждую переменную отдельно
vercel env add TELEGRAM_BOT_TOKEN production
# Введите: 7172072404:AAG4Kw6GfyXJnm_jG0Fvo8j61jGb6JNgJqs

vercel env add TELEGRAM_WEBHOOK_SECRET production
# Введите: your_webhook_secret_here

vercel env add DATABASE_URL production
# Введите: postgresql://user:pass@host:5432/db
```

## 🔍 Проверка переменных

### Просмотр всех переменных:
```bash
vercel env ls
```

### Просмотр конкретной переменной:
```bash
vercel env pull .env.local
cat .env.local
```

## 🚀 Развертывание после настройки

```bash
# Развертывание с переменными
vercel --prod
```

## 📋 Обязательные переменные

| Переменная | Описание | Пример |
|------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | `7172072404:AAG4Kw6GfyXJnm_jG0Fvo8j61jGb6JNgJqs` |
| `TELEGRAM_WEBHOOK_SECRET` | Секретный ключ для webhook | `random_string_16_chars` |
| `DATABASE_URL` | URL базы данных PostgreSQL | `postgresql://user:pass@host:5432/db` |

## 📋 Опциональные переменные

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `APP_BASE_URL` | Базовый URL приложения | `https://your-domain.vercel.app` |
| `PUBLIC_BOT_USERNAME` | Имя бота | `@cmpro_bot` |
| `ADMIN_ACCESS_TOKEN` | Токен администратора | `admin123` |
| `DEFAULT_LANG` | Язык по умолчанию | `ru` |
| `TZ` | Часовой пояс | `Asia/Almaty` |

## ⚠️ Важные замечания

1. **Не используйте токен бота как имя переменной** - он начинается с цифры
2. **Всегда указывайте environment** - `production`, `preview`, или `development`
3. **Проверьте переменные** перед развертыванием
4. **Используйте .env.local** для массовой загрузки

## 🧪 Тестирование

После настройки переменных проверьте:

```bash
# Проверка здоровья
curl https://your-domain.vercel.app/api/health

# Проверка webhook
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```
