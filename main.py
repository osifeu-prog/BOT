# -*- coding: utf-8 -*-
import logging
import os
import sys
import telebot
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import wallet_logic, saas, router, admin, ai_agent
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("SLH_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- WEB APP GUI (המיני-סייט) ---
@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    # שליפת נתונים אמיתיים מה-DB
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ font-family: sans-serif; background-color: #0f0f0f; color: white; text-align: center; padding: 20px; }}
            .card {{ background: linear-gradient(145deg, #1e1e1e, #111); border-radius: 20px; padding: 25px; border: 1px solid #d4af37; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }}
            .balance {{ font-size: 32px; color: #d4af37; font-weight: bold; margin: 10px 0; }}
            .address {{ font-size: 12px; color: #888; background: #222; padding: 5px; border-radius: 5px; }}
            .btn {{ background: #d4af37; color: black; border: none; padding: 12px 25px; border-radius: 10px; font-weight: bold; margin-top: 20px; width: 100%; cursor: pointer; }}
            .stats {{ display: flex; justify-content: space-around; margin-top: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="font-size: 14px; color: #aaa;">יתרה נוכחית</div>
            <div class="balance">{balance:,.2f} SLH</div>
            <div class="address">{addr}</div>
            
            <div class="stats">
                <div>🏆 דרגה: <br><strong>{rank}</strong></div>
                <div>✨ ניסיון: <br><strong>{xp} XP</strong></div>
            </div>
            
            <button class="btn" onclick="window.Telegram.WebApp.close()">חזרה לבוט</button>
        </div>
        <script>
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        </script>
    </body>
    </html>
    """
    return html_content

# --- שאר הפונקציות של הבוט (שחזור מלא) ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup()
    web_app_url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("🌐 פתח ארנק (Mini-App)", web_app=types.WebAppInfo(web_app_url)))
    bot.send_message(message.chat.id, "💎 **SLH OS Dashboard**\nלחץ על הכפתור למטה לפתיחת הממשק הגרפי.", reply_markup=markup)

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=port)
