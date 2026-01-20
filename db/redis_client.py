import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def test_redis():
    try:
        redis_client.set("test_key", "redis is working!")
        return redis_client.get("test_key")
    except Exception as e:
        return f"Redis error: {e}"
