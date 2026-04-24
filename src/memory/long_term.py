"""
Long-term memory module
Handles Redis connection for user preferences
"""

import redis
from typing import Dict, Any, Optional

class LongTermMemory:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(self.redis_url)
            self.client.ping()  # Test connection
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def set_preference(self, user_id: str, key: str, value: Any):
        """Set user preference"""
        if not self.client:
            return False
        
        try:
            self.client.hset(f"user:{user_id}", key, str(value))
            return True
        except Exception as e:
            print(f"Failed to set preference: {e}")
            return False
    
    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """Get user preference"""
        if not self.client:
            return None
        
        try:
            return self.client.hget(f"user:{user_id}", key)
        except Exception as e:
            print(f"Failed to get preference: {e}")
            return None
    
    def get_all_preferences(self, user_id: str) -> Dict[str, str]:
        """Get all user preferences"""
        if not self.client:
            return {}
        
        try:
            prefs = self.client.hgetall(f"user:{user_id}")
            return {k.decode(): v.decode() for k, v in prefs.items()}
        except Exception as e:
            print(f"Failed to get all preferences: {e}")
            return {}
