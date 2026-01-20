import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍉", "⭐", "7️⃣", "💎"]
TIER_MULTIPLIERS = {"Free": 1, "Pro": 1.5, "VIP": 2}

async def start_slots(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # בדיקת יתרה
    balance = int(user["balance"])
    bet_amount = 50
    
    if balance < bet_amount:
        await query.answer("❌ אין מספיק מטבעות! יתרה מינימלית: 50 🪙", show_alert=True)
        return
    
    # הפחתת הימור
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    # סיבוב המכונה
    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    
    # חישוב זכייה
    tier = user.get("tier", "Free")
    multiplier = TIER_MULTIPLIERS.get(tier, 1)
    
    if reels[0] == reels[1] == reels[2]:
        win_amount = bet_amount * 10 * multiplier
        result_text = f"🎰 **JACKPOT!** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n💰 זכית ב-{win_amount} מטבעות! (x{multiplier} מהדרגה שלך)"
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        win_amount = bet_amount * 2 * multiplier
        result_text = f"🎰 **זכייה חלקית!** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n💰 זכית ב-{win_amount} מטבעות!"
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
    else:
        result_text = f"🎰 **לא זכית הפעם** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n😔 הפסדת {bet_amount} מטבעות"
    
    # יצירת מקלדת
    keyboard = [
        [InlineKeyboardButton("🔄 סובב שוב (50 🪙)", callback_data="spin_slots")],
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=result_text + f"\n\n💎 דרגה: {tier}\n👛 יתרה נוכחית: {int(user['balance']) - bet_amount + (win_amount if 'win_amount' in locals() else 0)} 🪙",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
