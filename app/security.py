import time
from collections import defaultdict

class SmartRateLimiter:
    def __init__(self):
        self.limits = {
            'default': {'requests': 20, 'seconds': 60},
            'game_action': {'requests': 30, 'seconds': 60},
            'menu_navigation': {'requests': 40, 'seconds': 60},
            'admin': {'requests': 100, 'seconds': 60}
        }
        self.user_requests = defaultdict(lambda: defaultdict(list))
    
    def check_rate_limit(self, user_id, action_type='default'):
        now = time.time()
        user_reqs = self.user_requests[user_id][action_type]
        
        user_reqs = [req_time for req_time in user_reqs if now - req_time < self.limits[action_type]['seconds']]
        self.user_requests[user_id][action_type] = user_reqs
        
        if len(user_reqs) >= self.limits[action_type]['requests']:
            wait_time = int(self.limits[action_type]['seconds'] - (now - user_reqs[0]))
            return False, wait_time
        
        user_reqs.append(now)
        return True, 0
    
    def reset_user(self, user_id, action_type=None):
        if action_type:
            if user_id in self.user_requests and action_type in self.user_requests[user_id]:
                del self.user_requests[user_id][action_type]
        else:
            if user_id in self.user_requests:
                del self.user_requests[user_id]

smart_rate_limiter = SmartRateLimiter()
