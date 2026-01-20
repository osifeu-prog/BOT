const redis = require('./redis-client');
const config = require('./config.json');

class UserManager {
    constructor() {
        this.startingBalance = config.user.starting_balance;
        this.referralBonus = parseInt(process.env.REFERRAL_REWARD) || 10;
    }
    
    async getUser(userId) {
        const userData = await redis.hGetAll(\user:\\);
        
        if (!userData || !userData.id) {
            return null;
        }
        
        // המרת ערכים מספריים
        return {
            id: userData.id,
            username: userData.username || '',
            balance: parseInt(userData.balance) || 0,
            level: parseInt(userData.level) || 1,
            xp: parseInt(userData.xp) || 0,
            gamesPlayed: parseInt(userData.gamesPlayed) || 0,
            gamesWon: parseInt(userData.gamesWon) || 0,
            referrals: parseInt(userData.referrals) || 0,
            referralCode: userData.referralCode || \REF\\\,
            totalWon: parseInt(userData.totalWon) || 0,
            totalBet: parseInt(userData.totalBet) || 0,
            createdAt: userData.createdAt || new Date().toISOString(),
            lastActive: userData.lastActive || new Date().toISOString()
        };
    }
    
    async createUser(userId, username, referredBy = null) {
        const referralCode = \REF\\\;
        
        const userData = {
            id: userId.toString(),
            username: username || '',
            balance: this.startingBalance,
            level: 1,
            xp: 0,
            gamesPlayed: 0,
            gamesWon: 0,
            referrals: 0,
            referralCode: referralCode,
            referredBy: referredBy || '',
            totalWon: 0,
            totalBet: 0,
            createdAt: new Date().toISOString(),
            lastActive: new Date().toISOString()
        };
        
        // שמור ב-Redis
        for (const [key, value] of Object.entries(userData)) {
            await redis.hSet(\user:\\, key, value);
        }
        
        // הוסף לטבלת היתרות
        await redis.zAdd('users:byBalance', this.startingBalance, userId.toString());
        
        // אם הוזמן על ידי מישהו, תן בונוס
        if (referredBy) {
            await this.addReferralBonus(referredBy);
        }
        
        return userData;
    }
    
    async addReferralBonus(userId) {
        // הוסף בונוס למזמין
        const user = await this.getUser(userId);
        if (user) {
            const newBalance = user.balance + this.referralBonus;
            await redis.hSet(\user:\\, 'balance', newBalance);
            
            // עדכן טבלת יתרות
            await redis.zAdd('users:byBalance', newBalance, userId.toString());
            
            // עדכן ספירת מוזמנים
            await redis.hIncrBy(\user:\\, 'referrals', 1);
        }
    }
    
    async updateBalance(userId, amount) {
        const user = await this.getUser(userId);
        if (!user) return null;
        
        const newBalance = user.balance + amount;
        await redis.hSet(\user:\\, 'balance', newBalance);
        
        // עדכן טבלת יתרות
        await redis.zAdd('users:byBalance', newBalance, userId.toString());
        
        return newBalance;
    }
    
    async getLeaderboard(limit = 10) {
        const leaderboard = await redis.zRangeWithScores('users:byBalance', 0, limit - 1, { REV: true });
        
        const users = [];
        for (const item of leaderboard) {
            const user = await this.getUser(item.value);
            if (user) {
                users.push({
                    id: user.id,
                    username: user.username,
                    balance: user.balance,
                    level: user.level
                });
            }
        }
        
        return users;
    }
    
    async getTotalUsers() {
        const keys = await redis.client.keys('user:*');
        return keys.length;
    }
}

module.exports = UserManager;
