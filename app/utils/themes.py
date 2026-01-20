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
            }
        }
    
    def get_user_theme(self, user_id):
        theme = db.r.hget(f"user:{user_id}:settings", "theme")
        return theme if theme in self.themes else 'default'
    
    def set_user_theme(self, user_id, theme_name):
        if theme_name in self.themes:
            db.r.hset(f"user:{user_id}:settings", "theme", theme_name)
            return True
        return False

theme_system = ThemeSystem()
