# -*- coding: utf-8 -*-
import telebot, os, uvicorn, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    total_supply, _ = wallet_logic.get_economy_stats()
    return f"""
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background: #0b0e11; color: white; font-family: sans-serif; text-align: center; margin: 0; padding-top: 50px; }}
        .card {{ background: #1e2329; margin: auto; padding: 30px; border-radius: 20px; width: 80%; border-bottom: 4px solid #f0b90b; }}
        .balance {{ font-size: 45px; color: #f0b90b; margin: 10px 0; }}
        .supply-box {{ margin-top: 40px; font-size: 12px; opacity: 0.5; border-top: 1px solid #333; padding-top: 10px; }}
    </style></head>
    <body>
        <div class="card">
            <div style="opacity:0.7">Available Balance</div>
            <div class="balance">{balance} SLH</div>
            <div style="font-size:14px">{rank} Level | {xp} XP</div>
            <button onclick="window.Telegram.WebApp.close()" style="margin-top:20px; background:#f0b90b; border:none; padding:10px 20px; border-radius:10px; font-weight:bold;">Exit</button>
            <div class="supply-box">Global Circulating Supply: {total_supply:,.0f} SLH</div>
        </div>
    </body></html>"""

@bot.message_handler(commands=['send'])
def send_slh(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "💡 Usage: `/send [user_id] [amount]`\nExample: `/send 123456 50`", parse_mode="Markdown")
            return
        
        receiver_id, amount = parts[1], parts[2]
        success, feedback = wallet_logic.transfer_funds(message.from_user.id, receiver_id, amount)
        
        if success:
            bot.reply_to(message, f"✅ Sent {amount} SLH to `{receiver_id}`", parse_mode="Markdown")
            # עדכון המקבל (אם הבוט בשימוש אצלו)
            try: bot.send_message(receiver_id, f"🎁 You received {amount} SLH from `{message.from_user.id}`!")
            except: pass
        else:
            bot.reply_to(message, f"❌ Transfer failed: {feedback}")
    except:
        bot.reply_to(message, "❌ Invalid format.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID: return
    total_supply, total_users = wallet_logic.get_economy_stats()
    bot.reply_to(message, f"📊 **Economy Status**\n\nUsers: {total_users}\nSupply: {total_supply:,.2f} SLH")

@bot.message_handler(commands=['mint'])
def mint_coins(message):
    if str(message.from_user.id) != ADMIN_ID: return
    try:
        _, target_id, amount = message.text.split()
        if wallet_logic.mint_to_user(target_id, amount):
            bot.reply_to(message, f"✅ Minted {amount} SLH to {target_id}")
        else: bot.reply_to(message, "❌ User not found.")
    except: bot.reply_to(message, "Format: `/mint [id] [amount]`")

@bot.message_handler(commands=['start'])
def start(message):
    wallet_logic.register_user(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    wallet_url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(telebot.types.KeyboardButton("💰 My Wallet", web_app=telebot.types.WebAppInfo(wallet_url)))
    bot.send_message(message.chat.id, "💎 **SLH OS Activated**\n\nUse `/send [id] [amount]` to transfer SLH.", reply_markup=markup, parse_mode="Markdown")

@app.post("/")
async def process_webhook(request: Request):
    json_data = await request.json()
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
