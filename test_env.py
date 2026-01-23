import os
from utils.config import *

def check():
    print("--- Railway Environment Check ---")
    print(f"Token Loaded: {'Yes' if TELEGRAM_TOKEN else 'No'}")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Referral Reward: {os.environ.get('REFERRAL_REWARD', 'Not Set')}")
    print("---------------------------------")

if __name__ == '__main__':
    check()
