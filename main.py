
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, ADMIN_ID
from db import init_db, SessionLocal, User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    tg_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=tg_id).first()
    if not user:
        user = User(telegram_id=tg_id, name=update.effective_user.first_name)
        session.add(user)
        session.commit()
    if user.approved:
        await update.message.reply_text("ברוך הבא! יש לך גישה לתוכן ✅")
    else:
        await update.message.reply_text("תודה! הבקשה נשלחה לאישור אדמין ⏳")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    session = SessionLocal()
    if not context.args:
        await update.message.reply_text("ספק ID משתמש")
        return
    tg_id = int(context.args[0])
    user = session.query(User).filter_by(telegram_id=tg_id).first()
    if user:
        user.approved = True
        session.commit()
        await update.message.reply_text("אושר ✅")
    else:
        await update.message.reply_text("משתמש לא נמצא")

def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.run_polling()

if __name__ == "__main__":
    main()
