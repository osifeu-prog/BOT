"""Database models and initialization"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String)
    first_name = Column(String)
    language = Column(String, default='en')
    balance = Column(Float, default=0.0)
    vip_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    referrer_id = Column(Integer, ForeignKey('users.id'))
    referral_code = Column(String, unique=True, index=True)
    total_referral_earnings = Column(Float, default=0.0)
    bets = relationship('Bet', back_populates='user')
    investments = relationship('Investment', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')

class Bet(Base):
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_type = Column(String)
    bet_amount = Column(Float)
    win_amount = Column(Float, default=0.0)
    result = Column(String)
    is_win = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='bets')

class Investment(Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan = Column(String)
    amount = Column(Float)
    daily_roi = Column(Float)
    total_earned = Column(Float, default=0.0)
    status = Column(String, default='active')
    start_date = Column(DateTime, default=datetime.utcnow)
    last_payout = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='investments')

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)
    amount = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='transactions')

db_url = config.DATABASE_URL.replace('postgres://', 'postgresql://')
if not db_url.startswith('sqlite'):
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
