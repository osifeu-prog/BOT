from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db
from config import ADMIN_IDS
import random
from datetime import datetime

async def start(update, context):
    user = update.effective_user
    uid = user.id
    
    db.register_user(uid, user.username, user.first_name)
    
    user_info = db.get_user(uid)
    tier = user_info.get("tier", "Free")
    balance = int(user_info.get("balance", 0))
    referrals = db.r.scard(f"user:{uid}:referrals") or 0
    
    hour = datetime.now().hour
    if 6 <= hour < 12: time_emoji = "🌅"
    elif 12 <= hour < 18: time_emoji = "☀️"
    elif 18 <= hour < 23: time_emoji = "🌙"
    else: time_emoji = "🌌"
    
    tier_emojis = {"Free": "🆓", "Pro": "⚡", "VIP": "👑"}
    
    welcome_text = f"""
{time_emoji} **ברוך הבא ל-NFTY ULTRA CASINO PREMIUM!** 🎰

{tier_emojis.get(tier, "👤")} **משתמש:** {user.first_name}
💎 **דרגה:** {tier} {tier_emojis.get(tier, "")}
💰 **יתרה:** {balance:,} 🪙
👥 **הפניות:** {referrals} משתמשים
📊 **רמת ניסיון:** {random.randint(1, 100)}/100

🎮 **אוסף המשחקים שלנו:**
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💣 Mines", callback_data="play_mines"),
            InlineKeyboardButton("🎰 Slots", callback_data="play_slots"),
            InlineKeyboardButton("🚀 Crash", callback_data="play_crash")
        ],
        [
            InlineKeyboardButton("🎡 Roulette", callback_data="play_roulette"),
            InlineKeyboardButton("🃏 Blackjack", callback_data="play_blackjack"),
            InlineKeyboardButton("🎲 Dice", callback_data="play_dice")
        ],
        [
            InlineKeyboardButton("🛒 חנות VIP", callback_data="open_shop"),
            InlineKeyboardButton("🎁 בונוס יומי", callback_data="daily_bonus"),
            InlineKeyboardButton("📈 דוח", callback_data="user_report")
        ],
        [
            InlineKeyboardButton("👥 שותפים", callback_data="affiliate_panel"),
            InlineKeyboardButton("🏆 לוח תוצאות", callback_data="leaderboard"),
            InlineKeyboardButton("📋 משימות יומיות", callback_data="daily_tasks")
        ]
    ]
    
    if str(uid) in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("🔐 לוח בקרה", callback_data="admin_report")])
    
    keyboard.append([InlineKeyboardButton("ℹ️ עזרה", callback_data="help")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text=welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
