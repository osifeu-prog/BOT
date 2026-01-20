from telegram.ext import MessageHandler, filters

# --- פונקציה לבחירת סכום מותאם אישית ---
async def custom_bet_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # שומרים את המצב של המשתמש ב-context כדי לדעת שהוא כרגע בהקשת סכום
    context.user_data['waiting_for_bet'] = True
    
    await query.edit_message_text(
        text="⌨️ **הקלד את סכום ההימור שלך:**\n(מינימום 10, מקסימום 5,000)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ביטול", callback_data="play_dice")]])
    )

# --- פונקציה שתופסת את ההקלדה של המשתמש ---
async def handle_custom_bet_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_bet'):
        return

    uid = update.message.from_user.id
    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("❌ נא להזין מספר בלבד!")
        return

    amount = int(text)
    balance = int(db.get_user(uid).get("balance", 0))

    if amount < 10:
        await update.message.reply_text("❌ סכום מינימלי הוא 10 מטבעות.")
        return
    if amount > balance:
        await update.message.reply_text(f"❌ אין לך מספיק! היתרה שלך היא: {balance}")
        return

    # ניקוי המצב ומעבר למסך בחירת מספר
    context.user_data['waiting_for_bet'] = False
    
    # יוצרים אובייקט דמוי query כדי להשתמש בפונקציה הקיימת
    # או פשוט קוראים לפונקציה pick_number_screen עם נתונים מוזרקים
    await show_pick_number(update, context, amount)

async def show_pick_number(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int):
    """גרסה מותאמת להצגת בחירת המספר"""
    text = f"🎲 **הימור על: {amount} מטבעות**\nנחש מה יצא בקוביה:"
    buttons = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"dice_run_{amount}_1"),
            InlineKeyboardButton("2️⃣", callback_data=f"dice_run_{amount}_2"),
            InlineKeyboardButton("3️⃣", callback_data=f"dice_run_{amount}_3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"dice_run_{amount}_4"),
            InlineKeyboardButton("5️⃣", callback_data=f"dice_run_{amount}_5"),
            InlineKeyboardButton("6️⃣", callback_data=f"dice_run_{amount}_6"),
        ]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
