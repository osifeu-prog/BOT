import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.slots import run_slots_logic, get_leaderboard
from utils.edu_log import edu_step

async def play_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מפעיל את המשחק עם אנימציה."""
    query = update.callback_query
    user = query.from_user if query else update.effective_user
    
    if query:
        await query.answer()
        message = query.message
    else:
        message = await update.message.reply_text("🎰 מכין את המכונה...")

    game = run_slots_logic(user.id)
    
    for frame in game["frames"][:-1]:
        try:
            await message.edit_text(f"🎰 **קזינו LIVE** 🎰\n\n{frame}\n\nמסתובב...")
            await asyncio.sleep(0.5)
        except Exception: break

    result_text = f"🎰 **קזינו LIVE** 🎰\n\n{game['frames'][-1]}\n\n"
    result_text += f"🎉 זכית ב-{game['payout']}!" if game["won"] else "🍀 אולי בפעם הבאה..."
    
    keyboard = [[InlineKeyboardButton("🔄 שוב!", callback_data="play_slots")]]
    await message.edit_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_leaderboard(5)
    text = "🏆 **טבלת המנצחים** 🏆\n\n"
    for i, row in enumerate(rows, 1):
        text += f"{i}. משתמש {row[0]}: {row[2]} מטבעות\n"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")
