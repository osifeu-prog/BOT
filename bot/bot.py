
import os, requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

API = os.getenv("BACKEND_URL")
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    requests.post(f"{API}/user/register", params={"telegram_id": msg.from_user.id})
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🎰 Slots", callback_data="slots")
    )
    await msg.answer("🎮 ברוך הבא ל-FreePlay!", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "slots")
async def play(call: types.CallbackQuery):
    r = requests.post(f"{API}/game/slots", json={"telegram_id": call.from_user.id})
    if r.status_code != 200:
        await call.message.answer("⏳ חכה קצת בין משחקים")
        return
    data = r.json()
    await call.message.answer(
        f"{' '.join(data['result'])}\nנקודות: {data['user']['points']} | XP: {data['user']['xp']}"
    )

if __name__ == "__main__":
    executor.start_polling(dp)
