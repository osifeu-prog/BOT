import os
from sqlalchemy import create_engine, Column, Integer, String, Float, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True) # Telegram ID
    username = Column(String, nullable=True)
    balance = Column(Float, default=1000.0)
    is_admin = Column(Boolean, default=False)
    referred_by = Column(BigInteger, nullable=True)
    total_played = Column(Integer, default=0)

engine = create_engine(os.getenv("DATABASE_URL").replace("postgres://", "postgresql://"))
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
# models.py - הוסף/עדכן את השדות בתוך קלאס User
class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    balance = Column(Float, default=1000.0)
    is_admin = Column(Boolean, default=False)
    
    # מערכת חברים
    referred_by = Column(BigInteger, nullable=True) # ID של מי שהזמין
    referral_count = Column(Integer, default=0) # כמה אנשים הוא הזמין
    
    # כלכלה
    total_deposited = Column(Float, default=0.0)
    vip_status = Column(Boolean, default=False)
