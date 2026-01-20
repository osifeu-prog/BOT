import Redis from 'ioredis';
import { config } from '../config/config';

let redisClient: Redis;

export async function initRedis() {
  try {
    redisClient = new Redis(config.redisUrl, {
      maxRetriesPerRequest: 3,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
    });

    redisClient.on('connect', () => {
      console.log('✅ Redis connected successfully');
    });

    redisClient.on('error', (err) => {
      console.error('❌ Redis connection error:', err);
    });

    return redisClient;
  } catch (error) {
    console.error('Failed to initialize Redis:', error);
    process.exit(1);
  }
}

export function getRedisClient() {
  if (!redisClient) {
    throw new Error('Redis client not initialized. Call initRedis() first.');
  }
  return redisClient;
}

// Helper functions for common operations
export const redis = {
  async set(key: string, value: any, ttl?: number) {
    const serialized = JSON.stringify(value);
    if (ttl) {
      await redisClient.setex(key, ttl, serialized);
    } else {
      await redisClient.set(key, serialized);
    }
  },

  async get<T>(key: string): Promise<T | null> {
    const value = await redisClient.get(key);
    return value ? JSON.parse(value) : null;
  },

  async del(key: string) {
    await redisClient.del(key);
  },

  async incr(key: string) {
    return await redisClient.incr(key);
  },

  async decr(key: string) {
    return await redisClient.decr(key);
  },

  async hset(key: string, field: string, value: any) {
    const serialized = JSON.stringify(value);
    await redisClient.hset(key, field, serialized);
  },

  async hget<T>(key: string, field: string): Promise<T | null> {
    const value = await redisClient.hget(key, field);
    return value ? JSON.parse(value) : null;
  },

  async expire(key: string, seconds: number) {
    await redisClient.expire(key, seconds);
  },
};
