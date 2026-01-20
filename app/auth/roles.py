from enum import Enum
from functools import wraps
from app.database.manager import db

class Role(Enum):
    USER = 1
    ADMIN = 2
    SUPER_ADMIN = 3

def get_user_role(user_id: int) -> Role:
    """קבלת תפקיד משתמש מה-CRM"""
    user_data = db.get_user(user_id)
    if user_data.get("is_super_admin"):
        return Role.SUPER_ADMIN
    elif str(user_id) == str(db.ADMIN_ID):  # נניח ש-ADMIN_ID מוגדר ב-db
        return Role.ADMIN
    else:
        return Role.USER

def require_role(required_role: Role):
    """דקורטור למתן הרשאות לפקודות"""
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            user_role = get_user_role(user_id)
            
            if user_role.value < required_role.value:
                await update.message.reply_text("⛔ אין לך הרשאות מספיקות!")
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
