import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = os.getenv("DB_NAME", "telegram_bot")
    
    # Admin & Channels
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))
    SUPPORT_GROUP = int(os.getenv("SUPPORT_GROUP", "0"))
    
    # File Store
    FILE_STORE_CHANNEL = int(os.getenv("FILE_STORE_CHANNEL", "0"))
    
    # Monetization
    VIP_PRICE = int(os.getenv("VIP_PRICE", "99"))
    TRIAL_LIMIT = int(os.getenv("TRIAL_LIMIT", "5"))
    TRIAL_PERIOD_DAYS = int(os.getenv("TRIAL_PERIOD_DAYS", "1"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    AUTO_DELETE_DELAY = int(os.getenv("AUTO_DELETE_DELAY", "120"))
    
    # Languages
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
    SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "en,hi").split(",")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.MONGO_URI:
            raise ValueError("MONGO_URI is required")
        return True
