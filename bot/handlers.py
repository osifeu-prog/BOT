"""Bot command handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
import hashlib
from .database import AsyncSessionLocal, User, Bet, Investment, Transaction
from .config import config
from .games import SlotsGame, DiceGame

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user.id))
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            code = hashlib.md5(f"{user.id}".encode()).hexdigest()[:8]
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                referral_code=code
            )
            session.add(db_user)
            await session.commit()
    
    keyboard = [
        [InlineKeyboardButton("🎰 Casino", callback_data='casino'),
         InlineKeyboardButton("💰 Invest", callback_data='invest')],
        [InlineKeyboardButton("💰 Balance", callback_data='balance')]
    ]
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n💰 Balance: ${db_user.balance:.2f}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/casino /invest /balance /referral")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        user = result.scalar_one()
    await update.message.reply_text(f"💰 Balance: ${user.balance:.2f}")

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇮🇱 עברית", callback_data='lang_he')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')]
    ]
    await update.message.reply_text("Choose:", reply_markup=InlineKeyboardMarkup(keyboard))

async def casino_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎰 Slots", callback_data='play_slots')],
        [InlineKeyboardButton("🎲 Dice", callback_data='play_dice')]
    ]
    await update.message.reply_text("🎰 Casino", reply_markup=InlineKeyboardMarkup(keyboard))

async def investment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🥉 Bronze (1%)", callback_data='invest_bronze')],
        [InlineKeyboardButton("🥇 Gold (1.5%)", callback_data='invest_gold')],
        [InlineKeyboardButton("🐋 Whale (2%)", callback_data='invest_whale')]
    ]
    await update.message.reply_text("💰 Invest", reply_markup=InlineKeyboardMarkup(keyboard))

async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍️ Shop (Coming soon)")

async def referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        user = result.scalar_one()
    link = f"https://t.me/{context.bot.username}?start={user.referral_code}"
    await update.message.reply_text(f"👥 Link:\n{link}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("⛔ No access")
        return
    await update.message.reply_text("👨‍💼 Admin Panel")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'play_slots':
        game = SlotsGame(config.WIN_CHANCE_PERCENT)
        win, result, mult = game.play()
        await query.message.edit_text(f"{result}\n{'WIN!' if win else 'Loss'}")
    elif query.data == 'play_dice':
        game = DiceGame(config.WIN_CHANCE_PERCENT)
        win, roll = game.play()
        await query.message.edit_text(f"🎲 {roll}\n{'WIN!' if win else 'Loss'}")
