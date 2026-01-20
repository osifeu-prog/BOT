console.log('======================================');
console.log('🎰 בוט קזינו טלגרם מתחיל...');
console.log('======================================\n');

// טען משתני סביבה
require('dotenv').config();

// בדוק משתנים
const { validateEnvironment } = require('./test-env.js');

async function startApplication() {
    console.log('🔍 בודק תצורת מערכת...');
    
    if (!validateEnvironment()) {
        console.error('\n❌ לא ניתן להפעיל את המערכת - משתנים חסרים');
        console.log('אנא מלא את קובץ .env והרץ שוב');
        process.exit(1);
    }
    
    console.log('\n✅ כל המשתנים תקינים!');
    
    // הצג מידע מערכת
    console.log('\n📊 מידע מערכת:');
    console.log('----------------');
    console.log(\🤖 שם הבוט: @\\);
    console.log(\👑 מנהל: @\\);
    console.log(\🎯 סיכוי זכייה: \%\);
    console.log(\💰 עלות הצצה: \\);
    console.log(\👥 בונוס הזמנה: \\);
    console.log(\🐞 Debug: \\);
    
    // בדוק Redis
    console.log('\n🔗 בודק חיבור ל-Redis...');
    try {
        const redis = require('./redis-client');
        await redis.ping();
        console.log('✅ Redis: מחובר בהצלחה');
    } catch (error) {
        console.log('⚠️  Redis: לא מחובר');
        console.log('   הרץ: npm run redis');
    }
    
    console.log('\n🚀 אפשרויות הרצה:');
    console.log('-----------------');
    console.log('1. npm run dev    - הפעל בפיתוח (nodemon)');
    console.log('2. npm run bot    - הפעל את הבוט בלבד');
    console.log('3. npm start      - הפעל את המערכת המלאה');
    console.log('4. npm run redis  - הפעל Redis ב-Docker');
    console.log('5. npm test       - בדוק תצורה');
    
    console.log('\n📝 הוראות:');
    console.log('----------');
    console.log('1. התקן חבילות: npm install');
    console.log('2. הפעל Redis: npm run redis');
    console.log('3. הפעל את הבוט: npm run dev');
    console.log('4. פתח טלגרם וחפש את הבוט: @' + (process.env.BOT_USERNAME || 'YourBot'));
    
    // אם יש צורך, אפשר להפעיל את הבוט אוטומטית
    if (process.argv.includes('--auto-start')) {
        console.log('\n🎯 מפעיל את הבוט אוטומטית...');
        require('./bot.js');
    }
}

// הרץ את האפליקציה
startApplication().catch(console.error);
