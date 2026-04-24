"""
Configuration module
Contains environment variables and API keys
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the multi-memory agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database URLs
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Memory Configuration
    EPISODIC_STORAGE_PATH = os.getenv("EPISODIC_STORAGE_PATH", "data/episodic_memory.json")
    SHORT_TERM_BUFFER_SIZE = int(os.getenv("SHORT_TERM_BUFFER_SIZE", "10"))
    
    # Agent Configuration
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    SEMANTIC_SEARCH_RESULTS = int(os.getenv("SEMANTIC_SEARCH_RESULTS", "5"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/agent.log")
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check API keys
        if not cls.OPENAI_API_KEY:
            status["warnings"].append("OPENAI_API_KEY not set")
        
        if not cls.ANTHROPIC_API_KEY:
            status["warnings"].append("ANTHROPIC_API_KEY not set")
        
        # Check database connectivity (basic checks)
        try:
            import redis
            client = redis.from_url(cls.REDIS_URL)
            client.ping()
        except Exception as e:
            status["errors"].append(f"Redis connection failed: {e}")
            status["valid"] = False
        
        return status
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary (excluding sensitive data)"""
        return {
            "redis_url": cls.REDIS_URL,
            "chroma_persist_dir": cls.CHROMA_PERSIST_DIR,
            "episodic_storage_path": cls.EPISODIC_STORAGE_PATH,
            "short_term_buffer_size": cls.SHORT_TERM_BUFFER_SIZE,
            "max_conversation_history": cls.MAX_CONVERSATION_HISTORY,
            "semantic_search_results": cls.SEMANTIC_SEARCH_RESULTS,
            "log_level": cls.LOG_LEVEL,
            "log_file": cls.LOG_FILE,
            "has_openai_key": bool(cls.OPENAI_API_KEY),
            "has_anthropic_key": bool(cls.ANTHROPIC_API_KEY)
        }
