"""
Main entry point for the Multi-Memory Agent
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from graph.builder import build_memory_graph, run_memory_agent
from config import Config

class MultiMemoryAgent:
    """Main agent class that orchestrates the memory system"""
    
    def __init__(self):
        self.app = build_memory_graph()
        self.config = Config()
        
        # Validate configuration
        config_status = self.config.validate_config()
        if not config_status["valid"]:
            print("Configuration errors found:")
            for error in config_status["errors"]:
                print(f"  - {error}")
            return
        
        if config_status["warnings"]:
            print("Configuration warnings:")
            for warning in config_status["warnings"]:
                print(f"  - {warning}")
    
    def process_message(self, user_id: str, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user message through the memory agent"""
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Create initial state
        initial_state = {
            "user_id": user_id,
            "user_input": user_input,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Run the agent
            result = run_memory_agent(self.app, initial_state)
            return {
                "success": True,
                "response": result["agent_response"],
                "session_id": session_id,
                "timestamp": result["timestamp"],
                "memory_context": {
                    "preferences_used": result["long_term_preferences"],
                    "trajectories_count": len(result["episodic_trajectories"]),
                    "semantic_results": result["semantic_knowledge"] is not None
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def set_user_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Set a user preference in long-term memory"""
        from memory.long_term import LongTermMemory
        
        long_term = LongTermMemory(self.config.REDIS_URL)
        return long_term.set_preference(user_id, key, value)
    
    def get_user_preference(self, user_id: str, key: str) -> Any:
        """Get a user preference from long-term memory"""
        from memory.long_term import LongTermMemory
        
        long_term = LongTermMemory(self.config.REDIS_URL)
        return long_term.get_preference(user_id, key)

def main():
    """Main function to run the agent interactively"""
    print("Multi-Memory Agent - Interactive Mode")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    agent = MultiMemoryAgent()
    user_id = "default_user"
    session_id = str(uuid.uuid4())
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process the message
            result = agent.process_message(user_id, user_input, session_id)
            
            if result["success"]:
                print(f"\nAgent: {result['response']}")
                
                # Show memory context (optional)
                if result["memory_context"]["preferences_used"]:
                    print(f"[Used {len(result['memory_context']['preferences_used'])} preferences]")
                if result["memory_context"]["trajectories_count"] > 0:
                    print(f"[Referenced {result['memory_context']['trajectories_count']} past interactions]")
                if result["memory_context"]["semantic_results"]:
                    print("[Used semantic knowledge]")
            else:
                print(f"\nError: {result['error']}")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
