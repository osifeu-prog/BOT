import redis, json, os
from datetime import datetime
from config import REDIS_URL

class CRM:
    def __init__(self):
        self.r = redis.from_url(REDIS_URL, decode_responses=True)
    
    def get_user(self, uid, ref_by=None):
        key = f"user:{uid}:profile"
        user = self.r.hgetall(key)
        if not user:
            user = {
                "id": str(uid),
                "balance": "1000",
                "tier": "Free",  # Free, Pro, VIP
                "referrals": "0",
                "total_bet": "0",
                "joined": datetime.now().isoformat()
            }
            self.r.hset(key, mapping=user)
            self.r.sadd("users_list", uid)
        return user

    def set_tier(self, uid, tier_name):
        # פונקציה למכירת מנוי דרך ה-CRM
        self.r.hset(f"user:{uid}:profile", "tier", tier_name)
        
    def log_transaction(self, uid, amount, tx_type):
        # תיעוד היסטוריה לגרפים עתידיים
        log_entry = json.dumps({"t": datetime.now().isoformat(), "a": amount, "type": tx_type})
        self.r.lpush(f"user:{uid}:history", log_entry)

db = CRM()
