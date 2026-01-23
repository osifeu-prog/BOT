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

@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a; color: white; text-align: center; padding: 20px; margin: 0; }}
            .card {{ background: linear-gradient(145deg, #1a1a1a, #000); border-radius: 25px; padding: 30px; border: 1px solid #d4af37; box-shadow: 0 15px 35px rgba(0,0,0,0.8); margin-top: 20px; }}
            .balance {{ font-size: 40px; color: #d4af37; font-weight: bold; margin: 15px 0; letter-spacing: 1px; }}
            .address {{ font-size: 11px; color: #666; background: #111; padding: 8px; border-radius: 8px; font-family: monospace; display: block; margin-bottom: 20px; }}
            .stats-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }}
            .stat-box {{ background: #151515; padding: 15px; border-radius: 15px; border: 1px solid #333; }}
            .stat-label {{ font-size: 12px; color: #888; margin-bottom: 5px; }}
            .stat-value {{ font-size: 18px; font-weight: bold; color: #fff; }}
            .btn {{ background: linear-gradient(90deg, #d4af37, #f2d06b); color: black; border: none; padding: 15px; border-radius: 12px; font-weight: bold; margin-top: 30px; width: 100%; font-size: 16px; cursor: pointer; transition: 0.3s; }}
            .btn:active {{ transform: scale(0.98); opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="font-size: 14px; color: #d4af37; text-transform: uppercase; letter-spacing: 2px;">Digital Asset Vault</div>
            <div class="balance">{balance:,.2f} SLH</div>
            <span class="address">{addr}</span>
            
            <div class="stats-container">
                <div class="stat-box">
                    <div class="stat-label">דרגת חשבון</div>
                    <div class="stat-value">{rank}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">ניסיון (XP)</div>
                    <div class="stat-value">{xp}</div>
                </div>
            </div>
            
            <button class="btn" onclick="window.Telegram.WebApp.close()">סגור וחזור לבוט</button>
        </div>
        <script>
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        </script>
    </body>
    </html>
    """
    return html_content

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup()
    web_app_url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("🔱 פתח ארנק פרימיום", web_app=types.WebAppInfo(web_app_url)))
    bot.send_message(message.chat.id, "💎 **SLH OS v2.0**\nהממשק הגרפי שלך מוכן.", reply_markup=markup)

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
