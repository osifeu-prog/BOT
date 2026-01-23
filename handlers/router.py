import requests, sqlite3, logging, os, random, time
from datetime import datetime, timedelta
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ×‍×¢×¨×›×ھ ×”×“×¨×’×•×ھ ×•×”-VIP ---
def get_user_status(xp, is_vip):
    rank = "ًں¥‰ Starter"
    if xp > 500: rank = "ًں¥ˆ Advanced"
    if xp > 2000: rank = "ًں¥‡ Expert"
    if xp > 5000: rank = "ًں’ژ Diamond"
    vip_status = "âœ¨ VIP" if is_vip else "Standard"
    return rank, vip_status

# --- ×،×•×›×ں ×”×©×§×¢×•×ھ ×‍×ھ×§×“×‌ (Portfolio & Risk) ---
def get_investment_report(user_id):
    conn = get_db()
    journal = conn.execute("SELECT entry FROM user_journal WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,)).fetchall()
    user = conn.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not journal: return "×گ×™×ں ×‍×،×¤×™×§ × ×ھ×•× ×™×‌ ×‘×™×•×‍×ں. ×¨×©×•×‌ ×§× ×™×•×ھ/×‍×›×™×¨×•×ھ ×›×“×™ ×œ×§×‘×œ ×“×•×—."
    
    report = f"ًں“‹ **×“×•×— ×،×•×›×ں ×—×›×‌:**\n\n"
    report += f"ًں’° ×™×ھ×¨×” × ×•×›×—×™×ھ: {user['balance']} SLH\n"
    report += "ًں”چ ×ھ×•×‘× ×•×ھ: ×”×‍×©×ھ×‍×© ×‍×“×•×•×— ×¢×œ ×¤×¢×™×œ×•×ھ ×‘× ×›×،×™×‌ ×“×™×’×™×ک×œ×™×™×‌. "
    if user['balance'] < 100: report += "âڑ ï¸ڈ ×گ×–×”×¨×ھ ×،×™×›×•×ں: ×™×ھ×¨×” × ×‍×•×›×” ×œ×‘×™×¦×•×¢ ×¤×¢×•×œ×•×ھ ×—×“×©×•×ھ."
    return report

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    if not text: return

    # --- ×¤×§×•×“×•×ھ ×گ×“×‍×™×ں (Admin Menu) ---
    if user_id == ADMIN_ID:
        if text == "/admin":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "ًں›  **×ھ×¤×¨×™×ک × ×™×”×•×œ:**\n/stats - ×،×ک×ک×™×،×ک×™×§×”\n/broadcast [msg] - ×”×•×“×¢×” ×œ×›×•×œ×‌\n/give_vip [id] - ×”×¢× ×§×ھ VIP"})
            return

    # --- ×ھ×¤×¨×™×ک ×‍×©×ھ×‍×© ×¨×گ×©×™ ---
    if text.startswith("/start"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, balance, xp, rank) VALUES (?, 200, 0, 'Starter')", (user_id,))
        conn.commit(); conn.close()
        send_main_menu(chat_id)

    elif text == "ًں’³ ×”×¤×•×¨×ک×¤×•×œ×™×• ×©×œ×™":
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        rank, vip = get_user_status(u['xp'], u['is_vip'])
        msg = f"ًں‘¤ **×¤×¨×•×¤×™×œ ×‍×©×§×™×¢**\n\nًں’ژ ×،×ک×ک×•×،: {vip}\nًںڈ… ×“×¨×’×”: {rank}\nًں’° ×™×ھ×¨×”: {u['balance']} SLH\nًںڈ† XP: {u['xp']}"
        kb = {"inline_keyboard": [[{"text": "ًں“¥ ×”×¤×§×“×”", "callback_data": "dep"}, {"text": "ًں“¤ ×‍×©×™×›×”", "callback_data": "with"}],
                                   [{"text": "ًںڈ† Leaderboard", "callback_data": "lead"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb})

    elif text == "ًں¤– ×،×•×›×ں (AI)":
        report = get_investment_report(user_id)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": report})

    elif text == "ًں•¹ Arcade":
        send_arcade_menu(chat_id)

    elif text.startswith("ًں’° Bet:"):
        amt = text.split(":")[1].split()[0]
        send_guess_buttons(chat_id, amt)

    elif text == "ًںژپ Daily":
        process_daily(chat_id, user_id)

    else:
        # ×¨×™×©×•×‌ ×™×•×‍×ں (Data for AI)
        conn = get_db(); conn.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "âœ… ×¨×©×•×‌ ×‘×™×•×‍×ں ×”×©×•×§. ×”×،×•×›×ں ×‍×¢×‘×“ ×گ×ھ ×”× ×ھ×•× ×™×‌."})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = str(callback_query.get("from", {}).get("id"))
    data = callback_query.get("data")

    if data.startswith("p_"): # p_[amt]_[guess]
        process_arcade_play(chat_id, user_id, data)
    elif data == "lead":
        conn = get_db()
        top = conn.execute("SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT 5").fetchall()
        msg = "ًںڈ† **×‍×•×‘×™×œ×™ ×”×§×”×™×œ×”:**\n" + "\n".join([f"{i+1}. {u['user_id']}: {u['xp']} XP" for i, u in enumerate(top)])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

def send_main_menu(chat_id):
    kb = {"keyboard": [[{"text": "ًں’³ ×”×¤×•×¨×ک×¤×•×œ×™×• ×©×œ×™"}, {"text": "ًں¤– ×،×•×›×ں (AI)"}], 
                       [{"text": "ًں•¹ Arcade"}, {"text": "ًںژپ Daily"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "ًں’ژ **DIAMOND ELITE v3.0**", "reply_markup": kb})

def send_arcade_menu(chat_id):
    kb = {"keyboard": [[{"text": "ًں’° Bet: 10 SLH"}, {"text": "ًں’° Bet: 50 SLH"}], [{"text": "ًں”™ ×—×–×¨×”"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "ًں•¹ **×‘×—×¨ ×،×›×•×‌ ×”×™×‍×•×¨:**", "reply_markup": kb})

def send_guess_buttons(chat_id, amt):
    btns = [[{"text": f"ًںژ² {i}", "callback_data": f"p_{amt}_{i}"} for i in range(1, 4)],
            [{"text": f"ًںژ² {i}", "callback_data": f"p_{amt}_{i}"} for i in range(4, 7)]]
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"× ×—×© ×‍×،×¤×¨ (×”×™×‍×•×¨ {amt}):", "reply_markup": {"inline_keyboard": btns}})

def process_arcade_play(chat_id, user_id, data):
    # ×œ×•×’×™×§×ھ ×‍×©×—×§ ×‍×œ×گ×” ×›×•×œ×œ ×¢×“×›×•×ں XP ×•×“×¨×’×”
    _, amt, guess = data.split("_")
    amt, guess = int(amt), int(guess)
    conn = get_db(); u = conn.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if u['balance'] < amt:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "â‌Œ ×گ×™×ں ×‍×،×¤×™×§ SLH!"})
        return
    
    # ×گ× ×™×‍×¦×™×”
    dice = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "ًںژ²"}).json()
    val = dice['result']['dice']['value']
    time.sleep(3.5)
    
    win = (val == guess) and (random.randint(1, 100) <= int(os.getenv('WIN_CHANCE_PERCENT', 30)))
    if win:
        reward = amt * 5
        conn.execute("UPDATE users SET balance = balance + ?, xp = xp + 50 WHERE user_id = ?", (reward, user_id))
        msg = f"ًںژ¯ ×‘×•×œ! ×–×›×™×ھ ×‘-{reward} SLH!"
    else:
        conn.execute("UPDATE users SET balance = balance - ?, xp = xp + 5 WHERE user_id = ?", (amt, user_id))
        msg = f"â‌Œ ×™×¦×گ {val}. ×”×¤×،×“×ھ {amt} SLH."
    conn.commit(); conn.close()
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

def process_daily(chat_id, user_id):
    conn = get_db(); c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + 100, xp = xp + 20 WHERE user_id = ?", (user_id,))
    conn.commit(); conn.close()
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "ًںژپ ×§×™×‘×œ×ھ 100 SLH ×•-20 XP!"})


def send_admin_report(bot, user_id, action):
    print(f'Admin Report: User {user_id} performed {action}')
