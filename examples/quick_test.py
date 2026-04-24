"""
Quick test script for Multi-Memory Agent
Simple example to test basic functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import MultiMemoryAgent
from datetime import datetime

def test_basic_functionality():
    """Test basic agent functionality"""
    print("🧪 Testing Multi-Memory Agent Basic Functionality")
    print("=" * 50)
    
    try:
        # Initialize agent
        agent = MultiMemoryAgent()
        print("✅ Agent initialized successfully")
        
        # Test simple interaction
        user_id = "test_user_001"
        test_messages = [
            "Hello, my name is John and I love Python programming",
            "What do you remember about me?",
            "Can you help me with machine learning concepts?",
            "What was my name again?"
        ]
        
        print("\n📝 Testing conversation flow:")
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Turn {i} ---")
            print(f"User: {message}")
            
            result = agent.process_message(user_id, message)
            
            if result["success"]:
                print(f"Agent: {result['response'][:100]}...")
                print(f"Memory Context: {result['memory_context']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        print("\n✅ Basic functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

def test_memory_components():
    """Test individual memory components"""
    print("\n🧠 Testing Memory Components")
    print("=" * 30)
    
    try:
        from memory.short_term import ShortTermMemory
        from memory.long_term import LongTermMemory
        from memory.episodic import EpisodicMemory
        
        # Test short-term memory
        stm = ShortTermMemory()
        stm.add_to_buffer("Test message 1")
        stm.add_to_buffer("Test message 2")
        print(f"✅ Short-term memory: {len(stm.get_buffer())} items, {stm.get_buffer_tokens()} tokens")
        
        # Test long-term memory (if Redis is available)
        ltm = LongTermMemory()
        if ltm.client:
            ltm.set_preference("test_user", "language", "Python")
            pref = ltm.get_preference("test_user", "language")
            print(f"✅ Long-term memory: {pref}")
        else:
            print("⚠️  Long-term memory: Redis not available")
        
        # Test episodic memory
        em = EpisodicMemory()
        trajectory = {
            "user_input": "Test query",
            "agent_response": "Test response",
            "timestamp": datetime.now().isoformat()
        }
        em.save_trajectory("test_user", trajectory)
        trajectories = em.get_trajectories("test_user")
        print(f"✅ Episodic memory: {len(trajectories)} trajectories saved")
        
    except Exception as e:
        print(f"❌ Memory component test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Quick Test Suite")
    print("=" * 40)
    
    success = True
    
    # Run tests
    success &= test_basic_functionality()
    success &= test_memory_components()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Your Multi-Memory Agent is ready to use.")
    else:
        print("❌ Some tests failed. Please check the configuration.")
    
    print("\n📖 Next steps:")
    print("1. Run: python src/main.py (interactive mode)")
    print("2. Run: python src/benchmark.py (benchmark suite)")
    print("3. Check README.md for detailed instructions")
