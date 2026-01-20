import redis
import json
from datetime import datetime
from config import REDIS_URL

class DatabaseManager:
    def __init__(self):
        self.r = redis.from_url(REDIS_URL, decode_responses=True)
    
    def register_user(self, user_id, username, first_name):
        """Register a new user or update existing"""
        user_key = f"user:{user_id}:profile"
        
        if not self.r.exists(user_key):
            # New user
            user_data = {
                "id": user_id,
                "username": username or "",
                "first_name": first_name or "",
                "balance": 1000,  # Starting balance
                "tier": "Free",
                "joined": datetime.now().isoformat(),
                "referrer": None
            }
            
            # Check if referred
            if self.r.exists(f"ref_pending:{user_id}"):
                referrer = self.r.get(f"ref_pending:{user_id}")
                if referrer:
                    user_data["referrer"] = referrer
                    # Add to referrer's referrals
                    self.r.sadd(f"user:{referrer}:referrals", user_id)
                    # Give referral reward
                    from config import REFERRAL_REWARD
                    self.r.hincrby(f"user:{referrer}:profile", "balance", REFERRAL_REWARD)
                    # Log transaction
                    self.log_transaction(int(referrer), REFERRAL_REWARD, "Referral reward")
                self.r.delete(f"ref_pending:{user_id}")
            
            # Save user
            self.r.hset(user_key, mapping=user_data)
            # Add to total users set
            self.r.sadd("users:total", user_id)
            
            # Log
            self.log_transaction(user_id, 1000, "Initial balance")
            
            return True
        return False
    
    def get_user(self, user_id):
        """Get user data"""
        user_key = f"user:{user_id}:profile"
        user_data = self.r.hgetall(user_key)
        return user_data
    
    def set_tier(self, user_id, tier):
        """Update user tier"""
        user_key = f"user:{user_id}:profile"
        self.r.hset(user_key, "tier", tier)
        self.log_transaction(user_id, 0, f"Upgraded to {tier} tier")
    
    def log_transaction(self, user_id, amount, description):
        """Log a transaction"""
        tx_key = f"user:{user_id}:transactions"
        tx_data = {
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.r.lpush(tx_key, json.dumps(tx_data))
        # Keep only last 100 transactions
        self.r.ltrim(tx_key, 0, 99)
    
    def get_total_users(self):
        """Get total number of users"""
        return self.r.scard("users:total")
    
    def get_recent_users(self, days=7):
        """Get users who joined in the last N days"""
        # This is a simplified version
        # In production, you'd want to store join dates properly
        return self.r.scard("users:total")

db = DatabaseManager()
