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
from app.games.dice import start_dice, handle_dice_bet
from admin.dashboard import send_admin_report, broadcast
from admin.tools import gift_balance
from app.security import smart_rate_limiter
from app.database.manager import db
from app.utils.daily_tasks import daily_tasks
from app.utils.leaderboard import leaderboard
from app.utils.themes import theme_system
from app.auth.roles import user_roles

# הגדר logging מתקדם
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def daily_bonus(update, context):
    """בונוס יומי משופר"""
    query = update.callback_query
    uid = query.from_user.id
    
    # בדוק אם כבר קיבל היום
    today = db.r.get(f"daily_bonus:{uid}")
    if today:
        await query.answer("⏳ כבר אספת את הבונוס היום! מחר תוכל שוב.", show_alert=True)
        return
    
    # תן בונוס לפי דרגה
    user = db.get_user(uid)
    tier = user.get("tier", "Free")
    
    bonus_amounts = {"Free": 100, "Pro": 250, "VIP": 500}
    bonus = bonus_amounts.get(tier, 100)
    
    # עדכן יתרה
    db.r.hincrby(f"user:{uid}:profile", "balance", bonus)
    
    # סמן שקיבל היום
    db.r.setex(f"daily_bonus:{uid}", 86400, "1")
    
    # עדכן סטטיסטיקות
    db.r.hincrby(f"user:{uid}:stats", "daily_bonuses", 1)
    
    await query.answer(f"🎁 קיבלת {bonus} מטבעות בונוס יומי! (דרגה: {tier})", show_alert=True)
    await start(update, context)

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
        progress = f"{task_info['progress']}/{task_info['max_progress']}" if task_info['max_progress'] > 1 else ""
        
        tasks_text += f"{status} **{task_info['name']}**\n"
        tasks_text += f"   {task_info['description']}\n"
        tasks_text += f"   פרס: {task_info['reward']} 🪙 {progress}\n"
        
        if task_info['completed'] and not task_info['claimed']:
            tasks_text += f"   [👆 לחץ כדי לקבל פרס]\n"
        tasks_text += "\n"
        
        if task_info['completed']: completed_count += 1
        if task_info['claimed']: total_rewards += task_info['reward']
    
    tasks_text += f"**📊 סטטיסטיקה:**\n✅ הושלמו: {completed_count}/{len(tasks)}\n💰 פרסים שנאספו: {total_rewards} 🪙\n"
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔄 רענן", callback_data="daily_tasks"),
         InlineKeyboardButton("🎮 חזרה", callback_data="start")]
    ]
    
    for task_id, task_info in tasks.items():
        if task_info['completed'] and not task_info['claimed']:
            keyboard.append([InlineKeyboardButton(f"🎁 קבל פרס: {task_info['name']}", callback_data=f"claim_task_{task_id}")])
    
    await query.edit_message_text(text=tasks_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

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
    
    top_balance = leaderboard.get_leaderboard('balance', 'weekly', 10)
    top_wins = leaderboard.get_leaderboard('total_wins', 'weekly', 10)
    user_rank_balance = leaderboard.get_user_rank(uid, 'balance', 'weekly')
    user_rank_wins = leaderboard.get_user_rank(uid, 'total_wins', 'weekly')
    
    leaderboard_text = "🏆 **לוח תוצאות שבועי**\n\n**💰 טופ יתרות:**\n"
    for entry in top_balance:
        trophy = "👑" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else f"{entry['rank']}."
        leaderboard_text += f"{trophy} {entry['first_name']}: {entry['score']:,} 🪙\n"
    
    leaderboard_text += "\n**🎯 טופ ניצחונות:**\n"
    for entry in top_wins:
        trophy = "👑" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else f"{entry['rank']}."
        leaderboard_text += f"{trophy} {entry['first_name']}: {entry['score']} ניצחונות\n"
    
    if user_rank_balance:
        leaderboard_text += f"\n**📊 הדירוג שלך:**\n💰 יתרה: #{user_rank_balance['rank']} ({user_rank_balance['score']:,} 🪙)\n"
    if user_rank_wins:
        leaderboard_text += f"🎯 ניצחונות: #{user_rank_wins['rank']} ({user_rank_wins['score']} ניצחונות)\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 יתרות", callback_data="leaderboard_balance"),
         InlineKeyboardButton("🎯 ניצחונות", callback_data="leaderboard_wins"),
         InlineKeyboardButton("📅 יומי", callback_data="leaderboard_daily")],
        [InlineKeyboardButton("🏠 תפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(text=leaderboard_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_user_report(update, context):
    """הצג דוח משתמש מפורט"""
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    total_games = db.r.get(f"user:{uid}:stats:total_games") or 0
    total_wins = db.r.get(f"user:{uid}:stats:total_wins") or 0
    total_wagered = db.r.get(f"user:{uid}:stats:total_wagered") or 0
    total_won = db.r.get(f"user:{uid}:stats:total_won") or 0
    win_rate = (int(total_wins) / int(total_games) * 100) if int(total_games) > 0 else 0
    
    report_text = f"""
📊 **דוח משתמש מפורט**

👤 **זהות:** {user.get('first_name', 'משתמש')}
💎 **דרגה:** {user.get('tier', 'Free')}
💰 **יתרה:** {int(user.get('balance', 0)):,} 🪙

📈 **סטטיסטיקות משחק:**
• 🕹️ משחקים: {total_games}
• 🎯 ניצחונות: {total_wins}
• 📊 אחוז ניצחון: {win_rate:.1f}%
• 💸 הומר: {int(total_wagered):,} 🪙
• 🏆 נוצח: {int(total_won):,} 🪙
• 📉 רווח/הפסד: {int(total_won) - int(total_wagered):,} 🪙

👥 **שותפים:**
• 👥 הוזמנו: {db.r.scard(f"user:{uid}:referrals") or 0}
• 💰 רווח: {int(user.get('affiliate_earnings', 0)):,} 🪙

📅 **פעילות:**
• 🎁 בונוסים: {db.r.hget(f"user:{uid}:stats", "daily_bonuses") or 0}
• 📅 נרשם: {user.get('joined', 'לא ידוע')}
"""
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔄 רענן", callback_data="user_report"),
         InlineKeyboardButton("🏠 תפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(text=report_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def help_command(update, context):
    """הצג עזרה"""
    help_text = """
🤖 **NFTY ULTRA CASINO - עזרה**

**🎮 פקודות משחק:**
/start - תפריט ראשי
/stats - דוח אישי
/tasks - משימות יומיות
/leaderboard - לוח תוצאות

**👑 דרגות:**
• 🆓 Free - בסיסית, 5 מוקשים
• ⚡ Pro - 3 מוקשים, בונוסים
• 👑 VIP - 2 מוקשים, פרסים מיוחדים

**🎯 טיפים:**
1. אסוף בונוס יומי כל יום
2. הזמן חברים לקבל פרסים
3. שחק חכם - אל תהמר יותר מדי
4. שדרג ל-VIP לקבלת יתרונות

**❓ תמיכה:** פנה למנהל המערכת
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def main_handler(update, context):
    """Handler ראשי משופר"""
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    
    # Rate Limiting חכם
    if data.startswith('m_') or 'play_' in data or data.startswith(('roulette_', 'bj_', 'dice_')):
        action_type = 'game_action'
    elif data in ['start', 'open_shop', 'affiliate_panel', 'user_report', 'daily_tasks', 'leaderboard']:
        action_type = 'menu_navigation'
    else:
        action_type = 'default'
    
    allowed, wait_time = smart_rate_limiter.check_rate_limit(uid, action_type)
    if not allowed:
        await query.answer(f"⏳ יותר מדי בקשות. נסה שוב בעוד {wait_time} שניות", show_alert=True)
        return
    
    await query.answer()
    
    # טיפול בפקודות
    handlers = {
        "start": start,
        "open_shop": open_shop,
        "daily_bonus": daily_bonus,
        "affiliate_panel": show_affiliate_panel,
        "play_mines": start_mines,
        "play_slots": start_slots,
        "play_crash": start_crash,
        "play_roulette": start_roulette,
        "play_blackjack": start_blackjack,
        "play_dice": start_dice,
        "admin_report": send_admin_report,
        "daily_tasks": show_daily_tasks,
        "leaderboard": show_leaderboard,
        "user_report": show_user_report,
        "spin_slots": start_slots,
        "crash_cashout": handle_crash_click,
    }
    
    # בדוק אם יש handler ישיר
    for prefix, handler in handlers.items():
        if data == prefix:
            await handler(update, context)
            return
    
    # בדוק handler עם prefix
    if data.startswith("claim_task_"):
        await claim_task_reward(update, context)
    elif data.startswith("m_"):
        await handle_mine_click(update, context)
    elif data.startswith("roulette_"):
        await handle_roulette_bet(update, context)
    elif data.startswith("bj_"):
        await handle_blackjack_action(update, context)
    elif data.startswith("dice_"):
        await handle_dice_bet(update, context)
    elif data.startswith("leaderboard_"):
        await show_leaderboard(update, context)
    else:
        await start(update, context)

async def error_handler(update, context):
    """טיפול בשגיאות"""
    logger.error(f"שגיאה: {context.error}")
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ אירעה שגיאה. אנא נסה שוב או פנה לתמיכה."
        )
    except:
        pass

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("🚀 NFTY ULTRA CASINO BOT - PREMIUM EDITION")
    print("=" * 60)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        return
    
    # בדוק חיבור ל-Redis
    try:
        db.r.ping()
        logger.info("✅ חיבור ל-Redis תקין")
    except Exception as e:
        logger.error(f"❌ שגיאת Redis: {e}")
        return
    
    # צור אפליקציה
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # הוסף handlers
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gift", gift_balance))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", show_user_report))
    app.add_handler(CommandHandler("tasks", show_daily_tasks))
    app.add_handler(CommandHandler("leaderboard", show_leaderboard))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                  lambda u,c: u.message.reply_text("📝 השתמש בתפריט או ב-/start")))
    app.add_handler(CallbackQueryHandler(main_handler))
    
    # קבל משתני סביבה
    port = int(os.environ.get("PORT", 8080))
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", None)
    
    if railway_public_domain:
        # Webhook ב-Railway
        webhook_url = f"https://{railway_public_domain}/{TELEGRAM_TOKEN}"
        logger.info(f"🌐 PRODUCTION: {webhook_url}")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Polling מקומי
        logger.info("📡 DEVELOPMENT: Polling")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
