import random
import asyncio
from utils.telegram import send_message
from db.connection import get_conn

async def play_slots(user_id):
    symbols = ["💎", "💰", "💵", "🔥", "👑"]
    # הודעת טעינה/אנימציה
    status_msg = send_message(user_id, "🎰 **מפעיל את המכונה...**")
    
    # "אנימציה" פשוטה של החלפת סמלים
    for _ in range(3):
        fake_res = [random.choice(symbols) for _ in range(3)]
        # כאן בדרך כלל נשתמש ב-Edit Message, אבל לצורך הפשטות נשלח הודעה חדשה או נחכה
        await asyncio.sleep(0.5)

    res = [random.choice(symbols) for _ in range(3)]
    win = len(set(res)) == 1
    
    display = f"┃ {res[0]} ┃ {res[1]} ┃ {res[2]} ┃"
    result_text = "✨ **זכיית ענק!** ✨\nקיבלת קוד קופון ל-20% הנחה: VIP20" if win else "❌ **כמעט!** נסה שוב בעוד שעה."
    
    final_msg = f"🎰 **SLOT MACHINE** 🎰\n\n{display}\n\n{result_text}"
    send_message(user_id, final_msg)
