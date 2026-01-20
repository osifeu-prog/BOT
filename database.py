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
    return r.hincrby(key, field, amount)

def get_market_price():
    users = r.smembers("users_list")
    total_circulating = 0
    for u in users:
        total_circulating += int(r.hget(f"user:{u}:profile", "balance") or 0)
    price = 10 + (total_circulating // 10000)
    return max(10, price)
