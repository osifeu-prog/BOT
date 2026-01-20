import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from app.bot.welcome import start
from app.core.shop import open_shop
from app.core.affiliate import show_affiliate_panel
from app.games.mines import start_mines, handle_mine_click
from app.games.slots import start_slots, handle_slots_click
from app.games.crash import start_crash, handle_crash_click
from admin.dashboard import send_admin_report, broadcast
from admin.tools import gift_balance
from app.security import rate_limiter
from app.utils.logger import logger

async def daily_bonus(update, context):
    query = update.callback_query
    uid = query.from_user.id
    from app.database.manager import db
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
    elif data == "play_slots": 
        await start_slots(update, context)
    elif data == "play_crash": 
        await start_crash(update, context)
    elif data == "admin_report": 
        await send_admin_report(update, context)
    elif data.startswith("m_"): 
        await handle_mine_click(update, context)
    elif data.startswith("slots_"): 
        await handle_slots_click(update, context)
    elif data.startswith("crash_"): 
        await handle_crash_click(update, context)

def main():
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Check if we are on Railway
    port = int(os.environ.get("PORT", 8080))
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", None)
    is_railway = railway_public_domain is not None

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gift", gift_balance))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(main_handler))

    if is_railway:
        # Use webhook on Railway
        logger.info("🚀 Starting bot in Railway (webhook mode)...")
        webhook_url = f"https://{railway_public_domain}/{TELEGRAM_TOKEN}"
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Use polling locally
        logger.info("🚀 Starting bot locally (polling mode)...")
        app.run_polling()

if __name__ == "__main__":
    main()
