"""
Graph builder module
Compiles the LangGraph for the memory agent
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any
from .state import MemoryState
from .nodes import load_memory, agent_chat, save_memory, should_continue

def build_memory_graph() -> StateGraph:
    """Build and compile the LangGraph for memory agent"""
    
    # Create the graph
    workflow = StateGraph(MemoryState)
    
    # Add nodes
    workflow.add_node("load_memory", load_memory)
    workflow.add_node("agent_chat", agent_chat)
    workflow.add_node("save_memory", save_memory)
    
    # Add edges
    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "agent_chat")
    workflow.add_edge("agent_chat", "save_memory")
    workflow.add_edge("save_memory", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def run_memory_agent(app: StateGraph, initial_state: Dict[str, Any]) -> MemoryState:
    """Run the memory agent with initial state"""
    
    # Ensure required fields are present
    required_fields = ["user_id", "user_input", "session_id", "timestamp"]
    for field in required_fields:
        if field not in initial_state:
            raise ValueError(f"Missing required field: {field}")
    
    # Set default values
    state = MemoryState({
        "user_id": initial_state["user_id"],
        "user_input": initial_state["user_input"],
        "session_id": initial_state["session_id"],
        "timestamp": initial_state["timestamp"],
        "agent_response": None,
        "short_term_buffer": [],
        "long_term_preferences": {},
        "episodic_trajectories": [],
        "semantic_knowledge": None,
        "conversation_history": [],
        "current_step": "load_memory",
        "error_message": None
    })
    
    # Run the graph
    result = app.invoke(state)
    
    return result
