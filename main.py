# -*- coding: utf-8 -*-
import logging, os, sys, telebot, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID
from handlers import wallet_logic

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
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
            body {{ background: #000; color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }}
            .card {{ border: 1px solid #d4af37; border-radius: 15px; padding: 20px; background: #111; }}
            .btn {{ background: #d4af37; color: #000; border: none; padding: 12px; border-radius: 8px; width: 100%; font-weight: bold; margin-top: 15px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h3>הארנק שלי</h3>
            <div style="font-size: 24px; color: #d4af37;">{balance:,.2f} SLH</div>
            <p style="font-size: 10px; color: #666;">{addr if addr else "לא מחובר"}</p>
            <button class="btn" onclick="connect()">💎 קבל 5 SLH מתנה</button>
        </div>
        <script>
            function connect() {{
                window.Telegram.WebApp.sendData("ton_connect:UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp");
            }}
        </script>
    </body>
    </html>
    """
    return html_content

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    data = message.web_app_data.data
    if data.startswith("ton_connect:"):
        wallet_addr = data.split(":")[1]
        success, result = wallet_logic.claim_airdrop(message.from_user.id, wallet_addr)
        if success:
            bot.send_message(message.chat.id, f"✅ **Airdrop בוצע!**\nקיבלת {result} SLH.\nכתובת: {wallet_addr}")
        else:
            bot.send_message(message.chat.id, f"❌ {result}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🏦 פתח ארנק", web_app=types.WebAppInfo(url)))
    
    # פאנל אדמין
    if str(message.from_user.id) == str(ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 **שלום אדמין!**\nהבוט פועל ותקין.\nהשתמש ב-/stats לנתוני מערכת.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "💎 **SLH OS v2.0**\nלחץ על הכפתור למטה לקבלת אירדרופ!", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        # כאן תוכל להוסיף שליפה של כמות משתמשים מה-DB
        bot.reply_to(message, "📊 **סטטיסטיקת מערכת:**\n- שרת: Railway Active\n- רשת: TON Testnet\n- סך מטבעות שחולקו: 105 SLH")

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
