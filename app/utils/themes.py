# app/utils/themes.py
from app.database.manager import db

class ThemeSystem:
    def __init__(self):
        self.themes = {
            'default': {
                'name': 'ברירת מחדל',
                'primary_color': '🔵',
                'secondary_color': '🟡',
                'game_icons': {'mines': '💣', 'slots': '🎰', 'crash': '🚀'}
            },
            'dark': {
                'name': 'מצב לילה',
                'primary_color': '⚫',
                'secondary_color': '🟣',
                'game_icons': {'mines': '💀', 'slots': '🎲', 'crash': '☄️'}
            },
            'gold': {
                'name': 'ערכת זהב',
                'primary_color': '💰',
                'secondary_color': '👑',
                'game_icons': {'mines': '💎', 'slots': '✨', 'crash': '🚁'}
            },
            'neon': {
                'name': 'ניאון',
                'primary_color': '💚',
                'secondary_color': '💖',
                'game_icons': {'mines': '⚡', 'slots': '🌈', 'crash': '🎆'}
            }
        }
    
    def get_user_theme(self, user_id):
        """קבל את ערכת הנושא של המשתמש"""
        theme = db.r.hget(f"user:{user_id}:settings", "theme")
        return theme if theme in self.themes else 'default'
    
    def set_user_theme(self, user_id, theme_name):
        """הגדר ערכת נושא למשתמש"""
        if theme_name in self.themes:
            db.r.hset(f"user:{user_id}:settings", "theme", theme_name)
            return True
        return False
    
    def apply_theme_to_text(self, user_id, text, element_type='welcome'):
        """החל את ערכת הנושא על טקסט"""
        theme_name = self.get_user_theme(user_id)
        theme = self.themes[theme_name]
        
        # החלף אמוג'ים לפי ערכת הנושא
        if element_type == 'welcome':
            text = text.replace('🎰', theme['primary_color'])
            text = text.replace('💎', theme['secondary_color'])
        
        return text

theme_system = ThemeSystem()
