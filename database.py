import redis
import os
import time
import json

REDIS_URL = os.getenv("REDIS_URL")
r = redis.from_url(REDIS_URL, decode_responses=True)

def get_user_profile(uid):
    key = f"user:{uid}:profile"
    profile = r.hgetall(key)
    if not profile:
        profile = {
            "id": str(uid),
            "balance": "1000",
            "xp": "0",
            "stocks": "0",
            "tier": "Regular",
            "last_active": str(int(time.time())),
            "join_date": str(int(time.time())),
            "total_bets": "0",
            "wins": "0",
            "total_deposited": "0"
        }
        r.hset(key, mapping=profile)
        r.sadd("users_list", uid)
    return profile

def update_user_stat(uid, field, amount):
    key = f"user:{uid}:profile"
    r.hset(key, "last_active", str(int(time.time())))
    # שימוש ב-hincrby מבטיח פעולה אטומית (מונע באגים של כפל חיובים)
    return r.hincrby(key, field, int(amount))

def save_game_state(uid, game_type, data):
    """שמירת מצב משחק בצורה מאובטחת כ-JSON"""
    r.set(f"game:{game_type}:{uid}", json.dumps(data), ex=600)

def get_game_state(uid, game_type):
    """שליפת מצב משחק ופענוח JSON"""
    data = r.get(f"game:{game_type}:{uid}")
    return json.loads(data) if data else None
