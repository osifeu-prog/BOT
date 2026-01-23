# -*- coding: utf-8 -*-
import telebot, os, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db, get_conn

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    return f\"\"\"
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
        body {{ background: #050505; color: #fff; font-family: sans-serif; margin:0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .wallet-card {{ background: linear-gradient(135deg, rgba(0,136,204,0.2) 0%, rgba(0,0,0,0.8) 100%); border: 1px solid rgba(0,136,204,0.3); border-radius: 40px; width: 100%; max-width: 350px; padding: 40px 20px; text-align: center; box-shadow: 0 30px 60px rgba(0,0,0,0.8); }}
        .balance {{ font-size: 50px; font-weight: 900; color: #0088cc; margin: 20px 0; }}
        .btn {{ background: #0088cc; color: #fff; padding: 15px; border-radius: 20px; border: none; font-weight: bold; width: 100%; cursor: pointer; }}
    </style></head><body>
        <div class="wallet-card">
            <div style="opacity:0.5; font-size:12px;">ASSETS</div>
            <div class="balance">{balance} SLH</div>
            <button class="btn" onclick="window.Telegram.WebApp.close()">Back to Telegram</button>
        </div>
    </body></html>\"\"\"

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        conn.close()
        bot.reply_to(message, f"📊 Total Users: {{count}}")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    referrer = args[1] if len(args) > 1 else None
    is_new = wallet_logic.register_user(user_id, referrer)
    invite_link = f"https://t.me/{{bot.get_me().username}}?start={{user_id}}"
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🏦 Open Wallet", web_app=telebot.types.WebAppInfo(f"{WEBHOOK_URL}/gui/wallet?user_id={{user_id}}")))
    msg = "💎 Welcome to SLH OS!\n"
    if is_new: msg += "🎁 10 SLH Airdrop claimed!\n"
    msg += f"🔗 Share to earn: {invite_link}"
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {{"status": "ok"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
