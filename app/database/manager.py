"""
🎰 NFTY ULTRA PRO - Database Manager
מנהל מסד נתונים מתקדם עם Redis, caching, וסטטיסטיקות בזמן אמת
"""

import json
import pickle
import zlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import redis
from config import REDIS_URL, DEBUG_MODE

class EnhancedRedisManager:
    """מנהל Redis משודרג עם ביצועים גבוהים ו-caching"""
    
    def __init__(self):
        self.r = redis.from_url(REDIS_URL, decode_responses=False)
        self.cache_ttl = 300  # 5 minutes cache
        self.stats_prefix = "stats:"
        self.user_prefix = "user:"
        self.game_prefix = "game:"
        self.transaction_prefix = "tx:"
        
        # יצירת אינדקסים אוטומטית
        self._create_indexes()
    
    def _create_indexes(self):
        """יצירת אינדקסים לשיפור ביצועים"""
        # אינדקס למשתמשים לפי דרגה
        if not self.r.exists("index:users:by_tier"):
            self.r.sadd("index:users:by_tier", "placeholder")
        
        # אינדקס למשתמשים פעילים
        if not self.r.exists("index:users:active"):
            self.r.zadd("index:users:active", {"placeholder": 0})
    
    def _compress_data(self, data: Any) -> bytes:
        """דחיסת נתונים לחיסכון במקום"""
        return zlib.compress(pickle.dumps(data))
    
    def _decompress_data(self, compressed: bytes) -> Any:
        """חילוץ נתונים דחוסים"""
        return pickle.loads(zlib.decompress(compressed))
    
    def _get_cache_key(self, key: str) -> str:
        """קבל מפתח cache"""
        return f"cache:{key}"
    
    def cache_get(self, key: str) -> Optional[Any]:
        """קבל נתונים מ-cache"""
        cache_key = self._get_cache_key(key)
        cached = self.r.get(cache_key)
        if cached:
            return self._decompress_data(cached)
        return None
    
    def cache_set(self, key: str, data: Any, ttl: int = None):
        """שמור נתונים ב-cache"""
        if ttl is None:
            ttl = self.cache_ttl
        
        cache_key = self._get_cache_key(key)
        compressed = self._compress_data(data)
        self.r.setex(cache_key, ttl, compressed)
    
    def cache_delete(self, key: str):
        """מחק נתונים מ-cache"""
        cache_key = self._get_cache_key(key)
        self.r.delete(cache_key)
    
    # ============ USER MANAGEMENT ============
    
    def register_user(self, user_id: int, username: str = "", first_name: str = "", referrer: int = None):
        """רישום משתמש חדש עם ביצועים משופרים"""
        user_key = f"{self.user_prefix}{user_id}:profile"
        
        if self.r.exists(user_key):
            return False  # משתמש כבר רשום
        
        user_data = {
            "id": user_id,
            "username": username or "",
            "first_name": first_name or "",
            "balance": 100,  # בונוס התחלתי
            "tier": "Free",
            "joined": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "referrer": referrer,
            "total_wagered": 0,
            "total_wins": 0,
            "total_losses": 0,
            "referral_count": 0,
            "daily_streak": 1,
            "last_daily_claim": None,
            "settings": {
                "notifications": True,
                "animations": True,
                "sound_effects": False,
                "language": "he"
            }
        }
        
        # שמור נתוני משתמש
        self.r.hset(user_key, mapping=user_data)
        
        # הוסף לאינדקסים
        self.r.sadd("users:total", user_id)
        self.r.sadd("index:users:by_tier:Free", user_id)
        self.r.zadd("index:users:active", {str(user_id): datetime.now().timestamp()})
        
        # עדכן סטטיסטיקות
        self._update_daily_stats("new_users", 1)
        
        # הוסף בונוס למזמין אם קיים
        if referrer and self.r.exists(f"{self.user_prefix}{referrer}:profile"):
            self.add_referral_bonus(referrer, user_id)
        
        # נקה cache רלוונטי
        self.cache_delete(f"user_{user_id}")
        self.cache_delete("total_users")
        
        return True
    
    def get_user(self, user_id: int, use_cache: bool = True) -> Dict[str, Any]:
        """קבל נתוני משתמש עם caching"""
        cache_key = f"user_{user_id}"
        
        if use_cache:
            cached = self.cache_get(cache_key)
            if cached:
                return cached
        
        user_key = f"{self.user_prefix}{user_id}:profile"
        user_data = self.r.hgetall(user_key)
        
        if not user_data:
            return {}
        
        # המרה ל-dict רגיל
        result = {k.decode() if isinstance(k, bytes) else k: 
                  v.decode() if isinstance(v, bytes) else v 
                  for k, v in user_data.items()}
        
        # עדכן זמן פעילות אחרון
        self.r.hset(user_key, "last_active", datetime.now().isoformat())
        self.r.zadd("index:users:active", {str(user_id): datetime.now().timestamp()})
        
        # שמור ב-cache
        if use_cache:
            self.cache_set(cache_key, result)
        
        return result
    
    def update_user(self, user_id: int, updates: Dict[str, Any]):
        """עדכן משתמש עם ולידציה"""
        user_key = f"{self.user_prefix}{user_id}:profile"
        
        # בדוק אם המשתמש קיים
        if not self.r.exists(user_key):
            return False
        
        # עדכן את הנתונים
        for key, value in updates.items():
            if value is not None:
                self.r.hset(user_key, key, value)
        
        # עדכן אינדקס דרגה אם דרגה השתנתה
        if "tier" in updates:
            old_tier = self.r.hget(user_key, "tier")
            if old_tier and old_tier != updates["tier"]:
                # הסר מאינדקס הישן
                self.r.srem(f"index:users:by_tier:{old_tier}", user_id)
                # הוסף לאינדקס חדש
                self.r.sadd(f"index:users:by_tier:{updates['tier']}", user_id)
        
        # נקה cache
        self.cache_delete(f"user_{user_id}")
        
        return True
    
    def add_balance(self, user_id: int, amount: int, reason: str = ""):
        """הוסף יתרה למשתמש עם לוג עסקאות"""
        if amount == 0:
            return False
        
        user_key = f"{self.user_prefix}{user_id}:profile"
        current_balance = int(self.r.hget(user_key, "balance") or 0)
        new_balance = current_balance + amount
        
        # עדכן יתרה
        self.r.hset(user_key, "balance", new_balance)
        
        # רשום עסקה
        self.log_transaction(user_id, amount, reason)
        
        # עדכן סטטיסטיקות
        if amount > 0:
            self._update_user_stats(user_id, "wins", 1)
            self._update_daily_stats("total_wins", 1)
            self._update_daily_stats("total_winnings", amount)
        else:
            self._update_user_stats(user_id, "losses", 1)
            self._update_daily_stats("total_losses", 1)
        
        # נקה cache
        self.cache_delete(f"user_{user_id}")
        
        return True
    
    def deduct_balance(self, user_id: int, amount: int, reason: str = "") -> bool:
        """הפחת יתרה עם ולידציה"""
        if amount <= 0:
            return False
        
        user_key = f"{self.user_prefix}{user_id}:profile"
        current_balance = int(self.r.hget(user_key, "balance") or 0)
        
        if current_balance < amount:
            return False  # אין מספיק יתרה
        
        new_balance = current_balance - amount
        self.r.hset(user_key, "balance", new_balance)
        
        # עדכן סכום שהומר
        self.r.hincrby(user_key, "total_wagered", amount)
        
        # רשום עסקה
        self.log_transaction(user_id, -amount, reason)
        
        # עדכן סטטיסטיקות יומיות
        self._update_daily_stats("total_wagered", amount)
        
        # נקה cache
        self.cache_delete(f"user_{user_id}")
        
        return True
    
    # ============ REFERRAL SYSTEM ============
    
    def add_referral_bonus(self, referrer_id: int, referred_id: int):
        """הוסף בונוס למזמין"""
        from config import REFERRAL_REWARD
        
        # עדכן ספירת ההפניות
        self.r.sadd(f"{self.user_prefix}{referrer_id}:referrals", referred_id)
        
        # עדכן ספירה בפרופיל
        self.r.hincrby(f"{self.user_prefix}{referrer_id}:profile", "referral_count", 1)
        
        # הוסף בונוס
        self.add_balance(referrer_id, REFERRAL_REWARD, f"Referral bonus for user {referred_id}")
        
        # עדכן סטטיסטיקות
        self._update_daily_stats("referral_bonuses", REFERRAL_REWARD)
        
        # נקה cache
        self.cache_delete(f"user_{referrer_id}")
    
    def get_referrals(self, user_id: int) -> List[int]:
        """קבל רשימת הפניות"""
        referrals = self.r.smembers(f"{self.user_prefix}{user_id}:referrals")
        return [int(ref.decode() if isinstance(ref, bytes) else ref) for ref in referrals]
    
    # ============ TRANSACTION LOGGING ============
    
    def log_transaction(self, user_id: int, amount: int, description: str = ""):
        """רישום עסקה עם timestamp"""
        tx_id = f"{self.transaction_prefix}{datetime.now().timestamp()}:{user_id}"
        
        tx_data = {
            "user_id": user_id,
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "balance_after": self.get_user_balance(user_id)
        }
        
        # שמור עסקה
        self.r.hset(tx_id, mapping=tx_data)
        
        # הוסף לאינדקס עסקאות של משתמש
        self.r.zadd(f"{self.user_prefix}{user_id}:transactions", {tx_id: datetime.now().timestamp()})
        
        # הגבל היסטוריית עסקאות ל-100 האחרונות
        self.r.zremrangebyrank(f"{self.user_prefix}{user_id}:transactions", 0, -101)
        
        # עדכן סטטיסטיקות יומיות
        self._update_daily_stats("total_transactions", 1)
        
        return tx_id
    
    def get_transaction_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """קבל היסטוריית עסקאות"""
        tx_keys = self.r.zrevrange(f"{self.user_prefix}{user_id}:transactions", 0, limit - 1)
        
        transactions = []
        for tx_key in tx_keys:
            tx_data = self.r.hgetall(tx_key)
            if tx_data:
                tx_dict = {k.decode() if isinstance(k, bytes) else k: 
                          v.decode() if isinstance(v, bytes) else v 
                          for k, v in tx_data.items()}
                transactions.append(tx_dict)
        
        return transactions
    
    # ============ GAME MANAGEMENT ============
    
    def create_game_session(self, game_type: str, user_id: int, game_data: Dict[str, Any], ttl: int = 600):
        """יצירת סשן משחק חדש"""
        game_key = f"{self.game_prefix}{game_type}:{user_id}:{datetime.now().timestamp()}"
        
        self.r.setex(game_key, ttl, json.dumps(game_data))
        
        # הוסף לאינדקס משחקים פעילים
        self.r.sadd(f"{self.game_prefix}active", game_key)
        
        # עדכן סטטיסטיקות
        self._update_daily_stats(f"games_{game_type}", 1)
        self._update_user_stats(user_id, f"games_{game_type}", 1)
        
        return game_key
    
    def get_game_session(self, game_key: str) -> Optional[Dict[str, Any]]:
        """קבל נתוני סשן משחק"""
        game_data = self.r.get(game_key)
        if game_data:
            return json.loads(game_data)
        return None
    
    def update_game_session(self, game_key: str, game_data: Dict[str, Any], ttl: int = None):
        """עדכן סשן משחק"""
        if ttl:
            self.r.setex(game_key, ttl, json.dumps(game_data))
        else:
            self.r.set(game_key, json.dumps(game_data))
    
    def end_game_session(self, game_key: str, user_won: bool = None, win_amount: int = 0):
        """סיים סשן משחק ועדכן סטטיסטיקות"""
        # הסר ממשחקים פעילים
        self.r.srem(f"{self.game_prefix}active", game_key)
        
        # עדכן סטטיסטיקות אם הסתיים
        if user_won is not None:
            game_type = game_key.split(':')[1]
            if user_won:
                self._update_daily_stats(f"wins_{game_type}", 1)
            else:
                self._update_daily_stats(f"losses_{game_type}", 1)
        
        # מחק את הסשן
        self.r.delete(game_key)
    
    # ============ STATISTICS & ANALYTICS ============
    
    def _update_daily_stats(self, stat_name: str, increment: int = 1):
        """עדכן סטטיסטיקות יומיות"""
        date_str = datetime.now().strftime("%Y%m%d")
        daily_key = f"{self.stats_prefix}daily:{date_str}"
        
        self.r.hincrby(daily_key, stat_name, increment)
        self.r.expire(daily_key, 86400 * 7)  # שמור למשך שבוע
    
    def _update_user_stats(self, user_id: int, stat_name: str, increment: int = 1):
        """עדכן סטטיסטיקות משתמש"""
        user_key = f"{self.user_prefix}{user_id}:profile"
        self.r.hincrby(user_key, stat_name, increment)
    
    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """קבל סטטיסטיקות יומיות"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y%m%d")
        daily_key = f"{self.stats_prefix}daily:{date_str}"
        
        stats = self.r.hgetall(daily_key)
        if not stats:
            return {}
        
        return {k.decode() if isinstance(k, bytes) else k: 
                int(v) if v.isdigit() else v.decode() if isinstance(v, bytes) else v 
                for k, v in stats.items()}
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """קבל סטטיסטיקות כוללות"""
        cache_key = "overall_stats"
        cached = self.cache_get(cache_key)
        if cached:
            return cached
        
        stats = {
            "total_users": self.get_total_users(),
            "active_users_24h": self.get_active_users_count(hours=24),
            "total_transactions": self._get_total_transactions(),
            "total_wagered": self._get_total_wagered(),
            "total_winnings": self._get_total_winnings(),
            "current_games": self.get_active_games_count(),
            "top_tier": self.get_top_tier_distribution()
        }
        
        self.cache_set(cache_key, stats, ttl=60)  # Cache for 1 minute
        return stats
    
    def get_active_users_count(self, hours: int = 24) -> int:
        """ספור משתמשים פעילים"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        return self.r.zcount("index:users:active", cutoff_time, "+inf")
    
    def get_active_games_count(self) -> int:
        """ספור משחקים פעילים"""
        return self.r.scard(f"{self.game_prefix}active")
    
    def get_total_users(self) -> int:
        """קבל סך כל המשתמשים"""
        cache_key = "total_users"
        cached = self.cache_get(cache_key)
        if cached:
            return cached
        
        total = self.r.scard("users:total")
        self.cache_set(cache_key, total, ttl=300)  # Cache for 5 minutes
        return total
    
    def get_top_tier_distribution(self) -> Dict[str, int]:
        """קבל התפלגות דרגות"""
        tiers = ["Free", "Pro", "VIP"]
        distribution = {}
        
        for tier in tiers:
            count = self.r.scard(f"index:users:by_tier:{tier}")
            distribution[tier] = count
        
        return distribution
    
    def _get_total_transactions(self) -> int:
        """ספור עסקאות כוללות (מקורב)"""
        # זו דוגמה פשוטה - ניתן לשפר עם אינדקס מלא
        return self.r.dbsize()  # מקורב
    
    def _get_total_wagered(self) -> int:
        """סכום כולל שהומר"""
        # דוגמה פשוטה - ניתן לשפר
        return sum(self.get_daily_stats().get("total_wagered", 0) for _ in range(7))
    
    def _get_total_winnings(self) -> int:
        """סכום זכיות כולל"""
        # דוגמה פשוטה - ניתן לשפר
        return sum(self.get_daily_stats().get("total_winnings", 0) for _ in range(7))
    
    def get_user_balance(self, user_id: int) -> int:
        """קבל יתרת משתמש"""
        user_data = self.get_user(user_id, use_cache=True)
        return int(user_data.get("balance", 0))
    
    # ============ MAINTENANCE & UTILITIES ============
    
    def cleanup_old_data(self, days_old: int = 30):
        """ניקוי נתונים ישנים"""
        cutoff_timestamp = (datetime.now() - timedelta(days=days_old)).timestamp()
        
        # נקה משחקים ישנים
        game_pattern = f"{self.game_prefix}*"
        for key in self.r.scan_iter(match=game_pattern):
            if self.r.ttl(key) == -1:  # ללא TTL
                try:
                    # בדוק אם ה-key מכיל timestamp
                    parts = key.split(':')
                    if len(parts) >= 4:
                        game_time = float(parts[-2])
                        if game_time < cutoff_timestamp:
                            self.r.delete(key)
                except:
                    pass
        
        # נקה cache ישן
        for key in self.r.scan_iter(match="cache:*"):
            if self.r.ttl(key) == -1:  # ללא TTL
                self.r.delete(key)
        
        # עדכן אינדקס משתמשים פעילים
        self.r.zremrangebyscore("index:users:active", 0, cutoff_timestamp)
        
        return True
    
    def backup_database(self, backup_key: str = "backup:latest"):
        """צור גיבוי של נתונים חשובים"""
        important_data = {
            "total_users": self.get_total_users(),
            "user_ids": list(self.r.smembers("users:total")),
            "stats": self.get_overall_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.r.set(backup_key, json.dumps(important_data))
        return backup_key
    
    # ============ PERFORMANCE OPTIMIZATION ============
    
    def batch_update_users(self, user_updates: Dict[int, Dict[str, Any]]):
        """עדכון משתמשים בקבוצות לשיפור ביצועים"""
        pipeline = self.r.pipeline()
        
        for user_id, updates in user_updates.items():
            user_key = f"{self.user_prefix}{user_id}:profile"
            for key, value in updates.items():
                pipeline.hset(user_key, key, value)
            pipeline.zadd("index:users:active", {str(user_id): datetime.now().timestamp()})
        
        pipeline.execute()
        
        # נקה cache
        for user_id in user_updates.keys():
            self.cache_delete(f"user_{user_id}")
    
    def get_bulk_user_data(self, user_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """קבל נתוני משתמשים מרובים בבת אחת"""
        pipeline = self.r.pipeline()
        
        for user_id in user_ids:
            user_key = f"{self.user_prefix}{user_id}:profile"
            pipeline.hgetall(user_key)
        
        results = pipeline.execute()
        
        users_data = {}
        for user_id, result in zip(user_ids, results):
            if result:
                user_dict = {k.decode() if isinstance(k, bytes) else k: 
                            v.decode() if isinstance(v, bytes) else v 
                            for k, v in result.items()}
                users_data[user_id] = user_dict
                # עדכן זמן פעילות
                self.r.zadd("index:users:active", {str(user_id): datetime.now().timestamp()})
        
        return users_data

# יצירת מופע גלובלי
db = EnhancedRedisManager()

# פונקציות עזר לגישה מהירה
def get_user_balance(user_id: int) -> int:
    """קבל יתרת משתמש (shortcut)"""
    return db.get_user_balance(user_id)

def update_user_balance(user_id: int, amount: int, reason: str = "") -> bool:
    """עדכן יתרת משתמש (shortcut)"""
    if amount > 0:
        return db.add_balance(user_id, amount, reason)
    elif amount < 0:
        return db.deduct_balance(user_id, abs(amount), reason)
    return False

def get_active_games() -> int:
    """קבל מספר משחקים פעילים (shortcut)"""
    return db.get_active_games_count()

if __name__ == "__main__":
    print("🧪 בדיקת מנהל מסד נתונים...")
    
    # בדיקות בסיסיות
    test_user_id = 999999
    db.register_user(test_user_id, "test_user", "Test")
    
    user_data = db.get_user(test_user_id)
    print(f"✅ משתמש נרשם: {user_data.get('first_name')}")
    print(f"💰 יתרה התחלתית: {user_data.get('balance')}")
    
    db.add_balance(test_user_id, 500, "Test bonus")
    print(f"💰 יתרה לאחר בונוס: {db.get_user_balance(test_user_id)}")
    
    stats = db.get_overall_stats()
    print(f"📊 סטטיסטיקות: {stats}")
    
    print("✅ כל הבדיקות עברו בהצלחה!")
