import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db
from app.utils.leaderboard import leaderboard

class RouletteGame:
    def __init__(self):
        self.numbers = list(range(0, 37))
        self.colors = {
            'red': [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],
            'black': [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35],
            'green': [0]
        }
    
    def get_color(self, number):
        for color, numbers in self.colors.items():
            if number in numbers:
                return color
        return 'green'
    
    def calculate_payout(self, bet_type, bet_amount, winning_number):
        payouts = {
            'number': 36, 'red': 2, 'black': 2, 'even': 2, 'odd': 2,
            'dozen1': 3, 'dozen2': 3, 'dozen3': 3,
            'low': 2, 'high': 2
        }
        
        if self.check_win(bet_type, winning_number):
            return bet_amount * payouts.get(bet_type, 1)
        return 0
    
    def check_win(self, bet_type, winning_number):
        if bet_type.startswith('number_'):
            bet_num = int(bet_type.split('_')[1])
            return winning_number == bet_num
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
    
    game_text = """
🎡 **משחק רולטה אירופאי**

**חוקים:**
• המספרים: 0 (ירוק) + 1-36 (אדום/שחור)
• בחר סוג הימור ולחץ עליו

**תשלומים:**
• מספר בודד: x36
• אדום/שחור: x2
• זוגי/אי-זוגי: x2
• תריסר: x3
• גבוה/נמוך: x2

💰 **הימור מינימלי:** 10 מטבעות
"""
    
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
            InlineKeyboardButton("🎲 מספר ספציפי", callback_data="roulette_choose"),
            InlineKeyboardButton("💰 הימור מהיר: 50", callback_data="roulette_quick_50")
        ],
        [
            InlineKeyboardButton("🏠 תפריט", callback_data="start")
        ]
    ]
    
    await query.edit_message_text(text=game_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_roulette_bet(update, context):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data.replace("roulette_", "")
    
    if data == "choose":
        await choose_roulette_number(update, context)
        return
    
    user = db.get_user(uid)
    balance = int(user.get("balance", 0))
    bet_amount = 10
    
    if balance < bet_amount:
        await query.answer("❌ אין מספיק מטבעות!", show_alert=True)
        return
    
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    winning_number = random.randint(0, 36)
    win_amount = roulette_game.calculate_payout(data, bet_amount, winning_number)
    
    if win_amount > 0:
        db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
        db.log_transaction(uid, win_amount - bet_amount, f"Roulette win ({data})")
        leaderboard.update_score(uid, 'total_wins', 1)
        leaderboard.update_score(uid, 'total_winnings', win_amount)
        
        result_text = f"🎡 **הגלגל מסתובב...**\n\nהמספר: **{winning_number}** ({roulette_game.get_color(winning_number)})\n\n🎉 **זכית ב-{win_amount} מטבעות!** (x{win_amount/bet_amount:.1f})"
    else:
        db.log_transaction(uid, -bet_amount, f"Roulette loss ({data})")
        result_text = f"🎡 **הגלגל מסתובב...**\n\nהמספר: **{winning_number}** ({roulette_game.get_color(winning_number)})\n\n😔 **הפסדת {bet_amount} מטבעות.**"
    
    keyboard = [
        [InlineKeyboardButton("🔄 שחק שוב", callback_data="play_roulette"),
         InlineKeyboardButton("🏠 תפריט", callback_data="start")]
    ]
    
    await query.edit_message_text(text=result_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def choose_roulette_number(update, context):
    query = update.callback_query
    
    keyboard = []
    row = []
    for i in range(37):
        if i == 0:
            color = "🟢"
        elif i in roulette_game.colors['red']:
            color = "🔴"
        else:
            color = "⚫"
        
        row.append(InlineKeyboardButton(f"{color}{i}", callback_data=f"roulette_number_{i}"))
        
        if len(row) == 6 or (i == 0 and len(row) == 1):
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("🏠 חזרה", callback_data="play_roulette")])
    
    await query.edit_message_text(
        text="🎲 **בחר מספר (0-36):**\n🟢 0 = x36\n🔴 אדום = x2\n⚫ שחור = x2",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
