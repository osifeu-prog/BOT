async def handle_dice_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    מסך 3: שלב ההרצה, האנימציה והתוצאה הסופית.
    """
    query = update.callback_query
    uid = query.from_user.id
    
    # שליפת נתונים מה-Callback: dice_run_{amount}_{pick}
    parts = query.data.split("_")
    bet_amount = int(parts[2])
    user_pick = int(parts[3])
    
    # 1. בדיקת יתרה אחרונה לפני ביצוע (מניעת Race Condition)
    user = db.get_user(uid)
    current_balance = int(user.get("balance", 0))
    
    if current_balance < bet_amount:
        await query.answer("❌ היתרה שלך אינה מספיקה!", show_alert=True)
        return await start_dice(update, context)

    # 2. "נעילת" ההימור - הורדת הכסף מיד
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)

    # 3. אפקט "גלגול" ויזואלי (UX משופר)
    frames = ["🎲", "⏳", "🎲", "🎰"]
    for frame in frames:
        await query.edit_message_text(
            text=f"🎰 **הקוביה מתגלגלת...**\n\n{frame} הימרת על: `{user_pick}`\n💰 סכום: `{bet_amount}`"
        )
        await asyncio.sleep(0.4) # השהייה קלה ליצירת מתח

    # 4. הגרלת תוצאה
    dice_result = random.randint(1, 6)
    is_win = (user_pick == dice_result)
    
    # 5. לוגיקת זכייה/הפסד
    if is_win:
        win_total = bet_amount * MULTIPLIER
        db.r.hincrby(f"user:{uid}:profile", "balance", win_total)
        db.log_transaction(uid, win_total - bet_amount, f"Dice Win {user_pick}=={dice_result}")
        
        result_emoji = "🎉"
        result_title = "נצחון מוחץ!"
        result_msg = f"זכית ב-`{win_total}` מטבעות!"
    else:
        db.log_transaction(uid, -bet_amount, f"Dice Loss {user_pick}!={dice_result}")
        result_emoji = "💔"
        result_title = "אולי בפעם הבאה..."
        result_msg = f"הפסדת `{bet_amount}` מטבעות."

    # 6. הצגת המסך הסופי
    final_text = f"""
{result_emoji} **{result_title}**
➖➖➖➖➖➖➖➖➖➖
🎯 הניחוש שלך: `{user_pick}`
🎲 תוצאת הקוביה: `{dice_result}`

{result_msg}
➖➖➖➖➖➖➖➖➖➖
💰 יתרה מעודכנת: `{int(db.get_user(uid).get("balance", 0)):,}`
"""

    keyboard = [
        [
            InlineKeyboardButton("🔄 שוב באותו סכום", callback_data=f"dice_step2_bet_{bet_amount}"),
            InlineKeyboardButton("💰 שנה סכום", callback_data="play_dice")
        ],
        [InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")]
    ]

    await query.edit_message_text(
        text=final_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )
