# -*- coding: utf-8 -*-
import logging, os, telebot, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID
from handlers import wallet_logic
from db.connection import get_conn, init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("SLH_SaaS")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def force_db_fix():
    """פונקציה שמוודאת שהעמודה timestamp קיימת בטבלה"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        logger.info("✅ Database Migration: timestamp column verified.")
    except Exception as e:
        logger.error(f"❌ DB Fix Failed: {e}")
    finally:
        conn.close()

@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    try:
        balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
        txs = wallet_logic.get_last_transactions(user_id)
        
        tx_items = "".join([f'<div style="display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #222;"><span>{t[1]}</span><span style="color:#d4af37">+{t[0]} SLH</span></div>' for t in txs])
        if not tx_items: tx_items = '<div style="padding:20px;color:#666;">אין עסקאות עדיין</div>'

        return f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <style>
                body {{ background:#0b0b0b; color:#fff; font-family:sans-serif; text-align:center; padding:20px; }}
                .card {{ border:1px solid #d4af37; border-radius:20px; padding:25px; background:linear-gradient(145deg, #1a1a1a, #000); }}
                .balance {{ font-size:42px; color:#d4af37; margin:15px 0; font-weight:800; }}
                .btn {{ background:#d4af37; color:#000; border:none; padding:15px; border-radius:12px; width:100%; font-weight:bold; cursor:pointer; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="opacity:0.6;">Total Balance</div>
                <div class="balance">{balance:,.2f} SLH</div>
                <button class="btn" onclick="window.Telegram.WebApp.close()">סגור ארנק</button>
            </div>
            <div style="margin-top:20px; text-align:right;">
                <h4>פעולות אחרונות</h4>
                <div style="background:#111; border-radius:15px;">{tx_items}</div>
            </div>
            <script>window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand();</script>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"GUI Error: {e}")
        return f"<html><body>Error loading wallet. Admin notified.</body></html>"

@bot.message_handler(commands=['install'])
def install_cmd(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        init_db()
        force_db_fix()
        bot.reply_to(message, "✅ המערכת הותקנה מחדש ובסיס הנתונים סונכרן.")

@bot.message_handler(commands=['send'])
def send_coins(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        try:
            _, target_id, amount = message.text.split()
            success, msg = wallet_logic.manual_transfer(target_id, float(amount))
            bot.reply_to(message, f"💸 {msg}")
        except:
            bot.reply_to(message, "❌ פורמט: /send [ID] [AMOUNT]")

@bot.message_handler(commands=['start'])
def handle_start(message):
    wallet_logic.register_user(message.from_user.id)
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🏦 פתח ארנק Web3", web_app=types.WebAppInfo(url)))
    bot.send_message(message.chat.id, "💎 ברוך הבא ל-SLH OS!", reply_markup=markup)

@app.on_event("startup")
async def on_startup():
    force_db_fix()
    bot.set_my_commands([types.BotCommand("start", "🚀 פתח ארנק"), types.BotCommand("install", "⚙️ התקנה")])

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
