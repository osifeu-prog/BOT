import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

class RouletteGame:
    def __init__(self):
        self.numbers = list(range(0, 37))  # 0-36
        self.colors = {
            'red': [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
            'black': [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
            'green': [0]
        }
    
    def get_color(self, number):
        for color, numbers in self.colors.items():
            if number in numbers:
                return color
        return 'green'
    
    def calculate_payout(self, bet_type, bet_amount, winning_number):
        """חשב תשלום לפי סוג ההימור"""
        payouts = {
            'number': 36,       # הימור על מספר ספציפי
            'red': 2,           # הימור על אדום
            'black': 2,         # הימור על שחור
            'even': 2,          # הימור על זוגי
            'odd': 2,           # הימור על אי-זוגי
            'dozen1': 3,        # הימור על 1-12
            'dozen2': 3,        # הימור על 13-24
            'dozen3': 3,        # הימור על 25-36
            'column1': 3,       # הימור על עמודה ראשונה
            'column2': 3,       # הימור על עמודה שנייה
            'column3': 3,       # הימור על עמודה שלישית
            'low': 2,           # הימור על 1-18
            'high': 2           # הימור על 19-36
        }
        
        # בדוק אם ההימור זכה
        if self.check_win(bet_type, winning_number):
            return bet_amount * payouts.get(bet_type, 1)
        return 0
    
    def check_win(self, bet_type, winning_number):
        """בדוק אם ההימור זכה"""
        if bet_type == 'number':
            # במקרה הזה, bet_type כולל את המספר בפורמט "number_17"
            bet_number = int(bet_type.split('_')[1])
            return winning_number == bet_number
        elif bet_type == 'red':
            return winning_number in self.colors['red']
        elif bet_type == 'black':
            return winning_number in self.colors['black']
        elif bet_type == 'even':
            return winning_number % 2 == 0 and winning_number != 0
        elif bet_type == 'odd':
            return winning_number % 2 == 1
        elif bet_type == 'dozen1':
            return 1 <= winning_number <= 12
        elif bet_type == 'dozen2':
            return 13 <= winning_number <= 24
        elif bet_type == 'dozen3':
            return 25 <= winning_number <= 36
        elif bet_type == 'low':
            return 1 <= winning_number <= 18
        elif bet_type == 'high':
            return 19 <= winning_number <= 36
        return False

roulette_game = RouletteGame()

async def start_roulette(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    balance = int(user.get("balance", 0))
    min_bet = 10
    
    if balance < min_bet:
        await query.answer(f"❌ יתרה מינימלית: {min_bet} מטבעות", show_alert=True)
        return
    
    # צור מקלדת הימורים
    keyboard = [
        [
            InlineKeyboardButton("🔴 אדום (x2)", callback_data="roulette_red"),
            InlineKeyboardButton("⚫ שחור (x2)", callback_data="roulette_black"),
            InlineKeyboardButton("🟢 0 (x36)", callback_data="roulette_number_0")
        ],
        [
            InlineKeyboardButton("1️⃣ 1-12 (x3)", callback_data="roulette_dozen1"),
            InlineKeyboardButton("2️⃣ 13-24 (x3)", callback_data="roulette_dozen2"),
            InlineKeyboardButton("3️⃣ 25-36 (x3)", callback_data="roulette_dozen3")
        ],
        [
            InlineKeyboardButton("⚡ זוגי (x2)", callback_data="roulette_even"),
            InlineKeyboardButton("⚡ אי-זוגי (x2)", callback_data="roulette_odd")
        ],
        [
            InlineKeyboardButton("📉 1-18 (x2)", callback_data="roulette_low"),
            InlineKeyboardButton("📈 19-36 (x2)", callback_data="roulette_high")
        ],
        [
            InlineKeyboardButton("🎲 מספר ספציפי", callback_data="roulette_choose_number"),
            InlineKeyboardButton("💰 הימור מהיר: 100", callback_data="roulette_quick_100")
        ],
        [
            InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start"),
            InlineKeyboardButton("❓ עזרה", callback_data="roulette_help")
        ]
    ]
    
    game_text = """
🎡 **משחק רולטה אירופאי**

**חוקים:**
• המספרים: 0 (ירוק) + 1-36 (אדום/שחור)
• בחר את סוג ההימור שלך
• הכנסת ההימור: לחץ על כפתור ההימור

**תשלומים:**
• מספר בודד: x36
• אדום/שחור: x2
• זוגי/אי-זוגי: x2
• תריסר: x3
• גבוה/נמוך: x2

💰 **הימור מינימלי:** 10 מטבעות
"""
    
    await query.edit_message_text(
        text=game_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_roulette_bet(update, context):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data.replace("roulette_", "")
    
    if data == "choose_number":
        # הצג מקלדת עם מספרים
        await choose_roulette_number(update, context)
        return
    
    # כאן תוסיף את הלוגיקה לטיפול בהימורים
    
    await query.answer("🎡 הימור התקבל! מסובבים את הגלגל...", show_alert=False)
