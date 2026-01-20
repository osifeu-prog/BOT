import os
from sqlalchemy import create_engine, Column, Integer, String, Float, BigInteger, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)  # Telegram ID
    username = Column(String, nullable=True)
    balance = Column(Float, default=1000.0)
    is_admin = Column(Boolean, default=False)
    
    # CRM & Referrals
    referred_by = Column(BigInteger, nullable=True)
    referral_count = Column(Integer, default=0)
    total_deposited = Column(Float, default=0.0)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    vip_status = Column(Boolean, default=False)

# הגדרת החיבור ל-Postgres של Railway
engine = create_engine(os.getenv("DATABASE_URL").replace("postgres://", "postgresql://"))
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
