"""Main Bot Application"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config.settings import Config
from utils.database import db

# Import plugins
from plugins.auto_filter import get_handlers as get_auto_filter_handlers
from plugins.file_store import get_handlers as get_file_store_handlers
from plugins.admin import get_handlers as get_admin_handlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Initialize database after bot starts"""
    await db.connect()
    logger.info("✅ Bot initialized and connected to database")

async def post_shutdown(application):
    """Cleanup on shutdown"""
    await db.disconnect()
    logger.info("❌ Bot shutdown and disconnected from database")

async def error_handler(update: Update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")

def main():
    """Main function to run the bot"""
    
    # Validate configuration
    Config.validate()
    
    # Create application
    application = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Add handlers from all plugins
    all_handlers = []
    all_handlers.extend(get_auto_filter_handlers())
    all_handlers.extend(get_file_store_handlers())
    all_handlers.extend(get_admin_handlers())
    
    for handler in all_handlers:
        application.add_handler(handler)
    
    # Add global error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🚀 Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
