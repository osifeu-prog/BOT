"""
???? Redis ????
"""
import redis
import json
from datetime import datetime
from config import REDIS_URL

class DatabaseManager:
    def __init__(self):
        self.r = redis.from_url(REDIS_URL, decode_responses=True)
    
    def get_user(self, user_id):
        """??? ????? ?????"""
        user_data = self.r.hgetall(f"user:{user_id}")
        if user_data:
            user_data["balance"] = int(user_data.get("balance", 0))
        return user_data
    
    def update_balance(self, user_id, amount, reason=""):
        """???? ???? ?????"""
        current = int(self.r.hget(f"user:{user_id}", "balance") or 0)
        new_balance = current + amount
        self.r.hset(f"user:{user_id}", "balance", new_balance)
        
        # ???? ????
        if reason:
            tx_key = f"tx:{user_id}:{datetime.now().timestamp()}"
            self.r.hset(tx_key, mapping={
                "user_id": user_id,
                "amount": amount,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        
        return new_balance
    
    def get_total_users(self):
        """???? ??????? ??????"""
        return len(self.r.keys("user:*"))

db = DatabaseManager()
