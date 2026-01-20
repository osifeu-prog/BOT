"""
🎰 NFTY ULTRA PRO - Configuration File
קובץ הגדרות מרכזי עם וולידציה ואימות
"""

import os
import sys
from dotenv import load_dotenv
from typing import List, Dict, Any

# טען משתני סביבה
load_dotenv()

def validate_token(token: str) -> bool:
    """Validate Telegram bot token format"""
    if not token:
        return False
    # טוקן של טלגרם בדרך כלל באורך 46 תווים ומכיל ':'
    if len(token) < 30 or ':' not in token:
        return False
    return True

def get_required_env(var_name: str, default: str = None) -> str:
    """קבל משתנה סביבה חובה, אם חסר - שגיאה"""
    value = os.getenv(var_name, default)
    if value is None:
        print(f"❌ ERROR: Missing required environment variable: {var_name}")
        print(f"💡 Please add {var_name} to your .env file or Railway variables")
        sys.exit(1)
    return value

def get_optional_env(var_name: str, default: Any = None) -> Any:
    """קבל משתנה סביבה אופציונלי"""
    value = os.getenv(var_name)
    if value is None:
        return default
    
    # המרה אוטומטית לסוגים נפוצים
    if isinstance(default, bool):
        return value.lower() in ('true', '1', 'yes', 'y')
    elif isinstance(default, int):
        try:
            return int(value)
        except:
            return default
    elif isinstance(default, float):
        try:
            return float(value)
        except:
            return default
    elif isinstance(default, list):
        if value.strip() == "":
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    return value

# ============ REQUIRED VARIABLES ============
TELEGRAM_TOKEN = get_required_env("TELEGRAM_TOKEN")

# וולידציה של הטוקן
if not validate_token(TELEGRAM_TOKEN):
    print("❌ ERROR: Invalid Telegram token format!")
    print("💡 Please check your TELEGRAM_TOKEN in .env file")
    sys.exit(1)

# ============ ADMIN CONFIGURATION ============
ADMIN_IDS = get_optional_env("ADMIN_IDS", [])
if isinstance(ADMIN_IDS, str):
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS.split(',') if id.strip().isdigit()]

ADMIN_USERNAME = get_optional_env("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = get_optional_env("ADMIN_PASSWORD", "admin123")

# ============ BOT CONFIGURATION ============
BOT_USERNAME = get_optional_env("BOT_USERNAME", "")
BOT_NAME = get_optional_env("BOT_NAME", "NFTY ULTRA CASINO")
BOT_VERSION = get_optional_env("BOT_VERSION", "2.0.0")

# ============ DATABASE CONFIGURATION ============
REDIS_URL = get_required_env("REDIS_URL", "redis://localhost:6379")

# ============ GAME CONFIGURATION ============
WIN_CHANCE_PERCENT = get_optional_env("WIN_CHANCE_PERCENT", 80)
PEEK_COST = get_optional_env("PEEK_COST", 100)
REFERRAL_REWARD = get_optional_env("REFERRAL_REWARD", 500)
MIN_BET = get_optional_env("MIN_BET", 10)
MAX_BET = get_optional_env("MAX_BET", 10000)
DAILY_BONUS = get_optional_env("DAILY_BONUS", 100)
WELCOME_BONUS = get_optional_env("WELCOME_BONUS", 50)

# ============ PAYMENT CONFIGURATION ============
CRYPTO_PAY_TOKEN = get_optional_env("CRYPTO_PAY_TOKEN", "")
TON_WALLET = get_optional_env("TON_WALLET", "")
TOKEN_PACKS = get_optional_env("TOKEN_PACKS", "100:10,500:40,1000:70,5000:300,10000:500")

# Parse token packs
def parse_token_packs(packs_str: str) -> List[Dict[str, int]]:
    """Parse token packs from string format"""
    packs = []
    for pack in packs_str.split(','):
        if ':' in pack:
            tokens, price = pack.split(':')
            try:
                packs.append({
                    'tokens': int(tokens.strip()),
                    'price': int(price.strip())
                })
            except:
                continue
    return packs

TOKEN_PACKS_PARSED = parse_token_packs(TOKEN_PACKS)

# ============ GROUP LINKS ============
PARTICIPANTS_GROUP_LINK = get_optional_env("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = get_optional_env("TEST_GROUP_LINK", "")
SUPPORT_GROUP_LINK = get_optional_env("SUPPORT_GROUP_LINK", "")

# ============ FEATURE FLAGS ============
DEBUG_MODE = get_optional_env("DEBUG_MODE", False)
MAINTENANCE_MODE = get_optional_env("MAINTENANCE_MODE", False)
ENABLE_ANIMATIONS = get_optional_env("ENABLE_ANIMATIONS", True)
ENABLE_SOUND_EFFECTS = get_optional_env("ENABLE_SOUND_EFFECTS", False)
ENABLE_LEADERBOARD = get_optional_env("ENABLE_LEADERBOARD", True)
ENABLE_DAILY_TASKS = get_optional_env("ENABLE_DAILY_TASKS", True)

# ============ AI/ML CONFIGURATION ============
OPENAI_API_KEY = get_optional_env("OPENAI_API_KEY", "")
ENABLE_AI_ASSISTANT = get_optional_env("ENABLE_AI_ASSISTANT", False)

# ============ WEBHOOK CONFIGURATION ============
WEBHOOK_URL = get_optional_env("WEBHOOK_URL", "")
WEBHOOK_PORT = get_optional_env("PORT", 8080)

# ============ LOGGING CONFIGURATION ============
LOG_LEVEL = get_optional_env("LOG_LEVEL", "INFO")
LOG_FILE = get_optional_env("LOG_FILE", "bot.log")

# ============ VALIDATION ============
def validate_config():
    """Validate all configuration settings"""
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN is required")
    
    if not REDIS_URL:
        errors.append("REDIS_URL is required")
    
    if not ADMIN_IDS:
        print("⚠️  WARNING: No ADMIN_IDS specified. Admin features will be disabled.")
    
    if WIN_CHANCE_PERCENT < 1 or WIN_CHANCE_PERCENT > 100:
        errors.append("WIN_CHANCE_PERCENT must be between 1 and 100")
    
    if MIN_BET < 1:
        errors.append("MIN_BET must be at least 1")
    
    if MAX_BET < MIN_BET:
        errors.append("MAX_BET must be greater than MIN_BET")
    
    if REFERRAL_REWARD < 0:
        errors.append("REFERRAL_REWARD cannot be negative")
    
    if not TOKEN_PACKS_PARSED:
        errors.append("TOKEN_PACKS must contain at least one valid pack")
    
    return errors

# הרץ וולידציה
if __name__ == "__main__":
    print("🔧 NFTY ULTRA PRO - Configuration Validation")
    print("=" * 50)
    
    validation_errors = validate_config()
    
    if validation_errors:
        print("❌ Configuration errors found:")
        for error in validation_errors:
            print(f"   - {error}")
        sys.exit(1)
    
    print("✅ Configuration is valid!")
    print(f"🤖 Bot: {BOT_NAME} v{BOT_VERSION}")
    print(f"🔑 Token: {'✅ Set' if TELEGRAM_TOKEN else '❌ Missing'}")
    print(f"📊 Admin IDs: {len(ADMIN_IDS)}")
    print(f"💰 Token Packs: {len(TOKEN_PACKS_PARSED)}")
    print(f"🎮 Features: Animations={ENABLE_ANIMATIONS}, AI={ENABLE_AI_ASSISTANT}")
    print("=" * 50)
