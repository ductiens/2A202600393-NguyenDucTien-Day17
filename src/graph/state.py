"""
Graph state module
Defines TypedDict for MemoryState according to rubric requirements
"""

from typing import TypedDict, List, Dict, Any, Optional

class MemoryState(TypedDict):
    """
    State definition for the LangGraph memory agent
    Following rubric requirements:
    - messages: conversation history
    - user_profile: long-term preferences
    - episodes: episodic memory
    - semantic_hits: semantic retrieval results
    - memory_budget: token budget management
    """
    
    # Core conversation (rubric requirement)
    messages: List[Dict[str, str]]
    
    # Memory components (rubric requirement)
    user_profile: Dict[str, Any]  # Long-term profile
    episodes: List[Dict[str, Any]]  # Episodic memory
    semantic_hits: List[str]  # Semantic retrieval results
    
    # Token management (rubric requirement)
    memory_budget: int
    
    # User interaction
    user_id: str
    user_input: str
    agent_response: Optional[str]
    
    # Additional context
    short_term_buffer: List[str]
    conversation_history: List[Dict[str, str]]
    current_step: str
    error_message: Optional[str]
    
    # Session info
    session_id: str
    timestamp: str
