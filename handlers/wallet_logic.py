# -*- coding: utf-8 -*-
import uuid
from db.connection import get_conn

def generate_gift_link(sender_id, amount):
    # יצירת קוד ייחודי למתנה
    gift_code = str(uuid.uuid4())[:8]
    # כאן תוסיף לוגיקה ששומרת ב-DB ומורידה מהיתרה של השולח
    return f"https://t.me/YOUR_BOT_NAME?start=gift_{gift_code}"

def show_wallet(user_id):
    # נתונים מדומים לצורך התצוגה - יש לחבר ל-DB שלך
    balance = 1250 
    xp = 120
    address = f"SLH-{str(user_id)[:4]}-X{str(user_id)[-3:]}"
    
    text = f"💳 **THE DIAMOND VAULT**\n"
    text += f"━━━━━━━━━━━━━━━━━━\n"
    text += f"🆔 **Address:** {address}\n"
    text += f"🏆 **Rank:** Executive Silver\n"
    text += f"━━━━━━━━━━━━━━━━━━\n\n"
    
    text += f"💰 **Assets:**\n"
    text += f"└─ 💎 {balance:,} SLH\n"
    text += f"└─ 📊 **Growth:** +12.5% this month\n\n"
    
    text += f"🎁 **מתנות זמינות:**\n"
    text += f"ניתן ליצור לינק מתנה לחבר בלחיצה על הכפתור למטה.\n"
    text += f"━━━━━━━━━━━━━━━━━━\n"
    return text
