from app.database.manager import db
import os

async def gift_balance(update, context):
    if str(update.effective_user.id) != os.getenv("ADMIN_ID"):
        return
    
    try:
        # שימוש: /gift [user_id] [amount]
        target_id = context.args[0]
        amount = int(context.args[1])
        
        db.r.hincrby(f"user:{target_id}:profile", "balance", amount)
        db.log_transaction(target_id, amount, "Admin Gift")
        
        await update.message.reply_text(f"🎁 הוענקו {amount} מטבעות למשתמש {target_id}")
        await context.bot.send_message(chat_id=target_id, text=f"🎉 הפתעה! קיבלת מתנה מההנהלה: {amount} מטבעות!")
    except:
        await update.message.reply_text("❌ שימוש שגוי. פורמט: /gift [ID] [כמות]")
