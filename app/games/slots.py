import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_slots(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # Check balance
    balance = int(user.get("balance", 0))
    bet_amount = 50
    
    if balance < bet_amount:
        await query.answer("❌ אין מספיק מטבעות! יתרה מינימלית: 50 🪙", show_alert=True)
        return
    
    # Deduct bet
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    # Spin the slots
    symbols = ["🍒", "🍋", "🍊", "🍉", "⭐", "7️⃣", "💎"]
    reels = [random.choice(symbols) for _ in range(3)]
    
    # Calculate win based on tier
    tier = user.get("tier", "Free")
    tier_multiplier = 1.0
    if tier == "Pro":
        tier_multiplier = 1.5
    elif tier == "VIP":
        tier_multiplier = 2.0
    
    win_amount = 0
    if reels[0] == reels[1] == reels[2]:
        # Jackpot
        win_amount = bet_amount * 10 * tier_multiplier
        result_text = f"🎰 **JACKPOT!** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n💰 זכית ב-{win_amount} מטבעות! (x{tier_multiplier} מהדרגה שלך)"
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        # Partial win
        win_amount = bet_amount * 2 * tier_multiplier
        result_text = f"🎰 **זכייה חלקית!** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n💰 זכית ב-{win_amount} מטבעות!"
    else:
        result_text = f"🎰 **לא זכית הפעם** 🎰\n\n{reels[0]} | {reels[1]} | {reels[2]}\n\n😔 הפסדת {bet_amount} מטבעות"
    
    # Add winnings if any
    if win_amount > 0:
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
        db.log_transaction(uid, win_amount, f"Won slots game (x{tier_multiplier})")
    
    # Update balance for display
    user = db.get_user(uid)
    current_balance = int(user.get("balance", 0))
    
    keyboard = [
        [InlineKeyboardButton("🔄 סובב שוב (50 🪙)", callback_data="play_slots")],
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=result_text + f"\n\n💎 דרגה: {tier}\n👛 יתרה נוכחית: {current_balance} 🪙",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_slots_click(update, context):
    query = update.callback_query
    data = query.data
    
    if data == "play_slots":
        await start_slots(update, context)
