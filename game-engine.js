const redis = require('./redis-client');
const config = require('./config.json');

class GameEngine {
    constructor() {
        this.config = config.games;
        this.winChance = parseInt(process.env.WIN_CHANCE_PERCENT) || 30;
    }
    
    async playSlot(userId, betAmount) {
        // בדוק הגבלות סכום
        if (betAmount < this.config.slot.min_bet) {
            return { error: \הסכום המינימלי הוא \\ };
        }
        
        if (betAmount > this.config.slot.max_bet) {
            return { error: \הסכום המקסימלי הוא \\ };
        }
        
        // קבל יתרת משתמש
        const userData = await redis.hGetAll(\user:\\);
        if (!userData || !userData.id) {
            return { error: 'משתמש לא נמצא' };
        }
        
        const currentBalance = parseInt(userData.balance) || 0;
        if (currentBalance < betAmount) {
            return { error: 'יתרה לא מספיקה' };
        }
        
        // הפחת את הסכום
        const newBalance = currentBalance - betAmount;
        await redis.hSet(\user:\\, 'balance', newBalance);
        
        // שחק
        const reels = [
            this.config.slot.symbols[Math.floor(Math.random() * this.config.slot.symbols.length)],
            this.config.slot.symbols[Math.floor(Math.random() * this.config.slot.symbols.length)],
            this.config.slot.symbols[Math.floor(Math.random() * this.config.slot.symbols.length)]
        ];
        
        // בדוק זכייה
        let multiplier = 0;
        let won = false;
        
        if (reels[0] === reels[1] && reels[1] === reels[2]) {
            // שלושה זהים
            multiplier = this.config.slot.payouts.three_of_a_kind;
            
            // בונוס לסמלים מיוחדים
            if (reels[0] === '7️⃣') multiplier = this.config.slot.payouts.seven_seven_seven;
            if (reels[0] === '💎') multiplier = this.config.slot.payouts.diamond_diamond_diamond;
            
            won = true;
        } else if (reels[0] === reels[1] || reels[1] === reels[2] || reels[0] === reels[2]) {
            // זוג
            multiplier = this.config.slot.payouts.pair;
            won = true;
        }
        
        const winAmount = won ? betAmount * multiplier : 0;
        
        // עדכן יתרה אם ניצח
        if (won) {
            const finalBalance = newBalance + winAmount;
            await redis.hSet(\user:\\, 'balance', finalBalance);
            
            // עדכן סטטיסטיקות
            await this.recordGame(userId, betAmount, true, winAmount);
            
            return {
                reels,
                won: true,
                winAmount,
                multiplier,
                betAmount,
                newBalance: finalBalance
            };
        } else {
            // עדכן סטטיסטיקות הפסד
            await this.recordGame(userId, betAmount, false, 0);
            
            return {
                reels,
                won: false,
                winAmount: 0,
                multiplier: 0,
                betAmount,
                newBalance
            };
        }
    }
    
    async playDice(userId, betAmount, prediction) {
        // דומה לסלוט - מימוש בסיסי
        const userData = await redis.hGetAll(\user:\\);
        if (!userData || !userData.id) {
            return { error: 'משתמש לא נמצא' };
        }
        
        const currentBalance = parseInt(userData.balance) || 0;
        if (currentBalance < betAmount) {
            return { error: 'יתרה לא מספיקה' };
        }
        
        // הפחת
        const newBalance = currentBalance - betAmount;
        await redis.hSet(\user:\\, 'balance', newBalance);
        
        // השלך קוביות
        const dice1 = Math.floor(Math.random() * 6) + 1;
        const dice2 = Math.floor(Math.random() * 6) + 1;
        const total = dice1 + dice2;
        
        // בדוק ניצחון
        let won = false;
        let multiplier = 1;
        
        if (prediction === 'high' && total > 7) {
            won = true;
            multiplier = this.config.dice.payouts.high;
        } else if (prediction === 'low' && total < 7) {
            won = true;
            multiplier = this.config.dice.payouts.low;
        } else if (prediction === 'seven' && total === 7) {
            won = true;
            multiplier = this.config.dice.payouts.seven;
        } else if (prediction === 'pair' && dice1 === dice2) {
            won = true;
            multiplier = this.config.dice.payouts.pair;
        }
        
        const winAmount = won ? betAmount * multiplier : 0;
        
        if (won) {
            const finalBalance = newBalance + winAmount;
            await redis.hSet(\user:\\, 'balance', finalBalance);
            await this.recordGame(userId, betAmount, true, winAmount);
            
            return {
                dice1,
                dice2,
                total,
                won: true,
                winAmount,
                multiplier,
                betAmount,
                newBalance: finalBalance
            };
        } else {
            await this.recordGame(userId, betAmount, false, 0);
            
            return {
                dice1,
                dice2,
                total,
                won: false,
                winAmount: 0,
                multiplier: 0,
                betAmount,
                newBalance
            };
        }
    }
    
    async recordGame(userId, betAmount, won, winAmount) {
        const gamesPlayed = await redis.hIncrBy(\user:\\, 'gamesPlayed', 1);
        
        if (won) {
            await redis.hIncrBy(\user:\\, 'gamesWon', 1);
            await redis.hIncrBy(\user:\\, 'totalWon', winAmount);
        }
        
        await redis.hIncrBy(\user:\\, 'totalBet', betAmount);
        
        // הוסף XP
        const xpGain = Math.floor(betAmount / 10) + (won ? 50 : 10);
        await redis.hIncrBy(\user:\\, 'xp', xpGain);
    }
}

module.exports = GameEngine;
