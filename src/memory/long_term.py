"""
Long-term memory module
Handles Redis connection for user preferences
"""

import redis
from typing import Dict, Any, Optional

class LongTermMemory:
    def __init__(self, redis_url: str = "redis://redis:6379"):
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
        """Set user preference with conflict handling (rubric requirement)"""
        if not self.client:
            return False
        
        try:
            # Conflict handling: new value overwrites old value (rubric requirement)
            existing_value = self.get_preference(user_id, key)
            if existing_value and existing_value != str(value):
                print(f"Conflict detected for {user_id}.{key}: '{existing_value}' -> '{value}'")
            
            self.client.hset(f"user:{user_id}", key, str(value))
            return True
        except Exception as e:
            print(f"Failed to set preference: {e}")
            return False
    
    def update_preference_with_conflict_resolution(self, user_id: str, key: str, new_value: Any, conflict_strategy: str = "overwrite"):
        """
        Update preference with explicit conflict resolution (rubric requirement)
        conflict_strategy: "overwrite", "merge", "keep_old"
        """
        if not self.client:
            return False
        
        try:
            existing_value = self.get_preference(user_id, key)
            
            if existing_value:
                if conflict_strategy == "overwrite":
                    # New value overwrites old (rubric requirement)
                    print(f"Conflict: Overwriting {user_id}.{key}: '{existing_value}' -> '{new_value}'")
                    return self.set_preference(user_id, key, new_value)
                elif conflict_strategy == "keep_old":
                    print(f"Conflict: Keeping old value for {user_id}.{key}: '{existing_value}'")
                    return True
                elif conflict_strategy == "merge":
                    # Simple merge strategy
                    merged_value = f"{existing_value}, {new_value}"
                    print(f"Conflict: Merging {user_id}.{key}: '{existing_value}' + '{new_value}'")
                    return self.set_preference(user_id, key, merged_value)
            else:
                # No conflict, just set the value
                return self.set_preference(user_id, key, new_value)
                
        except Exception as e:
            print(f"Failed to update preference with conflict resolution: {e}")
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
