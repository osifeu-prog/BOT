import os
import asyncio
import random
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.utils.deep_linking import create_start_link
from models import init_db, SessionLocal, User

# משתני סביבה מה-Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WIN_CHANCE = float(os.getenv("WIN_CHANCE_PERCENT", 30)) / 100
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # הכתובת שקיבלת מרלוויי

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    init_db()
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

# --- לוגיקת פקודת Start ומערכת חברים ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, command: CommandObject):
    session = SessionLocal()
    user = session.query(User).filter(User.id == message.from_user.id).first()
    
    if not user:
        referrer_id = command.args
        user = User(id=message.from_user.id, username=message.from_user.username)
        
        if referrer_id and referrer_id.isdigit() and int(referrer_id) != user.id:
            referrer = session.query(User).filter(User.id == int(referrer_id)).first()
            if referrer:
                user.referred_by = referrer.id
                referrer.balance += float(os.getenv("REFERRAL_REWARD", 100))
                referrer.referral_count += 1
        
        session.add(user)
        session.commit()
    
    ref_link = await create_start_link(bot, str(user.id), encode=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 שחק בסלוטס (50 נק')", callback_data="play_slots")],
        [InlineKeyboardButton(text="💳 הטענת נקודות / VIP", callback_data="deposit")],
        [InlineKeyboardButton(text="👥 מערכת חברים", callback_data="ref_info")]
    ])
    
    await message.answer(f"ברוך הבא לקזינו! 🎰\nהיתרה שלך: {user.balance}\n\nלינק הזמנה: {ref_link}", reply_markup=kb)
    session.close()

# --- משחקים עם אנימציות טלגרם ---
@dp.callback_query(F.data == "play_slots")
async def play_slots(callback: types.CallbackQuery):
    session = SessionLocal()
    user = session.query(User).filter(User.id == callback.from_user.id).first()
    
    if user.balance < 50:
        return await callback.answer("אין לך מספיק נקודות!", show_alert=True)
    
    user.balance -= 50
    msg = await bot.send_dice(callback.message.chat.id, emoji="🎰")
    
    # לוגיקת זכייה משולבת אדמין
    is_winner = random.random() < WIN_CHANCE
    
    await asyncio.sleep(4) # המתנה לסיום האנימציה
    if is_winner:
        user.balance += 200
        await callback.message.answer(f"🎉 זכית! היתרה החדשה: {user.balance}")
    else:
        await callback.message.answer("הפסדת... נסה שוב!")
    
    session.commit()
    session.close()

# --- פאנל ניהול (Admin Only) ---
@dp.message(Command("admin"))
async def admin_dashboard(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    session = SessionLocal()
    total_users = session.query(User).count()
    total_bank = session.query(User).with_entities(User.balance).all()
    
    text = (f"🛠 פאנל ניהול קזינו\n"
            f"סה''כ רשומים: {total_users}\n"
            f"סיכוי זכייה נוכחי: {WIN_CHANCE*100}%\n")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 הודעה לכולם", callback_data="broadcast")],
        [InlineKeyboardButton(text="📈 שינוי סיכוי זכייה", callback_data="config_win")]
    ])
    await message.answer(text, reply_markup=kb)
    session.close()

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
