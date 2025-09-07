# CodeMastersPRO Telegram Bot

A production-ready Telegram bot for CodeMastersPRO programming school, built with Python and deployed on Vercel serverless functions.

## 🚀 Features

### Core Functionality
- **Student Registration**: Interactive enrollment flow with form validation
- **Course Directions**: Python, JavaScript, Go, Data Analytics
- **Schedule Management**: View upcoming lessons and course schedules
- **Admin Panel**: Manage enrollments, approve/reject applications
- **Payment Reminders**: Automated reminder system via cron jobs
- **Multi-language Support**: Russian (default) and Kazakh languages

### Technical Features
- **Webhook Mode**: No long polling, optimized for serverless
- **Clean Architecture**: Separation of concerns with services and repositories
- **Database Migrations**: Alembic for schema management
- **Structured Logging**: Comprehensive logging with structlog
- **Rate Limiting**: Built-in protection against spam
- **Security**: Webhook secret verification and admin token authentication

## 🏗️ Architecture

```
├─ vercel.json                 # Vercel deployment configuration
├─ requirements.txt            # Python dependencies
├─ runtime.txt                # Python version specification
├─ env.example                # Environment variables template
├─ alembic.ini                # Database migration configuration
├─ alembic/                   # Migration files
├─ app/
│  ├─ config.py               # Pydantic settings and validation
│  ├─ logging.py              # Structured logging configuration
│  ├─ db.py                   # Database connection and session management
│  ├─ models.py               # SQLAlchemy ORM models
│  ├─ seed.py                 # Database seeding script
│  ├─ i18n/                   # Internationalization files
│  │  ├─ ru.json              # Russian translations
│  │  └─ kk.json              # Kazakh translations
│  ├─ bot/
│  │  ├─ app.py               # PTB Application singleton
│  │  ├─ middlewares.py       # Rate limiting and i18n middleware
│  │  ├─ keyboards.py         # Telegram keyboard helpers
│  │  ├─ handlers/            # Bot command and conversation handlers
│  │  │  ├─ start.py          # Start command and main menu
│  │  │  ├─ enroll.py         # Student enrollment flow
│  │  │  ├─ directions.py     # Course directions display
│  │  │  ├─ schedule.py       # Schedule and lessons
│  │  │  ├─ admin.py          # Admin panel functionality
│  │  │  └─ lang.py           # Language switching
│  │  └─ services/            # Business logic services
│  │     ├─ enroll_service.py # Enrollment management
│  │     ├─ schedule_service.py # Schedule operations
│  │     ├─ reminders_service.py # Payment reminders
│  │     └─ repo.py           # Database repository layer
│  └─ utils/                  # Utility functions
│     ├─ telegram.py          # Telegram helpers
│     ├─ time.py              # Timezone and date utilities
│     └─ i18n.py              # Internationalization helpers
└─ api/                       # Vercel serverless functions
   ├─ webhook.py              # Telegram webhook endpoint
   ├─ health.py               # Health check endpoint
   └─ cron.py                 # Scheduled tasks endpoint
```

## 🛠️ Tech Stack

- **Python 3.11**: Modern Python with async/await support
- **python-telegram-bot 21+**: Async Telegram Bot API
- **Flask**: Web framework for API endpoints
- **SQLAlchemy 2.x**: Modern ORM with async support
- **PostgreSQL**: Primary database (Neon/Render/Cloud SQL)
- **Alembic**: Database migration management
- **Pydantic Settings**: Environment configuration and validation
- **structlog**: Structured logging
- **Vercel**: Serverless deployment platform

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database
- Telegram Bot Token (from @BotFather)
- Vercel account (for deployment)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd cmpro_bot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_WEBHOOK_SECRET=long-random-secret-string
APP_BASE_URL=https://your-vercel-domain.vercel.app
PUBLIC_BOT_USERNAME=@your_bot_username

DATABASE_URL=postgresql+psycopg://user:password@host:5432/cmpro_bot?sslmode=require

ADMIN_ACCESS_TOKEN=your-secure-admin-token
RATE_LIMIT_PER_MINUTE=20

DEFAULT_LANG=ru
TZ=Asia/Almaty
```

### 3. Database Setup

Initialize and run migrations:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Seed database with initial data
python -m app.seed
```

### 4. Local Development

For local development, you'll need a public URL for webhooks. Use ngrok:

```bash
# Install ngrok
npm install -g ngrok

# Start local server
python -m flask --app api.health run --port 5000

# In another terminal, expose with ngrok
ngrok http 5000
```

Update your `.env` with the ngrok URL:
```env
APP_BASE_URL=https://your-ngrok-url.ngrok.io
```

### 5. Set Webhook

Configure Telegram webhook:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=$APP_BASE_URL/api/webhook&secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

Verify webhook:
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

## 🚀 Deployment to Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Deploy

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add TELEGRAM_BOT_TOKEN
vercel env add TELEGRAM_WEBHOOK_SECRET
vercel env add APP_BASE_URL
vercel env add PUBLIC_BOT_USERNAME
vercel env add DATABASE_URL
vercel env add ADMIN_ACCESS_TOKEN
vercel env add RATE_LIMIT_PER_MINUTE
vercel env add DEFAULT_LANG
vercel env add TZ
```

### 3. Configure Webhook

After deployment, set the webhook URL:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=https://your-app.vercel.app/api/webhook&secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

## 📊 Database Schema

### Core Tables

- **students**: User information and preferences
- **directions**: Available course directions (Python, JS, Go, Data Analytics)
- **enrollments**: Student enrollment requests and status
- **groups**: Study groups for each direction
- **lessons**: Scheduled lessons and topics
- **payment_reminders**: Payment reminder tracking

### Key Relationships

- Students can have multiple enrollments
- Each enrollment belongs to a direction
- Groups belong to directions
- Lessons belong to groups
- Payment reminders belong to students

## 🔧 Bot Commands

### User Commands
- `/start` - Welcome message and main menu
- `/lang` - Language selection (Russian/Kazakh)

### Admin Commands
- `/admin` - Admin panel access (requires token)

### Menu Options
- **📝 Записаться на курс** - Start enrollment process
- **🎯 Направления** - View available courses
- **📅 Расписание** - View upcoming lessons
- **💬 Поддержка** - Contact information

## 🔐 Security Features

- **Webhook Secret Verification**: All webhook requests verified
- **Admin Token Authentication**: Secure admin access
- **Rate Limiting**: Protection against spam and abuse
- **Input Validation**: All user inputs validated and sanitized
- **Environment Variables**: Sensitive data in environment variables only

## 📈 Monitoring and Logging

### Health Check
```bash
curl https://your-app.vercel.app/api/health
```

### Structured Logging
All operations are logged with structured data including:
- User IDs and chat IDs
- Operation types and results
- Error details and stack traces
- Performance metrics

### Cron Jobs
Daily cron job runs at 06:00 Asia/Almaty time to:
- Process payment reminders
- Send notifications
- Clean up old data

## 🧪 Testing

### Manual Testing
1. Start the bot with `/start`
2. Test enrollment flow
3. Verify admin panel access
4. Check language switching
5. Test schedule display

### Database Testing
```bash
# Check database connection
python -c "from app.db import engine; print('DB connected')"

# Verify migrations
alembic current

# Check seed data
python -c "from app.seed import main; import asyncio; asyncio.run(main())"
```

## 🔄 Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migration
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## 🌐 Internationalization

### Adding New Languages
1. Create new JSON file in `app/i18n/`
2. Add language code to `LanguageCode` enum in `models.py`
3. Update language selection keyboard
4. Test language switching

### Translation Keys
All user-facing text uses translation keys:
- `welcome.title` - Welcome message title
- `menu.enroll` - Enrollment menu item
- `errors.general` - General error message

## 🚀 Scaling Considerations

### Current Limitations
- In-memory rate limiting (resets on cold start)
- No background job queue
- Single database connection per request

### Production Improvements
- **Redis**: For rate limiting and caching
- **Queue System**: For background jobs (Celery/RQ)
- **Connection Pooling**: PgBouncer for database connections
- **Monitoring**: Application performance monitoring
- **CDN**: For static assets and media

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not receiving updates**
   - Check webhook URL and secret token
   - Verify Vercel deployment is active
   - Check Vercel function logs

2. **Database connection errors**
   - Verify DATABASE_URL format
   - Check database server accessibility
   - Ensure SSL requirements are met

3. **Bot not responding**
   - Check bot token validity
   - Verify webhook is set correctly
   - Review application logs

### Debug Mode
Enable debug logging by setting:
```env
ENVIRONMENT=development
```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Use meaningful variable names

### Error Handling
- Always handle exceptions gracefully
- Log errors with context
- Provide user-friendly error messages
- Use structured logging

### Testing
- Test all user flows manually
- Verify database operations
- Check error scenarios
- Test with different languages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**CodeMastersPRO Telegram Bot** - Empowering programming education through technology.
