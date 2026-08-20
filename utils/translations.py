"""Translations for multi-language support"""

TRANSLATIONS = {
    "en": {
        "welcome": "👋 Welcome {name}!\n\nI'm an advanced file store and auto-filter bot.\n\n📁 Store your files permanently\n🔍 Search files instantly\n⚡ Fast and reliable\n\nUse /help to learn more!",
        "goodbye": "👋 Goodbye {name}! Hope to see you again soon.",
        "help": """ℹ️ **Bot Commands**\n\n**User Commands:**\n/start - Start the bot\n/help - Show this message\n/search <query> - Search for files\n/trending - Show trending files\n/redeem <token> - Redeem VIP token\n/myplan - Check your VIP status\n\n**File Store:**\nSend any file to the bot in private chat to store it permanently!\n\n**Advanced Search:**\nUse filters like:\n`/search movie quality:1080p language:hindi`\n""",
        "search_results": "📁 **SEARCH RESULTS**\n\n🎬 **File Name:** {name}\n📏 **Size:** {size}\n⬇️ **Downloads:** {count}\n\n━━━━━━━━━━━━━━━━━━━━\n📢 **SPONSORED ADS**\n━━━━━━━━━━━━━━━━━━━━\n{ad_text}\n[👉 {ad_button}]({ad_url})\n━━━━━━━━━━━━━━━━━━━━",
        "no_results": "❌ No results found for \"{query}\".\n\nTry different keywords or check for typos.",
        "suggestion": "💡 Did you mean: {suggestions}?",
        "download_limit": "⚠️ **Download Limit Reached!**\n\nYou've reached your daily download limit ({limit} files).\n\nUpgrade to VIP for unlimited downloads!\n\nUse /redeem to activate VIP.",
        "vip_active": "✅ **VIP Active**\n\nYour VIP subscription is active until:\n📅 {expiry}\n\nEnjoy unlimited downloads!",
        "vip_expired": "❌ **VIP Expired**\n\nYour VIP subscription has expired.\n\nUse /redeem to activate a new VIP token.",
        "not_vip": "⚠️ **VIP Required**\n\nThis feature requires VIP access.\n\nUse /redeem to activate VIP.",
        "file_saved": "✅ **File Saved Successfully!**\n\n📁 File Name: {name}\n📏 Size: {size}\n🔗 Share Link: {link}",
        "duplicate_file": "⚠️ **Duplicate Detected!**\n\nThis file already exists in our database.",
        "token_invalid": "❌ Invalid or expired token.",
        "token_used": "❌ This token has already been used.",
        "token_redeemed": "✅ **Token Redeemed!**\n\n{message}",
        "ban_message": "🚫 **You are banned!**\n\nYou cannot use this bot anymore.",
        "rate_limited": "⚠️ **Rate Limited**\n\nPlease wait {seconds} seconds before trying again.",
        "stats": """📊 **Bot Statistics**\n\n👥 Total Users: {users}\n📁 Total Files: {files}\n⬇️ Total Downloads: {downloads}\n🆕 New Users Today: {new_users}\n⭐ VIP Users: {vip_users}""",
        "admin_panel": "🔧 **Admin Panel**\n\nChoose an option:",
        "broadcast_sent": "✅ Broadcast sent to {count} users.",
        "backup_created": "✅ Backup created successfully!",
        "restore_complete": "✅ Restore completed successfully!",
    },
    "hi": {
        "welcome": "👋 स्वागत है {name}!\n\nमैं एक एडवांस्ड फाइल स्टोर और ऑटो-फिल्टर बॉट हूं।\n\n📁 अपनी फाइलों को स्थायी रूप से स्टोर करें\n🔍 तुरंत फाइलें खोजें\n⚡ तेज और विश्वसनीय\n\nअधिक जानने के लिए /help का उपयोग करें!",
        "goodbye": "👋 अलविदा {name}! जल्द ही फिर से मिलने की उम्मीद है।",
        "help": """ℹ️ **बॉट कमांड्स**\n\n**उपयोगकर्ता कमांड्स:**\n/start - बॉट शुरू करें\n/help - यह संदेश दिखाएं\n/search <query> - फाइलें खोजें\n/trending - ट्रेंडिंग फाइलें दिखाएं\n/redeem <token> - VIP टोकन रिडीम करें\n/myplan - अपनी VIP स्थिति जांचें\n\n**फाइल स्टोर:**\nकिसी भी फाइल को बॉट को प्राइवेट चैट में भेजें ताकि इसे स्थायी रूप से स्टोर किया जा सके!\n\n**एडवांस्ड सर्च:**\nफिल्टर का उपयोग करें जैसे:\n`/search movie quality:1080p language:hindi`\n""",
        "search_results": "📁 **खोज परिणाम**\n\n🎬 **फाइल नाम:** {name}\n📏 **आकार:** {size}\n⬇️ **डाउनलोड:** {count}\n\n━━━━━━━━━━━━━━━━━━━━\n📢 **प्रायोजित विज्ञापन**\n━━━━━━━━━━━━━━━━━━━━\n{ad_text}\n[👉 {ad_button}]({ad_url})\n━━━━━━━━━━━━━━━━━━━━",
        "no_results": "❌ \"{query}\" के लिए कोई परिणाम नहीं मिला।\n\nविभिन्न कीवर्ड आज़माएं या वर्तनी की जांच करें।",
        "suggestion": "💡 क्या आपका मतलब था: {suggestions}?",
        "download_limit": "⚠️ **डाउनलोड सीमा पूरी हुई!**\n\nआपने अपनी दैनिक डाउनलोड सीमा ({limit} फाइलें) पूरी कर ली है।\n\nअसीमित डाउनलोड के लिए VIP में अपग्रेड करें!\n\nVIP सक्रिय करने के लिए /redeem का उपयोग करें।",
        "vip_active": "✅ **VIP सक्रिय**\n\nआपकी VIP सदस्यता इस तक सक्रिय है:\n📅 {expiry}\n\nअसीमित डाउनलोड का आनंद लें!",
        "vip_expired": "❌ **VIP समाप्त हो गया**\n\nआपकी VIP सदस्यता समाप्त हो गई है।\n\nनया VIP टोकन सक्रिय करने के लिए /redeem का उपयोग करें।",
        "not_vip": "⚠️ **VIP आवश्यक**\n\nइस सुविधा के लिए VIP एक्सेस की आवश्यकता है।\n\nVIP सक्रिय करने के लिए /redeem का उपयोग करें।",
        "file_saved": "✅ **फाइल सफलतापूर्वक सहेजी गई!**\n\n📁 फाइल नाम: {name}\n📏 आकार: {size}\n🔗 शेयर लिंक: {link}",
        "duplicate_file": "⚠️ **डुप्लिकेट का पता चला!**\n\nयह फाइल पहले से हमारे डेटाबेस में मौजूद है।",
        "token_invalid": "❌ अमान्य या समाप्त टोकन।",
        "token_used": "❌ इस टोकन का पहले ही उपयोग किया जा चुका है।",
        "token_redeemed": "✅ **टोकन रिडीम किया गया!**\n\n{message}",
        "ban_message": "🚫 **आप प्रतिबंधित हैं!**\n\nआप अब इस बॉट का उपयोग नहीं कर सकते।",
        "rate_limited": "⚠️ **दर सीमित**\n\nकृपया पुनः प्रयास करने से पहले {seconds} सेकंड प्रतीक्षा करें।",
        "stats": """📊 **बॉट आंकड़े**\n\n👥 कुल उपयोगकर्ता: {users}\n📁 कुल फाइलें: {files}\n⬇️ कुल डाउनलोड: {downloads}\n🆕 आज नए उपयोगकर्ता: {new_users}\n⭐ VIP उपयोगकर्ता: {vip_users}""",
        "admin_panel": "🔧 **एडमिन पैनल**\n\nएक विकल्प चुनें:",
        "broadcast_sent": "✅ {count} उपयोगकर्ताओं को प्रसारण भेजा गया।",
        "backup_created": "✅ बैकअप सफलतापूर्वक बनाया गया!",
        "restore_complete": "✅ पुनर्स्थापना सफलतापूर्वक पूरी हुई!",
    }
}

def get_text(language: str, key: str, **kwargs) -> str:
    """Get translated text
    
    Args:
        language: Language code ('en' or 'hi')
        key: Translation key
        **kwargs: Format arguments
    
    Returns:
        Translated and formatted text
    """
    # Fallback to English if language not supported
    if language not in TRANSLATIONS:
        language = "en"
    
    text = TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)
    
    # Format with kwargs
    try:
        return text.format(**kwargs)
    except KeyError:
        return text
