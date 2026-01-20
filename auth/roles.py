# צור את תיקיית auth
New-Item -Path "app/auth" -ItemType Directory -Force

# צור את קובץ roles.py
Set-Content -Path "app/auth/roles.py" -Value @'
# app/auth/roles.py
# ניהול הרשאות משתמשים

from app.database.manager import db

class UserRoles:
    """מחלקה לניהול הרשאות משתמשים לפי דרגה"""
    
    # הגדרות הרשאות לפי דרגה
    TIER_PERMISSIONS = {
        "Free": {
            "max_bet": 100,
            "mines_count": 5,
            "multiplier": 1.1,
            "daily_bonus": 100,
            "max_referrals": 10,
            "can_withdraw": False,
            "games_available": ["mines", "slots"]
        },
        "Pro": {
            "max_bet": 500,
            "mines_count": 3,
            "multiplier": 1.3,
            "daily_bonus": 200,
            "max_referrals": 50,
            "can_withdraw": True,
            "games_available": ["mines", "slots", "crash"]
        },
        "VIP": {
            "max_bet": 1000,
            "mines_count": 2,
            "multiplier": 1.5,
            "daily_bonus": 500,
            "max_referrals": 100,
            "can_withdraw": True,
            "games_available": ["mines", "slots", "crash"]
        }
    }
    
    @staticmethod
    def get_user_permissions(user_id):
        """קבל הרשאות משתמש לפי דרגתו"""
        user = db.get_user(user_id)
        tier = user.get("tier", "Free")
        return UserRoles.TIER_PERMISSIONS.get(tier, UserRoles.TIER_PERMISSIONS["Free"])
    
    @staticmethod
    def can_play_game(user_id, game_name):
        """בדוק אם משתמש יכול לשחק במשחק מסוים"""
        permissions = UserRoles.get_user_permissions(user_id)
        return game_name in permissions.get("games_available", [])
    
    @staticmethod
    def get_max_bet(user_id):
        """קבל הימור מקסימלי למשתמש"""
        permissions = UserRoles.get_user_permissions(user_id)
        return permissions.get("max_bet", 100)
    
    @staticmethod
    def get_mines_count(user_id):
        """קבל מספר מוקשים למשחק Mines"""
        permissions = UserRoles.get_user_permissions(user_id)
        return permissions.get("mines_count", 5)
    
    @staticmethod
    def get_multiplier(user_id):
        """קבל מכפיל זכייה"""
        permissions = UserRoles.get_user_permissions(user_id)
        return permissions.get("multiplier", 1.1)

# מופע גלובלי
user_roles = UserRoles()
'@

# צור גם קובץ __init__.py בתיקיית auth
New-Item -Path "app/auth/__init__.py" -ItemType File -Force
