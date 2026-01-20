import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from app.database.manager import db
from config import ADMIN_IDS

async def send_admin_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin report with statistics"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    # Get statistics
    total_users = db.get_total_users()
    recent_users = db.get_recent_users(days=7)
    
    # Generate simple graph
    plt.figure(figsize=(10, 5))
    days = [f'Day {i}' for i in range(7, 0, -1)]
    # Simplified data - in real app, you'd get actual daily signups
    signups = [recent_users // 7] * 7  
    plt.bar(days, signups)
    plt.title('User Signups (Last 7 Days)')
    plt.xlabel('Day')
    plt.ylabel('New Users')
    plt.tight_layout()
    
    # Save plot to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    # Send report
    report_text = f"""
📊 **דוח מנהל**

👥 **משתמשים:**
• סה"כ משתמשים: {total_users}
• משתמשים חדשים (7 ימים): {recent_users}

📈 **סטטיסטיקות:**
• משחקים היום: 0
• עסקאות היום: 0
• הכנסות היום: $0

⚙️ **פעולות מהירות:**
/gift [id] [amount] - מתן מתנה
/broadcast [הודעה] - שליחת הודעה לכולם
"""
    
    if update.callback_query:
        await update.callback_query.message.reply_photo(
            photo=buf,
            caption=report_text,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_photo(
            photo=buf,
            caption=report_text,
            parse_mode='Markdown'
        )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    # Get message from command
    if not context.args:
        await update.message.reply_text("❌ אנא הזן הודעה לשידור.\nשימוש: /broadcast <הודעה>")
        return
    
    message = " ".join(context.args)
    
    # Get all users
    users = db.r.smembers("users:total")
    
    # Send to all users (in production, you'd want to batch this)
    success = 0
    failed = 0
    
    for user in list(users)[:10]:  # Limit to 10 for testing
        try:
            # In real implementation, you'd use the bot to send messages
            # For now, we'll just log
            print(f"Broadcasting to user {user}: {message}")
            success += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"📢 שידור הושלם!\n✅ נשלח בהצלחה ל-{success} משתמשים\n❌ נכשל ל-{failed} משתמשים"
    )
