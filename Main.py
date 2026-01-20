#!/usr/bin/env python3
"""
🎰 NFTY ULTRA CASINO - גרסה פשוטה ופועלת
גרסה מינימלית שתעבוד ב-Railway ללא בעיות
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any

# הוסף את נתיב הפרויקט ל-Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הגדר לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# כבה לוגים של ספריות חיצוניות
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        ContextTypes,
        MessageHandler,
        filters
    )
    
    # נסה לטעון את config
    try:
        from config import TELEGRAM_TOKEN, ADMIN_IDS, REDIS_URL, BOT_USERNAME, DEBUG_MODE
        logger.info("✅ Config נטען בהצלחה")
    except ImportError as e:
        logger.error(f"❌ שגיאה בטעינת config: {e}")
        # יצירת משתנים ברירת מחדל
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
        ADMIN_IDS = []
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        BOT_USERNAME = ""
        DEBUG_MODE = True
        
except ImportError as e:
    logger.error(f"❌ ספריות חסרות: {e}")
    sys.exit(1)

# ============ מצב הדגמה (אם אין Redis) ============
DEMO_MODE = False
user_balances = {}  # אחסון זמני במצב הדגמה

# ============ פונקציות משתמש בסיסיות ============
def get_user_balance(user_id: int) -> int:
    """קבל יתרת משתמש"""
    if DEMO_MODE:
        return user_balances.get(user_id, 1000)
    
    # אם יש Redis, נשתמש בו
    try:
        import redis
        r = redis.from_url(REDIS_URL)
        balance = r.hget(f"user:{user_id}:profile", "balance")
        return int(balance) if balance else 1000
    except:
        return 1000  # ברירת מחדל

def update_user_balance(user_id: int, amount: int, reason: str = ""):
    """עדכן יתרת משתמש"""
    if DEMO_MODE:
        current = user_balances.get(user_id, 1000)
        user_balances[user_id] = current + amount
        logger.info(f"💰 יתרה: {user_id} -> {amount} ({reason})")
        return True
    
    try:
        import redis
        r = redis.from_url(REDIS_URL)
        current = int(r.hget(f"user:{user_id}:profile", "balance") or 1000)
        r.hset(f"user:{user_id}:profile", "balance", current + amount)
        logger.info(f"💰 יתרה: {user_id} -> {amount} ({reason})")
        return True
    except Exception as e:
        logger.error(f"❌ שגיאה בעדכון יתרה: {e}")
        return False

# ============ פונקציות הבוט ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת /start"""
    user = update.effective_user
    user_id = user.id
    
    # רישום משתמש
    if DEMO_MODE:
        if user_id not in user_balances:
            user_balances[user_id] = 1000
    else:
        try:
            import redis
            r = redis.from_url(REDIS_URL)
            if not r.exists(f"user:{user_id}:profile"):
                r.hset(f"user:{user_id}:profile", mapping={
                    "id": user_id,
                    "username": user.username or "",
                    "first_name": user.first_name or "",
                    "balance": 1000,
                    "tier": "Free",
                    "joined": datetime.now().isoformat()
                })
        except:
            pass
    
    # צור תפריט ראשי
    balance = get_user_balance(user_id)
    
    welcome_text = f"""
🎰 **ברוך הבא ל-NFTY ULTRA CASINO!** 🚀

👤 **שחקן:** {user.first_name}
💰 **יתרה:** {balance:,} 🪙
🎮 **דרגה:** Free

👇 **בחר משחק:**
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💣 Mines", callback_data="play_mines"),
            InlineKeyboardButton("🎰 Slots", callback_data="play_slots"),
            InlineKeyboardButton("🚀 Crash", callback_data="play_crash")
        ],
        [
            InlineKeyboardButton("🎡 Roulette", callback_data="play_roulette"),
            InlineKeyboardButton("🃏 Blackjack", callback_data="play_blackjack"),
            InlineKeyboardButton("🎲 Dice", callback_data="play_dice")
        ],
        [
            InlineKeyboardButton("🛒 חנות", callback_data="open_shop"),
            InlineKeyboardButton("🎁 בונוס יומי", callback_data="daily_bonus")
        ],
        [
            InlineKeyboardButton("👥 שותפים", callback_data="affiliate_panel"),
            InlineKeyboardButton("📊 דוח", callback_data="user_report")
        ]
    ]
    
    if str(user_id) in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("🔐 לוח בקרה", callback_data="admin_report")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_game_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בבחירת משחק"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    game = query.data
    
    game_names = {
        "play_mines": "💣 Mines",
        "play_slots": "🎰 Slots", 
        "play_crash": "🚀 Crash",
        "play_roulette": "🎡 Roulette",
        "play_blackjack": "🃏 Blackjack",
        "play_dice": "🎲 Dice",
        "open_shop": "🛒 Shop",
        "daily_bonus": "🎁 Daily Bonus",
        "affiliate_panel": "👥 Affiliate",
        "user_report": "📊 Report",
        "admin_report": "🔐 Admin"
    }
    
    game_name = game_names.get(game, "משחק")
    
    # אם זה בונוס יומי
    if game == "daily_bonus":
        balance = get_user_balance(user_id)
        bonus = 100
        update_user_balance(user_id, bonus, "Daily bonus")
        new_balance = get_user_balance(user_id)
        
        await query.edit_message_text(
            text=f"🎁 **בונוס יומי נתקבל!**\n\n💰 +{bonus} מטבעות\n👛 יתרה חדשה: {new_balance:,} 🪙\n\nלחץ /start לחזרה לתפריט",
            parse_mode='Markdown'
        )
        return
    
    # אם זה דוח משתמש
    if game == "user_report":
        balance = get_user_balance(user_id)
        await query.edit_message_text(
            text=f"📊 **דוח משתמש**\n\n👤 {query.from_user.first_name}\n💰 יתרה: {balance:,} 🪙\n🎮 דרגה: Free\n\nהמשך לשחק כדי לשפר את הסטטיסטיקות!",
            parse_mode='Markdown'
        )
        return
    
    # אם זה פאנל מנהלים
    if game == "admin_report" and str(user_id) not in ADMIN_IDS:
        await query.answer("❌ אין לך הרשאות מנהל!", show_alert=True)
        return
    
    # עבור משחקים - נראה הודעת תחזוקה
    maintenance_text = f"""
🛠️ **{game_name} - בתחזוקה**

המשחק זמין בגרסאות המלאות של הבוט.

📋 **פיצ'רים זמינים כרגע:**
• 💰 בונוס יומי
• 📊 דוח משתמשים
• 🛒 מערכת חנות (בקרוב)
• 👥 שותפים (בקרוב)

🎮 **למשחקים המלאים:**
שדרג לגרסה המלאה עם כל המשחקים והאנימציות!
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=maintenance_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת /help"""
    help_text = """
🤖 **NFTY ULTRA CASINO - עזרה**

📋 **פקודות זמינות:**
/start - תפריט ראשי
/help - הודעה זו
/balance - בדיקת יתרה
/admin - פקודות מנהל (למנהלים בלבד)

🎮 **מערכת המשחקים:**
• 💣 Mines - מצא יהלומים והימנע ממוקשים
• 🎰 Slots - סובב גלגלים לזכייה
• 🚀 Crash - משוך לפני שהמטוס מתרסק
• 🎡 Roulette - הימורים על מספרים וצבעים
• 🃏 Blackjack - נצח את הדילר ב-21
• 🎲 Dice - ניחוש תוצאת קוביה

💰 **כלכלה:**
• יתרה התחלתית: 1,000 מטבעות
• בונוס יומי: 100 מטבעות
• הפניות: 500 מטבעות להזמנה

👨‍💻 **תמיכה:**
לשאלות ובעיות, פנה למפתח: @osifeu-prog
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת /balance"""
    user_id = update.effective_user.id
    balance = get_user_balance(user_id)
    
    await update.message.reply_text(
        f"💰 **היתרה שלך:** {balance:,} מטבעות 🪙\n\nלחץ /start לשחק!",
        parse_mode='Markdown'
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת /admin"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    admin_text = """
🔐 **פאנל מנהלים**

📊 **סטטיסטיקות:**
• מצב: פעיל ✅
• גרסה: 1.0.0
• זמן פעילות: כל הזמן

⚡ **פקודות מהירות:**
/gift [id] [amount] - מתן מתנה
/users - מספר משתמשים
/stats - סטטיסטיקות

🛠️ **ניהול:**
/restart - הפעלה מחדש
/broadcast [הודעה] - שידור לכולם
"""
    
    await update.message.reply_text(admin_text, parse_mode='Markdown')

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת /gift"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ שימוש: /gift [user_id] [amount]")
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        
        if amount <= 0:
            await update.message.reply_text("❌ כמות חייבת להיות חיובית")
            return
        
        success = update_user_balance(target_id, amount, f"Gift from admin {user_id}")
        
        if success:
            await update.message.reply_text(f"✅ נוספו {amount} מטבעות למשתמש {target_id}")
        else:
            await update.message.reply_text("❌ שגיאה בהוספת המטבעות")
            
    except ValueError:
        await update.message.reply_text("❌ קלט לא חוקי")

# ============ שרת Health Check ============
def start_health_server():
    """הפעל שרת health check"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        
        def log_message(self, format, *args):
            pass  # כבה לוגים
    
    def run_server():
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"🌐 Health check server running on port {port}")
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

# ============ הגדרת הבוט ============
def setup_bot():
    """הגדר והפעל את הבוט"""
    
    # בדוק טוקן
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        logger.info("💡 אנא הגדר את TELEGRAM_TOKEN ב-Environment Variables")
        sys.exit(1)
    
    logger.info(f"🤖 אתחול בוט עם טוקן: {TELEGRAM_TOKEN[:10]}...")
    
    # בדוק Redis
    try:
        import redis
        r = redis.from_url(REDIS_URL)
        r.ping()
        logger.info("✅ Redis מחובר")
        global DEMO_MODE
        DEMO_MODE = False
    except Exception as e:
        logger.warning(f"⚠️  Redis לא זמין, מעבר למצב הדגמה: {e}")
        DEMO_MODE = True
    
    # צור אפליקציה
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # הוסף handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("gift", gift_command))
    app.add_handler(CallbackQueryHandler(start_command, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(handle_game_selection, pattern="^play_|^open_|^daily_|^affiliate_|^user_|^admin_"))
    
    return app

# ============ נקודת כניסה ראשית ============
def main():
    """נקודת כניסה ראשית"""
    print("""
    ╔══════════════════════════════════════╗
    ║     🎰 NFTY ULTRA CASINO             ║
    ║           גרסה בסיסית                ║
    ╚══════════════════════════════════════╝
    """)
    
    # הפעל שרת health check
    health_thread = start_health_server()
    
    # הגדר בוט
    app = setup_bot()
    
    # בדוק אם אנחנו ב-Railway
    is_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
    port = int(os.environ.get("PORT", 8080))
    
    async def run_app():
        if is_railway:
            logger.info(f"🚂 Railway mode - פורט {port}")
            
            # קבל domain
            domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "bot.up.railway.app")
            webhook_url = f"https://{domain}/{TELEGRAM_TOKEN}"
            
            logger.info(f"🌐 מגדיר webhook: {webhook_url}")
            
            # נקה webhook ישן
            import requests
            try:
                requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook",
                    params={"drop_pending_updates": "true"},
                    timeout=5
                )
            except:
                pass
            
            # המתן לאתחול
            await app.initialize()
            
            # הגדר webhook
            await app.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            # הפעל webhook
            await app.start()
            await app.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=webhook_url,
                drop_pending_updates=True
            )
            
            logger.info("✅ הבוט פועל עם webhook!")
            
            # החזק פעיל
            await asyncio.Event().wait()
            
        else:
            logger.info("💻 מצב מקומי - polling")
            
            # נקה webhook ישן
            import requests
            try:
                requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook",
                    params={"drop_pending_updates": "true"},
                    timeout=5
                )
            except:
                pass
            
            # הרץ polling
            await app.initialize()
            await app.start()
            logger.info("🔄 מפעיל polling...")
            await app.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            # החזק פעיל
            await asyncio.Event().wait()
    
    # הרץ את האפליקציה
    try:
        asyncio.run(run_app())
    except KeyboardInterrupt:
        logger.info("👋 הבוט נסגר")
    except Exception as e:
        logger.error(f"❌ שגיאה קריטית: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
