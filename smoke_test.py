import sys
try:
    from utils.config import *
    from handlers import wallet_logic
    print("✅ Smoke Test: Modules loaded successfully.")
    print(f"✅ Smoke Test: Admin ID {ADMIN_ID} recognized.")
    print(f"✅ Smoke Test: Referral Reward set to {REFERRAL_REWARD}.")
    print("🚀 All systems ready for Deployment.")
except Exception as e:
    print(f"❌ Smoke Test Failed: {e}")
    sys.exit(1)
