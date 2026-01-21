"""
slots.py (handler)
==================
HE: לוגיקת משחק SLOTS.
EN: SLOTS game logic.
"""

import random
from utils.telegram import send_message
from db.slots import add_slots_result, get_leaderboard
from utils.i18n import LanguageCode, t
from utils.config import WIN_CHANCE_PERCENT
from utils.edu_log import edu_step, edu_path

SYMBOLS = ["🍒", "🍋", "🍇", "⭐", "💎"]

async def play_slots(chat: dict, lang: LanguageCode):
    """
    HE: מריץ משחק SLOTS אחד.
    EN: Runs a single SLOTS game.
    """
    user_id = chat["id"]
    edu_path("USER → MENU → SLOTS_GAME")
    edu_step(1, f"Starting SLOTS game for user {user_id}.")

    # HE: כאן אפשר לשלוט בסיכוי לזכייה (WIN_CHANCE_PERCENT)
    # EN: Here we can control win chance (WIN_CHANCE_PERCENT)
    if random.randint(1, 100) <= WIN_CHANCE_PERCENT:
        # HE: ניצחון — שלושה סמלים זהים
        # EN: Win — three identical symbols
        symbol = random.choice(SYMBOLS)
        result = [symbol, symbol, symbol]
        outcome = "WIN"
        msg = t(
            lang,
            he=f"{' '.join(result)}\n\n🎉 ניצחון!",
            en=f"{' '.join(result)}\n\n🎉 You win!"
        )
    else:
        # HE: הפסד — סמלים שונים
        # EN: Loss — different symbols
        result = [random.choice(SYMBOLS) for _ in range(3)]
        outcome = "LOSE"
        msg = t(
            lang,
            he=f"{' '.join(result)}\n\n❌ נסה שוב.",
            en=f"{' '.join(result)}\n\n❌ Try again."
        )

    add_slots_result(user_id, outcome)
    send_message(user_id, msg)

async def show_leaderboard(chat: dict, lang: LanguageCode):
    """
    HE: מציג טבלת מובילים.
    EN: Shows leaderboard.
    """
    user_id = chat["id"]
    edu_path("USER → MENU → LEADERBOARD")
    edu_step(1, f"Showing leaderboard to user {user_id}.")
    rows = get_leaderboard()
    if not rows:
        return send_message(
            user_id,
            t(lang, "אין עדיין נתונים.", "No data yet.")
        )
    lines = []
    for idx, (uid, plays) in enumerate(rows, start=1):
        lines.append(f"{idx}. {uid} — {plays} plays")
    send_message(
        user_id,
        t(lang, "🏆 טבלת מובילים:\n", "🏆 Leaderboard:\n") + "\n".join(lines)
    )
