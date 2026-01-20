from app.database.manager import db

async def show_affiliate_panel(update, context):
    uid = update.effective_user.id
    user = db.get_user(uid)
    ref_link = f"https://t.me/YOUR_BOT_NAME?start={uid}"
    
    text = (f"👥 **מערכת שותפים (Affiliate)**\n\n"
            f"🔗 הקישור שלך: `{ref_link}`\n"
            f"💰 רווח שנצבר: {int(user['referrals']) * 500} 🪙\n"
            f"📈 סה\"כ חברים שהצטרפו: {user['referrals']}\n\n"
            f"על כל חבר שתביא תקבל בונוס מיידי ליתרה!")
    
    await update.callback_query.edit_message_text(text, parse_mode='Markdown')
