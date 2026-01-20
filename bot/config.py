"""Configuration management"""
import os

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
    ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    PORT = int(os.getenv('PORT', '8080'))
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CRYPTO_PAY_TOKEN = os.getenv('CRYPTO_PAY_TOKEN', '')
    WIN_CHANCE_PERCENT = int(os.getenv('WIN_CHANCE_PERCENT', '45'))
    REFERRAL_REWARD = float(os.getenv('REFERRAL_REWARD', '0.1'))
    REFERRAL_LEVEL_2 = 0.05
    REFERRAL_LEVEL_3 = 0.02
    
    INVESTMENT_PLANS = {
        'bronze': {'min': 10, 'max': 100, 'daily_roi': 0.01},
        'gold': {'min': 100, 'max': 1000, 'daily_roi': 0.015},
        'whale': {'min': 1000, 'max': 100000, 'daily_roi': 0.02}
    }
    
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN required")
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID required")
        return True

config = Config()
