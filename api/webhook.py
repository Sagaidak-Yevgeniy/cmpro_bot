from http.server import BaseHTTPRequestHandler
import json
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')

def send_message(chat_id, text, reply_markup=None):
    """Отправить сообщение через Telegram Bot API."""
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def get_main_menu_keyboard():
    """Получить клавиатуру главного меню."""
    return {
        "inline_keyboard": [
            [
                {"text": "🎯 Направления", "callback_data": "directions"},
                {"text": "📝 Записаться", "callback_data": "enroll"}
            ],
            [
                {"text": "📍 Контакты", "callback_data": "contacts"},
                {"text": "🎯 Миссия", "callback_data": "mission"}
            ],
            [
                {"text": "🌐 Ссылки", "callback_data": "links"},
                {"text": "📚 Помощь", "callback_data": "help"}
            ]
        ]
    }

def process_webhook(update):
    """Обработать webhook от Telegram."""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            response_text = """🚀 <b>Добро пожаловать в школу программирования CodeMastersPRO!</b>

🎯 <b>Наша миссия:</b>
Мы обучаем программированию с нуля и готовим специалистов для IT-индустрии.

📚 <b>Направления обучения:</b>
• 🐍 Python разработка
• 🌐 JavaScript разработка  
• 🔧 Go разработка
• 📊 Анализ данных

🏢 <b>О нас:</b>
• Современные методики обучения
• Опытные преподаватели
• Практические проекты
• Помощь в трудоустройстве
• Возможность участвовать в соревнованиях и хакатонах
• Прививаем интерес и любовь к IT с первых шагов обучения

Выберите действие:"""
            
            send_message(chat_id, response_text, get_main_menu_keyboard())
        
        elif text == "/help":
            response_text = """📚 <b>Доступные команды:</b>

/start - Главное меню
/directions - Направления обучения  
/enroll - Записаться на курс
/contacts - Контакты и адрес
/mission - Наша миссия
/links - Ссылки на ресурсы
/admin - Панель администратора

🎯 <b>Как записаться на курс:</b>
1. Нажмите "📝 Записаться"
2. Выберите направление
3. Поделитесь контактом
4. Ждите звонка менеджера"""
            
            send_message(chat_id, response_text, get_main_menu_keyboard())
        
        else:
            send_message(chat_id, "❓ Неизвестная команда. Используйте /start для главного меню.", get_main_menu_keyboard())

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            process_webhook(update)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            
        except Exception as e:
            print(f"Error processing webhook: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'CodeMastersPRO Bot is running!')