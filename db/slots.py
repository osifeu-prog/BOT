import random
import logging
from typing import List, Dict, Any, Tuple
from db.connection import get_conn
from utils.edu_log import edu_step

logger = logging.getLogger(__name__)

# הגדרות סמלים וסיכויים (Weighted Probability)
SYMBOLS_DATA = {
    "💎": {"weight": 5, "payout": 100},
    "7️⃣": {"weight": 12, "payout": 50},
    "🔔": {"weight": 20, "payout": 20},
    "🍋": {"weight": 28, "payout": 10},
    "🍒": {"weight": 35, "payout": 5}
}

def _ensure_table():
    """Migration: מוודא טבלה ועמודות מעודכנות."""
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
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS payout INTEGER DEFAULT 0")
                cur.execute("ALTER TABLE slots_history ADD COLUMN IF NOT EXISTS is_win BOOLEAN DEFAULT FALSE")
                conn.commit()
    except Exception as e:
        logger.error(f"DB Ensure Error: {e}")

def add_slots_result(user_id: int, result: str, payout: int = 0, is_win: bool = False):
    """שמירת תוצאה למסד הנתונים."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO slots_history (user_id, result, payout, is_win) VALUES (%s, %s, %s, %s)",
                    (user_id, result, payout, is_win)
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Error saving slots: {e}")

def get_leaderboard(limit: int = 10):
    """לידרבורד משופר לפי סך זכיות."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id, COUNT(*) as plays, SUM(payout) as total_payout
                    FROM slots_history
                    GROUP BY user_id
                    ORDER BY total_payout DESC
                    LIMIT %s
                """, (limit,))
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return []

def run_slots_logic(user_id: int) -> Dict[str, Any]:
    """מנוע המשחק המרכזי."""
    symbols = list(SYMBOLS_DATA.keys())
    weights = [s["weight"] for s in SYMBOLS_DATA.values()]
    
    # הגרלה
    res_list = random.choices(symbols, weights=weights, k=3)
    res_str = "".join(res_list)
    
    # חישוב זכייה
    payout = 0
    if len(set(res_list)) == 1:
        payout = SYMBOLS_DATA[res_list[0]]["payout"]
    
    # פריימים לאנימציה (5 פריימים של מתח)
    frames = []
    for i in range(4):
        fake = [random.choice(symbols) for _ in range(3)]
        frames.append(f"🎰 ┃ {' ┃ '.join(fake)} ┃")
    
    final_frame = f"✨ ┃ {' ┃ '.join(res_list)} ┃ ✨"
    frames.append(final_frame)
    
    # שמירה
    add_slots_result(user_id, res_str, payout, payout > 0)
    
    return {
        "frames": frames,
        "payout": payout,
        "won": payout > 0,
        "res_str": res_str
    }

_ensure_table()
