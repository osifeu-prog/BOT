# -*- coding: utf-8 -*-
import logging, os, telebot, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID
from handlers import wallet_logic
from db.connection import get_conn, init_db

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    txs = wallet_logic.get_last_transactions(user_id)
    
    # בדיקה אם המשתמש כבר עשה Claim (נניח ש-addr קיים = בוצע)
    claim_button = ""
    if not addr:
        claim_button = f'''
        <div style="background: rgba(212,175,55,0.1); border: 1px dashed #d4af37; padding: 15px; border-radius: 15px; margin-top: 20px;">
            <p style="color: #d4af37; font-size: 14px; margin-top: 0;">🎁 אירדרופ זמין עבורך!</p>
            <button class="btn" onclick="claimAirdrop()">Claim Free SLH</button>
        </div>
        '''

    tx_html = "".join([f'<div style="display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid #222;">'
                       f'<span style="color:#888;">{t[1]}</span>'
                       f'<span style="color:#d4af37; font-weight:bold;">+{t[0]} SLH</span></div>' for t in txs])

    return f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ background: #050505; color: #fff; font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .balance-card {{ background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 1px solid #333; border-radius: 25px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); position: relative; overflow: hidden; }}
            .balance-card::after {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(212,175,55,0.05) 0%, transparent 70%); }}
            .label {{ color: #888; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
            .amount {{ font-size: 45px; font-weight: 800; color: #d4af37; margin: 10px 0; }}
            .btn {{ background: #d4af37; color: #000; border: none; padding: 15px 25px; border-radius: 15px; width: 100%; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }}
            .btn:active {{ transform: scale(0.97); }}
            .history {{ margin-top: 30px; }}
            .history-title {{ font-size: 18px; margin-bottom: 15px; color: #d4af37; border-right: 3px solid #d4af37; padding-right: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0; font-size:22px;">SLH Digital Wallet</h2>
        </div>
        
        <div class="balance-card">
            <div class="label">Balance</div>
            <div class="amount">{balance:,.2f} <span style="font-size:18px;">SLH</span></div>
            <div style="font-size:11px; color:#555; word-break:break-all;">{addr if addr else "כתובת ארנק לא מחוברת"}</div>
        </div>

        {claim_button}

        <div class="history">
            <div class="history-title">פעולות אחרונות</div>
            <div style="background:#111; border-radius:20px; padding:5px;">{tx_html if tx_html else '<p style="padding:20px; color:#444;">אין תנועות עדיין</p>'}</div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            function claimAirdrop() {{
                tg.showConfirm("האם לחבר ארנק ולקבל אירדרופ?", function(ok) {{
                    if (ok) {{
                        // שליחת כתובת ארנק דמו לטובת הבדיקה
                        tg.sendData("ton_connect:UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp");
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
