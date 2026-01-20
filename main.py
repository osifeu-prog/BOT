import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import init_db, SessionLocal, User

# טעינת משתנים
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WIN_CHANCE = float(os.getenv("WIN_CHANCE_PERCENT", 30)) / 100

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    session = SessionLocal()
    user = session.query(User).filter(User.id == message.from_user.id).first()
    
    if not user:
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        session.commit()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Slot Machine (50 pts)", callback_data="play_slots")],
        [InlineKeyboardButton(text="🎲 Dice Roll (20 pts)", callback_data="play_dice")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="profile"), InlineKeyboardButton(text="🛠 Admin", callback_data="admin_panel")]
    ])
    
    await message.answer(f"ברוך הבא לקזינו! 🎰\nהיתרה שלך: {user.balance} נקודות.", reply_markup=kb)
    session.close()

@dp.callback_query(F.data == "play_slots")
async def play_slots(callback: types.CallbackQuery):
    session = SessionLocal()
    user = session.query(User).filter(User.id == callback.from_user.id).first()
    
    if user.balance < 50:
        return await callback.answer("אין לך מספיק נקודות!", show_alert=True)
    
    user.balance -= 50
    # שליחת אנימציית קזינו מקורית של טלגרם
    msg = await bot.send_dice(callback.message.chat.id, emoji="🎰")
    value = msg.dice.value
    
    # לוגיקת זכייה (במכונת מזל ערכים מסוימים הם זכייה)
    win_values = [1, 22, 43, 64] # דוגמא לערכי זכייה בטלגרם סלוטס
    if value in win_values or random.random() < WIN_CHANCE:
        prize = 250
        user.balance += prize
        await asyncio.sleep(4) # המתנה לסיום האנימציה
        await callback.message.answer(f"🎉 זכית ב-{prize} נקודות!")
    else:
        await asyncio.sleep(4)
        await callback.message.answer("הפסדת... נסה שוב! 💸")
    
    session.commit()
    session.close()

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("גישה נחסמה.", show_alert=True)
    
    await callback.message.answer("שלום אדמין, כאן תוכל לנהל את המשתמשים ולשנות סיכויי זכייה.")

async def main():
    init_db()
    # Webhook setup for Railway
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
