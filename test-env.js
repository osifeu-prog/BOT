require('dotenv').config();
const fs = require('fs');
const path = require('path');

console.log('🔍 בודק משתני סביבה...');
console.log('===========================');

// טען את קובץ התצורה
const config = require('./config.json');

// פונקציה לבדיקת משתנים
function validateEnvironment() {
    const missing = [];
    const warnings = [];
    const loaded = [];
    
    console.log('📋 רשימת משתנים נדרשים:');
    console.log('-----------------------');
    
    // בדוק משתנים נדרשים
    config.validation.required_variables.forEach(varName => {
        if (process.env[varName]) {
            const value = process.env[varName];
            const maskedValue = value.length > 8 ? 
                value.substring(0, 4) + '...' + value.substring(value.length - 4) : 
                '****';
            console.log(✅ : );
            loaded.push(varName);
        } else {
            console.log(❌ : חסר!);
            missing.push(varName);
        }
    });
    
    console.log('\n🔢 משתנים מספריים:');
    console.log('-------------------');
    
    // בדוק משתנים מספריים
    config.validation.numeric_variables.forEach(varName => {
        if (process.env[varName]) {
            const value = parseFloat(process.env[varName]);
            if (isNaN(value)) {
                console.log(⚠️ : צריך להיות מספר (נוכחי: ));
                warnings.push(${varName} צריך להיות מספר);
            } else {
                console.log(✅ : );
            }
        }
    });
    
    // בדוק משתנים נוספים
    console.log('\n📊 משתנים נוספים:');
    console.log('-----------------');
    
    const optionalVars = [
        'OPENAI_API_KEY',
        'CRYPTO_PAY_TOKEN', 
        'TON_WALLET',
        'PARTICIPANTS_GROUP_LINK',
        'TEST_GROUP_LINK',
        'WEBHOOK_URL',
        'DEBUG_MODE',
        'TOKEN_PACKS'
    ];
    
    optionalVars.forEach(varName => {
        if (process.env[varName]) {
            const value = process.env[varName];
            if (varName.includes('TOKEN') || varName.includes('KEY')) {
                console.log(✅ : *******);
            } else if (varName === 'TOKEN_PACKS') {
                try {
                    JSON.parse(value);
                    console.log(✅ : JSON תקין);
                } catch (e) {
                    console.log(⚠️ : JSON לא תקין);
                    warnings.push(${varName} JSON לא תקין);
                }
            } else {
                console.log(✅ : );
            }
        } else {
            console.log(➖ : לא הוגדר (אופציונלי));
        }
    });
    
    console.log('\n📊 סיכום:');
    console.log('==========');
    console.log(✅ משתנים שנטענו: );
    console.log(❌ משתנים חסרים: );
    console.log(⚠️  אזהרות: );
    
    if (missing.length > 0) {
        console.log('\n🚨 שגיאות קריטיות:');
        missing.forEach(m => console.log(   - ));
        return false;
    }
    
    if (warnings.length > 0) {
        console.log('\n⚠️  אזהרות:');
        warnings.forEach(w => console.log(   - ));
    }
    
    // הצג הגדרות קזינו
    console.log('\n🎰 הגדרות קזינו:');
    console.log('================');
    console.log(💰 עלות הצצה: );
    console.log(👥 בונוס הזמנה: );
    console.log(🎯 סיכוי זכייה: %);
    console.log(🐞 מצב Debug: );
    
    return true;
}

// בדוק חיבור ל-Redis
async function testRedisConnection() {
    console.log('\n🔗 בדיקת חיבור ל-Redis...');
    try {
        const redis = require('redis');
        const client = redis.createClient({
            url: process.env.REDIS_URL || 'redis://localhost:6379'
        });
        
        client.on('error', (err) => {
            console.log('❌ Redis: לא ניתן להתחבר');
            console.log(   שגיאה: );
        });
        
        await client.connect();
        const pong = await client.ping();
        console.log(✅ Redis: מחובר בהצלחה ());
        await client.quit();
        return true;
    } catch (error) {
        console.log('❌ Redis: שגיאה בחיבור');
        console.log(   פרטים: );
        return false;
    }
}

// הרץ את כל הבדיקות
async function runAllTests() {
    console.log('🚀 מתחיל בדיקות מערכת...\n');
    
    const envValid = validateEnvironment();
    
    if (envValid) {
        console.log('\n✅ כל המשתנים הדרושים קיימים!');
        
        // בדוק Redis רק אם הוגדר
        if (process.env.REDIS_URL) {
            await testRedisConnection();
        }
        
        console.log('\n🎉 המערכת מוכנה להפעלה!');
        console.log('\nהרץ את הפקודות הבאות:');
        console.log('1. npm install - להתקנת חבילות');
        console.log('2. npm run redis - להפעלת Redis (Docker)');
        console.log('3. npm run dev - להפעלת הבוט בפיתוח');
        console.log('4. npm run bot - להפעלת הבוט');
    } else {
        console.log('\n❌ המערכת לא מוכנה - משתנים חסרים');
        console.log('אנא מלא את כל המשתנים הנדרשים בקובץ .env');
        process.exit(1);
    }
}

// אם הקובץ הופעל ישירות
if (require.main === module) {
    runAllTests().catch(console.error);
}

module.exports = { validateEnvironment, testRedisConnection };
