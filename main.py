# -*- coding: utf-8 -*-
import telebot, os, uvicorn, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db

# לוגים מקצועיים לרלווי
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SLH-OS] - %(levelname)s - %(message)s')
logger = logging.getLogger("SLH_OS")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("🚀 SLH OS Engine is Live")

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    balance, xp, rank = wallet_logic.get_user_full_data(user_id)
    total_supply, _ = wallet_logic.get_economy_stats()
    return f"""
    <html><head><meta charset="UTF-8">
    <script>
        function refresh() {{ fetch(window.location.href).then(r => r.text()).then(html => {{
            let parser = new DOMParser();
            let newDoc = parser.parseFromString(html, 'text/html');
            document.getElementById('balance').innerHTML = newDoc.getElementById('balance').innerHTML;
            document.getElementById('supply').innerHTML = newDoc.getElementById('supply').innerHTML;
        }}); }}
        setInterval(refresh, 5000); // עדכון אוטומטי כל 5 שניות
    </script>
    <style>
        body {{ background: #0b0e11; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }}
        .card {{ background: #1e2329; margin: auto; padding: 30px; border-radius: 20px; width: 85%; border-bottom: 4px solid #f0b90b; }}
        .balance {{ font-size: 50px; color: #f0b90b; font-weight: bold; }}
        .id-badge {{ font-size: 10px; opacity: 0.5; margin-top: 10px; }}
    </style></head>
    <body>
        <div class="card">
            <div style="opacity:0.7">SLH Balance</div>
            <div class="balance" id="balance">{balance}</div>
            <div>{rank} | {xp} XP</div>
            <div class="id-badge">User ID: {user_id}</div>
            <div style="margin-top:40px; font-size:11px; opacity:0.4" id="supply">Circulating Supply: {total_supply:,.0f} SLH</div>
        </div>
    </body></html>"""

@bot.message_handler(commands=['start'])
def start(message):
    wallet_logic.register_user(message.from_user.id)
    logger.info(f"📥 Command /start by {message.from_user.id}")
    bot.send_message(message.chat.id, "💎 **SLH OS Activated**\nType `/all` to see all commands.", parse_mode="Markdown")

@bot.message_handler(commands=['all'])
def show_all(message):
    menu = """
🖥 **SLH OS - Master Menu**

**General:**
/start - Refresh System
/myid - Show your identity
/all - This menu
/AI - Ask SLH AI (Beta)

**Wallet:**
/send [id] [amount] - Transfer
/receive - Get your payment link
/balance - Quick check

**Admin:**
/admin - Econ Monitor
/mint [id] [amount] - Issue SLH
/health - System Check
"""
    bot.reply_to(message, menu, parse_mode="Markdown")

@bot.message_handler(commands=['myid'])
def my_id(message):
    bot.reply_to(message, f"🆔 Your User ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['receive'])
def receive_slh(message):
    instruction = f"To receive SLH, send this to your friend:\n\n`/send {message.from_user.id} [amount]`"
    bot.reply_to(message, instruction, parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID: return
    supply, users = wallet_logic.get_economy_stats()
    bot.reply_to(message, f"📊 **Economy Status**\nUsers: {users}\nSupply: {supply:,.2f}")

@bot.message_handler(commands=['mint'])
def mint(message):
    if str(message.from_user.id) != ADMIN_ID: return
    parts = message.text.split()
    if len(parts) == 3:
        wallet_logic.mint_to_user(parts[1], parts[2])
        bot.reply_to(message, "✅ Mint Completed")

@app.post("/")
async def process_webhook(request: Request):
    json_data = await request.json()
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
