import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import get_user_profile, update_user_stat, get_market_price
from mines import start_mines, handle_mine_click
from payment_flow import handle_payment_screenshot, send_broadcast
from admin_panel import admin_main

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = get_user_profile(user.id)
    
    welcome_text = (
        f"👑 <b>ברוכים הבאים ל-NFTY MADNESS</b> 👑\n\n"
        f"👤 שחקן: <code>{user.first_name}</code>\n"
        f"💰 יתרה: <b>{int(profile['balance']):,} 🪙</b>\n"
        f"📈 מניות: <b>{profile['stocks']}</b>\n"
        f"🏆 דרגה: <b>{profile['tier']}</b>\n"
        f"━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 משחק מוקשים", callback_data="game_mines"), 
         InlineKeyboardButton("💹 בורסה", callback_data="nav_market")],
        [InlineKeyboardButton("💎 הפקדה (AI)", callback_data="nav_shop"),
         InlineKeyboardButton("📊 פרופיל", callback_data="nav_profile")]
    ]
    
    if str(user.id) == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ ניהול אדמין", callback_data="admin_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", send_broadcast))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(start, pattern="nav_home"))
    application.add_handler(CallbackQueryHandler(start_mines, pattern="game_mines"))
    application.add_handler(CallbackQueryHandler(handle_mine_click, pattern="mine_"))
    application.add_handler(CallbackQueryHandler(admin_main, pattern="admin_main"))
    
    # AI Payment (Photo listener)
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
    
    print("🚀 NFTY Madness is running...")
    application.run_polling()
