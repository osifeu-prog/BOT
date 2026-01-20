import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN, ADMIN_ID
from app.database.manager import db

async def start(update: Update, context):
    uid = update.effective_user.id
    user = db.get_user(uid, context.args[0] if context.args else None)
    
    # טקסט שיווקי ממיר
    text = (
        f"👑 **ברוך הבא ל-NFTY PRO CASINO**\n"
        f"הפלטפורמה המובילה למסחר ומשחקי הסתברות בטלגרם.\n\n"
        f"👤 **פרופיל משתמש:**\n"
        f"🆔 מזהה: `{uid}`\n"
        f"💎 דרגה: *{user.get('tier', 'Free')}*\n"
        f"💰 יתרה: `{user['balance']}` 🪙\n\n"
        f"🚀 **מה עושים עכשיו?**\n"
        f"בחר משחק מהתפריט למטה או שדרג את החשבון שלך ל-VIP כדי לקבל סיכויי זכייה של עד 95%!"
    )
    
    kb = [
        [InlineKeyboardButton("💣 משחק Mines (פופולרי)", callback_data="play_mines")],
        [InlineKeyboardButton("🛒 חנות שדרוגים & VIP", callback_data="open_shop")],
        [InlineKeyboardButton("👥 תוכנית שותפים (רווח פסיבי)", callback_data="affiliate_panel")],
        [InlineKeyboardButton("🆘 תמיכה ומדריכים", url=os.getenv("PARTICIPANTS_GROUP_LINK", "https://t.me/"))]
    ]
    
    if str(uid) == str(ADMIN_ID):
        kb.append([InlineKeyboardButton("📊 פאנל ניהול CRM", callback_data="admin_report")])

    markup = InlineKeyboardMarkup(kb)
    if update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode='Markdown')
