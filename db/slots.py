"""
slots.py - The Ultimate Version
===============================
HE: מנוע סלוטס מתקדם: אנימציה, ניהול סיכויים, וסטטיסטיקות.
EN: High-end Slots Engine: Animation frames, probability control, and stats.
"""

import random
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from db.connection import get_conn
from utils.edu_log import edu_step

# הגדרות לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- הגדרות המשחק (ניתן להוציא לקובץ קונפיג) ---
SYMBOLS = {
    "💎": {"weight": 5, "payout": 50},  # נדיר מאוד
    "7️⃣": {"weight": 10, "payout": 25},
    "🔔": {"weight": 20, "payout": 10},
    "🍋": {"weight": 30, "payout": 5},
    "🍒": {"weight": 35, "payout": 2}   # נפוץ
}

class SlotsEngine:
    """מנוע המשחק האחראי על הלוגיקה והאנימציה."""
    
    def __init__(self):
        self.symbol_list = list(SYMBOLS.keys())
        self.weights = [s["weight"] for s in SYMBOLS.values()]

    def spin(self) -> List[str]:
        """מבצע הגרלה משוקללת (Weighted Random)."""
        return random.choices(self.symbol_list, weights=self.weights, k=3)

    def calculate_win(self, result: List[str]) -> int:
        """חישוב זכייה: בודק אם כל הסמלים זהים."""
        if len(set(result)) == 1:  # כל השלושה זהים
            return SYMBOLS[result[0]]["payout"]
        return 0

    def generate_animation_frames(self, final_result: List[str], num_frames: int = 4) -> List[str]:
        """
        יוצר פריימים לאנימציה חלקה.
        מדמה סיבוב של גלגלי המכונה.
        """
        frames = []
        for i in range(num_frames):
            # יצירת פריים אקראי לערבוב
            frame = [random.choice(self.symbol_list) for _ in range(3)]
            frames.append(f"🎰 ┃ {' ┃ '.join(frame)} ┃")
        
        # פריים סופי עם עיצוב מנצח
        final_str = f"✨ ┃ {' ┃ '.join(final_result)} ┃ ✨"
        frames.append(final_str)
        return frames

# --- ניהול מסד נתונים (Data Layer) ---

def _ensure_table():
    """מוודא קיום טבלה ואינדקסים לביצועים מקסימליים."""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            result_str TEXT NOT NULL,
            payout INTEGER DEFAULT 0,
            is_win BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_slots_user_id ON slots_history(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_slots_win ON slots_history(is_win)"
    ]
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                for cmd in commands:
                    cur.execute(cmd)
                conn.commit()
    except Exception as e:
        logger.error(f"Database Init Error: {e}")

def save_game(user_id: int, result: List[str], payout: int):
    """שומר את תוצאת המשחק בצורה אסינכרונית/בטוחה."""
    res_string = "".join(result)
    is_win = payout > 0
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO slots_history (user_id, result_str, payout, is_win) VALUES (%s, %s, %s, %s)",
                    (user_id, res_string, payout, is_win)
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Error saving game for {user_id}: {e}")

# --- פונקציות ממשק (API) ---

def play_slots(user_id: int) -> Dict[str, Any]:
    """
    הפונקציה המרכזית שצריך לקרוא לה מה-Main.
    מחזירה אובייקט שלם עם כל מה שצריך לתצוגה.
    """
    engine = SlotsEngine()
    edu_step(1, f"User {user_id} started a spin.")
    
    # הגרלה
    result = engine.spin()
    payout = engine.calculate_win(result)
    
    # יצירת חוויה ויזואלית
    frames = engine.generate_animation_frames(result)
    
    # שמירה ל-DB
    save_game(user_id, result, payout)
    
    return {
        "frames": frames,
        "payout": payout,
        "won": payout > 0,
        "final_display": frames[-1],
        "message": "🎉 מזל טוב! זכית!" if payout > 0 else "לא נורא, נסה שוב! 🍀"
    }

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """מחזיר לידרבורד מעוצב עם נתונים סטטיסטיים."""
    query = """
        SELECT user_id, 
               COUNT(*) as total_games, 
               SUM(payout) as total_won
        FROM slots_history
        GROUP BY user_id
        ORDER BY total_won DESC
        LIMIT %s
    """
    leaderboard = []
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    leaderboard.append({
                        "user_id": row[0],
                        "games": row[1],
                        "total_prizes": row[2]
                    })
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
    return leaderboard

# הרצה ראשונית של הטבלה
_ensure_table()
