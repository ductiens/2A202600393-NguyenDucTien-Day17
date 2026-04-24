"""
Graph state module
Defines TypedDict for MemoryState
"""

from typing import TypedDict, List, Dict, Any, Optional

class MemoryState(TypedDict):
    """State definition for the LangGraph memory agent"""
    
    # User interaction
    user_id: str
    user_input: str
    agent_response: Optional[str]
    
    # Memory components
    short_term_buffer: List[str]
    long_term_preferences: Dict[str, Any]
    episodic_trajectories: List[Dict[str, Any]]
    semantic_knowledge: Optional[Dict[str, Any]]
    
    # Context and metadata
    conversation_history: List[Dict[str, str]]
    current_step: str
    error_message: Optional[str]
    
    # Timestamp and session info
    session_id: str
    timestamp: str
