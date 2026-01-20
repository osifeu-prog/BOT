#!/usr/bin/env python3
"""
?? NFTY ULTRA CASINO - ???? ????? ????
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        ContextTypes,
        MessageHandler,
        filters
    )
    import redis
    from config import TELEGRAM_TOKEN, ADMIN_IDS, REDIS_URL, DEBUG_MODE
except ImportError as e:
    logger.error(f"????? ??????: {e}")
    sys.exit(1)

# ============ ????? Redis ============
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_user_balance(user_id):
    balance = redis_client.hget(f"user:{user_id}", "balance")
    return int(balance) if balance else 1000

def update_user_balance(user_id, amount):
    current = get_user_balance(user_id)
    new_balance = current + amount
    redis_client.hset(f"user:{user_id}", "balance", new_balance)
    return new_balance

def register_user(user_id, username, first_name):
    user_key = f"user:{user_id}"
    if not redis_client.exists(user_key):
        redis_client.hset(user_key, mapping={
            "id": user_id,
            "username": username or "",
            "first_name": first_name or "",
            "balance": 1000,
            "tier": "Free",
            "joined": datetime.now().isoformat()
        })
        return True
    return False

# ============ Health Check Server ============
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/health", "/"]:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_health_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

# ============ ???????? ???? ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    register_user(user_id, user.username, user.first_name)
    balance = get_user_balance(user_id)
    
    welcome_text = f"""
?? **???? ??? ?-NFTY ULTRA CASINO!**

?? **????:** {user.first_name}
?? **????:** {balance:,} ??
?? **????:** Free

?? **??? ?????:**
"""
    
    keyboard = [
        [InlineKeyboardButton("?? Mines Game", callback_data="play_mines")],
        [InlineKeyboardButton("?? Slots", callback_data="play_slots")],
        [InlineKeyboardButton("?? Crash", callback_data="play_crash")],
        [InlineKeyboardButton("?? ????? ????", callback_data="daily_bonus")],
        [InlineKeyboardButton("?? ????? ????", callback_data="check_balance")],
        [InlineKeyboardButton("?? ??????", callback_data="affiliate")]
    ]
    
    if str(user_id) in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("?? ???? ????", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "check_balance":
        balance = get_user_balance(user_id)
        await query.edit_message_text(f"?? **????? ???:** {balance:,} ??????")
    
    elif data == "daily_bonus":
        new_balance = update_user_balance(user_id, 100)
        await query.edit_message_text(f"?? **????? ???? ?????!**\n\n+100 ??????\n?? ???? ????: {new_balance:,}")
    
    elif data == "admin_panel":
        if str(user_id) not in ADMIN_IDS:
            await query.answer("? ??? ?????? ????!", show_alert=True)
            return
        await query.edit_message_text("?? **???? ??????**\n\n/gift [id] [amount] - ??? ????\n/users - ????? ???????\n/stats - ??????????")
    
    elif data == "affiliate":
        ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start=ref{user_id}"
        await query.edit_message_text(f"?? **???? ??????**\n\n?? ????? ?????? ???:\n`{ref_link}`\n\n?? ??? ?????? ??? ????? ?? ???? ???? ?-500 ??????!")
    
    else:
        # ??????? - ????? ??????
        game_name = "????"
        if "mines" in data: game_name = "?? Mines"
        elif "slots" in data: game_name = "?? Slots"
        elif "crash" in data: game_name = "?? Crash"
        
        await query.edit_message_text(f"??? **{game_name} - ???????**\n\n????? ???? ??????? ??????. ???? ???? ???? ????? ???? ?????? ????.\n\n?? ??? /start ?????")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
?? **???? - NFTY ULTRA CASINO**

?? **?????? ??????:**
/start - ????? ????
/help - ????? ??
/balance - ????? ????

?? **????? ???????:**
• ?? Mines - ??? ??????? ?????? ???????
• ?? Slots - ???? ?????? ??????
• ?? Crash - ???? ???? ?????? ?????

?? **?????:**
• ???? ???????: 1,000 ??????
• ????? ????: 100 ??????
• ??????: 500 ?????? ??????
""", parse_mode="Markdown")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = get_user_balance(user_id)
    await update.message.reply_text(f"?? **????? ???:** {balance:,} ?????? ??")

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("? ??? ?????? ????!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("? ?????: /gift [user_id] [amount]")
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        new_balance = update_user_balance(target_id, amount)
        await update.message.reply_text(f"? ????? {amount} ?????? ?????? {target_id}\n?? ???? ????: {new_balance:,}")
    except:
        await update.message.reply_text("? ????? ?????? ?????")

# ============ ???? ????? ============
def main():
    # ????? ????
    if not TELEGRAM_TOKEN:
        logger.error("? TELEGRAM_TOKEN ?? ?????!")
        return
    
    # ???? ??? health check
    port = int(os.environ.get("PORT", 8080))
    health_thread = threading.Thread(target=start_health_server, args=(port,), daemon=True)
    health_thread.start()
    
    # ??? ????????? ????
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # ???? handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("gift", gift_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # ???? ????? ??????
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        logger.info("?? Running in Railway mode (webhook)")
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "bot.up.railway.app")
        url = f"https://{domain}/{TELEGRAM_TOKEN}"
        
        # ??? webhook ???? ????? ???
        async def setup_webhook():
            await application.bot.delete_webhook()
            await application.bot.set_webhook(url=url)
            await application.start()
            await application.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=url
            )
            logger.info(f"? Webhook set: {url}")
            await asyncio.Event().wait()
        
        asyncio.run(setup_webhook())
    else:
        logger.info("?? Running in local mode (polling)")
        application.run_polling()

if __name__ == "__main__":
    main()
