import telebot, psycopg2, datetime
from utils.config import DATABASE_URL

def get_db(): return psycopg2.connect(DATABASE_URL)

def get_rank_emoji(rank):
    ranks = {
        "Starter": "🥉",
        "Bronze": "🥈",
        "Silver": "🥇",
        "Gold": "🏆",
        "Diamond": "💎",
        "Whale": "🐋"
    }
    return ranks.get(rank, "👤")

def show_wallet(uid):
    conn = get_db(); cur = conn.cursor()
    # שליפת נתוני משתמש
    cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (str(uid),))
    user = cur.fetchone()
    
    # שליפת 5 עסקאות אחרונות (אם קיימת טבלת עסקאות)
    cur.execute("CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id TEXT, amount INTEGER, type TEXT, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    cur.execute("SELECT amount, description, created_at FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (str(uid),))
    txs = cur.fetchall()
    conn.commit(); cur.close(); conn.close()

    if not user: return "❌ משתמש לא נמצא."

    balance, xp, rank = user
    emoji = get_rank_emoji(rank)
    
    # חישוב התקדמות לדרגה הבאה (למשל כל 500 XP עולים דרגה)
    next_rank_xp = ((xp // 500) + 1) * 500
    progress_bar = "▓" * (xp % 500 // 50) + "░" * (10 - (xp % 500 // 50))

    wallet_msg = (
        f"💳 **DIAMOND WALLET**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **משתמש:** {uid}\n"
        f"{emoji} **דרגה:** {rank}\n\n"
        f"💰 **יתרה נוכחית:** {balance:,} SLH\n"
        f"✨ **ניסיון (XP):** {xp}\n"
        f"📈 **התקדמות:** [{progress_bar}] {xp}/{next_rank_xp}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📜 **פעולות אחרונות:**\n"
    )
    
    if not txs:
        wallet_msg += "_אין עסקאות רשומות עדיין_\n"
    else:
        for tx in txs:
            icon = "➕" if tx[0] > 0 else "➖"
            date = tx[2].strftime("%d/%m")
            wallet_msg += f"{icon} {tx[0]} | {tx[1]} ({date})\n"
            
    wallet_msg += "━━━━━━━━━━━━━━━"
    return wallet_msg

# פונקציה להוספת עסקה (לשימוש בשאר הבוט)
def add_transaction(uid, amount, description):
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO transactions (user_id, amount, description) VALUES (%s, %s, %s)", (str(uid), amount, description))
    cur.execute("UPDATE users SET balance = balance + %s, xp = xp + %s WHERE user_id = %s", (amount, abs(amount)//10, str(uid)))
    conn.commit(); cur.close(); conn.close()
