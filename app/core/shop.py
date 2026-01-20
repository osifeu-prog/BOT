from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def open_shop(update, context):
    text = "🛒 **חנות השדרוגים של NFTY**\n\nבחר חבילה לשדרוג סיכויי הזכייה:"
    kb = [
        [InlineKeyboardButton("🥈 PRO (10% Boost) - 50$", callback_data="buy_pro")],
        [InlineKeyboardButton("🥇 VIP (30% Boost + No Mines) - 150$", callback_data="buy_vip")],
        [InlineKeyboardButton("⬅️ חזור", callback_data="start")]
    ]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
