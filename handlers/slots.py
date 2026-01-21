import random
from utils.telegram import send_message
from db.slots import add_slots_result, get_leaderboard

SYMBOLS = ["🍒", "🍋", "⭐", "🍉", "💎"]

def roll_slots():
    return [random.choice(SYMBOLS) for _ in range(3)]

def calc_score(slots):
    # 3 זהים → 50 נק'
    if slots[0] == slots[1] == slots[2]:
        return 50
    # 2 זהים → 15 נק'
    if slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
        return 15
    # אחרת → 0
    return 0

async def play_slots(chat):
    user_id = chat["id"]
    slots = roll_slots()
    score = calc_score(slots)

    line = " | ".join(slots)
    text = f"🎰 {line}\n"

    if score > 0:
        text += f"\n🎉 זכית ב־{score} נקודות!"
    else:
        text += "\n😢 לא זכית הפעם..."

    add_slots_result(user_id, slots, score)

    await send_message(user_id, text)

async def show_leaderboard(chat):
    user_id = chat["id"]
    leaders = get_leaderboard()

    if not leaders:
        return await send_message(user_id, "עדיין אין מובילים. שחק ראשון! 🎰")

    lines = ["🏆 טבלת מובילים:\n"]
    for idx, (uid, score) in enumerate(leaders, start=1):
        lines.append(f"{idx}. משתמש {uid} — {int(score)} נק'")

    await send_message(user_id, "\n".join(lines))
