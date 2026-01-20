import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from app.database.manager import db
from app.bot.welcome import start
from app.core.shop import open_shop
from app.core.affiliate import show_affiliate_panel
from app.games.mines import start_mines, handle_mine_click
from admin.dashboard import send_admin_report, broadcast
from admin.tools import gift_balance
from app.security import rate_limiter

async def daily_bonus(update, context):
    query = update.callback_query
    uid = query.from_user.id
    if db.r.set(f"daily:{uid}", "1", ex=86400, nx=True):
        db.r.hincrby(f"user:{uid}:profile", "balance", 100)
        await query.answer("🎁 קיבלת 100 מטבעות בונוס יומי!", show_alert=True)
    else:
        await query.answer("⏳ כבר אספת את הבונוס היום!", show_alert=True)

async def main_handler(update, context):
    query = update.callback_query
    uid = query.from_user.id

    # Rate limiting check
    if not rate_limiter.check_rate_limit(uid):
        await query.answer("⏳ יותר מדי בקשות, נסה שוב בעוד דקה!", show_alert=True)
        return

    data = query.data
    await query.answer()

    if data == "start": 
        await start(update, context)
    elif data == "open_shop": 
        await open_shop(update, context)
    elif data == "daily_bonus": 
        await daily_bonus(update, context)
    elif data == "affiliate_panel": 
        await show_affiliate_panel(update, context)
    elif data == "play_mines": 
        await start_mines(update, context)
    elif data == "admin_report": 
        await send_admin_report(update, context)
    elif data.startswith("m_"): 
        await handle_mine_click(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gift", gift_balance))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(main_handler))
    print("🚀 NFTY ULTRA IS LIVE!")
    app.run_polling()
