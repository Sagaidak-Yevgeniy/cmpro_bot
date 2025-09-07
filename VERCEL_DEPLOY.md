# 🚀 Развертывание на Vercel

## ✅ Исправлена ошибка с runtime

Проблема с версией Python runtime решена! Теперь используется совместимая конфигурация.

## 🔧 Исправления

### ✅ **Обновлена конфигурация:**
- `vercel.json` - убрано явное указание runtime (автоопределение)
- `vercel-alternative.json` - альтернативная конфигурация с `@vercel/python`
- `requirements.txt` - совместимые версии библиотек
- `runtime.txt` - Python 3.9
- `app/models_simple.py` - упрощенные модели для совместимости

### ✅ **Совместимые версии:**
- Python 3.9 (поддерживается Vercel)
- Flask 2.3.3
- python-telegram-bot 20.7
- SQLAlchemy 1.4.53
- psycopg2-binary 2.9.9

## 🚀 Пошаговое развертывание

### 1. Подготовка проекта
```bash
# Убедитесь, что все файлы готовы
git add .
git commit -m "Ready for Vercel deployment"
```

### 2. Установка Vercel CLI
```bash
npm install -g vercel
```

### 3. Вход в аккаунт
```bash
vercel login
```

### 4. Развертывание

**Вариант 1: Стандартная конфигурация**
```bash
vercel
```

**Вариант 2: Если возникает ошибка с runtime**
```bash
# Переименуйте файл конфигурации
mv vercel.json vercel-backup.json
mv vercel-alternative.json vercel.json

# Развертывание
vercel
```

### 5. Настройка переменных окружения
```bash
# Обязательные переменные
vercel env add TELEGRAM_BOT_TOKEN
vercel env add TELEGRAM_WEBHOOK_SECRET
vercel env add DATABASE_URL

# Дополнительные переменные
vercel env add APP_BASE_URL
vercel env add PUBLIC_BOT_USERNAME
vercel env add ADMIN_ACCESS_TOKEN
vercel env add DEFAULT_LANG
vercel env add TZ
```

### 6. Повторное развертывание
```bash
vercel --prod
```

### 7. Настройка webhook
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=https://ваш-домен.vercel.app/api/webhook&secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

## 📋 Переменные окружения

### Обязательные:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather
TELEGRAM_WEBHOOK_SECRET=случайная_строка_16_символов
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Опциональные:
```env
APP_BASE_URL=https://ваш-домен.vercel.app
PUBLIC_BOT_USERNAME=@ваш_бот
ADMIN_ACCESS_TOKEN=ваш_секретный_токен
DEFAULT_LANG=ru
TZ=Asia/Almaty
```

## 🧪 Тестирование развертывания

### 1. Проверка здоровья
```bash
curl https://ваш-домен.vercel.app/api/health
```

**Ожидаемый результат:**
```json
{
  "status": "healthy",
  "service": "cmpro-bot",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. Проверка webhook
```bash
curl "https://api.telegram.org/bot$TOKEN/getWebhookInfo"
```

### 3. Тестирование бота
1. Отправьте `/start` боту
2. Проверьте все команды
3. Убедитесь, что меню работает

## 🔧 Устранение проблем

### Если возникает ошибка "Function Runtimes must have a valid version":
1. **Используйте альтернативную конфигурацию:**
   ```bash
   mv vercel.json vercel-backup.json
   mv vercel-alternative.json vercel.json
   vercel
   ```

2. **Или создайте минимальную конфигурацию:**
   ```bash
   # Удалите vercel.json и создайте новый
   rm vercel.json
   echo '{"version": 2}' > vercel.json
   vercel
   ```

### Если развертывание не удается:
1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все переменные окружения установлены
3. Проверьте совместимость версий библиотек

### Если бот не отвечает:
1. Проверьте webhook URL
2. Убедитесь, что токен бота правильный
3. Проверьте логи функций в Vercel

### Если база данных не подключается:
1. Проверьте формат DATABASE_URL
2. Убедитесь, что база данных доступна
3. Проверьте SSL настройки

## 📊 Мониторинг

### Vercel Dashboard:
- Функции → Логи
- Аналитика → Использование
- Настройки → Переменные окружения

### Логи приложения:
- Структурированные логи с structlog
- Информация об ошибках и операциях
- Метрики производительности

## 🎉 Готово!

После успешного развертывания:

- ✅ **API endpoints** работают
- ✅ **Webhook** настроен
- ✅ **База данных** подключена
- ✅ **Cron задачи** активны
- ✅ **Бот** готов к работе

Ваш бот CodeMastersPRO готов принимать студентов! 🎓
