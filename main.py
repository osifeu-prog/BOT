# -*- coding: utf-8 -*-
import telebot, os, uvicorn, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, BotCommand
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SLH-OS] - %(levelname)s - %(message)s')
logger = logging.getLogger("SLH_OS")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"

@app.on_event("startup")
async def startup_event():
    init_db()
    # הגדרת תפריט הפקודות בטלגרם (התפריט הכחול)
    bot.set_my_commands([
        BotCommand("start", "🚀 Open System"),
        BotCommand("wallet", "💰 Open SLH Wallet"),
        BotCommand("all", "📋 Master Menu"),
        BotCommand("myid", "🆔 Copy my ID"),
        BotCommand("ai", "🤖 Ask SLH AI")
    ])
    logger.info("🚀 SLH OS Engine is Live")

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    balance, xp, rank = wallet_logic.get_user_full_data(user_id)
    total_supply, _ = wallet_logic.get_economy_stats()
    return f"""
    <html><head><meta charset="UTF-8">
    <script>
        function refresh() {{ fetch(window.location.href).then(r => r.text()).then(html => {{
            let parser = new DOMParser();
            let newDoc = parser.parseFromString(html, 'text/html');
            document.getElementById('balance').innerHTML = newDoc.getElementById('balance').innerHTML;
            document.getElementById('supply').innerHTML = newDoc.getElementById('supply').innerHTML;
        }}); }}
        setInterval(refresh, 3000); 
    </script>
    <style>
        body {{ background: #0b0e11; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; overflow: hidden; }}
        .card {{ background: #1e2329; margin: auto; padding: 30px; border-radius: 25px; width: 85%; border-top: 5px solid #f0b90b; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .balance {{ font-size: 50px; color: #f0b90b; font-weight: bold; margin: 15px 0; }}
        .btn {{ background: #f0b90b; color: #0b0e11; padding: 12px; border-radius: 12px; font-weight: bold; border: none; width: 100%; cursor: pointer; }}
    </style></head>
    <body>
        <div class="card">
            <div style="opacity:0.7; font-size: 14px;">AVAILABLE SLH</div>
            <div class="balance" id="balance">{balance}</div>
            <div style="margin-bottom: 20px;">{rank} | {xp} XP</div>
            <button class="btn" onclick="window.Telegram.WebApp.close()">BACK TO BOT</button>
            <div style="margin-top:30px; font-size:10px; opacity:0.3;" id="supply">TOTAL SUPPLY: {total_supply:,.0f} SLH</div>
        </div>
    </body></html>"""

@bot.message_handler(commands=['start', 'wallet'])
def start_and_wallet(message):
    user_id = message.from_user.id
    wallet_logic.register_user(user_id)
    
    # יצירת כפתור מובנה (Inline) להודעה
    markup = InlineKeyboardMarkup()
    wallet_url = f"{WEBHOOK_URL}/gui/wallet?user_id={user_id}"
    markup.add(InlineKeyboardButton("💰 Open My Wallet", web_app=WebAppInfo(wallet_url)))
    
    # כפתור תפריט רגיל (Reply)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(KeyboardButton("💰 Wallet", web_app=WebAppInfo(wallet_url)))
    
    bot.send_message(
        message.chat.id, 
        "💎 **SLH OS Dashboard**\n\nYour wallet and commands are ready. Click the button below to view your balance in real-time.", 
        reply_markup=reply_markup, # מוסיף כפתור מקלדת
        parse_mode="Markdown"
    )
    # שולח גם את הכפתור המובנה
    bot.send_message(message.chat.id, "Quick Access:", reply_markup=markup)

@bot.message_handler(commands=['ai'])
def ai_handler(message):
    bot.reply_to(message, "🤖 **SLH AI:** I am monitoring the blockchain. Economy is stable. Total users: checking...")

@bot.message_handler(commands=['all'])
def show_all(message):
    bot.reply_to(message, "📋 Click any command:\n/wallet - Open Wallet\n/myid - Get ID\n/receive - Get paid\n/admin - Dashboard")

@bot.message_handler(commands=['myid'])
def my_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`\n(Tap to copy)", parse_mode="Markdown")

@app.post("/")
async def process_webhook(request: Request):
    json_data = await request.json()
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
