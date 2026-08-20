"""Admin Plugin - Admin commands and management"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.settings import Config
from utils.user_manager import UserManager
from utils.file_manager import FileManager
from utils.managers import TokenManager, AdManager, RateLimiter
from utils.translations import get_text
from utils.database import db
import json
from datetime import datetime

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎁 Manage Tokens", callback_data="admin_tokens")],
        [InlineKeyboardButton("📺 Manage Ads", callback_data="admin_ads")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("💾 Backup/Restore", callback_data="admin_backup")],
        [InlineKeyboardButton("🚫 Ban/Unban", callback_data="admin_ban")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("en", "admin_panel"),
        reply_markup=reply_markup
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    # Get stats
    total_users = await UserManager.get_user_count()
    new_users_today = await UserManager.get_new_users_today()
    total_files = await FileManager.get_file_count()
    
    # Count VIP users
    vip_users = await db.users.count_documents({"is_vip": True})
    
    # Get total downloads
    all_users = await db.users.aggregate([
        {"$group": {"_id": None, "total_downloads": {"$sum": "$total_downloads"}}}
    ]).to_list(length=1)
    total_downloads = all_users[0]["total_downloads"] if all_users else 0
    
    message = get_text(
        "en", "stats",
        users=total_users,
        files=total_files,
        downloads=total_downloads,
        new_users=new_users_today,
        vip_users=vip_users
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    # Get message to broadcast (reply to a message or use args)
    if update.message.reply_to_message:
        message_to_send = update.message.reply_to_message
    elif context.args:
        message_to_send = ' '.join(context.args)
    else:
        await update.message.reply_text(
            "Usage: Reply to a message with /broadcast or\n/broadcast <message>"
        )
        return
    
    # Confirm broadcast
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Send", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    confirm_msg = await update.message.reply_text(
        "⚠️ **Confirm Broadcast**\n\n"
        "This will send a message to all users.\n"
        "Continue?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Store broadcast data
    context.user_data['broadcast_message'] = message_to_send
    context.user_data['broadcast_confirm_msg'] = confirm_msg

async def generate_token_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate VIP token"""
    
    user_id = update.effective_user.id
    
    # Check if admin or reseller
    if user_id not in Config.ADMIN_IDS:
        return
    
    # Get token parameters
    days = 30
    if context.args and context.args[0].isdigit():
        days = int(context.args[0])
    
    # Generate token
    token = await TokenManager.generate_token(user_id, days)
    
    await update.message.reply_text(
        f"✅ **Token Generated!**\n\n"
        f"🎫 Token: `{token}`\n"
        f"⏰ Duration: {days} days\n\n"
        f"Share this token with users!",
        parse_mode='Markdown'
    )

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem VIP token"""
    
    user_id = update.effective_user.id
    
    # Create user if not exists
    await UserManager.create_user(user_id, update.effective_user.username)
    
    # Check if banned
    if await UserManager.is_banned(user_id):
        lang_doc = await UserManager.get_user(user_id)
        language = lang_doc.get('language', 'en') if lang_doc else 'en'
        await update.message.reply_text(get_text(language, "ban_message"))
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /redeem <token>")
        return
    
    token = context.args[0]
    
    # Redeem token
    success, message = await TokenManager.redeem_token(user_id, token)
    
    lang_doc = await UserManager.get_user(user_id)
    language = lang_doc.get('language', 'en') if lang_doc else 'en'
    
    if success:
        await update.message.reply_text(
            get_text(language, "token_redeemed", message=message)
        )
    else:
        if "already used" in message.lower():
            await update.message.reply_text(get_text(language, "token_used"))
        else:
            await update.message.reply_text(get_text(language, "token_invalid"))

async def myplan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check VIP status"""
    
    user_id = update.effective_user.id
    
    user = await UserManager.get_user(user_id)
    if not user:
        await update.message.reply_text("User not found.")
        return
    
    lang_doc = await UserManager.get_user(user_id)
    language = lang_doc.get('language', 'en') if lang_doc else 'en'
    
    if user.get('is_vip'):
        expiry = user.get('vip_expiry')
        if expiry:
            expiry_str = expiry.strftime("%Y-%m-%d %H:%M")
        else:
            expiry_str = "Lifetime"
        
        await update.message.reply_text(
            get_text(language, "vip_active", expiry=expiry_str),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            get_text(language, "vip_expired"),
            parse_mode='Markdown'
        )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        await UserManager.ban_user(target_id)
        await update.message.reply_text(f"✅ User {target_id} has been banned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID.")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        await UserManager.unban_user(target_id)
        await update.message.reply_text(f"✅ User {target_id} has been unbanned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID.")

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup all data to JSON"""
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    await update.message.reply_text("🔄 Creating backup...")
    
    # Collect all data
    backup_data = {
        "users": await db.users.find().to_list(length=None),
        "files": await db.files.find().to_list(length=None),
        "settings": await db.settings.find().to_list(length=None),
        "ads": await db.ads.find().to_list(length=None),
        "tokens": await db.tokens.find().to_list(length=None),
        "backup_date": datetime.utcnow().isoformat()
    }
    
    # Convert ObjectId to string for JSON serialization
    def convert_objectid(obj):
        if isinstance(obj, dict):
            return {k: convert_objectid(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_objectid(i) for i in obj]
        elif hasattr(obj, '__str__') and type(obj).__name__ == 'ObjectId':
            return str(obj)
        return obj
    
    backup_data = convert_objectid(backup_data)
    
    # Save to file
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    # Send file to admin
    with open(filename, 'rb') as f:
        await context.bot.send_document(
            chat_id=user_id,
            document=f,
            filename=filename
        )
    
    await update.message.reply_text(get_text("en", "backup_created"))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    
    user_id = update.effective_user.id
    
    # Create user if not exists
    await UserManager.create_user(user_id, update.effective_user.username)
    
    # Get user language
    lang_doc = await UserManager.get_user(user_id)
    language = lang_doc.get('language', 'en') if lang_doc else 'en'
    
    await update.message.reply_text(
        get_text(language, "help"),
        parse_mode='Markdown'
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries"""
    
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in Config.ADMIN_IDS:
        return
    
    if query.data == "admin_stats":
        await stats_command(update, context)
    
    elif query.data == "broadcast_confirm":
        # Send broadcast
        message_to_send = context.user_data.get('broadcast_message')
        if message_to_send:
            count = 0
            async for user in db.users.find({}):
                try:
                    if isinstance(message_to_send, dict):
                        # It's a message object
                        await message_to_send.copy(chat_id=user['user_id'])
                    else:
                        # It's text
                        await context.bot.send_message(
                            chat_id=user['user_id'],
                            text=message_to_send
                        )
                    count += 1
                except:
                    pass
            
            await query.edit_message_text(
                get_text("en", "broadcast_sent", count=count)
            )
    
    elif query.data == "broadcast_cancel":
        await query.edit_message_text("❌ Broadcast cancelled.")

def get_handlers():
    """Get all handlers for this plugin"""
    return [
        CommandHandler('admin', admin_panel),
        CommandHandler('stats', stats_command),
        CommandHandler('broadcast', broadcast_command),
        CommandHandler('gentoken', generate_token_command),
        CommandHandler('redeem', redeem_command),
        CommandHandler('myplan', myplan_command),
        CommandHandler('ban', ban_command),
        CommandHandler('unban', unban_command),
        CommandHandler('backup', backup_command),
        CommandHandler('help', help_command),
        CallbackQueryHandler(callback_handler, pattern='^admin_'),
        CallbackQueryHandler(callback_handler, pattern='^broadcast_')
    ]
