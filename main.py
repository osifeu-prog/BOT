# -*- coding: utf-8 -*-
import logging, os, telebot, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID
from handlers import wallet_logic

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("SLH_SaaS")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- UI / WEB APP ---
@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    txs = wallet_logic.get_last_transactions(user_id)
    
    tx_items = ""
    for t in txs:
        # t[1] = amount, t[2] = type/date
        tx_items += f'<div class="tx-row"><span>{t[2]}</span><span class="plus">+{t[1]} SLH</span></div>'
    
    if not tx_items: tx_items = '<div style="color:#666; padding:20px;">אין פעולות עדיין</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ background: #080808; color: #fff; font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 20px; }}
            .card {{ border: 1px solid #d4af37; border-radius: 24px; padding: 30px; background: linear-gradient(145deg, #1a1a1a, #000); box-shadow: 0 10px 40px rgba(0,0,0,0.8); margin-bottom: 25px; text-align: center; }}
            .balance {{ font-size: 48px; color: #d4af37; font-weight: 900; margin: 10px 0; letter-spacing: -1px; }}
            .tx-list {{ background: #111; border-radius: 20px; padding: 10px; border: 1px solid #222; }}
            .tx-row {{ display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #222; font-size: 14px; }}
            .plus {{ color: #d4af37; font-weight: bold; }}
            .btn {{ background: #d4af37; color: #000; border: none; padding: 18px; border-radius: 15px; width: 100%; font-weight: bold; font-size: 16px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="opacity:0.6; font-size:14px; text-transform:uppercase;">Available Balance</div>
            <div class="balance">{balance:,.2f} <span style="font-size:20px">SLH</span></div>
            <div style="font-size:11px; color:#555; margin-bottom:20px; word-break:break-all;">{addr if addr else "Address Not Connected"}</div>
            <button class="btn" onclick="window.Telegram.WebApp.close()">סגור ארנק</button>
        </div>
        <h3 style="font-size:18px; margin-bottom:15px; padding-right:10px;">פעולות אחרונות</h3>
        <div class="tx-list">{tx_items}</div>
        <script>window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand();</script>
    </body>
    </html>
    """

# --- BOT HANDLERS ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💰 סכום אירדרופ", callback_data="set_val"),
            types.InlineKeyboardButton("📊 סטטיסטיקות", callback_data="view_stats"),
            types.InlineKeyboardButton("📢 הודעה לכולם", callback_data="broadcast")
        )
        bot.send_message(message.chat.id, "💎 **SLH Backoffice v2.0**\nברוך הבא למערכת הניהול.", reply_markup=markup)

@bot.message_handler(commands=['start'])
def handle_start(message):
    # לוגיקת Referral: בודק אם הגיע דרך קישור (למשל start=123)
    args = message.text.split()
    ref_by = args[1] if len(args) > 1 else None
    
    # רישום משתמש חדש וטיפול בהפניה ב-Logic
    wallet_logic.register_user(message.from_user.id, ref_by)
    
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    ref_link = f"https://t.me/{(bot.get_me()).username}?start={message.from_user.id}"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🏦 פתח ארנק Web3", web_app=types.WebAppInfo(url)))
    
    welcome_text = (
        f"💎 **ברוך הבא ל-SLH SaaS Platform**\n\n"
        f"הזמן חברים וקבל בונוס על כל הצטרפות!\n"
        f"קישור ההזמנה שלך:\n{ref_link}"
    )
    
    if str(message.from_user.id) == str(ADMIN_ID):
        welcome_text = "🛠 **מצב מנהל פעיל**\nהשתמש ב-/admin לניהול המערכת."
        
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    data = message.web_app_data.data
    if data.startswith("ton_connect:"):
        wallet_addr = data.split(":")[1]
        success, result = wallet_logic.claim_airdrop(message.from_user.id, wallet_addr)
        bot.send_message(message.chat.id, f"✅ **Airdrop:** {result}")

@app.on_event("startup")
async def on_startup():
    bot.set_my_commands([
        types.BotCommand("start", "🚀 פתח ארנק"),
        types.BotCommand("admin", "🔐 פאנל ניהול")
    ])

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
