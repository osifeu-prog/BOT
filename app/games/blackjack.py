import random
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

class BlackjackGame:
    def __init__(self):
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    
    def create_deck(self):
        deck = []
        for suit in self.suits:
            for value in self.values:
                deck.append(f"{value}{suit}")
        random.shuffle(deck)
        return deck
    
    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        
        for card in hand:
            card_value = card[:-2]
            if card_value in ['J','Q','K']:
                value += 10
            elif card_value == 'A':
                value += 11
                aces += 1
            else:
                value += int(card_value)
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value

async def start_blackjack(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    balance = int(user.get("balance", 0))
    bet_amount = 50
    
    if balance < bet_amount:
        await query.answer(f"❌ יתרה מינימלית: {bet_amount} מטבעות", show_alert=True)
        return
    
    game = BlackjackGame()
    deck = game.create_deck()
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    player_value = game.calculate_hand_value(player_hand)
    dealer_showing = game.calculate_hand_value([dealer_hand[0]])
    
    game_state = {
        'deck': deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'player_value': player_value,
        'dealer_showing': dealer_showing,
        'bet_amount': bet_amount,
        'game_over': False
    }
    
    db.r.setex(f"game:blackjack:{uid}", 300, json.dumps(game_state))
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    player_cards = " ".join(player_hand)
    dealer_cards = f"{dealer_hand[0]} 🃏"
    
    game_text = f"""
🃏 **בלאקג'ק - 21**

**הדילר:** {dealer_cards}
**ערך גלוי:** {dealer_showing}

**היד שלך:** {player_cards}
**ערך היד שלך:** {player_value}

💰 **הימור:** {bet_amount} מטבעות

**בחר פעולה:**
"""
    
    keyboard = [
        [
            InlineKeyboardButton("👇 קח קלף", callback_data="bj_hit"),
            InlineKeyboardButton("✋ עצור", callback_data="bj_stand")
        ],
        [
            InlineKeyboardButton("💰 הכפיל", callback_data="bj_double"),
            InlineKeyboardButton("🔄 משחק חדש", callback_data="play_blackjack")
        ],
        [
            InlineKeyboardButton("🏠 תפריט", callback_data="start")
        ]
    ]
    
    await query.edit_message_text(text=game_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_blackjack_action(update, context):
    query = update.callback_query
    uid = query.from_user.id
    action = query.data.replace("bj_", "")
    
    game_state_str = db.r.get(f"game:blackjack:{uid}")
    if not game_state_str:
        await query.answer("❌ המשחק נגמר או לא קיים!", show_alert=True)
        await start_blackjack(update, context)
        return
    
    game_state = json.loads(game_state_str)
    game = BlackjackGame()
    
    if action == "hit":
        game_state['player_hand'].append(game_state['deck'].pop())
        game_state['player_value'] = game.calculate_hand_value(game_state['player_hand'])
        
        if game_state['player_value'] > 21:
            game_state['game_over'] = True
            result = "התפוצצת! הדילר מנצח."
            db.log_transaction(uid, -game_state['bet_amount'], "Blackjack loss (bust)")
        else:
            result = None
    
    elif action == "stand":
        game_state['game_over'] = True
        
        dealer_hand = game_state['dealer_hand']
        dealer_value = game.calculate_hand_value(dealer_hand)
        
        while dealer_value < 17:
            dealer_hand.append(game_state['deck'].pop())
            dealer_value = game.calculate_hand_value(dealer_hand)
        
        game_state['dealer_hand'] = dealer_hand
        game_state['dealer_value'] = dealer_value
        
        if dealer_value > 21 or game_state['player_value'] > dealer_value:
            win_amount = game_state['bet_amount'] * 2
            db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
            db.log_transaction(uid, win_amount - game_state['bet_amount'], "Blackjack win")
            result = f"🎉 ניצחת! זכית ב-{win_amount} מטבעות."
        elif game_state['player_value'] < dealer_value:
            db.log_transaction(uid, -game_state['bet_amount'], "Blackjack loss")
            result = "😔 הדילר ניצח."
        else:
            db.r.hincrby(f"user:{uid}:profile", "balance", game_state['bet_amount'])
            result = "🤝 תיקו! הכסף הוחזר."
    
    elif action == "double":
        if int(db.get_user(uid).get("balance", 0)) >= game_state['bet_amount']:
            game_state['bet_amount'] *= 2
            db.r.hincrby(f"user:{uid}:profile", "balance", -game_state['bet_amount'] // 2)
            
            game_state['player_hand'].append(game_state['deck'].pop())
            game_state['player_value'] = game.calculate_hand_value(game_state['player_hand'])
            
            if game_state['player_value'] > 21:
                game_state['game_over'] = True
                result = "התפוצצת לאחר הכפלה!"
                db.log_transaction(uid, -game_state['bet_amount'], "Blackjack loss (double bust)")
            else:
                result = None
        else:
            await query.answer("❌ אין מספיק מטבעות להכפלה!", show_alert=True)
            return
    
    db.r.setex(f"game:blackjack:{uid}", 300, json.dumps(game_state))
    
    if game_state['game_over']:
        player_cards = " ".join(game_state['player_hand'])
        dealer_cards = " ".join(game_state['dealer_hand'])
        
        final_text = f"""
🃏 **בלאקג'ק - סיום**

**הדילר:** {dealer_cards}
**ערך הדילר:** {game_state.get('dealer_value', '?')}

**היד שלך:** {player_cards}
**ערך היד שלך:** {game_state['player_value']}

💰 **הימור:** {game_state['bet_amount']} מטבעות

**תוצאה:** {result}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 משחק חדש", callback_data="play_blackjack"),
             InlineKeyboardButton("🏠 תפריט", callback_data="start")]
        ]
        
        await query.edit_message_text(text=final_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        player_cards = " ".join(game_state['player_hand'])
        dealer_cards = f"{game_state['dealer_hand'][0]} 🃏"
        
        game_text = f"""
🃏 **בלאקג'ק - במהלך**

**הדילר:** {dealer_cards}
**ערך גלוי:** {game_state['dealer_showing']}

**היד שלך:** {player_cards}
**ערך היד שלך:** {game_state['player_value']}

💰 **הימור:** {game_state['bet_amount']} מטבעות

**בחר פעולה:**
"""
        
        keyboard = [
            [
                InlineKeyboardButton("👇 קח קלף", callback_data="bj_hit"),
                InlineKeyboardButton("✋ עצור", callback_data="bj_stand")
            ],
            [
                InlineKeyboardButton("💰 הכפיל", callback_data="bj_double"),
                InlineKeyboardButton("🏠 תפריט", callback_data="start")
            ]
        ]
        
        await query.edit_message_text(text=game_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
