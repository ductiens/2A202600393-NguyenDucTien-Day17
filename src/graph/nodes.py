"""
Graph nodes module
Contains the main node functions for LangGraph
"""

import tiktoken
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from .state import MemoryState
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory
from ..memory.episodic import EpisodicMemory
from ..memory.semantic import SemanticMemory

# Token budget configuration
MAX_TOKENS = 4000
TOKENIZER = tiktoken.get_encoding("cl100k_base")

def load_memory(state: MemoryState) -> MemoryState:
    """Load relevant memories based on user input and context"""
    
    # Initialize memory components
    short_term = ShortTermMemory()
    long_term = LongTermMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()
    
    # Load short-term memory
    state["short_term_buffer"] = short_term.get_buffer()
    
    # Load long-term preferences
    state["long_term_preferences"] = long_term.get_all_preferences(state["user_id"])
    
    # Load episodic trajectories
    state["episodic_trajectories"] = episodic.get_trajectories(state["user_id"])
    
    # Query semantic knowledge if relevant
    if state["user_input"]:
        semantic_results = semantic.query_knowledge(state["user_input"])
        state["semantic_knowledge"] = semantic_results
    
    state["current_step"] = "agent_chat"
    return state

def count_tokens(text: str) -> int:
    """Count tokens using cl100k_base encoding"""
    if not text:
        return 0
    return len(TOKENIZER.encode(text))

def build_context_with_token_budget(state: MemoryState) -> str:
    """
    Build context string with token budget management.
    Priority order: Short-term > Long-term > Episodic > Semantic
    """
    user_input = state["user_input"]
    preferences = state["long_term_preferences"]
    trajectories = state["episodic_trajectories"]
    semantic_knowledge = state["semantic_knowledge"]
    short_term_buffer = state["short_term_buffer"]
    
    # Always keep user input
    context_parts = [f"User Input: {user_input}"]
    current_tokens = count_tokens(context_parts[0])
    
    # Reserve tokens for system prompt and response overhead
    reserved_tokens = 500  # For system instructions and LLM response
    available_tokens = MAX_TOKENS - reserved_tokens - current_tokens
    
    # Priority 1: Short-term memory (highest priority)
    if short_term_buffer and available_tokens > 0:
        short_term_text = "Short-term Memory:\n" + "\n".join([
            f"- {msg}" for msg in short_term_buffer[-5:]  # Last 5 items
        ])
        short_term_tokens = count_tokens(short_term_text)
        
        if short_term_tokens <= available_tokens:
            context_parts.append(short_term_text)
            current_tokens += short_term_tokens
            available_tokens -= short_term_tokens
        else:
            # Try to include truncated short-term memory
            truncated = "Short-term Memory (recent):\n" + "\n".join([
                f"- {msg}" for msg in short_term_buffer[-2:]  # Last 2 items only
            ])
            truncated_tokens = count_tokens(truncated)
            if truncated_tokens <= available_tokens:
                context_parts.append(truncated)
                current_tokens += truncated_tokens
                available_tokens -= truncated_tokens
    
    # Priority 2: Long-term preferences
    if preferences and available_tokens > 0:
        pref_text = "User Preferences:\n" + "\n".join([
            f"- {k}: {v}" for k, v in list(preferences.items())[:10]  # Top 10 preferences
        ])
        pref_tokens = count_tokens(pref_text)
        
        if pref_tokens <= available_tokens:
            context_parts.append(pref_text)
            current_tokens += pref_tokens
            available_tokens -= pref_tokens
        else:
            # Include key preferences only
            key_prefs = "User Preferences (key):\n" + "\n".join([
                f"- {k}: {v}" for k, v in list(preferences.items())[:3]  # Top 3 only
            ])
            key_tokens = count_tokens(key_prefs)
            if key_tokens <= available_tokens:
                context_parts.append(key_prefs)
                current_tokens += key_tokens
                available_tokens -= key_tokens
    
    # Priority 3: Episodic trajectories
    if trajectories and available_tokens > 0:
        recent_trajectories = trajectories[:3]  # Last 3 trajectories
        episodic_parts = []
        for i, traj in enumerate(recent_trajectories):
            traj_text = f"Trajectory {i+1}: {traj.get('trajectory', {}).get('user_input', 'N/A')}"
            episodic_parts.append(traj_text)
        
        episodic_text = "Past Interactions:\n" + "\n".join(episodic_parts)
        episodic_tokens = count_tokens(episodic_text)
        
        if episodic_tokens <= available_tokens:
            context_parts.append(episodic_text)
            current_tokens += episodic_tokens
            available_tokens -= episodic_tokens
        else:
            # Include only most recent trajectory
            single_traj = "Past Interaction (most recent):\n" + episodic_parts[0] if episodic_parts else ""
            single_tokens = count_tokens(single_traj)
            if single_tokens <= available_tokens:
                context_parts.append(single_traj)
                current_tokens += single_tokens
                available_tokens -= single_tokens
    
    # Priority 4: Semantic knowledge (lowest priority)
    if semantic_knowledge and available_tokens > 0 and semantic_knowledge.get("documents"):
        docs = semantic_knowledge["documents"][0][:2]  # Top 2 documents
        semantic_parts = []
        for i, doc in enumerate(docs):
            semantic_parts.append(f"Knowledge {i+1}: {doc[:200]}...")  # Truncate long docs
        
        semantic_text = "Relevant Knowledge:\n" + "\n".join(semantic_parts)
        semantic_tokens = count_tokens(semantic_text)
        
        if semantic_tokens <= available_tokens:
            context_parts.append(semantic_text)
    
    return "\n\n".join(context_parts)

def agent_chat(state: MemoryState) -> MemoryState:
    """
    Main agent chat function with token budget management and LLM integration
    """
    try:
        # Build context with token budget management
        context = build_context_with_token_budget(state)
        
        # Create comprehensive system prompt
        system_prompt = """You are a helpful AI assistant with access to multiple memory systems. 
Use the provided context to give personalized and informed responses.

Context Information:
- User preferences help you tailor responses to their needs
- Past interactions provide continuity and context
- Short-term memory contains recent conversation details
- Semantic knowledge provides relevant domain information

Always be helpful, accurate, and maintain conversation continuity.
If you don't have enough context, ask clarifying questions."""
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
        # Create the prompt
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context}\n\nUser Question: {state['user_input']}")
        ]
        
        # Invoke LLM
        response = llm.invoke(messages)
        state["agent_response"] = response.content
        
    except Exception as e:
        # Fallback response if LLM fails
        state["agent_response"] = f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    state["current_step"] = "save_memory"
    return state

def save_memory(state: MemoryState) -> MemoryState:
    """Save the current interaction to appropriate memory stores"""
    
    # Initialize memory components
    short_term = ShortTermMemory()
    long_term = LongTermMemory()
    episodic = EpisodicMemory()
    
    # Save to short-term memory
    short_term.add_to_buffer({
        "user_input": state["user_input"],
        "agent_response": state["agent_response"],
        "timestamp": state["timestamp"]
    })
    
    # Save trajectory to episodic memory
    trajectory = {
        "user_input": state["user_input"],
        "agent_response": state["agent_response"],
        "context": {
            "preferences_used": state["long_term_preferences"],
            "semantic_results": state["semantic_knowledge"]
        },
        "timestamp": state["timestamp"]
    }
    episodic.save_trajectory(state["user_id"], trajectory)
    
    # Update conversation history
    state["conversation_history"].append({
        "user": state["user_input"],
        "agent": state["agent_response"],
        "timestamp": state["timestamp"]
    })
    
    state["current_step"] = "complete"
    return state

def should_continue(state: MemoryState) -> bool:
    """Determine if the conversation should continue"""
    return state["current_step"] != "complete"
