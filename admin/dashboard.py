import matplotlib.pyplot as plt
from io import BytesIO
import os
from app.database.manager import db

async def send_admin_report(update, context):
    if str(update.effective_user.id) != os.getenv("ADMIN_ID"):
        return
    total_users = db.r.scard("users_list")
    plt.figure(figsize=(6, 4))
    plt.bar(['Total Users'], [total_users], color='#00ffcc')
    plt.title("NFTY PRO - Overview")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption=f"📊 סה\"כ משתמשים: {total_users}")

async def broadcast(update, context):
    if str(update.effective_user.id) != os.getenv("ADMIN_ID"):
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("שימוש: /broadcast [הודעה]")
        return
    users = db.r.smembers("users_list")
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 **הודעה מהנהלת המערכת:**\n\n{msg}", parse_mode='Markdown')
            count += 1
        except: continue
    await update.message.reply_text(f"✅ נשלח ל-{count} משתמשים.")