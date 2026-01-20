import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from app.database.manager import db

# --- הגדרות עיצוב וקונפיגורציה ---
MULTIPLIER = 6
BET_OPTIONS = [10, 25, 50, 100, 500]

# כותרת מעוצבת למשחק (אפשר להחליף בלינק לתמונה שלך)
GAME_BANNER = "https://cdn-icons-png.flaticon.com/512/282/282463.png" 

async def start_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    מסך 1: לובי המשחק - בחירת סכום הימור.
    העיצוב כולל תמונה ומד היתרה.
    """
    query = update.callback_query
    uid = query.from_user.id
    
    # שליפת יתרה עדכנית
    user = db.get_user(uid)
    balance = int(user.get("balance", 0))

    # עיצוב ההודעה
    caption = f"""
🎰 **קזינו הקוביות** 🎰
➖➖➖➖➖➖➖➖➖➖
💰 **היתרה שלך:** `{balance:,}` מטבעות
📈 **מכפיל זכייה:** x{MULTIPLIER}
➖➖➖➖➖➖➖➖➖➖

🔥 **איך משחקים?**
1️⃣ בוחרים סכום הימור
2️⃣ מנחשים מספר (1-6)
3️⃣ אם הקוביה נופלת על המספר שלך - הזכייה ענקית!

👇 **בחר סכום להתחלה:**
"""
    
    # בניית כפתורים דינמית + אינדיקציה ויזואלית למה שאפשר להרשות לעצמך
    keyboard = []
    row = []
    for amount in BET_OPTIONS:
        if balance >= amount:
            btn_text = f"{amount} 💰"
            callback = f"dice_step2_bet_{amount}"
        else:
            btn_text = f"🔒 {amount}" # נעול
            callback = "dice_no_money"
            
        row.append(InlineKeyboardButton(btn_text, callback_data=callback))
        
        if len(row) == 3: # שבירת שורה כל 3 כפתורים
            keyboard.append(row)
            row = []
    
    if row: keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 חזרה ללובי ראשי", callback_data="start")])

    # שימוש ב-edit_message_media אם רוצים לשנות תמונה, או text אם אין תמונה קודמת
    # כאן נניח שאנחנו עורכים הודעה קיימת. ל-UX מושלם היינו מוחקים ושולחים חדש עם תמונה,
    # אבל כדי לשמור על רצף, נשתמש בטקסט מעוצב היטב.
    
    await query.edit_message_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def pick_number_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    מסך 2: בחירת המספר המנצח.
    """
    query = update.callback_query
    
    if query.data == "dice_no_money":
        await query.answer("❌ אין לך מספיק מטבעות להימור זה!", show_alert=True)
        return

    bet_amount = int(query.data.split("_")[-1])
    
    text = f"""
🎲 **הימור על: {bet_amount} מטבעות**
➖➖➖➖➖➖➖➖➖➖

🤔 **מה המספר המנצח שלך?**
בחר בחוכמה...
"""
    
    # סידור כפתורים בצורת קוביה (2 שורות של 3)
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"dice_run_{bet_amount}_1"),
            InlineKeyboardButton("2️⃣", callback_data=f"dice_run_{bet_amount}_2"),
            InlineKeyboardButton("3️⃣", callback_data=f"dice_run_{bet_amount}_3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"dice_run_{bet_amount}_4"),
            InlineKeyboardButton("5️⃣", callback_data=f"dice_run_{bet_amount}_5"),
            InlineKeyboardButton("6️⃣", callback_data=f"
