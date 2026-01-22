import random, psycopg2
from utils.config import DATABASE_URL, WIN_CHANCE

def play_dice(chat_id, user_id, amount, bet_on):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    res = cur.fetchone()
    if not res or res[0] < amount:
        return "❌ יתרה נמוכה מדי להימור זה."
    
    # חישוב תוצאה לפי אחוז הזכייה שהגדרת
    is_win = random.randint(1, 100) <= WIN_CHANCE
    
    if is_win:
        new_balance = res[0] + amount
        msg = f"🎲 קוביה: {bet_on}\n✅ ניצחת! זכית ב-{amount} SLH.\nיתרה חדשה: {new_balance}"
        cur.execute("UPDATE users SET balance = %s, xp = xp + 10 WHERE user_id = %s", (new_balance, user_id))
    else:
        new_balance = res[0] - amount
        msg = f"🎲 קוביה: {random.choice([1,2,3,4,5])}\n❌ הפסדת {amount} SLH. נסה שוב!"
        cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
        
    conn.commit()
    cur.close()
    conn.close()
    return msg
