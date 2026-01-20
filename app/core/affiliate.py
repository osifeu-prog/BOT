from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db
from config import BOT_USERNAME, REFERRAL_REWARD

async def show_affiliate_panel(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    # Get referral count
    referrals = db.r.scard(f"user:{uid}:referrals") or 0
    
    # Calculate total earned from referrals
    total_earned = referrals * REFERRAL_REWARD
    
    # Generate referral link
    ref_link = f"https://t.me/{BOT_USERNAME.replace('@', '')}?start=ref{uid}"
    
    panel_text = f"""
👥 **פאנל שותפים**

📊 **סטטיסטיקות:**
• 👥 משתמשים שהזמנת: **{referrals}**
• 💰 הרווחת מהזמנות: **{total_earned}** מטבעות
• 🎁 פרס לכל הזמנה: **{REFERRAL_REWARD}** מטבעות

🔗 **קישור ההזמנה שלך:**
`{ref_link}`

**🎯 איך זה עובד:**
1. שלח את הקישור לחברים
2. הם חייבים ללחוץ עליו ולהתחיל עם הבוט
3. אתה מקבל {REFERRAL_REWARD} מטבעות אוטומטית!

**💰 אפשרויות נוספות:**
• קבל 10% מההפסדים של המשתמשים שהזמנת
• קבל 5% מההכנסות שלהם מקניות בחנות
"""
    
    keyboard = [
        [InlineKeyboardButton("📤 שתף קישור", url=f"https://t.me/share/url?url={ref_link}&text=הצטרפו%20למשחק%20המדהים%20שלי!")],
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=panel_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
