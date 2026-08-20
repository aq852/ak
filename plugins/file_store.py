"""File Store Plugin - Save and share files"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.settings import Config
from utils.user_manager import UserManager
from utils.file_manager import FileManager
from utils.managers import RateLimiter
from utils.translations import get_text
import re

async def file_store_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle files sent to bot in private chat"""
    
    # Only work in private chat
    if update.effective_chat.type != 'private':
        return
    
    user_id = update.effective_user.id
    
    # Create user if not exists
    await UserManager.create_user(user_id, update.effective_user.username)
    
    # Check if banned
    if await UserManager.is_banned(user_id):
        lang_doc = await UserManager.get_user(user_id)
        language = lang_doc.get('language', 'en') if lang_doc else 'en'
        await update.message.reply_text(get_text(language, "ban_message"))
        return
    
    # Check for file in message
    message = update.message
    file = None
    file_type = None
    
    if message.video:
        file = message.video
        file_type = 'video'
    elif message.document:
        file = message.document
        file_type = 'document'
    elif message.audio:
        file = message.audio
        file_type = 'audio'
    elif message.photo:
        file = message.photo[-1]  # Get highest resolution
        file_type = 'photo'
    
    if not file:
        return
    
    # Get file details
    file_id = file.file_id
    file_name = getattr(file, 'file_name', 'Unknown') or 'Unknown'
    file_size = file.file_size
    
    # Save to database
    success, existing = await FileManager.save_file(
        file_id=file_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        user_id=user_id,
        caption=message.caption
    )
    
    lang_doc = await UserManager.get_user(user_id)
    language = lang_doc.get('language', 'en') if lang_doc else 'en'
    
    if not success:
        # Duplicate file
        await update.message.reply_text(get_text(language, "duplicate_file"))
        return
    
    # Generate share link
    share_link = f"https://t.me/{context.bot.username}?start=file_{file_id}"
    
    # Send confirmation
    keyboard = [[InlineKeyboardButton("🔗 Share Link", url=share_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(
            language, "file_saved",
            name=file_name,
            size=format_size(file_size),
            link=share_link
        ),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with file sharing support"""
    
    user_id = update.effective_user.id
    args = context.args
    
    # Check for referral or file link
    if args:
        param = args[0]
        
        # Handle referral
        if param.startswith('REF'):
            success = await UserManager.add_referral(user_id, param)
            if success:
                await update.message.reply_text("🎉 Welcome! You've received 1 day VIP bonus from your referrer!")
        
        # Handle file link
        elif param.startswith('file_'):
            file_id = param.replace('file_', '')
            await send_stored_file(update, context, file_id, user_id)
            return
    
    # New user registration
    user = await UserManager.create_user(user_id, update.effective_user.username)
    
    # Determine language from user's language code
    language = 'en'
    if update.effective_user.language_code:
        if update.effective_user.language_code.startswith('hi'):
            language = 'hi'
    
    # Update user language
    await context.db.users.update_one(
        {"user_id": user_id},
        {"$set": {"language": language}}
    )
    
    # Send welcome message
    await update.message.reply_text(
        get_text(language, "welcome", name=update.effective_user.first_name),
        parse_mode='Markdown'
    )

async def send_stored_file(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          file_id: str, user_id: int):
    """Send a stored file to user"""
    
    # Check rate limit
    if RateLimiter.is_rate_limited(user_id, Config.RATE_LIMIT_PER_MINUTE):
        remaining = RateLimiter.get_remaining_requests(user_id, Config.RATE_LIMIT_PER_MINUTE)
        if remaining == 0:
            lang_doc = await UserManager.get_user(user_id)
            language = lang_doc.get('language', 'en') if lang_doc else 'en'
            await update.message.reply_text(
                get_text(language, "rate_limited", seconds=60)
            )
            return
    
    # Check download limit for non-VIP
    is_vip = await UserManager.is_vip(user_id)
    if not is_vip:
        download_count = await UserManager.get_download_count(user_id)
        if download_count >= Config.TRIAL_LIMIT:
            lang_doc = await UserManager.get_user(user_id)
            language = lang_doc.get('language', 'en') if lang_doc else 'en'
            await update.message.reply_text(
                get_text(language, "download_limit", limit=Config.TRIAL_LIMIT),
                parse_mode='Markdown'
            )
            return
    
    # Get file from database
    file_doc = await FileManager.get_file(file_id)
    
    if not file_doc:
        await update.message.reply_text("❌ File not found!")
        return
    
    # Increment downloads
    await FileManager.increment_downloads(file_id)
    await UserManager.increment_downloads(user_id)
    
    # Send file based on type
    try:
        if file_doc.get('file_type') == 'video':
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=file_id,
                caption=file_doc.get('caption', ''),
                protect_content=not is_vip
            )
        elif file_doc.get('file_type') == 'audio':
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=file_id,
                caption=file_doc.get('caption', ''),
                protect_content=not is_vip
            )
        elif file_doc.get('file_type') == 'photo':
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=file_id,
                caption=file_doc.get('caption', ''),
                protect_content=not is_vip
            )
        else:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_id,
                caption=file_doc.get('caption', ''),
                protect_content=not is_vip
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error sending file: {str(e)}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    
    user_id = update.effective_user.id
    
    # Create user if not exists
    await UserManager.create_user(user_id, update.effective_user.username)
    
    # Check if banned
    if await UserManager.is_banned(user_id):
        lang_doc = await UserManager.get_user(user_id)
        language = lang_doc.get('language', 'en') if lang_doc else 'en'
        await update.message.reply_text(get_text(language, "ban_message"))
        return
    
    # Get query
    if not context.args:
        await update.message.reply_text("Usage: /search <query>\n\nExample: /search Avengers 1080p")
        return
    
    query = ' '.join(context.args)
    
    # Parse filters
    search_query, search_filters = FuzzySearch.parse_filters(query)
    
    if not search_query:
        await update.message.reply_text("Please provide a search query.")
        return
    
    # Search files
    results = await FileManager.search_files(search_query, search_filters)
    
    if not results:
        lang_doc = await UserManager.get_user(user_id)
        language = lang_doc.get('language', 'en') if lang_doc else 'en'
        await update.message.reply_text(
            get_text(language, "no_results", query=search_query)
        )
        return
    
    # Send results
    for file_doc in results[:10]:
        # Similar logic as auto_filter
        pass

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trending command"""
    
    user_id = update.effective_user.id
    
    # Get trending files
    trending = await FileManager.get_trending_files(days=7, limit=10)
    
    if not trending:
        await update.message.reply_text("No trending files yet.")
        return
    
    # Format results
    message = "🔥 **Trending Files (Last 7 Days)**\n\n"
    for i, file_doc in enumerate(trending, 1):
        size = format_size(file_doc.get('file_size', 0))
        message += f"{i}. **{file_doc.get('file_name', 'Unknown')}**\n"
        message += f"   📏 Size: {size} | ⬇️ Downloads: {file_doc.get('downloads', 0)}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

def format_size(size_bytes: int) -> str:
    """Format file size"""
    if size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

# Import here to avoid circular imports
from utils.fuzzy_search import FuzzySearch

def get_handlers():
    """Get all handlers for this plugin"""
    return [
        CommandHandler('start', start_handler),
        CommandHandler('search', search_command),
        CommandHandler('trending', trending_command),
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            file_store_handler
        ),
        CallbackQueryHandler(callback_handler, pattern='^download_')
    ]

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('download_'):
        file_id = query.data.replace('download_', '')
        user_id = update.effective_user.id
        await send_stored_file(update, context, file_id, user_id)
