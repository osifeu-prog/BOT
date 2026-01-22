import random
import asyncio
from utils.telegram import send_message

async def play_slots(user_id):
    # הודעת טעינה מעוצבת
    send_message(user_id, "🎰 *Spinning the Reels...* \n💎 💎 💎")
    await asyncio.sleep(1.2)

    symbols = ["💎", "💰", "💵", "🔥", "👑"]
    res = [random.choice(symbols) for _ in range(3)]
    
    # עיצוב ויזואלי של המכונה
    machine = (
        "╔════════════╗\n"
        f"  ║  {res[0]}  ║  {res[1]}  ║  {res[2]}  ║\n"
        "╚════════════╝"
    )
    
    win = len(set(res)) == 1
    if win:
        msg = f"🎰 *JACKPOT* 🎰\n\n{machine}\n\n🎊 *מזל טוב!* זכית בקוד קופון בלעדי:\nVIP-PRO-20 \n(בתוקף ל-15 דקות הקרובות)"
    else:
        msg = f"🎰 *SLOT RESULTS* 🎰\n\n{machine}\n\n💡 *טיפ:* סוחרים מקצועיים יודעים מתי להמשיך ומתי לעצור. נסה שוב בעוד שעה!"
    
    send_message(user_id, msg)
