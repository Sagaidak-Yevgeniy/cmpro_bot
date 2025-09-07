from http.server import BaseHTTPRequestHandler
import json
import os
import time

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Админ настройки
ADMIN_LOGIN = "Saga"
ADMIN_PASSWORD = "Saga190989$"

# Хранилище данных (в реальном проекте используйте базу данных)
user_sessions = {}
enrollments = []
students = {}
groups = {}
schedules = {}
payments = {}

# Файл для сохранения данных
DATA_FILE = "bot_data.json"

def load_data():
    """Загрузить данные из файла."""
    global user_sessions, enrollments, students, groups, schedules, payments
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_sessions = data.get('user_sessions', {})
                enrollments = data.get('enrollments', [])
                students = data.get('students', {})
                groups = data.get('groups', {})
                schedules = data.get('schedules', {})
                payments = data.get('payments', {})
                print(f"Data loaded: {len(students)} students, {len(enrollments)} enrollments")
    except Exception as e:
        print(f"Error loading data: {e}")

def save_data():
    """Сохранить данные в файл."""
    try:
        data = {
            'user_sessions': user_sessions,
            'enrollments': enrollments,
            'students': students,
            'groups': groups,
            'schedules': schedules,
            'payments': payments
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Data saved successfully")
    except Exception as e:
        print(f"Error saving data: {e}")

# Загружаем данные при запуске
load_data()

def send_message(chat_id, text, reply_markup=None):
    """Отправить сообщение через Telegram Bot API."""
    import requests
    
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set")
        return None
    
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
        result = response.json()
        print(f"Send message result: {result}")
        return result
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def get_main_menu_keyboard(user_id=None):
    """Получить клавиатуру главного меню."""
    keyboard = {
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
    
    # Добавляем кнопку "Личный кабинет" для подтвержденных студентов
    if user_id and user_id in students and students[user_id].get("status") == "approved":
        keyboard["inline_keyboard"].insert(0, [
            {"text": "👤 Личный кабинет", "callback_data": "student_cabinet"}
        ])
    
    # Добавляем кнопку "Админ панель" для авторизованных админов
    if user_id and is_admin(user_id):
        keyboard["inline_keyboard"].insert(0, [
            {"text": "🔧 Админ панель", "callback_data": "admin_panel"}
        ])
    
    return keyboard

def get_directions_keyboard():
    """Получить клавиатуру направлений."""
    return {
        "inline_keyboard": [
            [
                {"text": "🐍 Python разработка", "callback_data": "direction_python"},
                {"text": "🌐 JavaScript разработка", "callback_data": "direction_js"}
            ],
            [
                {"text": "🔧 Go разработка", "callback_data": "direction_go"},
                {"text": "📊 Анализ данных", "callback_data": "direction_data"}
            ],
            [
                {"text": "🔙 Главное меню", "callback_data": "main_menu"}
            ]
        ]
    }

def get_enroll_keyboard():
    """Получить клавиатуру записи на курс."""
    return {
        "inline_keyboard": [
            [
                {"text": "🐍 Python", "callback_data": "enroll_python"},
                {"text": "🌐 JavaScript", "callback_data": "enroll_js"}
            ],
            [
                {"text": "🔧 Go", "callback_data": "enroll_go"},
                {"text": "📊 Data Science", "callback_data": "enroll_data"}
            ],
            [
                {"text": "🔙 Главное меню", "callback_data": "main_menu"}
            ]
        ]
    }

def get_contact_keyboard():
    """Получить клавиатуру для запроса контакта."""
    return {
        "keyboard": [
            [
                {
                    "text": "📱 Поделиться контактом",
                    "request_contact": True
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

def get_student_menu_keyboard():
    """Получить клавиатуру меню студента."""
    return {
        "inline_keyboard": [
            [
                {"text": "📅 Расписание", "callback_data": "student_schedule"},
                {"text": "💰 Платежи", "callback_data": "student_payments"}
            ],
            [
                {"text": "👥 Моя группа", "callback_data": "student_group"},
                {"text": "📚 Материалы", "callback_data": "student_materials"}
            ],
            [
                {"text": "📞 Поддержка", "callback_data": "student_support"},
                {"text": "🔙 Главное меню", "callback_data": "main_menu"}
            ]
        ]
    }

def get_school_management_keyboard():
    """Получить клавиатуру управления школой."""
    return {
        "inline_keyboard": [
            [
                {"text": "📋 Записи", "callback_data": "admin_enrollments"},
                {"text": "👥 Группы", "callback_data": "admin_groups"}
            ],
            [
                {"text": "📅 Расписание", "callback_data": "admin_schedule"},
                {"text": "💰 Платежи", "callback_data": "admin_payments"}
            ],
            [
                {"text": "📢 Рассылки", "callback_data": "admin_broadcast"},
                {"text": "📊 Статистика", "callback_data": "admin_stats"}
            ],
            [
                {"text": "✏️ Тексты", "callback_data": "admin_edit"},
                {"text": "🔙 Главное меню", "callback_data": "main_menu"}
            ]
        ]
    }

def is_admin(user_id):
    """Проверить, является ли пользователь админом."""
    return user_sessions.get(user_id, {}).get("is_admin", False)

def notify_admin(enrollment_data):
    """Уведомить админа о новой записи."""
    # Находим админа
    admin_id = None
    for uid, session in user_sessions.items():
        if session.get("is_admin"):
            admin_id = uid
            break
    
    if admin_id:
        message = f"""📝 <b>Новая запись на курс!</b>

👤 <b>Имя:</b> {enrollment_data['name']}
📞 <b>Телефон:</b> {enrollment_data['phone']}
🎯 <b>Курс:</b> {enrollment_data['course']}
👤 <b>Username:</b> @{enrollment_data['username']}
📅 <b>Дата:</b> {enrollment_data['timestamp']}

Подтвердите или отклоните запись:"""
        
        # Создаем клавиатуру для подтверждения/отклонения
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Подтвердить", "callback_data": f"approve_{enrollment_data['user_id']}"},
                    {"text": "❌ Отклонить", "callback_data": f"reject_{enrollment_data['user_id']}"}
                ],
                [
                    {"text": "🔧 Админ панель", "callback_data": "admin_panel"}
                ]
            ]
        }
        
        send_message(admin_id, message, keyboard)
        print(f"Admin notification sent to {admin_id}")
    else:
        print("No admin found to notify")

def process_message(message):
    """Обработать сообщение."""
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    user = message.get("from", {})
    user_id = user.get("id")
    username = user.get("username", "Unknown")
    contact = message.get("contact")
    
    print(f"Processing message: {text} from user {user_id}")
    
    # Обработка контакта
    if contact:
        phone = contact.get("phone_number", "")
        first_name = contact.get("first_name", "")
        last_name = contact.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # Получаем выбранный курс из сессии
        if user_id in user_sessions and "selected_course" in user_sessions[user_id]:
            selected_course = user_sessions[user_id]["selected_course"]
            
            # Сохраняем запись
            enrollment_data = {
                "name": full_name,
                "phone": phone,
                "course": selected_course,
                "username": username,
                "user_id": user_id,
                "timestamp": time.strftime("%d.%m.%Y %H:%M")
            }
            enrollments.append(enrollment_data)
            
            # Создаем запись студента (ожидает подтверждения)
            students[user_id] = {
                "name": full_name,
                "phone": phone,
                "course": selected_course,
                "username": username,
                "status": "pending",  # Ожидает подтверждения
                "group": None,
                "enrollment_date": time.strftime("%d.%m.%Y %H:%M")
            }
            
            response_text = f"""✅ <b>Заявка на запись отправлена!</b>

👤 <b>Имя:</b> {full_name}
📞 <b>Телефон:</b> {phone}
🎯 <b>Курс:</b> {selected_course}
📅 <b>Дата:</b> {time.strftime("%d.%m.%Y %H:%M")}

⏳ <b>Статус:</b> Ожидает подтверждения

📞 <b>Наш менеджер свяжется с вами в ближайшее время!</b>"""
            
            send_message(chat_id, response_text, get_main_menu_keyboard(user_id))
            
            # Уведомляем админа о новой записи
            notify_admin(enrollment_data)
            
            # Сохраняем данные
            save_data()
        else:
            send_message(chat_id, "❌ Ошибка: курс не выбран. Попробуйте записаться заново.", get_main_menu_keyboard(user_id))
        
        return
    
    # Обработка команд
    if text == "/start":
        response_text = """🚀 <b>Добро пожаловать в школу программирования CodeMastersPRO!</b>

🎯 <b>Наша миссия:</b>
Обучать IT‑специалистов с нуля, развивать навыки программирования и прививать любовь к технологиям.

📍 <b>Где нас найти:</b>
🏢 Павлодар, Казахстан
Бекмаханова 115/2 (угол ул. Естая и проспекта Назарбаева)

💻 <b>Формат обучения:</b>
✅ Офлайн-занятия в уютных и современно оборудованных аудиториях
✅ Практика на реальных проектах под руководством наставников
✅ Пошаговое освоение основ программирования с возможностью углубленного развития

🌐 <b>Наши ресурсы:</b>
🌟 Сайт: codemasterspro.dev
📸 Instagram: @code_masterspro

🔥 <b>Почему CodeMastersPRO:</b>
• Интерактивные уроки и живые проекты
• Поддержка и постоянное общение с наставниками
• Возможность участвовать в соревнованиях и хакатонах
• Прививаем интерес и любовь к IT с первых шагов обучения

Выберите действие:"""
        keyboard = get_main_menu_keyboard(user_id)
        
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
        keyboard = get_main_menu_keyboard(user_id)
        
    elif text == "/admin":
        response_text = """🔐 <b>Вход в админ панель</b>

Введите логин и пароль через пробел.

⚠️ <b>Внимание:</b> Пароль будет скрыт при вводе для безопасности."""
        keyboard = None
        
    # Обработка админ-авторизации
    elif text.startswith(ADMIN_LOGIN) and ADMIN_PASSWORD in text:
        user_sessions[user_id] = {"is_admin": True}
        save_data()  # Сохраняем авторизацию админа
        
        response_text = f"""✅ <b>Добро пожаловать, {ADMIN_LOGIN}!</b>

🔧 <b>Панель управления школой CodeMastersPRO</b>

📊 <b>Статистика:</b>
• Записей на курсы: {len(enrollments)}
• Студентов: {len(students)}
• Групп: {len(groups)}

🎯 <b>Доступные функции:</b>
• Управление записями студентов
• Создание и редактирование групп
• Управление расписанием занятий
• Контроль платежей студентов
• Рассылки и уведомления
• Редактирование контента"""
        keyboard = get_school_management_keyboard()
        
    else:
        response_text = "❓ Неизвестная команда. Используйте /start для главного меню."
        keyboard = get_main_menu_keyboard(user_id)
    
    send_message(chat_id, response_text, keyboard)

def process_callback_query(callback_query):
    """Обработать callback query."""
    data = callback_query.get("data", "")
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    message_id = callback_query.get("message", {}).get("message_id")
    
    print(f"Processing callback: {data} from user {user_id}")
    
    # Обработка callback'ов
    if data == "main_menu":
        response_text = """🚀 <b>Добро пожаловать в школу программирования CodeMastersPRO!</b>

🎯 <b>Наша миссия:</b>
Обучать IT‑специалистов с нуля, развивать навыки программирования и прививать любовь к технологиям.

📍 <b>Где нас найти:</b>
🏢 Павлодар, Казахстан
Бекмаханова 115/2 (угол ул. Естая и проспекта Назарбаева)

💻 <b>Формат обучения:</b>
✅ Офлайн-занятия в уютных и современно оборудованных аудиториях
✅ Практика на реальных проектах под руководством наставников
✅ Пошаговое освоение основ программирования с возможностью углубленного развития

🌐 <b>Наши ресурсы:</b>
🌟 Сайт: codemasterspro.dev
📸 Instagram: @code_masterspro

🔥 <b>Почему CodeMastersPRO:</b>
• Интерактивные уроки и живые проекты
• Поддержка и постоянное общение с наставниками
• Возможность участвовать в соревнованиях и хакатонах
• Прививаем интерес и любовь к IT с первых шагов обучения

Выберите действие:"""
        keyboard = get_main_menu_keyboard(user_id)
        
    elif data == "directions":
        response_text = """🎯 <b>Направления обучения CodeMastersPRO</b>

🐍 <b>Python разработка</b>
Изучение одного из самых популярных языков программирования. От основ синтаксиса до создания веб-приложений и работы с данными.

🌐 <b>JavaScript разработка</b>
Современная веб-разработка с использованием JavaScript, React, Node.js. Создание интерактивных пользовательских интерфейсов.

🔧 <b>Go разработка</b>
Изучение языка Go от Google. Высокая производительность, простота и эффективность для создания масштабируемых приложений.

📊 <b>Анализ данных</b>
Работа с большими данными, машинное обучение, визуализация данных. Python, pandas, numpy, matplotlib.

Выберите направление для подробной информации:"""
        keyboard = get_directions_keyboard()
        
    elif data == "enroll":
        response_text = """📝 <b>Запись на курс</b>

Выберите направление, на которое хотите записаться:

🐍 <b>Python</b> - от основ до веб-разработки
🌐 <b>JavaScript</b> - современная веб-разработка  
🔧 <b>Go</b> - высокопроизводительные приложения
📊 <b>Data Science</b> - анализ данных и ML

После выбора направления поделитесь контактом для связи."""
        keyboard = get_enroll_keyboard()
        
    elif data.startswith("enroll_"):
        course = data.split("_")[1]
        course_names = {
            "python": "🐍 Python разработка",
            "js": "🌐 JavaScript разработка",
            "go": "🔧 Go разработка", 
            "data": "📊 Анализ данных"
        }
        course_name = course_names.get(course, course)
        
        # Сохраняем выбранный курс
        user_sessions[user_id] = user_sessions.get(user_id, {})
        user_sessions[user_id]["selected_course"] = course
        
        # Проверяем, не записан ли уже студент
        if user_id in students and students[user_id].get("status") == "approved":
            response_text = f"""✅ <b>Вы уже записаны на курс!</b>

🎓 <b>Ваш курс:</b> {course_name}
✅ <b>Статус:</b> Подтвержден

Используйте личный кабинет для управления обучением."""
            keyboard = get_main_menu_keyboard(user_id)
        else:
            response_text = f"""📝 <b>Запись на курс: {course_name}</b>

Для завершения записи поделитесь своим контактом.

📱 <b>Нажмите кнопку ниже:</b>"""
            keyboard = get_contact_keyboard()
        
    elif data == "contacts":
        response_text = """📍 <b>Контакты CodeMastersPRO:</b>
🏢 <b>Адрес:</b>
Павлодар, Казахстан
Бекмаханова 115/2
(угол ул. Естая и проспекта Назарбаева)
📞 <b>Телефон:</b> +7 (777) 332-36-76
📧 <b>Email:</b> info@codemasterspro.dev
🕒 <b>Время работы:</b>
Пн-Пт: 9:00 - 21:00
Сб: 10:00 - 18:00
Вс: Выходной
🌐 <b>Онлайн:</b>
🔗 <b>Сайт:</b> https://www.codemasterspro.dev/
📸 <b>Instagram:</b> https://www.instagram.com/code_masterspro"""
        keyboard = get_main_menu_keyboard(user_id)
        
    elif data == "mission":
        response_text = """🎯 <b>Наша миссия CodeMastersPRO</b>

Мы обучаем IT‑специалистов с нуля, развиваем навыки программирования и прививаем любовь к технологиям.

🎓 <b>Наши цели:</b>
• Дать качественное образование в сфере IT
• Подготовить конкурентоспособных специалистов
• Развить практические навыки программирования
• Создать комьюнити единомышленников

💡 <b>Наш подход:</b>
• Индивидуальный подход к каждому студенту
• Практико-ориентированное обучение
• Современные технологии и методики
• Поддержка на всех этапах обучения

🚀 <b>Результат:</b>
Выпускники CodeMastersPRO успешно трудоустраиваются в ведущие IT-компании и создают собственные проекты."""
        keyboard = get_main_menu_keyboard(user_id)
        
    elif data == "links":
        response_text = """🌐 <b>Полезные ссылки CodeMastersPRO</b>

🔗 <b>Основные ресурсы:</b>
• <b>Сайт:</b> https://www.codemasterspro.dev/
• <b>Instagram:</b> https://www.instagram.com/code_masterspro

📚 <b>Образовательные материалы:</b>
• <b>GitHub:</b> https://github.com/codemasterspro
• <b>YouTube:</b> https://youtube.com/@codemasterspro

💼 <b>Карьера:</b>
• <b>Вакансии:</b> https://www.codemasterspro.dev/careers
• <b>Портфолио выпускников:</b> https://www.codemasterspro.dev/portfolio

📞 <b>Связь с нами:</b>
• <b>Telegram:</b> @CodeMastersPRO_bot
• <b>Email:</b> info@codemasterspro.dev
• <b>Телефон:</b> +7 (777) 332-36-76"""
        keyboard = get_main_menu_keyboard(user_id)
        
    elif data == "help":
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
        keyboard = get_main_menu_keyboard(user_id)
        
    elif data == "admin_panel":
        if is_admin(user_id):
            response_text = f"""🔧 <b>Панель управления школой</b>

📊 <b>Статистика:</b>
• Записей на курсы: {len(enrollments)}
• Студентов: {len(students)}
• Групп: {len(groups)}

Выберите действие:"""
            keyboard = get_school_management_keyboard()
        else:
            response_text = "❌ <b>Доступ запрещен</b>\n\nУ вас нет прав администратора."
            keyboard = get_main_menu_keyboard(user_id)
            
    elif data == "admin_enrollments":
        if is_admin(user_id):
            if enrollments:
                response_text = f"📋 <b>Записи на курсы</b>\n\n"
                for i, enrollment in enumerate(enrollments):
                    status = students.get(enrollment["user_id"], {}).get("status", "pending")
                    status_emoji = "✅" if status == "approved" else "⏳" if status == "pending" else "❌"
                    response_text += f"{i+1}. {status_emoji} {enrollment['name']} - {enrollment['course']}\n"
            else:
                response_text = "📋 <b>Записи на курсы</b>\n\nПока нет записей."
            keyboard = get_school_management_keyboard()
        else:
            response_text = "❌ <b>Доступ запрещен</b>"
            keyboard = get_main_menu_keyboard(user_id)
            
    elif data == "student_cabinet":
        if user_id in students and students[user_id].get("status") == "approved":
            student = students[user_id]
            response_text = f"""👤 <b>Личный кабинет</b>

👤 <b>Имя:</b> {student.get('name', '')}
📞 <b>Телефон:</b> {student.get('phone', '')}
🎓 <b>Курс:</b> {student.get('course', '')}
✅ <b>Статус:</b> Подтвержден
📅 <b>Дата записи:</b> {student.get('enrollment_date', '')}

Выберите действие:"""
            keyboard = get_student_menu_keyboard()
        else:
            response_text = "❌ <b>Доступ запрещен</b>\n\nУ вас нет доступа к личному кабинету."
            keyboard = get_main_menu_keyboard(user_id)
            
    elif data.startswith("approve_"):
        if is_admin(user_id):
            student_id = int(data.split("_")[1])
            if student_id in students:
                students[student_id]["status"] = "approved"
                response_text = f"✅ <b>Запись подтверждена!</b>\n\nСтудент {students[student_id]['name']} добавлен в систему."
                
                # Уведомляем студента о подтверждении
                student_message = f"""🎉 <b>Поздравляем!</b>

Ваша заявка на курс <b>{students[student_id]['course']}</b> подтверждена!

👤 <b>Имя:</b> {students[student_id]['name']}
🎓 <b>Курс:</b> {students[student_id]['course']}
✅ <b>Статус:</b> Подтвержден

Теперь у вас есть доступ к личному кабинету!"""
                send_message(student_id, student_message, get_main_menu_keyboard(student_id))
                
                # Сохраняем изменения
                save_data()
            else:
                response_text = "❌ Студент не найден."
            keyboard = get_school_management_keyboard()
        else:
            response_text = "❌ <b>Доступ запрещен</b>"
            keyboard = get_main_menu_keyboard(user_id)
            
    elif data.startswith("reject_"):
        if is_admin(user_id):
            student_id = int(data.split("_")[1])
            if student_id in students:
                students[student_id]["status"] = "rejected"
                response_text = f"❌ <b>Запись отклонена!</b>\n\nЗаявка студента {students[student_id]['name']} отклонена."
                
                # Уведомляем студента об отклонении
                student_message = f"""❌ <b>Заявка отклонена</b>

К сожалению, ваша заявка на курс <b>{students[student_id]['course']}</b> была отклонена.

Если у вас есть вопросы, свяжитесь с нами:
📞 +7 (777) 332-36-76
📧 info@codemasterspro.dev"""
                send_message(student_id, student_message, get_main_menu_keyboard(student_id))
                
                # Сохраняем изменения
                save_data()
            else:
                response_text = "❌ Студент не найден."
            keyboard = get_school_management_keyboard()
        else:
            response_text = "❌ <b>Доступ запрещен</b>"
            keyboard = get_main_menu_keyboard(user_id)
            
    else:
        response_text = "❓ Неизвестная команда."
        keyboard = get_main_menu_keyboard(user_id)
    
    # Отправляем ответ
    send_message(chat_id, response_text, keyboard)

def process_webhook(update):
    """Обработать webhook от Telegram."""
    print(f"Processing webhook: {json.dumps(update, indent=2)}")
    
    if "message" in update:
        process_message(update["message"])
    elif "callback_query" in update:
        process_callback_query(update["callback_query"])

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