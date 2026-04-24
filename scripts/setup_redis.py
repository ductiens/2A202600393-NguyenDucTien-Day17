"""
Setup script for Redis with sample data
"""

import redis
import json
import time
from datetime import datetime

def setup_redis_sample_data():
    """Setup sample data for testing"""
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Test connection
        r.ping()
        print("✅ Connected to Redis successfully")
        
        # Sample user preferences
        sample_users = {
            "user_001": {
                "name": "Alice",
                "language": "Python",
                "experience": "intermediate",
                "interests": "machine learning, data science, AI",
                "preferred_response_style": "detailed"
            },
            "user_002": {
                "name": "Bob", 
                "language": "JavaScript",
                "experience": "beginner",
                "interests": "web development, frontend, React",
                "preferred_response_style": "concise"
            },
            "user_003": {
                "name": "Charlie",
                "language": "Java", 
                "experience": "advanced",
                "interests": "backend, microservices, cloud computing",
                "preferred_response_style": "technical"
            }
        }
        
        # Add sample data to Redis
        for user_id, preferences in sample_users.items():
            for key, value in preferences.items():
                r.hset(f"user:{user_id}", key, value)
            print(f"✅ Added preferences for {user_id}")
        
        # Add some session data
        session_data = {
            "user_001:session_001": json.dumps({
                "start_time": datetime.now().isoformat(),
                "message_count": 5,
                "last_activity": datetime.now().isoformat()
            })
        }
        
        for key, value in session_data.items():
            r.set(key, value, ex=3600)  # Expire in 1 hour
        
        print("✅ Sample Redis data setup completed!")
        
        # Display what was added
        print("\n📊 Redis Data Summary:")
        for user_id in sample_users.keys():
            user_data = r.hgetall(f"user:{user_id}")
            print(f"  {user_id}: {len(user_data)} preferences")
        
        return True
        
    except redis.ConnectionError:
        print("❌ Cannot connect to Redis. Make sure Redis is running:")
        print("   docker run -d -p 6379:6379 redis:latest")
        print("   or: redis-server")
        return False
    except Exception as e:
        print(f"❌ Error setting up Redis: {e}")
        return False

def clear_redis_data():
    """Clear all sample data from Redis"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Clear user data
        keys = r.keys("user:*")
        if keys:
            r.delete(*keys)
            print(f"✅ Cleared {len(keys)} user records")
        
        # Clear session data
        session_keys = r.keys("*:session_*")
        if session_keys:
            r.delete(*session_keys)
            print(f"✅ Cleared {len(session_keys)} session records")
        
        print("✅ Redis data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing Redis: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_redis_data()
    else:
        setup_redis_sample_data()
