from app.database.manager import db

class LeaderboardSystem:
    def __init__(self):
        self.periods = {'daily': 86400, 'weekly': 604800, 'monthly': 2592000, 'all_time': 0}
    
    def update_score(self, user_id, score_type, amount):
        for period_name, ttl in self.periods.items():
            key = f"leaderboard:{period_name}:{score_type}"
            db.r.zincrby(key, amount, user_id)
            if ttl > 0 and db.r.ttl(key) == -1:
                db.r.expire(key, ttl)
    
    def get_leaderboard(self, score_type='balance', period='weekly', limit=10):
        key = f"leaderboard:{period}:{score_type}"
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
        key = f"leaderboard:{period}:{score_type}"
        rank = db.r.zrevrank(key, user_id)
        score = db.r.zscore(key, user_id)
        
        if rank is not None:
            return {'rank': rank + 1, 'score': int(score) if score else 0}
        return None

leaderboard = LeaderboardSystem()
