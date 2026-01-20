from telegram import Update
from telegram.ext import ContextTypes
from app.database.manager import db
from config import ADMIN_IDS

async def gift_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gift balance to a user"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ אין לך הרשאות מנהל!")
        return
    
    # Check command format
    if len(context.args) != 2:
        await update.message.reply_text("❌ פורמט שגוי.\nשימוש: /gift <user_id> <amount>")
        return
    
    try:
        target_user = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ קלט לא חוקי. אנא השתמש במספרים בלבד.")
        return
    
    # Check if target user exists
    if not db.r.exists(f"user:{target_user}:profile"):
        await update.message.reply_text(f"❌ משתמש עם ID {target_user} לא נמצא.")
        return
    
    # Gift balance
    db.r.hincrby(f"user:{target_user}:profile", "balance", amount)
    db.log_transaction(target_user, amount, f"Gift from admin {user_id}")
    
    await update.message.reply_text(
        f"✅ היתרה של משתמש {target_user} עודכנה בהצלחה!\n"
        f"💰 נוספו {amount} מטבעות לחשבונו."
    )
