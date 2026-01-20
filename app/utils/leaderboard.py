# app/utils/leaderboard.py
from app.database.manager import db
from datetime import datetime, timedelta

class LeaderboardSystem:
    def __init__(self):
        self.periods = {
            'daily': 86400,
            'weekly': 604800,
            'monthly': 2592000,
            'all_time': 0
        }
    
    def update_score(self, user_id, score_type, amount):
        """עדכן ניקוד במערכת הלוח תוצאות"""
        for period_name, ttl in self.periods.items():
            if ttl == 0:
                # all_time - אין TTL
                key = f"leaderboard:{period_name}:{score_type}"
                db.r.zincrby(key, amount, user_id)
            else:
                key = f"leaderboard:{period_name}:{score_type}"
                db.r.zincrby(key, amount, user_id)
                
                # הגדר TTL רק אם אין אחד כבר
                if db.r.ttl(key) == -1:
                    db.r.expire(key, ttl)
    
    def get_leaderboard(self, score_type='balance', period='weekly', limit=10):
        """קבל את לוח התוצאות"""
        key = f"leaderboard:{period}:{score_type}"
        
        # קבל את הטופ N
        top_users = db.r.zrevrange(key, 0, limit-1, withscores=True)
        
        leaderboard = []
        for rank, (user_id, score) in enumerate(top_users, 1):
            user_data = db.get_user(user_id)
            if user_data:
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_id,
                    'username': user_data.get('username', 'Unknown'),
                    'first_name': user_data.get('first_name', 'User'),
                    'score': int(score),
                    'tier': user_data.get('tier', 'Free')
                })
        
        return leaderboard
    
    def get_user_rank(self, user_id, score_type='balance', period='weekly'):
        """קבל את הדירוג של משתמש ספציפי"""
        key = f"leaderboard:{period}:{score_type}"
        
        # קבל את הדירוג (0-indexed)
        rank = db.r.zrevrank(key, user_id)
        score = db.r.zscore(key, user_id)
        
        if rank is not None:
            return {
                'rank': rank + 1,  # המר ל-1-indexed
                'score': int(score) if score else 0
            }
        
        return None

leaderboard = LeaderboardSystem()

# פונקציות עזר לעדכון אוטומטי
def update_win_leaderboard(user_id, win_amount):
    """עדכן לוח תוצאות לאחר ניצחון"""
    leaderboard.update_score(user_id, 'total_wins', 1)
    leaderboard.update_score(user_id, 'total_winnings', win_amount)

def update_game_leaderboard(user_id, game_name):
    """עדכן לוח תוצאות לאחר משחק"""
    leaderboard.update_score(user_id, f'games_played_{game_name}', 1)
