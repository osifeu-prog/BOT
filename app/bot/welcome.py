# app/bot/welcome.py - גרסה משופרת
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db
from config import ADMIN_IDS
import random

async def start(update, context):
    user = update.effective_user
    uid = user.id
    
    # שמור משתמש חדש אם לא קיים
    db.register_user(uid, user.username, user.first_name)
    
    # קבל מידע משתמש
    user_info = db.get_user(uid)
    tier = user_info.get("tier", "Free")
    balance = int(user_info.get("balance", 0))
    referrals = db.r.scard(f"user:{uid}:referrals") or 0
    
    # אמוג'ים דינמיים לפי שעה ביום
    from datetime import datetime
    hour = datetime.now().hour
    if 6 <= hour < 12:
        time_emoji = "🌅"
    elif 12 <= hour < 18:
        time_emoji = "☀️"
    elif 18 <= hour < 23:
        time_emoji = "🌙"
    else:
        time_emoji = "🌌"
    
    # אמוג'י דרגה
    tier_emojis = {"Free": "🆓", "Pro": "⚡", "VIP": "👑"}
    
    # טקסט פתיחה עשיר
    welcome_text = f"""
{time_emoji} **ברוך הבא ל-NFTY ULTRA CASINO PREMIUM!** 🎰

{tier_emojis.get(tier, "👤")} **משתמש:** {user.first_name}
💎 **דרגה:** {tier} {tier_emojis.get(tier, "")}
💰 **יתרה:** {balance:,} 🪙
👥 **הפניות:** {referrals} משתמשים
📊 **רמת ניסיון:** {random.randint(1, 100)}/100

🎮 **אוסף המשחקים שלנו:**
"""
    
    # יצירת מקלדת משחקים משופרת עם פריסה טובה יותר
    keyboard = [
        [
            InlineKeyboardButton("💣 Mines", callback_data="play_mines"),
            InlineKeyboardButton("🎰 Slots", callback_data="play_slots"),
            InlineKeyboardButton("🚀 Crash", callback_data="play_crash")
        ],
        [
            InlineKeyboardButton("🎯 Roulette", callback_data="play_roulette"),
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
            InlineKeyboardButton("⚙️ הגדרות", callback_data="settings")
        ]
    ]
    
    # כפתור אדמין רק למנהלים
    if str(uid) in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("🔐 לוח בקרה", callback_data="admin_dashboard")])
    
    keyboard.append([InlineKeyboardButton("ℹ️ עזרה & תמיכה", callback_data="help_support")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # אם זה הודעת callback, ערוך את ההודעה הקיימת
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # שלח הודעה חדשה עם אנימציה
        try:
            await update.message.reply_chat_action(action='typing')
            await asyncio.sleep(0.5)
            await update.message.reply_text(
                text=welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text(
                text=welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

async def send_animated_message(update, text, parse_mode='Markdown'):
    """שלח הודעה עם אנימציית הקלדה"""
    try:
        if update.callback_query:
            await update.callback_query.message.reply_chat_action(action='typing')
        else:
            await update.message.reply_chat_action(action='typing')
        
        await asyncio.sleep(0.3)
        
        if update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode=parse_mode)
        else:
            await update.message.reply_text(text, parse_mode=parse_mode)
    except Exception as e:
        # Fallback אם האנימציה נכשלת
        if update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode=parse_mode)
        else:
            await update.message.reply_text(text, parse_mode=parse_mode)
