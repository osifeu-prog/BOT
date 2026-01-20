const redis = require('redis');

class RedisClient {
    constructor() {
        this.client = null;
        this.isConnected = false;
    }
    
    async connect() {
        if (this.isConnected) return;
        
        const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
        
        this.client = redis.createClient({
            url: redisUrl,
            socket: {
                reconnectStrategy: (retries) => {
                    if (retries > 10) {
                        console.log('❌ יותר מדי נסיונות חיבור ל-Redis');
                        return new Error('Too many retries');
                    }
                    return Math.min(retries * 100, 3000);
                }
            }
        });
        
        this.client.on('error', (err) => {
            console.error('Redis Client Error:', err);
            this.isConnected = false;
        });
        
        this.client.on('connect', () => {
            console.log('✅ Redis: מחובר');
            this.isConnected = true;
        });
        
        this.client.on('reconnecting', () => {
            console.log('🔄 Redis: מנסה להתחבר מחדש...');
        });
        
        await this.client.connect();
        return this.client;
    }
    
    async get(key) {
        if (!this.isConnected) await this.connect();
        return await this.client.get(key);
    }
    
    async set(key, value, ttl = null) {
        if (!this.isConnected) await this.connect();
        
        if (ttl) {
            await this.client.setEx(key, ttl, value);
        } else {
            await this.client.set(key, value);
        }
    }
    
    async hSet(key, field, value) {
        if (!this.isConnected) await this.connect();
        await this.client.hSet(key, field, value);
    }
    
    async hGetAll(key) {
        if (!this.isConnected) await this.connect();
        return await this.client.hGetAll(key);
    }
    
    async zAdd(key, score, member) {
        if (!this.isConnected) await this.connect();
        await this.client.zAdd(key, { score, value: member });
    }
    
    async zRangeWithScores(key, start, stop, options = {}) {
        if (!this.isConnected) await this.connect();
        return await this.client.zRangeWithScores(key, start, stop, options);
    }
    
    async quit() {
        if (this.client && this.isConnected) {
            await this.client.quit();
            this.isConnected = false;
        }
    }
    
    async ping() {
        if (!this.isConnected) await this.connect();
        return await this.client.ping();
    }
}

module.exports = new RedisClient();
