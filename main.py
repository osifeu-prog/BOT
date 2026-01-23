# -*- coding: utf-8 -*-
import telebot, os, logging, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db, get_conn

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# פונקציה להטענת ארנק אדמין
def setup_admin_balance():
    conn = get_conn()
    cur = conn.cursor()
    # נותן לאדמין מיליון מטבעות לחלוקה
    cur.execute("UPDATE users SET balance = 1000000.0 WHERE user_id = %s", (str(ADMIN_ID),))
    conn.commit()
    conn.close()

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    txs = wallet_logic.get_last_transactions(user_id)
    tx_items = "".join([f'<div style="display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #222;"><span>{t[1]}</span><span style="color:#d4af37">+{t[0]} SLH</span></div>' for t in txs])
    
    return f"""
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{background:#050505;color:white;font-family:sans-serif;text-align:center;padding:20px;}}
    .card{{background:#111;padding:25px;border-radius:20px;border:1px solid #d4af37;}}
    .balance{{font-size:40px;color:#d4af37;margin:10px 0;}}
    .btn{{background:#d4af37;color:black;padding:15px;border-radius:10px;width:100%;font-weight:bold;border:none;}}</style>
    </head><body>
    <div class="card"><div style="opacity:0.6">Balance</div><div class="balance">{balance} SLH</div>
    <button class="btn" onclick="window.Telegram.WebApp.close()">Close</button></div>
    <div style="margin-top:20px;text-align:right"><h4>History</h4>{tx_items if tx_items else "No transactions"}</div>
    </body></html>"""

@bot.message_handler(commands=['start', 'setup', 'startall'])
def handle_commands(message):
    user_id = message.from_user.id
    wallet_logic.register_user(user_id)
    
    if message.text in ['/setup', '/startall'] and str(user_id) == str(ADMIN_ID):
        init_db()
        setup_admin_balance()
        bot.set_my_commands([telebot.types.BotCommand("start", "Open Wallet")])
        bot.reply_to(message, "✅ המערכת אותחלה! קיבלת 1,000,000 SLH לחלוקה.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={user_id}"
    markup.add(telebot.types.KeyboardButton("🏦 פתח ארנק SLH", web_app=telebot.types.WebAppInfo(url)))
    bot.send_message(message.chat.id, "💎 ברוך הבא ל-SLH OS!", reply_markup=markup)

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
