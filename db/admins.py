from utils.config import ADMIN_ID

def is_admin(user_id):
    # בדיקה פשוטה מול הקונפיג
    return str(user_id) == str(ADMIN_ID)
