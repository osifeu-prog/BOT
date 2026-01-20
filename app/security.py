# app/security.py - גרסה משופרת
import time
from collections import defaultdict
import asyncio

class SmartRateLimiter:
    def __init__(self):
        # הגדרות שונות לסוגי פעולות
        self.limits = {
            'default': {'requests': 10, 'seconds': 60},
            'game_action': {'requests': 20, 'seconds': 60},
            'menu_navigation': {'requests': 30, 'seconds': 60},
            'admin': {'requests': 50, 'seconds': 60}
        }
        
        self.user_requests = defaultdict(lambda: defaultdict(list))
    
    def check_rate_limit(self, user_id, action_type='default'):
        """בדוק מגבלת בקשות חכמה עם סיווג פעולות"""
        now = time.time()
        user_reqs = self.user_requests[user_id][action_type]
        
        # נקה בקשות ישנות
        user_reqs = [req_time for req_time in user_reqs if now - req_time < self.limits[action_type]['seconds']]
        self.user_requests[user_id][action_type] = user_reqs
        
        # בדוק אם חרג מהמגבלה
        if len(user_reqs) >= self.limits[action_type]['requests']:
            wait_time = int(self.limits[action_type]['seconds'] - (now - user_reqs[0]))
            return False, wait_time
        
        # הוסף בקשה חדשה
        user_reqs.append(now)
        return True, 0
    
    def reset_user(self, user_id, action_type=None):
        """אפס מגבלות למשתמש"""
        if action_type:
            if user_id in self.user_requests and action_type in self.user_requests[user_id]:
                del self.user_requests[user_id][action_type]
        else:
            if user_id in self.user_requests:
                del self.user_requests[user_id]

# מופע גלובלי
smart_rate_limiter = SmartRateLimiter()


# תוסף: מערכת אימות משתמשים מתקדמת
class AdvancedSecurity:
    def __init__(self):
        self.suspicious_activity = defaultdict(int)
    
    def log_activity(self, user_id, action):
        """רישום פעילות לזיהוי התנהגות חשודה"""
        # פעולות חשודות
        suspicious_actions = ['rapid_clicks', 'game_exploit', 'spam']
        
        if action in suspicious_actions:
            self.suspicious_activity[user_id] += 1
            
            # אם יש יותר מדי פעילות חשודה, הגבל את המשתמש
            if self.suspicious_activity[user_id] > 5:
                return False
        
        return True
    
    def is_user_allowed(self, user_id, tier):
        """בדוק אם משתמש מורשה לפי דרגתו"""
        # בדיקות נוספות לפי דרגה
        tier_checks = {
            'Free': {'min_balance': 0, 'max_bet': 100, 'daily_limit': 10},
            'Pro': {'min_balance': 0, 'max_bet': 500, 'daily_limit': 50},
            'VIP': {'min_balance': 0, 'max_bet': 1000, 'daily_limit': 100}
        }
        
        return tier in tier_checks

advanced_security = AdvancedSecurity()
