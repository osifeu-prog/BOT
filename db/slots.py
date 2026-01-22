import random, asyncio
from utils.telegram import send_message
from db.connection import get_conn

def save_game(user_id, result, payout):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO slots_history (user_id, result, payout) VALUES (%s, %s, %s)", (user_id, result, payout))
            conn.commit()

async def play_slots(user_id, lang):
    symbols = ["💎", "7️⃣", "🔔", "🍋", "🍒"]
    # אנימציה מזויפת (מתח)
    for _ in range(3):
        temp_res = f"| {random.choice(symbols)} | {random.choice(symbols)} | {random.choice(symbols)} |"
        # כאן אפשר להוסיף עריכת הודעה, כרגע נשלח את הסופי למען הפשטות
        pass
    
    res = [random.choice(symbols) for _ in range(3)]
    display = f"| {' | '.join(res)} |"
    win = len(set(res)) == 1
    payout = 100 if win else 0
    save_game(user_id, "".join(res), payout)
    
    msg = f"🎰 **SLOTS** 🎰\n\n{display}\n\n"
    msg += "🎉 זכית ב-100 נקודות הנחה!" if win else "כמעט! נסה שוב 🍀"
    send_message(user_id, msg)
