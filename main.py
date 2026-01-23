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

# ط£â€”أ¢â‚¬â€Œط£â€”أ¢â‚¬â„¢ط£â€”أ¢â‚¬إ“ط£â€”ط¢آ¨ط£â€”ط¹آ¾ ط£â€”ط¥â€œط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬â„¢ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬إ’ ط£â€”أ¢â‚¬ع†ط£â€”ط¢آ§ط£â€”ط¢آ¦ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¢ط£â€”أ¢â€‍آ¢ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ط£â€”ط¢آ§ط£â€”أ¢â€‍آ¢ط£â€”ط¢آ ط£â€”أ¢â‚¬â€Œ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SLH_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
@bot.middleware_handler(update_types=['message'])
def log_incoming_messages(bot_instance, message):
    logger.info(f"ظ‹ع؛â€œآ© Incoming: UserID: {message.from_user.id} | Text: {message.text}")
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
            .btn {{ background: #d4af37; color: black; border: none; padding: 15px; border-radius: 12px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 10px; }}
        </style>
    <script src="https://unpkg.com/@tonconnect/sdk@latest/dist/tonconnect-sdk.min.js"></script>
</head>
    <body>
        <div class="card">
            <div style="color: #888; font-size: 12px;">ط£â€”أ¢â€‍آ¢ط£â€”ط¹آ¾ط£â€”ط¢آ¨ط£â€”أ¢â‚¬â€Œ ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬â€‌ط£â€”ط¢آ©ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬آ¢ط£â€”ط¹ط›</div>
            <div class="balance">{balance:,.2f} SLH</div>
            <div style="font-size: 11px; opacity: 0.6;">{addr}</div>
            <button class="btn" onclick="window.Telegram.WebApp.close()">ط£â€”ط·إ’ط£â€”أ¢â‚¬â„¢ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¨</button>
        </div>
                <script>
            const webApp = window.Telegram.WebApp;
            webApp.ready();

            async function connectTon() {
                // הדמיית חיבור ארנק לצורך הבדיקה הראשונית (נשתמש בכתובת טסט)
                const mockWallet = "EQB...SLH_WALLET_ADDRESS"; 
                webApp.sendData("ton_connect:" + mockWallet);
                webApp.close();
            }
        </script>
    </body>
    </html>
    """
    return html_content

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"User {message.from_user.id} used /start")
    markup = types.InlineKeyboardMarkup()
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("ط¸â€¹ط¹ط›أ¢â‚¬â€Œط¢آ± ط£â€”ط¢آ¤ط£â€”ط¹آ¾ط£â€”أ¢â‚¬â€‌ ط£â€”ط¹آ¯ط£â€”ط¢آ¨ط£â€”ط¢آ ط£â€”ط¢آ§ ط£â€”ط¢آ¤ط£â€”ط¢آ¨ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬ع†ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬إ’", web_app=types.WebAppInfo(url)))
    bot.send_message(message.chat.id, "ط¸â€¹ط¹ط›أ¢â‚¬â„¢ط¹ع© **SLH OS Dashboard**", reply_markup=markup)

@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    user_id = message.from_user.id
    success, result = wallet_logic.claim_daily(user_id)
    if success:
        bot.reply_to(message, f"ط¸â€¹ط¹ط›ط¹ع©ط¸آ¾ **ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ ط£â€”أ¢â‚¬آ¢ط£â€”ط·إ’!** ط£â€”ط¢آ§ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬ع©ط£â€”ط¥â€œط£â€”ط¹آ¾ {result} SLH")
    else:
        bot.reply_to(message, f"ط£آ¢ط¹ث†ط¢آ³ ط£â€”أ¢â‚¬â€‌ط£â€”أ¢â‚¬â€œط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¨ ط£â€”أ¢â‚¬ع©ط£â€”ط¢آ¢ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬إ“ {result}")

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



