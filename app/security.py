import time
from typing import Dict, List

class RateLimiter:
    def __init__(self, max_calls: int = 5, time_frame: int = 60):
        self.user_calls: Dict[int, List[float]] = {}
        self.max_calls = max_calls
        self.time_frame = time_frame
    
    def check_rate_limit(self, user_id: int) -> bool:
        current_time = time.time()
        
        if user_id not in self.user_calls:
            self.user_calls[user_id] = []
        
        # Clean old calls
        self.user_calls[user_id] = [
            call_time for call_time in self.user_calls[user_id]
            if current_time - call_time < self.time_frame
        ]
        
        if len(self.user_calls[user_id]) >= self.max_calls:
            return False
        
        self.user_calls[user_id].append(current_time)
        return True

# Global instance
rate_limiter = RateLimiter()
