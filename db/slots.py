import random
import logging
from typing import List, Dict, Any, Tuple
from db.connection import get_conn
from utils.edu_log import edu_step

logger = logging.getLogger(__name__)

# הגדרות סמלים וסיכויים (לוגיקה פנימית)
SYMBOLS_DATA = {
    "💎": {"weight": 5, "payout": 50},
    "7️⃣": {"weight": 10, "payout": 25},
    "🔔": {"weight": 20, "payout": 10},
    "🍋": {"weight": 30, "payout": 5},
    "🍒": {"weight": 35, "payout": 2}
}

def _ensure_table():
    """מוודא שהטבלה קיימת ומעודכנת."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS slots_history (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        result TEXT NOT NULL,
                        payout INTEGER DEFAULT 0,
                        is_win BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                # הוספת עמודות למקרה שהטבלה כבר הייתה קיימת בלי השדרוג
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS payout INTEGER DEFAULT 0")
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS is_win BOOLEAN DEFAULT FALSE")
                conn.commit()
    except Exception as e:
        logger.error(f"Error initializing table: {e}")

def add_slots_result(user_id: int, result: str):
    """
    HE: מוסיף תוצאה למסד הנתונים.
    שמרנו על השם המקורי כדי לא לשבור את שאר חלקי הפרויקט.
    """
    edu_step(1, f"DB: Saving slots result for {user_id}")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO slots_history (user_id, result) VALUES (%s, %s)",
                    (user_id, result)
                )
                conn.commit()
    except Exception as e:
        logger.error(f"DB Error in add_slots_result: {e}")

def get_leaderboard(limit: int = 10):
    """
    HE: מחזיר את טבלת המובילים.
    """
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
        logger.error(f"DB Error in get_leaderboard: {e}")
        return []

def run_slots_logic(user_id: int) -> Dict[str, Any]:
    """
    מנוע המשחק המשודרג - מייצר אנימציה ותוצאה.
    """
    symbols = list(SYMBOLS_DATA.keys())
    weights = [s["weight"] for s in SYMBOLS_DATA.values()]
    
    # הגרלה משוקללת
    final_res = random.choices(symbols, weights=weights, k=3)
    res_str = "".join(final_res)
    
    # חישוב זכייה
    payout = 0
    if len(set(final_res)) == 1:
        payout = SYMBOLS_DATA[final_res[0]]["payout"]
    
    # יצירת פריימים לאנימציה
    frames = []
    for _ in range(3):
        fake = [random.choice(symbols) for _ in range(3)]
        frames.append(f"🎰 ┃ {' ┃ '.join(fake)} ┃")
    frames.append(f"✨ ┃ {' ┃ '.join(final_res)} ┃ ✨")
    
    # שמירה ל-DB
    add_slots_result(user_id, f"{res_str} (Won: {payout})")
    
    return {
        "frames": frames,
        "payout": payout,
        "won": payout > 0,
        "res_str": res_str
    }

# הפעלת הבדיקה בטעינה
_ensure_table()
