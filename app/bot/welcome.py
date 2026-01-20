from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start(update, context):
    user = update.effective_user
    uid = user.id
    
    # Register user if not exists
    db.register_user(uid, user.username, user.first_name)
    
    # Get user info
    user_info = db.get_user(uid)
    tier = user_info.get("tier", "Free")
    balance = int(user_info.get("balance", 0))
    referrals = db.r.scard(f"user:{uid}:referrals") or 0
    
    welcome_text = f"""
🎰 **ברוך הבא ל-NFTY ULTRA CASINO!** 🎰

👤 **משתמש:** {user.first_name}
💎 **דרגה:** {tier}
💰 **יתרה:** {balance} מטבעות
👥 **הפניות:** {referrals} משתמשים

🎮 **בחר משחק:**
"""
    
    keyboard = [
        [InlineKeyboardButton("💣 Mines (מוקשים)", callback_data="play_mines")],
        [InlineKeyboardButton("🎰 Slots (מכונות)", callback_data="play_slots")],
        [InlineKeyboardButton("🚀 Crash (התרסקות)", callback_data="play_crash")],
        [
            InlineKeyboardButton("🛒 חנות VIP", callback_data="open_shop"),
            InlineKeyboardButton("🎁 בונוס יומי", callback_data="daily_bonus")
        ],
        [
            InlineKeyboardButton("👥 שותפים", callback_data="affiliate_panel"),
            InlineKeyboardButton("📊 דוח משתמש", callback_data="user_report")
        ]
    ]
    
    from config import ADMIN_IDS
    if str(uid) in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ לוח בקרה", callback_data="admin_report")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
