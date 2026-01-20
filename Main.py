import os
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN, ADMIN_IDS
from app.bot.welcome import start
from app.core.shop import open_shop
from app.core.affiliate import show_affiliate_panel
from app.games.mines import start_mines, handle_mine_click
from app.games.slots import start_slots
from app.games.crash import start_crash, handle_crash_click
from app.games.roulette import start_roulette, handle_roulette_bet
from app.games.blackjack import start_blackjack, handle_blackjack_action
from admin.dashboard import send_admin_report, broadcast
from admin.tools import gift_balance
from app.security import smart_rate_limiter
from app.database.manager import db
from app.utils.daily_tasks import daily_tasks
from app.utils.leaderboard import leaderboard

# הגדר logging מתקדם
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def daily_bonus(update, context):
    """בונוס יומי משופר"""
    query = update.callback_query
    uid = query.from_user.id
    
    # בדוק אם כבר קיבל היום
    today_key = f"daily_bonus:{uid}:{os.environ.get('BOT_USERNAME', 'nfty')}:{os.environ.get('BONUS_DATE', 'today')}"
    
    if db.r.exists(today_key):
        await query.answer("⏳ כבר אספת את הבונוס היום! מחר תוכל שוב.", show_alert=True)
        return
    
    # תן בונוס לפי דרגה
    user = db.get_user(uid)
    tier = user.get("tier", "Free")
    
    bonus_amounts = {
        "Free": 100,
        "Pro": 250,
        "VIP": 500
    }
    
    bonus = bonus_amounts.get(tier, 100)
    
    # עדכן יתרה
    db.r.hincrby(f"user:{uid}:profile", "balance", bonus)
    
    # סמן שקיבל היום
    db.r.setex(today_key, 86400, "1")
    
    # עדכן סטטיסטיקות
    db.r.hincrby(f"user:{uid}:stats", "daily_bonuses", 1)
    
    await query.answer(f"🎁 קיבלת {bonus} מטבעות בונוס יומי! (דרגה: {tier})", show_alert=True)

async def show_daily_tasks(update, context):
    """הצג משימות יומיות"""
    query = update.callback_query
    uid = query.from_user.id
    
    tasks = daily_tasks.get_daily_tasks(uid)
    
    tasks_text = "📋 **משימות יומיות**\n\n"
    
    completed_count = 0
    total_rewards = 0
    
    for task_id, task_info in tasks.items():
        status = "✅" if task_info['completed'] and task_info['claimed'] else "🔄" if task_info['completed'] else "⭕"
        
        if task_info['max_progress'] > 1:
            progress = f"{task_info['progress']}/{task_info['max_progress']}"
        else:
            progress = ""
        
        tasks_text += f"{status} **{task_info['name']}**\n"
        tasks_text += f"   {task_info['description']}\n"
        tasks_text += f"   פרס: {task_info['reward']} 🪙 {progress}\n"
        
        if task_info['completed'] and not task_info['claimed']:
            tasks_text += f"   [👆 לחץ כדי לקבל פרס]\n"
        
        tasks_text += "\n"
        
        if task_info['completed']:
            completed_count += 1
        if task_info['claimed']:
            total_rewards += task_info['reward']
    
    # הוספת סטטיסטיקה
    tasks_text += f"**📊 סטטיסטיקה:**\n"
    tasks_text += f"✅ הושלמו: {completed_count}/{len(tasks)}\n"
    tasks_text += f"💰 פרסים שנאספו: {total_rewards} 🪙\n"
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔄 רענן", callback_data="daily_tasks"),
         InlineKeyboardButton("🎮 חזרה למשחקים", callback_data="start")]
    ]
    
    # הוספת כפתורים למשימות ספציפיות
    for task_id, task_info in tasks.items():
        if task_info['completed'] and not task_info['claimed']:
            keyboard.append([InlineKeyboardButton(f"🎁 קבל פרס: {task_info['name']}", callback_data=f"claim_task_{task_id}")])
    
    await query.edit_message_text(
        text=tasks_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def claim_task_reward(update, context):
    """קבל פרס על משימה"""
    query = update.callback_query
    uid = query.from_user.id
    task_id = query.data.replace("claim_task_", "")
    
    reward = daily_tasks.claim_task_reward(uid, task_id)
    
    if reward > 0:
        await query.answer(f"🎉 קיבלת {reward} מטבעות פרס!", show_alert=True)
        await show_daily_tasks(update, context)
    else:
        await query.answer("❌ לא ניתן לקבל פרס למשימה זו", show_alert=True)

async def show_leaderboard(update, context):
    """הצג לוח תוצאות"""
    query = update.callback_query
    uid = query.from_user.id
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # קבל לוחות תוצאות שונים
    top_balance = leaderboard.get_leaderboard('balance', 'weekly', 10)
    top_wins = leaderboard.get_leaderboard('total_wins', 'weekly', 10)
    
    # קבל דירוג המשתמש
    user_rank_balance = leaderboard.get_user_rank(uid, 'balance', 'weekly')
    user_rank_wins = leaderboard.get_user_rank(uid, 'total_wins', 'weekly')
    
    leaderboard_text = "🏆 **לוח תוצאות שבועי**\n\n"
    
    leaderboard_text += "**💰 טופ יתרות:**\n"
    for entry in top_balance:
        trophy = "👑" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else f"{entry['rank']}."
        leaderboard_text += f"{trophy} {entry['first_name']}: {entry['score']:,} 🪙\n"
    
    leaderboard_text += "\n**🎯 טופ ניצחונות:**\n"
    for entry in top_wins:
        trophy = "👑" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else f"{entry['rank']}."
        leaderboard_text += f"{trophy} {entry['first_name']}: {entry['score']} ניצחונות\n"
    
    # הוסף דירוג המשתמש
    if user_rank_balance:
        leaderboard_text += f"\n**📊 הדירוג שלך:**\n"
        leaderboard_text += f"💰 יתרה: מקום #{user_rank_balance['rank']} ({user_rank_balance['score']:,} 🪙)\n"
    
    if user_rank_wins:
        leaderboard_text += f"🎯 ניצחונות: מקום #{user_rank_wins['rank']} ({user_rank_wins['score']} ניצחונות)\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 יתרות", callback_data="leaderboard_balance"),
         InlineKeyboardButton("🎯 ניצחונות", callback_data="leaderboard_wins"),
         InlineKeyboardButton("🕹️ משחקים", callback_data="leaderboard_games")],
        [InlineKeyboardButton("📅 יומי", callback_data="leaderboard_daily"),
         InlineKeyboardButton("📅 חודשי", callback_data="leaderboard_monthly"),
         InlineKeyboardButton("⭐ כל הזמנים", callback_data="leaderboard_alltime")],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=leaderboard_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_user_report(update, context):
    """הצג דוח משתמש מפורט"""
    query = update.callback_query
    uid = query.from_user.id
    
    user = db.get_user(uid)
    
    # חשב סטטיסטיקות נוספות
    total_games = (db.r.get(f"user:{uid}:stats:total_games") or 0)
    total_wins = (db.r.get(f"user:{uid}:stats:total_wins") or 0)
    total_wagered = (db.r.get(f"user:{uid}:stats:total_wagered") or 0)
    total_won = (db.r.get(f"user:{uid}:stats:total_won") or 0)
    
    win_rate = (int(total_wins) / int(total_games) * 100) if int(total_games) > 0 else 0
    
    report_text = f"""
📊 **דוח משתמש מפורט**

👤 **זהות:** {user.get('first_name', 'משתמש')}
💎 **דרגה:** {user.get('tier', 'Free')}
💰 **יתרה:** {int(user.get('balance', 0)):,} 🪙

📈 **סטטיסטיקות משחק:**
• 🕹️ משחקים ששוחקו: {total_games}
• 🎯 משחקים שנוצחו: {total_wins}
• 📊 אחוז ניצחון: {win_rate:.1f}%
• 💸 סך הכל הומר: {int(total_wagered):,} 🪙
• 🏆 סך הכל נוצח: {int(total_won):,} 🪙
• 📉 רווח/הפסד נטו: {int(total_won) - int(total_wagered):,} 🪙

👥 **סטטיסטיקות שותפים:**
• 👥 משתמשים שהוזמנו: {db.r.scard(f"user:{uid}:referrals") or 0}
• 💰 רווח משותפים: {int(user.get('affiliate_earnings', 0)):,} 🪙

📅 **פעילות:**
• 🎁 בונוסים יומיים: {db.r.hget(f"user:{uid}:stats", "daily_bonuses") or 0}
• 📅 נרשם בתאריך: {user.get('joined', 'לא ידוע')}
"""
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔄 רענן דוח", callback_data="user_report"),
         InlineKeyboardButton("📤 שתף דוח", callback_data="share_report")],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=report_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def main_handler(update, context):
    """Handler ראשי משופר עם Rate Limiting חכם"""
    query = update.callback_query
    uid = query.from_user.id
    
    # בדיקת Rate Limiting חכמה
    data = query.data
    
    # קבע סוג פעולה לפי הנתונים
    if data.startswith('m_') or 'play_' in data:
        action_type = 'game_action'
    elif data in ['start', 'open_shop', 'affiliate_panel', 'user_report', 'daily_tasks', 'leaderboard']:
        action_type = 'menu_navigation'
    elif data.startswith('roulette_') or data.startswith('bj_') or data.startswith('claim_'):
        action_type = 'game_action'
    else:
        action_type = 'default'
    
    allowed, wait_time = smart_rate_limiter.check_rate_limit(uid, action_type)
    if not allowed:
        await query.answer(f"⏳ יותר מדי בקשות מסוג זה. נסה שוב בעוד {wait_time} שניות", show_alert=True)
        return
    
    await query.answer()
    
    # טיפול בפקודות לפי סוג
    try:
        if data == "start": 
            await start(update, context)
        elif data == "open_shop": 
            await open_shop(update, context)
        elif data == "daily_bonus": 
            await daily_bonus(update, context)
        elif data == "affiliate_panel": 
            await show_affiliate_panel(update, context)
        elif data == "play_mines": 
            await start_mines(update, context)
        elif data == "play_slots": 
            await start_slots(update, context)
        elif data == "play_crash": 
            await start_crash(update, context)
        elif data == "play_roulette": 
            await start_roulette(update, context)
        elif data == "play_blackjack": 
            await start_blackjack(update, context)
        elif data == "admin_report": 
            await send_admin_report(update, context)
        elif data == "daily_tasks": 
            await show_daily_tasks(update, context)
        elif data == "leaderboard": 
            await show_leaderboard(update, context)
        elif data == "user_report": 
            await show_user_report(update, context)
        elif data.startswith("claim_task_"): 
            await claim_task_reward(update, context)
        elif data.startswith("m_"): 
            await handle_mine_click(update, context)
        elif data == "spin_slots": 
            await start_slots(update, context)
        elif data == "crash_cashout": 
            await handle_crash_click(update, context)
        elif data.startswith("roulette_"): 
            await handle_roulette_bet(update, context)
        elif data.startswith("bj_"): 
            await handle_blackjack_action(update, context)
        elif data.startswith("leaderboard_"): 
            await show_leaderboard(update, context)
        else:
            # פקודה לא מוכרת - חזרה לתפריט
            await query.message.reply_text("❔ פקודה לא מוכרת. מחזיר אותך לתפריט הראשי...")
            await start(update, context)
    
    except Exception as e:
        logger.error(f"שגיאה בטיפול בפקודה {data}: {str(e)}")
        await query.message.reply_text("❌ אירעה שגיאה. אנא נסה שוב או פנה לתמיכה.")

async def error_handler(update, context):
    """טיפול בשגיאות"""
    logger.error(f"שגיאה בזמן עדכון: {context.error}")
    
    try:
        # שלח הודעת שגיאה למשתמש
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ אירעה שגיאה במערכת. הפיתוחים כבר קיבלו התראה ותתקנו זאת בהקדם."
        )
    except:
        pass

def main():
    """פונקציה ראשית משופרת"""
    print("=" * 60)
    print("🚀 NFTY ULTRA CASINO BOT - PREMIUM EDITION")
    print("=" * 60)
    
    # בדוק שהטוקן קיים
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר או עדיין ברירת מחדל!")
        print("⚠️  אנא הגדר את TELEGRAM_TOKEN בקובץ config.py או משתנה סביבה")
        return
    
    # בדוק חיבור ל-Redis
    try:
        db.r.ping()
        logger.info("✅ חיבור ל-Redis תקין")
    except Exception as e:
        logger.error(f"❌ שגיאת Redis: {e}")
        print("⚠️  אנא ודא ש-REDIS_URL תקין")
        return
    
    # צור את האפליקציה
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # הוסף error handler
    app.add_error_handler(error_handler)
    
    # הוסף את ה-handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gift", gift_balance))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", show_user_report))
    app.add_handler(CommandHandler("tasks", show_daily_tasks))
    app.add_handler(CommandHandler("leaderboard", show_leaderboard))
    
    # הוסף handler לאימות הודעות טקסט (להרחבה עתידית)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                  lambda update, context: update.message.reply_text(
                                      "📝 השתמש בתפריט או בפקודות. כתוב /start להתחיל.")))
    
    # הוסף את ה-callback handler הראשי
    app.add_handler(CallbackQueryHandler(main_handler))
    
    # קבל את משתני הסביבה
    port = int(os.environ.get("PORT", 8080))
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", None)
    
    # בדוק אם אנחנו ב-Railway
    if railway_public_domain:
        # ב-Railway - השתמש ב-webhooks
        webhook_url = f"https://{railway_public_domain}/{TELEGRAM_TOKEN}"
        
        logger.info(f"🔗 דומיין ציבורי: {railway_public_domain}")
        logger.info(f"🌐 כתובת Webhook: {webhook_url}")
        logger.info(f"🔧 פורט: {port}")
        
        print(f"\n🌐 מצב: PRODUCTION (Railway)")
        print(f"🔗 Webhook: {webhook_url}")
        
        # הגדר webhook
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
    else:
        # מקומי - השתמש ב-polling
        logger.info("📡 הרצה עם polling (פיתוח מקומי)...")
        
        print("\n💻 מצב: DEVELOPMENT (מקומי)")
        print("📡 שיטת חיבור: Polling")
        
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            poll_interval=0.5
        )

if __name__ == "__main__":
    main()
