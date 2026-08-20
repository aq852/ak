"""Auto Filter Plugin - Search files in groups"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from config.settings import Config
from utils.database import db
from utils.user_manager import UserManager
from utils.file_manager import FileManager
from utils.fuzzy_search import FuzzySearch
from utils.managers import RateLimiter, AdManager
from utils.translations import get_text
import re
import asyncio

async def auto_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle auto-filter search in groups"""
    
    # Check if in group
    if not update.message or not update.message.chat.type in ['group', 'supergroup']:
        return
    
    user_id = update.effective_user.id
    query = update.message.text
    
    # Skip if message is a command
    if query.startswith('/'):
        return
    
    # Check rate limit
    if RateLimiter.is_rate_limited(user_id, Config.RATE_LIMIT_PER_MINUTE):
        remaining = RateLimiter.get_remaining_requests(user_id, Config.RATE_LIMIT_PER_MINUTE)
        if remaining == 0:
            return
    
    # Create user if not exists
    await UserManager.create_user(user_id, update.effective_user.username)
    
    # Check if banned
    if await UserManager.is_banned(user_id):
        lang = await UserManager.get_user(user_id)
        language = lang.get('language', 'en') if lang else 'en'
        await update.message.reply_text(get_text(language, "ban_message"))
        return
    
    # Parse query and filters
    search_query, search_filters = FuzzySearch.parse_filters(query)
    
    if not search_query:
        return
    
    # Search files
    results = await FileManager.search_files(search_query, search_filters)
    
    if not results:
        # Try fuzzy search suggestions
        all_files = await db.files.find().to_list(length=100)
        file_names = [f['file_name'] for f in all_files]
        suggestions = FuzzySearch.suggest_correction(search_query, file_names)
        
        if suggestions:
            lang_doc = await UserManager.get_user(user_id)
            language = lang_doc.get('language', 'en') if lang_doc else 'en'
            sugg_text = ", ".join(suggestions[:3])
            await update.message.reply_text(
                get_text(language, "suggestion", suggestions=sugg_text)
            )
        return
    
    # Get random ad
    ad = await AdManager.get_random_ad()
    
    # Send results
    for file_doc in results[:10]:  # Limit to 10 results
        await send_file_result(
            update, context, file_doc, ad, user_id
        )
    
    # Delete user's message after delay (anti-spam)
    asyncio.create_task(delete_message_later(update.message, Config.AUTO_DELETE_DELAY))

async def send_file_result(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          file_doc: dict, ad: dict, user_id: int):
    """Send file result with download button and ad"""
    
    lang_doc = await UserManager.get_user(user_id)
    language = lang_doc.get('language', 'en') if lang_doc else 'en'
    
    # Format file size
    size = format_size(file_doc.get('file_size', 0))
    
    # Create inline keyboard
    keyboard = [[InlineKeyboardButton("🎬 Download Now", callback_data=f"download_{file_doc['file_id']}")]]
    
    # Add ad to message if available
    if ad:
        caption = get_text(
            language, "search_results",
            name=file_doc.get('file_name', 'Unknown'),
            size=size,
            count=file_doc.get('downloads', 0),
            ad_text=ad.get('text', ''),
            ad_button=ad.get('button_text', 'Learn More'),
            ad_url=ad.get('button_url', '#')
        )
    else:
        caption = f"""━━━━━━━━━━━━━━━━━━━━
📁 **SEARCH RESULTS**
━━━━━━━━━━━━━━━━━━━━
🎬 **File Name:** {file_doc.get('file_name', 'Unknown')}
📏 **Size:** {size}
⬇️ **Downloads:** {file_doc.get('downloads', 0)}

[🎬 Download Now](https://t.me/{context.bot.username}?start=file_{file_doc['file_id']})
━━━━━━━━━━━━━━━━━━━━"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send based on file type
    try:
        if file_doc.get('file_type') == 'video':
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=file_doc['file_id'],
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                protect_content=not await UserManager.is_vip(user_id)
            )
        elif file_doc.get('file_type') == 'audio':
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=file_doc['file_id'],
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                protect_content=not await UserManager.is_vip(user_id)
            )
        elif file_doc.get('file_type') == 'photo':
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=file_doc['file_id'],
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                protect_content=not await UserManager.is_vip(user_id)
            )
        else:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_doc['file_id'],
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                protect_content=not await UserManager.is_vip(user_id)
            )
    except Exception as e:
        # Fallback to link
        await update.message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def delete_message_later(message: Message, delay: int):
    """Delete message after delay"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {units[i]}"

def get_handlers():
    """Get all handlers for this plugin"""
    return [
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            auto_filter_handler
        )
    ]
