console.log('🔧 התקנת מערכת קזינו טלגרם...\n');

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function setup() {
    console.log('📦 שלב 1: התקנת חבילות...');
    try {
        const { stdout, stderr } = await execAsync('npm install');
        console.log('✅ חבילות הותקנו בהצלחה');
    } catch (error) {
        console.log('❌ שגיאה בהתקנת חבילות:', error.message);
    }
    
    console.log('\n🔍 שלב 2: בדיקת קבצי תצורה...');
    
    // בדוק אם קובץ .env קיים
    if (!fs.existsSync('.env')) {
        console.log('❌ קובץ .env לא נמצא');
        console.log('   יצירת קובץ .env מדוגמה...');
        if (fs.existsSync('.env.example')) {
            fs.copyFileSync('.env.example', '.env');
            console.log('✅ קובץ .env נוצר מ-.env.example');
            console.log('   אנא ערוך את קובץ .env והוסף את הערכים האמיתיים');
        }
    } else {
        console.log('✅ קובץ .env קיים');
    }
    
    // בדוק קבצים חשובים
    const requiredFiles = ['package.json', 'bot.js', 'config.json', 'redis-client.js'];
    for (const file of requiredFiles) {
        if (fs.existsSync(file)) {
            console.log(\✅ \ קיים\);
        } else {
            console.log(\❌ \ חסר\);
        }
    }
    
    console.log('\n🎯 שלב 3: בדיקת חיבורים...');
    
    // בדוק Node.js
    console.log(\📟 Node.js: \\);
    
    // בדוק npm
    try {
        const { stdout } = await execAsync('npm --version');
        console.log(\📦 npm: \\);
    } catch (error) {
        console.log('❌ npm לא מותקן');
    }
    
    console.log('\n🎰 שלב 4: בדיקת משתני סביבה...');
    
    // טען את .env
    require('dotenv').config();
    
    const requiredVars = ['TELEGRAM_TOKEN', 'REDIS_URL', 'ADMIN_ID'];
    let missingVars = [];
    
    for (const varName of requiredVars) {
        if (process.env[varName]) {
            console.log(\✅ \: מוגדר\);
        } else {
            console.log(\❌ \: חסר\);
            missingVars.push(varName);
        }
    }
    
    if (missingVars.length > 0) {
        console.log('\n🚨 אנא הגדר את המשתנים החסרים בקובץ .env:');
        missingVars.forEach(v => console.log(\   - \\));
    } else {
        console.log('\n✅ כל המשתנים הנדרשים מוגדרים');
    }
    
    console.log('\n🚀 התקנה הושלמה!');
    console.log('\nהרץ את הפקודות הבאות:');
    console.log('1. npm run redis  - להפעלת Redis');
    console.log('2. npm run dev    - להפעלת הבוט בפיתוח');
    console.log('3. npm run test   - לבדיקת תצורה');
    
    // שאל אם להפעיל Redis
    console.log('\n💡 טיפ: ודא ש-Docker פועל לפני הרצת Redis');
}

setup().catch(console.error);
