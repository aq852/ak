# Ultimate Telegram Auto-Filter & File Store Bot

A highly advanced, multi-purpose Telegram bot using Python (python-telegram-bot v20+), MongoDB (Motor async driver), designed to handle millions of files/users.

## 🚀 Features

### Core Functionality
1. **Auto Filter Mode** - Search files in groups with instant results
2. **File Store (DM Mode)** - Permanent file storage with shareable links
3. **Auto Posting / Channel Forwarder** - Automatic content forwarding
4. **Custom Captions & Dynamic Buttons** - Templated captions with variables
5. **Duplicate Detection** - Prevent duplicate file storage

### Monetization & Payments
6. **Token/Subscription System (VIP)** - Redeemable VIP tokens
7. **Payment Integration** - Manual payment verification
8. **Trial & Free Limits** - Configurable free tier limits
9. **Reseller Panel** - Multi-tier admin system
10. **In-Search Sponsored Ads** - Rotating ads with analytics

### User Experience
11. **Welcome & Leave Messages** - Customizable greetings
12. **Fuzzy Search / Typo Tolerance** - Smart search suggestions
13. **Advanced Filters** - Quality, language, and type filters
14. **Trending & Popular Files** - Top downloads tracking
15. **Inline Mode** - Search from any chat
16. **Multi-Language Support** - English and Hindi

### Security & Admin
17. **Content Protection** - Prevent forwarding for non-VIP
18. **Auto-Delete & Anti-Spam** - Rate limiting and cleanup
19. **Broadcast / Bulk Messaging** - Send to all users
20. **User Activity Logs & Analytics** - Detailed statistics
21. **Custom Commands** - Configurable triggers
22. **Referral System** - Bonus for referrals
23. **Rate Limiting & Anti-Abuse** - Spam protection
24. **Backup & Restore** - Data export/import
25. **Ban/Unban System** - User management

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Libraries:** python-telegram-bot==20.6, motor, pymongo, python-dotenv, aiohttp
- **Database:** MongoDB Atlas
- **Hosting:** Koyeb (Docker)

## 📋 Prerequisites

- Python 3.10 or higher
- MongoDB Atlas account (free tier works)
- Telegram Bot Token (from @BotFather)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Edit `.env` file with your credentials:
```env
BOT_TOKEN=your_bot_token_here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=telegram_bot
ADMIN_IDS=123456789,987654321
```

### 4. Run the bot
```bash
python bot/main.py
```

## 🐳 Docker Deployment

### Build and run locally
```bash
docker build -t telegram-bot .
docker run -d --env-file .env telegram-bot
```

### Deploy on Koyeb

1. Push code to GitHub
2. Create new service on Koyeb
3. Connect your GitHub repository
4. Add environment variables from `.env`
5. Deploy!

## 📁 Project Structure

```
├── bot/
│   ├── __init__.py
│   └── main.py              # Main entry point
├── plugins/
│   ├── __init__.py
│   ├── auto_filter.py       # Auto-filter functionality
│   ├── file_store.py        # File storage & sharing
│   └── admin.py             # Admin commands
├── utils/
│   ├── __init__.py
│   ├── database.py          # MongoDB connection
│   ├── user_manager.py      # User operations
│   ├── file_manager.py      # File operations
│   ├── fuzzy_search.py      # Search algorithms
│   ├── managers.py          # Token, Ad, Rate limiting
│   └── translations.py      # Multi-language support
├── config/
│   └── settings.py          # Configuration
├── .env                     # Environment variables
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## 🎯 Usage

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/search <query>` - Search for files
- `/trending` - Show trending files
- `/redeem <token>` - Redeem VIP token
- `/myplan` - Check VIP status

### Admin Commands
- `/admin` - Open admin panel
- `/stats` - View bot statistics
- `/broadcast` - Broadcast message to all users
- `/gentoken [days]` - Generate VIP token
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/backup` - Create data backup

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot Token | Required |
| `MONGO_URI` | MongoDB Connection String | Required |
| `DB_NAME` | Database Name | `telegram_bot` |
| `ADMIN_IDS` | Comma-separated Admin User IDs | - |
| `VIP_PRICE` | VIP Price (for display) | `99` |
| `TRIAL_LIMIT` | Daily download limit for free users | `5` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute | `10` |

## 📊 Database Collections

- `users` - User data and VIP status
- `files` - Stored files metadata
- `groups` - Group configurations
- `settings` - Bot settings
- `ads` - Sponsored advertisements
- `payments` - Payment records
- `tokens` - VIP tokens

## 🎨 UI Design

The bot features clean, professional inline keyboards and formatted messages with:
- Structured search results with sponsored ads section
- Interactive admin panel with inline buttons
- Custom captions with dynamic variables

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Support

For issues and feature requests, please open an issue on GitHub.

---

**Built with ❤️ using Python and Telegram Bot API**
