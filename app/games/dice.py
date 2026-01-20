import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from app.database.manager import db

# --- קונפיגורציה ---
MULTIPLIER = 6
MIN_BET = 10
MAX_BET = 5000
BET_OPTIONS = [10, 50, 100, 250, 500]

async def start_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מסך 1: בחירת סכום הימור (כולל אפשרות לסכום מותאם אישית)"""
    query = update.callback_query
    uid = query.from_user.id
    
    # איפוס מצב המתנה להקלדה (למקרה שחזר אחורה)
    context.user_data['waiting_for_dice_bet'] = False
    
    user = db.get_user(uid)
    balance = int(user.get("balance", 0))

    caption = f"""
🎲 **קזינו קוביות**
➖➖➖➖➖➖➖➖➖➖
💰 **היתרה שלך:** `{balance:,}` מטבעות
📈 **מכפיל זכייה:** x{MULTIPLIER}
➖➖➖➖➖➖➖➖➖➖

👇 **בחר סכום הימור מהרשימה או הקלד סכום משלך:**
"""
    
    keyboard = []
    # יצירת כפתורי סכומים קבועים
    row = []
    for amount in BET_OPTIONS:
        status = "💰" if balance >= amount else "🔒"
        row.append(InlineKeyboardButton(f"{status} {amount}", callback_data=f"dice_step2_{amount}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)

    # כפתורי שליטה נוספים
    keyboard.append([InlineKeyboardButton("✍️ סכום אחר (Custom)", callback_data="dice_custom_bet")])
    keyboard.append([InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")])

    await query.edit_message_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def custom_bet_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מעבר למצב המתנה להקלדת סכום"""
    query = update.callback_query
    context.user_data['waiting_for_dice_bet'] = True
    
    await query.edit_message_text(
        text=f"⌨️ **הקלד את סכום ההימור שלך:**\n\n• מינימום: `{MIN_BET}`\n• מקסימום: `{MAX_BET}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ביטול", callback_data="play_dice")]]),
        parse_mode=ParseMode.MARKDOWN
    )

async def pick_number_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, custom_amount: int = None):
    """מסך 2: בחירת המספר המנצח (1-6)"""
    query = update.callback_query
    
    # אם הגענו מכפתור סכום קבוע
    if custom_amount is None:
        amount = int(query.data.split("_")[-1])
    else:
        amount = custom_amount

    text = f"""
🎲 **הימור פעיל: {amount} מטבעות**
➖➖➖➖➖➖➖➖➖➖
🤔 **מה המספר שיעלה בגורל?**
נחש מספר בין 1 ל-6:
"""
    
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"dice_run_{amount}_1"),
            InlineKeyboardButton("2️⃣", callback_data=f"dice_run_{amount}_2"),
            InlineKeyboardButton("3️⃣", callback_data=f"dice_run_{amount}_3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"dice_run_{amount}_4"),
            InlineKeyboardButton("5️⃣", callback_data=f"dice_run_{amount}_5"),
            InlineKeyboardButton("6️⃣", callback_data=f"dice_run_{amount}_6"),
        ],
        [InlineKeyboardButton("🎲 בחירה אקראית", callback_data=f"dice_run_{amount}_rand")],
        [InlineKeyboardButton("🔙 שנה סכום", callback_data="play_dice")]
    ]
    
    if query:
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def handle_dice_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מסך 3: לוגיקה, אנימציה ותוצאה"""
    query = update.callback_query
    uid = query.from_user.id
    
    # פירוק נתונים: dice_run_AMOUNT_PICK
    _, _, amt_str, pick_str = query.data.split("_")
    bet_amount = int(amt_str)
    
    # הגרלת בחירה אקראית אם המשתמש ביקש
    user_pick = random.randint(1, 6) if pick_str == "rand" else int(pick_str)

    # בדיקת יתרה אחרונה
    user = db.get_user(uid)
    if int(user.get("balance", 0)) < bet_amount:
        await query.answer("❌ אין לך מספיק מטבעות!", show_alert=True)
        return await start_dice(update, context)

    # הורדת הכסף מיד (מניעת רמאויות)
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)

    # אנימציית גלגול
    frames = ["🎲", "⏳", "🎲", "🎰"]
    for frame in frames:
        await query.edit_message_text(f"🎰 **מגלגל קוביות...**\n\n{frame} הימור: `{bet_amount}` | ניחוש: `{user_pick}`")
        await asyncio.sleep(0.4)

    # תוצאה
    dice_result = random.randint(1, 6)
    is_win = (user_pick == dice_result)
    
    if is_win:
        win_amt = bet_amount * MULTIPLIER
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amt)
        db.log_transaction(uid, win_amt - bet_amount, f"Dice Win {dice_result}")
        msg = f"🎉 **ניצחון ענק!**\nזכית ב-`{win_amt}` מטבעות!"
    else:
        db.log_transaction(uid, -bet_amount, f"Dice Loss (Result: {dice_result})")
        msg = f"💔 **הפסד...**\nהקוביה הראתה `{dice_result}`."

    final_text = f"""
{msg}
➖➖➖➖➖➖➖➖➖➖
🎯 הניחוש שלך: `{user_pick}`
🎲 תוצאת הקוביה: `{dice_result}`
💰 יתרה חדשה: `{int(db.get_user(uid).get("balance", 0)):,}`
"""

    keyboard = [
        [InlineKeyboardButton("🔄 שוב באותו סכום", callback_data=f"dice_step2_{bet_amount}")],
        [InlineKeyboardButton("💰 סכום אחר", callback_data="play_dice"), 
         InlineKeyboardButton("🏠 תפריט", callback_data="start")]
    ]

    await query.edit_message_text(final_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

# --- פונקציה לטיפול בהודעות טקסט (עבור ה-Custom Bet) ---
async def handle_dice_msg_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מעבד את הודעת הטקסט של המשתמש כשהוא מזין סכום הימור"""
    if not context.user_data.get('waiting_for_dice_bet'):
        return

    uid = update.message.from_user.id
    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("❌ נא להזין מספר שלם בלבד.")
        return

    amount = int(text)
    balance = int(db.get_user(uid).get("balance", 0))

    if amount < MIN_BET or amount > MAX_BET:
        await update.message.reply_text(f"❌ סכום לא חוקי. מינימום {MIN_BET}, מקסימום {MAX_BET}.")
        return
    if amount > balance:
        await update.message.reply_text(f"❌ אין לך מספיק! יתרה: `{balance}`")
        return

    context.user_data['waiting_for_dice_bet'] = False
    await pick_number_screen(update, context, custom_amount=amount)
