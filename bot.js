require('dotenv').config();
console.log('🎰 טוען בוט קזינו טלגרם...\n');

// בדוק משתני סביבה
const { validateEnvironment } = require('./test-env.js');
if (!validateEnvironment()) {
    console.error('❌ בוט לא יכול להפעיל - משתנים חסרים');
    process.exit(1);
}

const { Telegraf, Markup } = require('telegraf');
const config = require('./config.json');
const redis = require('./redis-client');
const GameEngine = require('./game-engine');
const UserManager = require('./user-manager');

// אתחול הבוט
const bot = new Telegraf(process.env.TELEGRAM_TOKEN);

// אתחול מנהלים
const userManager = new UserManager();
const gameEngine = new GameEngine();

// נתוני מערכת
const SYSTEM_CONFIG = {
    botName: process.env.BOT_USERNAME || 'CasinoBot',
    adminId: process.env.ADMIN_ID,
    adminUsername: process.env.ADMIN_USERNAME,
    debugMode: process.env.DEBUG_MODE === 'true',
    winChance: parseInt(process.env.WIN_CHANCE_PERCENT) || 30,
    peekCost: parseInt(process.env.PEEK_COST) || 50,
    referralReward: parseInt(process.env.REFERRAL_REWARD) || 10
};

// לוגר
const log = {
    info: (msg) => console.log([INFO]  - ),
    error: (msg) => console.error([ERROR]  - ),
    debug: (msg) => SYSTEM_CONFIG.debugMode && console.log([DEBUG]  - )
};

// ==================== פקודות בסיסיות ====================

bot.start(async (ctx) => {
    const userId = ctx.from.id;
    const username = ctx.from.username || ctx.from.first_name;
    const args = ctx.message.text.split(' ');
    const referralCode = args.length > 1 ? args[1] : null;
    
    log.info(משתמש התחיל:  ());
    
    try {
        let user = await userManager.getUser(userId);
        
        if (!user) {
            // משתמש חדש
            user = await userManager.createUser(userId, username, referralCode);
            
            const welcomeMsg = \
🎰 *ברוך הבא לקזינו הטלגרם!* 🎉

👤 *שם:* \
💰 *יתרת התחלתית:* 1,000 מטבעות
🔑 *קוד הזמנה:* \\\

*🎮 פקודות זמינות:*
/play - התחל לשחק
/balance - צפה ביתרה
/profile - פרופיל מלא
/shop - חנות מטבעות
/leaderboard - טבלת המובילים
/referral - הזמן חברים
/help - עזרה ומדריך

*💡 טיפ:* השתמש ב-/play כדי להתחיל לשחק!
            \;
            
            await ctx.replyWithMarkdown(welcomeMsg, Markup.keyboard([
                ['🎰 שחק', '💰 יתרה'],
                ['🏆 פרופיל', '👥 הזמן'],
                ['🛒 חנות', '🏆 טבלה']
            ]).resize());
            
        } else {
            // משתמש קיים
            const welcomeBack = \
🎰 *ברוך השב, \!* 👋

💰 *יתרה נוכחית:* \ מטבעות
📊 *רמה:* \
🎮 *משחקים:* \

הקלד /play כדי להתחיל לשחק!
            \;
            
            await ctx.replyWithMarkdown(welcomeBack);
        }
    } catch (error) {
        log.error(\שגיאה ב-start: \\);
        await ctx.reply('❌ אירעה שגיאה, אנא נסה שוב מאוחר יותר.');
    }
});

bot.command('play', (ctx) => {
    const gamesMenu = \
🎮 *בחר משחק:*

1. 🎰 *מכונת סלוט* - /slot [סכום]
   *דוגמה:* \/slot 100\

2. 🎲 *קוביות* - /dice [סכום] [high/low/seven/pair]
   *דוגמה:* \/dice 50 high\

3. ⚪ *הטלת מטבע* - /coin [סכום] [heads/tails]
   *דוגמה:* \/coin 25 heads\

4. 🎡 *רולטה* - /roulette [סכום] [אפשרות]
   *דוגמה:* \/roulette 100 red\

💡 *טיפ:* התחל עם סכומים קטנים!
    \;
    
    ctx.replyWithMarkdown(gamesMenu, Markup.inlineKeyboard([
        [Markup.button.callback('🎰 סלוט', 'game_slot')],
        [Markup.button.callback('🎲 קוביות', 'game_dice')],
        [Markup.button.callback('⚪ מטבע', 'game_coin')],
        [Markup.button.callback('🎡 רולטה', 'game_roulette')]
    ]));
});

bot.command('balance', async (ctx) => {
    const userId = ctx.from.id;
    const user = await userManager.getUser(userId);
    
    if (user) {
        const msg = \
💰 *יתרה אישית*

💎 *יתרה נוכחית:* \ מטבעות
📊 *סטטיסטיקות:*
   🏆 רמה: \
   ⭐ XP: \
   🎮 משחקים: \
   ✅ ניצחונות: \
   👥 מוזמנים: \

*📥 אפשרויות להגדלת היתרה:*
1. 🎮 שחק וזכה במשחקים
2. 👥 הזמן חברים עם /referral
3. 🛒 קנה מטבעות עם /shop
        \;
        
        await ctx.replyWithMarkdown(msg);
    } else {
        await ctx.reply('❌ משתמש לא נמצא. הקלד /start להתחיל.');
    }
});

bot.command('slot', async (ctx) => {
    const args = ctx.message.text.split(' ');
    if (args.length < 2) {
        return ctx.reply('*שימוש:* /slot [סכום]\n*דוגמה:* /slot 100', { parse_mode: 'Markdown' });
    }
    
    const betAmount = parseInt(args[1]);
    const userId = ctx.from.id;
    
    try {
        const result = await gameEngine.playSlot(userId, betAmount);
        
        if (result.error) {
            return ctx.reply(\❌ \\);
        }
        
        let message = \
🎰 *מכונת סלוט*

\

💰 *סכום:* \ מטבעות
        \;
        
        if (result.won) {
            message += \
🎉 *ניצחון!* x\
🏆 *זכית:* \ מטבעות
💎 *יתרה חדשה:* \ מטבעות
            \;
        } else {
            message += \
😔 *לא זכית הפעם*
💎 *יתרה נוכחית:* \ מטבעות
            \;
        }
        
        await ctx.replyWithMarkdown(message);
    } catch (error) {
        log.error(\שגיאה במשחק סלוט: \\);
        await ctx.reply('❌ אירעה שגיאה במשחק, אנא נסה שוב.');
    }
});

bot.command('leaderboard', async (ctx) => {
    try {
        const leaderboard = await userManager.getLeaderboard();
        
        let text = '🏆 *טבלת המובילים* 🏆\n\n';
        
        leaderboard.forEach((user, index) => {
            const rank = index + 1;
            const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : \\.\;
            text += \\ \ - \ מטבעות\n\;
        });
        
        await ctx.replyWithMarkdown(text);
    } catch (error) {
        await ctx.reply('❌ שגיאה בטעינת טבלת המובילים.');
    }
});

bot.command('referral', async (ctx) => {
    const userId = ctx.from.id;
    const user = await userManager.getUser(userId);
    
    if (user) {
        const msg = \
👥 *תוכנית ההזמנות*

🔗 *קוד ההזמנה שלך:* \\\

💰 *בונוס:* \ מטבעות לכל חבר
👥 *מוזמנים עד כה:* \

*📝 איך להזמין:*
החבר מקליד:
\/start \\
        \;
        
        await ctx.replyWithMarkdown(msg);
    } else {
        await ctx.reply('❌ משתמש לא נמצא. הקלד /start להתחיל.');
    }
});

// ==================== inline buttons ====================

bot.action('game_slot', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('*הקלד:* /slot [סכום]\n*דוגמה:* /slot 100', { 
        parse_mode: 'Markdown' 
    });
});

// ==================== שגיאות ====================

bot.catch((err, ctx) => {
    log.error(\[Bot Error] \: \\);
    ctx.reply('❌ אירעה שגיאה. אנא נסה שוב.');
});

// ==================== הפעלת הבוט ====================

async function startBot() {
    try {
        // בדוק חיבור ל-Redis
        await redis.connect();
        log.info('✅ התחבר ל-Redis בהצלחה');
        
        // הפעל את הבוט
        await bot.launch();
        log.info(\🤖 בוט פועל! (@\)\);
        log.info(\👑 מנהל: @\\);
        log.info(\🎯 סיכוי זכייה: \%\);
        
        // עצירה מסודרת
        process.once('SIGINT', () => bot.stop('SIGINT'));
        process.once('SIGTERM', () => bot.stop('SIGTERM'));
        
    } catch (error) {
        log.error(\שגיאה בהפעלת הבוט: \\);
        process.exit(1);
    }
}

// הפעל את הבוט
startBot();

module.exports = bot;
