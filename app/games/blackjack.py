import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

class BlackjackGame:
    def __init__(self):
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = self.create_deck()
    
    def create_deck(self):
        """צור חפיסת קלפים"""
        deck = []
        for suit in self.suits:
            for value in self.values:
                deck.append(f"{value}{suit}")
        random.shuffle(deck)
        return deck
    
    def calculate_hand_value(self, hand):
        """חשב ערך יד"""
        value = 0
        aces = 0
        
        for card in hand:
            card_value = card[:-2]  # הסר את הסימן
            if card_value in ['J', 'Q', 'K']:
                value += 10
            elif card_value == 'A':
                value += 11
                aces += 1
            else:
                value += int(card_value)
        
        # התאם את ה-Aces אם הערך גדול מ-21
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value

async def start_blackjack(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    game = BlackjackGame()
    
    # התחל משחק חדש
    player_hand = [game.deck.pop(), game.deck.pop()]
    dealer_hand = [game.deck.pop(), game.deck.pop()]
    
    player_value = game.calculate_hand_value(player_hand)
    dealer_value = game.calculate_hand_value([dealer_hand[0]])  # רק הקלף הגלוי
    
    game_state = {
        'deck': game.deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'player_value': player_value,
        'dealer_value': dealer_value,
        'game_over': False
    }
    
    # שמור את מצב המשחק
    db.r.setex(f"game:blackjack:{uid}", 300, str(game_state))
    
    # צור תצוגת קלפים
    player_cards = " ".join(player_hand)
    dealer_cards = f"{dealer_hand[0]} 🃏"  # הקלף השני מוסתר
    
    game_text = f"""
🃏 **בלאקג'ק - 21**

**הדילר:** {dealer_cards}
**ערך גלוי:** {dealer_value}

**היד שלך:** {player_cards}
**ערך היד שלך:** {player_value}

**בחר פעולה:**
"""
    
    keyboard = [
        [
            InlineKeyboardButton("👇 קח קלף", callback_data="bj_hit"),
            InlineKeyboardButton("✋ עצור", callback_data="bj_stand"),
            InlineKeyboardButton("💰 הכפיל", callback_data="bj_double")
        ],
        [
            InlineKeyboardButton("🔄 משחק חדש", callback_data="play_blackjack"),
            InlineKeyboardButton("🏠 תפריט", callback_data="start")
        ]
    ]
    
    await query.edit_message_text(
        text=game_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
