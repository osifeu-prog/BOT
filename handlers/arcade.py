import requests, random, time, os, psycopg2
from utils.config import TELEGRAM_API_URL, DATABASE_URL, WIN_CHANCE

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def play_dice(chat_id, user_id, amount, guess):
    conn = get_db_conn(); cur = conn.cursor()
    
    # בדיקת יתרה
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if not user or user[0] < amount:
        return "❌ יתרה נמוכה מדי להימור זה."

    # שליחת האנימציה
    dice_res = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"}).json()
    actual_value = dice_res['result']['dice']['value']
    
    time.sleep(3.5) # המתנה לאנימציה
    
    # חישוב זכייה (ניחוש נכון + מזל מה-Railway)
    is_win = (actual_value == int(guess)) and (random.randint(1, 100) <= WIN_CHANCE)
    
    if is_win:
        win_amt = amount * 5
        cur.execute("UPDATE users SET balance = balance + %s, xp = xp + 50 WHERE user_id = %s", (win_amt, user_id))
        result = f"🎯 בול! הקוביה הראתה {actual_value}. זכית ב-{win_amt} SLH!"
    else:
        cur.execute("UPDATE users SET balance = balance - %s, xp = xp + 5 WHERE user_id = %s", (amount, user_id))
        result = f"❌ יצא {actual_value}. הפסדת {amount} SLH. נסה שוב!"
    
    conn.commit(); cur.close(); conn.close()
    return result
