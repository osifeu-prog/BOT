#!/usr/bin/env python3
"""
🎰 NFTY ULTRA PRO - Telegram Casino & Trading Platform
גרסה משודרגת עם אנימציות מתקדמות, UI מושלם וביצועים גבוהים
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any
from http.server import HTTPServer
from threading import Thread

import redis
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# כבה לוגים מיותרים
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ייבוא מודולים מקומיים
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import TELEGRAM_TOKEN, ADMIN_IDS, REDIS_URL, BOT_USERNAME
    from app.database.manager import db
    from app.bot.welcome import start
    from app.games import mines, slots, crash, roulette, blackjack, dice
    from app.core.shop import open_shop
    from app.core.affiliate import show_affiliate_panel
    from app.utils.leaderboard import show_leaderboard
    from app.utils.daily_tasks import show_daily_tasks, claim_daily_bonus
    from app.utils.themes import get_theme, apply_theme
    from admin.dashboard import send_admin_report, broadcast, gift_balance
    from app.security import smart_rate_limiter
except ImportError as e:
    print(f"❌ שגיאה בייבוא מודולים: {e}")
    sys.exit(1)

# Global variables
app = None
redis_client = None

# ============ HEALTH CHECK SERVER ============
class HealthCheckHandler:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
    
    async def handle_health(self):
        """Handle health check requests"""
        self.request_count += 1
        uptime = datetime.now() - self.start_time
        return {
            "status": "healthy",
            "uptime": str(uptime),
            "requests": self.request_count,
            "timestamp": datetime.now().isoformat()
        }

health_handler = HealthCheckHandler()

# ============ ANIMATION MANAGER ============
class AnimationManager:
    """מנהל אנימציות מתקדמות"""
    
    @staticmethod
    async def loading_animation(query, text: str = "טוען...", steps: int = 3):
        """הצג אנימציית טעינה"""
        dots = ["⏳", "⌛", "⏳", "🎰"]
        for dot in dots:
            try:
                await query.edit_message_text(f"{text} {dot}")
                await asyncio.sleep(0.3)
            except:
                pass
    
    @staticmethod
    async def countdown_animation(query, from_num: int = 3, text: str = "המשחק מתחיל"):
        """אנימציית ספירה לאחור"""
        for i in range(from_num, 0, -1):
            try:
                await query.edit_message_text(f"{text}... {i} ⏱️")
                await asyncio.sleep(0.7)
            except:
                pass
    
    @staticmethod
    async def win_animation(query, amount: int):
        """אנימציית זכייה"""
        fireworks = ["🎆", "🎇", "✨", "🎉", "🏆", "💰"]
        for firework in fireworks:
            try:
                await query.edit_message_text(f"🎉 **זכית ב-{amount:,} מטבעות!** {firework}")
                await asyncio.sleep(0.2)
            except:
                pass

# ============ GAME HANDLERS ============
async def handle_game_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בבחירת משחק"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # בדיקת הגבלת rate
    allowed, wait_time = smart_rate_limiter.check_rate_limit(user_id, 'game_action')
    if not allowed:
        await query.answer(f"⏳ אנא המתן {wait_time} שניות לפני פעולה נוספת", show_alert=True)
        return
    
    game_map = {
        "play_mines": mines.start_mines,
        "play_slots": slots.start_slots,
        "play_crash": crash.start_crash,
        "play_roulette": roulette.start_roulette,
        "play_blackjack": blackjack.start_blackjack,
        "play_dice": dice.start_dice,
        "open_shop": open_shop,
        "daily_bonus": claim_daily_bonus,
        "affiliate_panel": show_affiliate_panel,
        "leaderboard": show_leaderboard,
        "daily_tasks": show_daily_tasks,
        "user_report": show_user_report,
        "admin_report": send_admin_report
    }
    
    game_func = game_map.get(query.data)
    if game_func:
        await game_func(update, context)
    else:
        await query.answer("❌ פעולה לא זמינה כרגע")

async def show_user_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """הצג דוח משתמש מפורט"""
    query = update.callback_query
    user_id = query.from_user.id
    
    user = db.get_user(user_id)
    if not user:
        await query.answer("❌ משתמש לא נמצא")
        return
    
    tier = user.get("tier", "Free")
    balance = int(user.get("balance", 0))
    referrals = db.r.scard(f"user:{user_id}:referrals") or 0
    total_wins = int(db.r.get(f"user:{user_id}:stats:wins") or 0)
    total_wagered = int(db.r.get(f"user:{user_id}:stats:wagered") or 0)
    
    # חישוב דירוג
    if total_wins > 0 and total_wagered > 0:
        win_rate = (total_wins / (total_wagered / 100)) * 100
    else:
        win_rate = 0
    
    report_text = f"""
📊 **דוח משתמש מפורט**

👤 **פרופיל:**
• שם: {query.from_user.first_name}
• דרגה: {tier}
• יתרה: {balance:,} 🪙
• הפניות: {referrals} 👥

🎮 **סטטיסטיקות משחק:**
• זכיות: {total_wins}
• סכום שהומר: {total_wagered:,}
• אחוז זכייה: {win_rate:.1f}%
• ניסיון: {min(balance // 100, 100)}/100

📈 **הישגים:**
{get_achievements(user_id)}

💡 **טיפים:**
• שחק בזהירות ובהנאה
• קח הפסקות קבועות
• הגדר מגבלות לעצמך
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 רענן", callback_data="user_report")],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=report_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

def get_achievements(user_id: int) -> str:
    """קבל הישגי משתמש"""
    achievements = []
    user = db.get_user(user_id)
    balance = int(user.get("balance", 0))
    
    if balance >= 1000:
        achievements.append("💰 אספן זהב (1,000+ מטבעות)")
    if balance >= 5000:
        achievements.append("🏦 טייקון (5,000+ מטבעות)")
    
    referrals = db.r.scard(f"user:{user_id}:referrals") or 0
    if referrals >= 5:
        achievements.append("👥 מגייס (5+ הפניות)")
    if referrals >= 20:
        achievements.append("🌟 סלבס (20+ הפניות)")
    
    if len(achievements) == 0:
        return "• עדיין אין הישגים - המשך לשחק!"
    
    return "\n".join([f"• {ach}" for ach in achievements])

# ============ ADMIN COMMANDS ============
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודות מנהל"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    if not context.args:
        keyboard = [
            [InlineKeyboardButton("📊 דוח סטטיסטיקות", callback_data="admin_report")],
            [InlineKeyboardButton("📢 שידור למשתמשים", callback_data="broadcast_menu")],
            [InlineKeyboardButton("🎁 מתן מתנות", callback_data="gift_menu")],
            [InlineKeyboardButton("📈 גרפים מתקדמים", callback_data="admin_charts")]
        ]
        
        await update.message.reply_text(
            "🔐 **פאנל מנהלים**\n\nבחר פעולה:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    command = context.args[0].lower()
    
    if command == "stats":
        await send_admin_report(update, context)
    elif command == "broadcast":
        await broadcast(update, context)
    elif command == "gift":
        await gift_balance(update, context)
    elif command == "users":
        total = db.get_total_users()
        await update.message.reply_text(f"👥 סה״כ משתמשים: {total}")
    else:
        await update.message.reply_text(
            "📖 **פקודות מנהל זמינות:**\n"
            "/admin stats - דוח סטטיסטיקות\n"
            "/admin broadcast - שידור הודעה\n"
            "/admin gift - מתן מתנות\n"
            "/admin users - מספר משתמשים"
        )

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בשגיאות"""
    try:
        raise context.error
    except Exception as e:
        print(f"⚠️  שגיאה: {e}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ אירעה שגיאה. אנא נסה שוב או פנה לתמיכה."
            )

# ============ WEBHOOK MANAGEMENT ============
async def set_webhook_railway(token: str, domain: str, port: int):
    """הגדר webhook עבור Railway"""
    import requests
    
    print("🚀 מגדיר webhook עבור Railway...")
    
    # נקה webhook קודם
    for _ in range(3):
        try:
            requests.get(
                f"https://api.telegram.org/bot{token}/deleteWebhook",
                params={"drop_pending_updates": "true"},
                timeout=5
            )
            await asyncio.sleep(1)
        except:
            pass
    
    # הגדר webhook חדש
    webhook_url = f"https://{domain}/{token}"
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={
                "url": webhook_url,
                "drop_pending_updates": True,
                "allowed_updates": ["message", "callback_query"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook הוגדר: {webhook_url}")
            return True
        else:
            print(f"❌ שגיאה בהגדרת webhook: {response.text}")
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

# ============ MAIN APPLICATION ============
def setup_handlers(application: Application):
    """הגדר כל המטפלים"""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", send_admin_report))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("gift", gift_balance))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_game_selection, pattern="^(play_|open_|daily_|affiliate_|leaderboard|user_|admin_).*"))
    application.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בהודעות טקסט"""
    # ניתן להוסיף לוגיקה לטיפול בהודעות טקסט מותאמות אישית
    await update.message.reply_text(
        "👋 שלום! השתמש בתפריט או בפקודות כדי להתחיל לשחק.\n"
        "לחץ /start כדי לראות את התפריט הראשי."
    )

async def run_polling():
    """הרץ את הבוט במצב polling"""
    print("🔄 מפעיל בוט במצב polling...")
    await app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

async def run_webhook(domain: str, port: int):
    """הרץ את הבוט במצב webhook"""
    print(f"🌐 מפעיל בוט עם webhook על {domain}:{port}")
    
    # המתן לאתחול
    await asyncio.sleep(2)
    
    # התחל את ה-webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://{domain}/{TELEGRAM_TOKEN}",
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

def health_server():
    """הרץ שרת health check"""
    from health import run_health_server
    run_health_server()

def main():
    """נקודת כניסה ראשית"""
    global app, redis_client
    
    print("""
    ╔══════════════════════════════════════╗
    ║     🎰 NFTY ULTRA PRO CASINO        ║
    ║         גרסה משודרגת V2.0           ║
    ╚══════════════════════════════════════╝
    """)
    
    # בדיקת טוקן
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ טוקן לא תקין. אנא הגדר TELEGRAM_TOKEN בקובץ .env")
        sys.exit(1)
    
    # אתחול Redis
    try:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        print("✅ Redis מחובר בהצלחה")
    except Exception as e:
        print(f"❌ שגיאה בחיבור ל-Redis: {e}")
        sys.exit(1)
    
    # אתחול האפליקציה
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_handlers(app)
    
    # בדיקת מצב Railway
    is_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
    port = int(os.environ.get("PORT", 8080))
    
    if is_railway:
        print(f"🚂 Railway mode - פורט {port}")
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "bot.up.railway.app")
        
        # הרץ שרת health check ברקע
        health_thread = Thread(target=health_server, daemon=True)
        health_thread.start()
        
        # הרץ webhook
        asyncio.run(run_webhook(domain, port))
    else:
        print("💻 מצב מקומי - polling")
        # הרץ polling
        asyncio.run(run_polling())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 הבוט נסגר")
    except Exception as e:
        print(f"❌ שגיאה קריטית: {e}")
        sys.exit(1)
