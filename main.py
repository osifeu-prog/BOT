# -*- coding: utf-8 -*-
import logging
import os
import sys
import telebot
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import wallet_logic
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
            body {{ font-family: sans-serif; background-color: #0a0a0a; color: white; text-align: center; padding: 20px; }}
            .card {{ background: linear-gradient(145deg, #1a1a1a, #000); border-radius: 25px; padding: 25px; border: 1px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
            .balance {{ font-size: 36px; color: #d4af37; font-weight: bold; margin: 10px 0; }}
            .btn-group {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }}
            .btn {{ background: #222; color: #d4af37; border: 1px solid #d4af37; padding: 15px; border-radius: 12px; font-weight: bold; cursor: pointer; }}
            .btn-main {{ background: #d4af37; color: black; grid-column: span 2; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="color: #888; font-size: 12px;">יתרה בחשבון</div>
            <div class="balance">{balance:,.2f} SLH</div>
            <div style="font-size: 11px; opacity: 0.6;">{addr}</div>
            
            <div class="btn-group">
                <button class="btn btn-main" onclick="scanQR()">🔍 סרוק QR להעברה</button>
                <button class="btn" onclick="showAddress()">📥 הכתובת שלי</button>
                <button class="btn" onclick="window.Telegram.WebApp.close()">✖️ סגור</button>
            </div>
        </div>

        <script>
            const webApp = window.Telegram.WebApp;
            webApp.ready();

            function scanQR() {{
                webApp.showScanQrPopup({{ text: "סרוק כתובת ארנק להעברה" }}, function(data) {{
                    webApp.sendData("transfer:" + data); // שולח את הכתובת חזרה לבוט
                    webApp.close();
                }});
            }}

            function showAddress() {{
                webApp.showAlert("כתובת הארנק שלך היא:\n{addr}");
            }}
        </script>
    </body>
    </html>
    """
    return html_content

@bot.message_handler(func=lambda message: True)
def handle_webapp_data(message):
    if message.web_app_data:
        data = message.web_app_data.data
        if data.startswith("transfer:"):
            target_addr = data.split(":")[1]
            bot.reply_to(message, f"💸 **העברה בביצוע...**\nיעד: {target_addr}\nכמה תרצה להעביר?")
            # כאן נמשיך ללוגיקת התשלום

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup()
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("🔱 פתח ארנק פרימיום", web_app=types.WebAppInfo(url)))
    bot.send_message(message.chat.id, "💎 **SLH OS Dashboard**", reply_markup=markup)

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
