import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=5, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = defaultdict(list)
    
    def check_rate_limit(self, user_id):
        """Check if user has exceeded rate limit"""
        now = time.time()
        user_reqs = self.user_requests[user_id]
        
        # Remove old requests
        user_reqs = [req_time for req_time in user_reqs if now - req_time < self.time_window]
        self.user_requests[user_id] = user_reqs
        
        if len(user_reqs) >= self.max_requests:
            return False
        
        # Add current request
        user_reqs.append(now)
        return True
    
    def reset_user(self, user_id):
        """Reset rate limit for a user"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]

# Global instance
rate_limiter = RateLimiter(max_requests=5, time_window=60)
