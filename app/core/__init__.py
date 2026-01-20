from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db
from app.core.payments import create_payment

async def open_shop(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    tier = user.get("tier", "Free")
    
    shop_text = f"""
🛒 **חנות NFTY PRO**

💎 **הדרגה הנוכחית שלך:** {tier}

**📦 חבילות זמינות:**

1. **Pro Tier** - $50
   • 3 מוקשים בלבד במשחק Mines
   • 30% יותר סיכוי לזכייה
   • 50% יותר מטבעות מהזמנות

2. **VIP Tier** - $150  
   • 2 מוקשים בלבד במשחק Mines
   • 50% יותר סיכוי לזכייה
   • 100% יותר מטבעות מהזמנות
   • גישה למשחקים אקסקלוסיביים

**💳 אמצעי תשלום:** CryptoBot (USDT/TON)

**👥 מערכת שותפים:** הזמן חברים וקבל 20% מההכנסות שלהם!
"""
    
    keyboard = [
        [InlineKeyboardButton("💎 שדרג ל-Pro ($50)", callback_data="shop_pro")],
        [InlineKeyboardButton("👑 שדרג ל-VIP ($150)", callback_data="shop_vip")],
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=shop_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
