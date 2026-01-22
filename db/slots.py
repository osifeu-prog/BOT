import random
from utils.telegram import send_message
from db.connection import get_conn

def play_slots(user_id):
    symbols = ["💎", "7️⃣", "🍋", "🍒"]
    res = [random.choice(symbols) for _ in range(3)]
    display = f"| {' | '.join(res)} |"
    
    win = len(set(res)) == 1
    msg = f"🎰 **SLOTS** 🎰\n\n{display}\n\n"
    msg += "🎉 זכית!" if win else "נסה שוב 🍀"
    
    # שמירה ב-DB
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO slots_history (user_id, result, payout) VALUES (%s, %s, %s)", (user_id, "".join(res), 100 if win else 0))
        conn.commit()
        conn.close()
    except:
        pass
        
    send_message(user_id, msg)
