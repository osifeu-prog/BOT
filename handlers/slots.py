import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.slots import run_slots_logic, get_leaderboard
from utils.edu_log import edu_step

async def play_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    מבצע את המשחק עם אנימציית Edit Message.
    """
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        message = query.message
    else:
        user_id = update.effective_user.id
        message = await update.message.reply_text("🎰 מתחילים לסובב...")

    edu_step(1, f"User {user_id} spinning slots")

    # הרצת לוגיקה
    game = run_slots_logic(user_id)
    
    # --- שלב האנימציה ---
    for frame in game["frames"][:-1]:
        await message.edit_text(f"🎰 **סלוטס קזינו** 🎰\n\n{frame}\n\nמהמרים...")
        await asyncio.sleep(0.4) # מהירות הסיבוב

    # --- תוצאה סופית ---
    result_text = f"🎰 **סלוטס קזינו** 🎰\n\n{game['frames'][-1]}\n\n"
    
    if game["won"]:
        result_text += f"🎉 **וואו! זכית ב-{game['payout']} נקודות!** 🎉"
    else:
        result_text += "🍀 הפעם לא זכית... נסה שוב!"

    keyboard = [[InlineKeyboardButton("🎰 סיבוב נוסף!", callback_data="play_slots")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.edit_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מציג את טבלת המובילים."""
    edu_step(1, "Showing slots leaderboard")
    rows = get_leaderboard(5)
    
    text = "🏆 **מובילי הקזינו (לפי רווחים)** 🏆\n\n"
    for i, row in enumerate(rows, 1):
        text += f"{i}. משתמש {row[0]}: {row[2]} נקודות ({row[1]} משחקים)\n"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")
