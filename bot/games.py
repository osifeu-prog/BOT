"""Game logic"""
import random

class SlotsGame:
    SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
    
    def __init__(self, win_chance):
        self.win_chance = win_chance
    
    def play(self):
        reels = [random.choice(self.SYMBOLS) for _ in range(3)]
        result = ' '.join(reels)
        
        if reels[0] == reels[1] == reels[2]:
            if reels[0] == '7️⃣':
                return True, result, 100
            elif reels[0] == '💎':
                return True, result, 50
            return True, result, 10
        elif reels[0] == reels[1] or reels[1] == reels[2]:
            return True, result, 2
        
        return random.randint(1, 100) <= self.win_chance, result, 0

class RouletteGame:
    RED = list(range(1, 11)) + list(range(19, 29))
    BLACK = list(range(11, 19)) + list(range(29, 37))
    
    def play(self, bet_type):
        result = random.randint(0, 36)
        if bet_type == 'red':
            return result in self.RED, result
        elif bet_type == 'black':
            return result in self.BLACK, result
        elif bet_type == 'green':
            return result == 0, result
        return False, result

class DiceGame:
    def __init__(self, win_chance):
        self.win_chance = win_chance
    
    def play(self):
        roll = random.randint(1, 100)
        win = roll >= (100 - self.win_chance)
        return win, roll
