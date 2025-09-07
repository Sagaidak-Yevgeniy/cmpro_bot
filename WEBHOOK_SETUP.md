# 🔧 Настройка Webhook для Vercel

## 🚀 Быстрая настройка

### 1. Проверьте, что бот развернут на Vercel
```bash
# Проверьте статус
vercel ls

# Если нужно, передеплойте
vercel --prod
```

### 2. Получите URL вашего бота
```bash
# Получите URL
vercel ls
# Скопируйте URL (например: https://your-bot-name.vercel.app)
```

### 3. Настройте webhook
```bash
# Замените YOUR_BOT_TOKEN и YOUR_VERCEL_URL на ваши значения
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://YOUR_VERCEL_URL.vercel.app/api/webhook"}'
```

### 4. Проверьте webhook
```bash
# Проверьте статус webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

## 🔍 Диагностика проблем

### Проблема: Webhook не работает
1. **Проверьте URL:**
   ```bash
   curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
   ```
   
2. **Проверьте, что бот отвечает:**
   ```bash
   curl "https://YOUR_VERCEL_URL.vercel.app/api/webhook"
   # Должен вернуть: CodeMastersPRO Bot is running!
   ```

3. **Проверьте переменные окружения:**
   ```bash
   vercel env ls
   # Должна быть переменная BOT_TOKEN
   ```

### Проблема: Бот не отвечает на команды
1. **Проверьте логи Vercel:**
   ```bash
   vercel logs
   ```

2. **Проверьте, что BOT_TOKEN установлен:**
   ```bash
   vercel env add BOT_TOKEN
   # Введите токен вашего бота
   ```

3. **Передеплойте:**
   ```bash
   vercel --prod
   ```

## 🧪 Тестирование

### Тест 1: Проверка webhook
```bash
# Отправьте тестовое сообщение боту
# Должен ответить на /start
```

### Тест 2: Проверка админ-панели
1. Отправьте `/admin` боту
2. Введите `Saga Saga190989$`
3. Должна открыться админ-панель

### Тест 3: Проверка записи
1. Нажмите "📝 Записаться"
2. Выберите курс
3. Поделитесь контактом
4. Админ должен получить уведомление

## 📋 Чек-лист

- [ ] Бот развернут на Vercel
- [ ] Переменная BOT_TOKEN установлена
- [ ] Webhook настроен правильно
- [ ] URL webhook соответствует Vercel URL
- [ ] Бот отвечает на /start
- [ ] Админ-панель работает
- [ ] Записи студентов работают

## 🆘 Если ничего не работает

1. **Удалите webhook:**
   ```bash
   curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"
   ```

2. **Передеплойте бота:**
   ```bash
   vercel --prod
   ```

3. **Настройте webhook заново:**
   ```bash
   curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://YOUR_VERCEL_URL.vercel.app/api/webhook"}'
   ```

4. **Проверьте работу:**
   ```bash
   curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
   ```
