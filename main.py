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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SLH_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    # שימוש ב-{{ }} רק בתוך ה-CSS/JS ב-HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ background-color: #0a0a0a; color: white; text-align: center; font-family: sans-serif; padding: 20px; }}
            .card {{ background: linear-gradient(145deg, #1a1a1a, #000); border-radius: 20px; padding: 25px; border: 1px solid #d4af37; box-shadow: 0 5px 15px rgba(212,175,55,0.2); }}
            .balance {{ font-size: 32px; color: #d4af37; margin: 10px 0; font-weight: bold; }}
            .btn {{ background: #007AFF; color: white; border: none; padding: 15px; border-radius: 12px; width: 100%; font-weight: bold; margin-top: 20px; cursor: pointer; font-size: 16px; }}
            .status {{ font-size: 11px; color: #666; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="font-size: 14px; opacity: 0.8;">יתרת SLH</div>
            <div class="balance">{balance:,.2f}</div>
            <div style="font-size: 11px; color: #888; overflow-wrap: break-word;">{addr if addr else "ארנק לא מחובר"}</div>
            
            <button class="btn" onclick="connectTon()">💎 חבר ארנק TON (Airdrop)</button>
            <div class="status">TON Testnet Active</div>
        </div>

        <script>
            const webApp = window.Telegram.WebApp;
            webApp.ready();
            webApp.expand();

            function connectTon() {{
                // הדמיית כתובת הארנק שקיבלת מהבוט של ה-Testnet
                const myWallet = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"; 
                webApp.sendData("ton_connect:" + myWallet);
            }}
        </script>
    </body>
    </html>
    """
    return html_content

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    data = message.web_app_data.data
    logger.info(f"Received WebApp data: {data}")
    if data.startswith("ton_connect:"):
        wallet_addr = data.split(":")[1]
        success, result = wallet_logic.claim_airdrop(message.from_user.id, wallet_addr)
        if success:
            bot.send_message(message.chat.id, f"✅ **Airdrop מוצלח!**\n\nקיבלת {result} SLH לארנק החדש שלך.\nכתובת: {wallet_addr}", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"❌ **שים לב:** {result}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    
    # שימוש ב-ReplyKeyboardMarkup כדי לאפשר העברת מידע (sendData)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🏦 פתח ארנק Web3", web_app=types.WebAppInfo(url)))
    
    bot.send_message(
        message.chat.id, 
        "💎 **ברוך הבא ל-SLH OS v2.0**\n\nמערכת הבלוקצ'יין שלך מוכנה.\nלחץ על הכפתור למטה כדי לחבר את ארנק ה-Testnet שלך ולקבל 100 SLH.",
        reply_markup=markup
    )

@app.post("/")
async def process_webhook(request: Request):
    try:
        json_data = await request.json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return {"status": "ok"} # תיקון הדיקשנרי כאן
    except Exception as e:
        logger.error(f"Webhook Error: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=port)
