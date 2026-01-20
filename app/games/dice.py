import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_dice(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    game_text = """
🎲 **משחק קוביות**

**חוקים:**
• בחר מספר בין 1-6
• הקוביה תגריל מספר 1-6
• אם ניחשת נכון - זכית x6
• אם טעית - הפסדת

💰 **הימור מינימלי:** 10 מטבעות
"""
    
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data="dice_bet_1"),
            InlineKeyboardButton("2️⃣", callback_data="dice_bet_2"),
            InlineKeyboardButton("3️⃣", callback_data="dice_bet_3")
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data="dice_bet_4"),
            InlineKeyboardButton("5️⃣", callback_data="dice_bet_5"),
            InlineKeyboardButton("6️⃣", callback_data="dice_bet_6")
        ],
        [
            InlineKeyboardButton("🎲 גלגל מספר אקראי", callback_data="dice_random"),
            InlineKeyboardButton("🏠 תפריט", callback_data="start")
        ]
    ]
    
    await query.edit_message_text(text=game_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_dice_bet(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    if query.data == "dice_random":
        chosen_number = random.randint(1, 6)
        await query.answer(f"🎲 המספר שנבחר: {chosen_number}", show_alert=False)
        query.data = f"dice_bet_{chosen_number}"
    
    bet_number = int(query.data.split("_")[2])
    user = db.get_user(uid)
    balance = int(user.get("balance", 0))
    bet_amount = 10
    
    if balance < bet_amount:
        await query.answer("❌ אין מספיק מטבעות!", show_alert=True)
        return
    
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    dice_roll = random.randint(1, 6)
    
    if bet_number == dice_roll:
        win_amount = bet_amount * 6
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
        db.log_transaction(uid, win_amount - bet_amount, f"Dice win (bet: {bet_number}, roll: {dice_roll})")
        
        result_text = f"""
🎲 **גלגול קוביות**

🎯 **ניחוש שלך:** {bet_number}
🎲 **הקוביה הראתה:** {dice_roll}

🎉 **זכית ב-{win_amount} מטבעות!** (x6)
💰 **רווח נקי:** {win_amount - bet_amount} מטבעות
"""
    else:
        db.log_transaction(uid, -bet_amount, f"Dice loss (bet: {bet_number}, roll: {dice_roll})")
        
        result_text = f"""
🎲 **גלגול קוביות**

🎯 **ניחוש שלך:** {bet_number}
🎲 **הקוביה הראתה:** {dice_roll}

😔 **הפסדת {bet_amount} מטבעות.**
💡 **טיפ:** נסה שוב, המספרים משתנים!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 שחק שוב", callback_data="play_dice"),
         InlineKeyboardButton("🏠 תפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(text=result_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
