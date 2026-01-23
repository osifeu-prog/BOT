import telebot, os, logging
from utils.config import *
from handlers import wallet_logic

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['admin'])
def admin_dashboard(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    
    stats = wallet_logic.get_system_stats()
    
    dashboard_text = f"""
💎 **SLH SaaS Admin Panel**
----------------------------
📊 **סטטיסטיקות:**
- משתמשים: {stats['users']}
- עסקאות: {stats['tx_count']}
- יתרה במחזור: {stats['total_supply']} SLH

⚙️ **הגדרות פעילות (Railway):**
- בונוס הפניה: {REFERRAL_REWARD} SLH
- סיכוי זכייה: {WIN_CHANCE_PERCENT}%
- עלות הצצה: {PEEK_COST} SLH
- מחיר שיעור: {LESSON_DB_PRICE}

🚀 **סטטוס מערכת:**
- OpenAI API: {'✅' if OPENAI_API_KEY else '❌'}
- Crypto Pay: {'✅' if CRYPTO_PAY_TOKEN else '❌'}
- Debug Mode: {DEBUG_MODE}
----------------------------
השתמש ב- /config [KEY] [VALUE] כדי לעדכן (זמנית)
או עדכן ב-Railway לשינוי קבוע.
"""
    bot.send_message(message.chat.id, dashboard_text)

# פקודה להרצת בדיקת עשן ידנית
@bot.message_handler(commands=['smoke_test'])
def smoke_test_cmd(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        results = []
        # בדיקת DB
        try:
            wallet_logic.get_system_stats()
            results.append("✅ Database: Connected")
        except: results.append("❌ Database: Failed")
        
        # בדיקת סנכרון משתנים
        if REFERRAL_REWARD > 0: results.append("✅ Config: Synced")
        else: results.append("❌ Config: Missing Variables")
        
        bot.reply_to(message, "💨 **תוצאות הרצת עשן:**\n" + "\n".join(results))

if __name__ == "__main__":
    print("🚀 Starting Bot in Admin Mode...")
    bot.infinity_polling()
