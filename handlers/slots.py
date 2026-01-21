"""
handlers/slots.py
==================
מימוש משחק SLOTS.

מטרתו:
- להגריל סמלים
- לחשב ניקוד
- לשמור תוצאה ב-DB + Redis
- להציג טבלת מובילים
"""
import random
from utils.telegram import send_message
from db.slots import add_slots_result, get_leaderboard

SYMBOLS = ["🍒", "🍋", "🍇", "⭐", "💎"]

async def play_slots(chat):
    user_id = chat["id"]
    result = [random.choice(SYMBOLS) for _ in range(3)]
    text = " ".join(result)

    if len(set(result)) == 1:
        outcome = "WIN"
        msg = f"{text}\n\n🎉 ניצחון!"
    else:
        outcome = "LOSE"
        msg = f"{text}\n\n❌ נסה שוב."

    add_slots_result(user_id, outcome)
    send_message(user_id, msg)

async def show_leaderboard(chat):
    user_id = chat["id"]
    rows = get_leaderboard()
    if not rows:
        return send_message(user_id, "אין עדיין נתונים.")
    lines = []
    for idx, (uid, plays) in enumerate(rows, start=1):
        lines.append(f"{idx}. {uid} — {plays} משחקים")
    send_message(user_id, "🏆 טבלת מובילים:\n" + "\n".join(lines))
