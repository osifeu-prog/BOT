import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from sqlalchemy import create_engine, Column, BigInteger, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- משיכת משתנים מ-Railway ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./casino.db")
ADMIN_ID = os.getenv("ADMIN_ID")

# --- הגדרת מסד נתונים ---
# אם ה-URL מתחיל ב-postgres, נתקן אותו עבור SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String)
    balance = Column(Float, default=1000.0)

# --- הגדרת בוט ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    session = SessionLocal()
    user = session.query(User).filter(User.id == message.from_user.id).first()
    if not user:
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        session.commit()
    
    await message.answer(f"ברוך הבא! היתרה שלך: {user.balance} 💰")
    session.close()

async def main():
    Base.metadata.create_all(engine)
    print("Bot is starting on Railway...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
