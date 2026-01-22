import requests, sqlite3, logging, os, random, time
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")

    if text == "/start":
        send_menu(chat_id)
    
    elif text == "🎰 ארקייד":
        send_arcade_menu(chat_id)

    elif text.startswith("🎰 הימור:"):
        # המשתמש בחר סכום הימור
        amount = text.split(":")[1].split()[0]
        send_guess_menu(chat_id, amount)

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = str(callback_query.get("from", {}).get("id"))
    data = callback_query.get("data")

    if data.startswith("bet_"): # פורמט: bet_[amount]_[guess]
        _, amount, guess = data.split("_")
        amount, guess = int(amount), int(guess)
        
        conn = get_db(); c = conn.cursor()
        user = c.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
        if user['balance'] < amount:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין לך מספיק SLH להימור הזה!"})
            return

        # הפחתת סכום ההימור
        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

        # שליחת אנימציית קוביה
        dice_msg = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"}).json()
        dice_value = dice_msg['result']['dice']['value']
        
        # המתנה לאנימציה
        time.sleep(3)

        # לוגיקת זכייה מבוססת סיכוי מה-Railway
        win_chance = int(os.getenv('WIN_CHANCE_PERCENT', 30))
        is_lucky_draw = random.randint(1, 100) <= win_chance
        
        # אם הניחוש נכון וגם ה-Chance עבד
        if dice_value == guess and is_lucky_draw:
            win_amount = amount * 5
            c.execute("UPDATE users SET balance = balance + ?, xp = xp + 50 WHERE user_id = ?", (win_amount, user_id))
            result_text = f"🎯 בול! הקוביה הראתה {dice_value}.\nזכית ב-{win_amount} SLH (מכפיל X5)!"
        else:
            c.execute("UPDATE users SET xp = xp + 10 WHERE user_id = ?", (user_id,))
            result_text = f"😔 הקוביה הראתה {dice_value}. הניחוש שלך היה {guess}.\nאולי בפעם הבאה!"
        
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": result_text})

def send_arcade_menu(chat_id):
    kb = {"keyboard": [[{"text": "🎰 הימור: 10 SLH"}, {"text": "🎰 הימור: 50 SLH"}], 
                       [{"text": "🎰 הימור: 100 SLH"}, {"text": "🔙 חזרה"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎮 **מרכז הארקייד**\nבחר סכום הימור:", "reply_markup": kb})

def send_guess_menu(chat_id, amount):
    # יצירת כפתורי ניחוש 1-6
    buttons = []
    row = []
    for i in range(1, 7):
        row.append({"text": f"🎲 {i}", "callback_data": f"bet_{amount}_{i}"})
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    kb = {"inline_keyboard": buttons}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"נבחר הימור של {amount} SLH.\nעל איזה מספר אתה מהמר?", "reply_markup": kb})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], 
                       [{"text": "🎰 ארקייד"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME**\nבחר פעולה:", "reply_markup": kb})
