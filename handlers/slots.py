"""
slots.py (handler)
==================
HE: לוגיקת משחק SLOTS.
EN: SLOTS game logic.
"""
import random
import logging
from typing import List, Dict, Any, Tuple
from db.connection import get_conn
from utils.edu_log import edu_step

logger = logging.getLogger(__name__)

# הגדרות סמלים וסיכויים
SYMBOLS = {
    "💎": {"weight": 5, "payout": 50},
    "7️⃣": {"weight": 10, "payout": 25},
    "🔔": {"weight": 20, "payout": 10},
    "🍋": {"weight": 30, "payout": 5},
    "🍒": {"weight": 35, "payout": 2}
}

def _ensure_table():
    """יוצר את הטבלה ומעדכן עמודות חסרות (Migration)."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # יצירת הטבלה הבסיסית אם לא קיימת
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS slots_history (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        result TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                # תיקון: הוספת עמודות חדשות לטבלה קיימת ב-Railway
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS payout INTEGER DEFAULT 0")
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS is_win BOOLEAN DEFAULT FALSE")
                conn.commit()
    except Exception as e:
        logger.error(f"Database Migration Error: {e}")

def add_slots_result(user_id: int, result: str):
    """
    פונקציית תאימות לאחור (Backward Compatibility).
    השם נשמר בדיוק כפי שהיה כדי למנוע את ה-ImportError.
    """
    edu_step(1, f"Saving slots result for user {user_id}")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO slots_history (user_id, result) VALUES (%s, %s)",
                    (user_id, result)
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Error in add_slots_result: {e}")

def play_slots_logic(user_id: int) -> Dict[str, Any]:
    """
    הלוגיקה המשופרת של המשחק כולל אנימציה.
    """
    symbol_list = list(SYMBOLS.keys())
    weights = [s["weight"] for s in SYMBOLS.values()]
    
    # הגרלה
    res_list = random.choices(symbol_list, weights=weights, k=3)
    res_str = "".join(res_list)
    
    # חישוב זכייה
    payout = 0
    if len(set(res_list)) == 1:
        payout = SYMBOLS[res_list[0]]["payout"]
    
    # יצירת פריימים לאנימציה (UX)
    frames = []
    for _ in range(3):
        fake_res = [random.choice(symbol_list) for _ in range(3)]
        frames.append(f"🎰 ┃ {' ┃ '.join(fake_res)} ┃")
    frames.append(f"✨ ┃ {' ┃ '.join(res_list)} ┃ ✨")
    
    # שמירה ל-DB
    add_slots_result(user_id, f"{res_str} (Win: {payout})")
    
    return {
        "frames": frames,
        "payout": payout,
        "won": payout > 0,
        "final_res": res_str
    }

def get_leaderboard(limit: int = 10):
    """מחזיר את טבלת המובילים - תואם למבנה המקורי."""
    edu_step(1, "Fetching leaderboard.")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id, COUNT(*) as plays
                    FROM slots_history
                    GROUP BY user_id
                    ORDER BY plays DESC
                    LIMIT %s
                """, (limit,))
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return []

# הרצה אוטומטית של עדכון הטבלה
_ensure_table()
