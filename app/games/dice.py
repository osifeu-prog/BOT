import random
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from app.database.manager import db

# --- Constants & Configuration ---
MIN_BET = 10
MULTIPLIER = 6
BET_OPTIONS = [10, 25, 50, 100, 500]

# --- Helpers ---
def get_balance(uid: int) -> int:
    """Helper to get user balance safely."""
    user = db.get_user(uid)
    return int(user.get("balance", 0))

def build_keyboard(buttons: list, cols: int = 3) -> list:
    """Helper to build dynamic grid keyboards."""
    return [buttons[i:i + cols] for i in range(0, len(buttons), cols)]

# --- Handlers ---

async def start_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    מסך הראשי: המשתמש בוחר סכום להימור.
    """
    query = update.callback_query
    uid = query.from_user.id
    balance = get_balance(uid)

    text = f"""
🎲 **קזינו קוביות: בחר סכום להימור**

💰 **היתרה שלך:** {balance:,} מטבעות
🔢 **מכפיל זכייה:** x{MULTIPLIER}

בחר בכמה מטבעות תרצה להמר:
"""
    
    # יצירת כפתורים דינמית לפי הסכומים המוגדרים
    buttons = [
        InlineKeyboardButton(f"{amt} 💰", callback_data=f"dice_set_bet_{amt}") 
        for amt in BET_OPTIONS if amt <= balance
    ]
    
    # אם למשתמש אין מספיק כסף להימור המינימלי
    if balance < MIN_BET:
        await query.answer("❌ אין לך מספיק מטבעות למשחק!", show_alert=True)
        return

    keyboard = build_keyboard(buttons, cols=3)
    keyboard.append([InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")])

    await query.edit_message_text(
        text=text, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode=ParseMode.MARKDOWN
    )

async def pick_number_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    שלב שני: המשתמש בוחר מספר (1-6) לאחר שבחר סכום.
    """
    query = update.callback_query
    # הפורמט של המידע: dice_set_bet_{amount}
    bet_amount = int(query.data.split("_")[-1])
    
    text = f"""
🎲 **הימור על סך: {bet_amount} מטבעות**

עכשיו, נחש איזה מספר יצא בקוביה (1-6)?
אם תצדק - תזכה ב-**{bet_amount * MULTIPLIER}** מטבעות!
"""

    buttons = [
        InlineKeyboardButton(f"{i} ️⃣", callback_data=f"dice_roll_{bet_amount}_{i}") 
        for i in range(1, 7)
    ]
    
    # כפתורי שליטה נוספים
    control_buttons = [
        InlineKeyboardButton("🎲 בחר עבורי אקראית", callback_data=f"dice_roll_{bet_amount}_random"),
        InlineKeyboardButton("🔙 שנה סכום", callback_data="play_dice")
    ]

    keyboard = build_keyboard(buttons, cols=3)
    keyboard.append(control_buttons)

    await query.edit_message_text(
        text=text, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_dice_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    שלב שלישי: לוגיקת המשחק, אנימציה ועדכון מסד נתונים.
    """
    query = update.callback_query
    uid = query.from_user.id
    
    # Parsing data: dice_roll_{amount}_{picked_number/random}
    _, _, amount_str, pick_str = query.data.split("_")
    bet_amount = int(amount_str)
    
    # 1. בדיקת יתרה אטומית (חשוב למניעת רמאות)
    current_balance = get_balance(uid)
    if current_balance < bet_amount:
        await query.answer("❌ היתרה שלך השתנתה או שאין לך מספיק כסף!", show_alert=True)
        return await start_dice(update, context)

    # 2. בחירת המספר (אם המשתמש בחר "אקראי")
    if pick_str == "random":
        user_choice = random.randint(1, 6)
        choice_text = f"המערכת בחרה עבורך: {user_choice}"
    else:
        user_choice = int(pick_str)
        choice_text = f"המספר שבחרת: {user_choice}"

    # 3. אנימציית מתח (UX Upgrade)
    # אנחנו מורידים את הכסף *לפני* הגלגול כדי "לנעול" את ההימור
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    await query.edit_message_text(
        text=f"🎲 **מגלגל את הקוביות...**\n💎 הימור: {bet_amount}\n🎯 {choice_text}",
        parse_mode=ParseMode.MARKDOWN
    )
    await asyncio.sleep(1.5) # השהייה ליצירת מתח

    # 4. הגרלת התוצאה
    dice_result = random.randint(1, 6)
    is_win = (user_choice == dice_result)
    
    # 5. חישוב תוצאות
    if is_win:
        win_amount = bet_amount * MULTIPLIER
        profit = win_amount - bet_amount
        # החזרת סכום הזכייה (הקרן כבר ירדה, אז מוסיפים את כל הזכייה)
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
        
        db.log_transaction(uid, profit, f"Dice WIN (Bet: {bet_amount}, Num: {user_choice}, Res: {dice_result})")
        
        result_text = f"""
🎰 **יששש! זכייה גדולה!**

🎲 הקוביה הראתה: **{dice_result}**
🎯 הניחוש שלך: **{user_choice}**

💰 **זכית ב-{win_amount} מטבעות!**
"""
    else:
        db.log_transaction(uid, -bet_amount, f"Dice LOSS (Bet: {bet_amount}, Num: {user_choice}, Res: {dice_result})")
        
        result_text = f"""
📉 **לא נורא, אולי בפעם הבאה...**

🎲 הקוביה הראתה: **{dice_result}**
🎯 הניחוש שלך: **{user_choice}**

💸 **הפסדת {bet_amount} מטבעות.**
"""

    # 6. תפריט סיום
    keyboard = [
        [
            InlineKeyboardButton("🔄 שחק שוב (אותו סכום)", callback_data=f"dice_set_bet_{bet_amount}"),
            InlineKeyboardButton("💰 שנה סכום", callback_data="play_dice")
        ],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]

    await query.edit_message_text(
        text=result_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )
