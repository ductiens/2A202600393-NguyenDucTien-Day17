"""
Short-term memory module
Handles buffer & summary operations with token-based management
"""

import tiktoken
from typing import Any, List

class ShortTermMemory:
    def __init__(self):
        self.buffer = []
        self.max_token_limit = 1000  # Token-based limit instead of message count
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using cl100k_base encoding
        """
        if not text:
            return 0
        return len(self.tokenizer.encode(text))
    
    def count_buffer_tokens(self) -> int:
        """
        Count total tokens in the entire buffer
        """
        total_tokens = 0
        for item in self.buffer:
            # Convert item to string representation
            item_text = str(item)
            total_tokens += self.count_tokens(item_text)
        return total_tokens
    
    def add_to_buffer(self, message: Any):
        """
        Add message to buffer with token-based management
        Removes oldest messages if token limit is exceeded
        """
        # Add new message
        self.buffer.append(message)
        
        # Check if we exceed token limit
        current_tokens = self.count_buffer_tokens()
        
        # Remove oldest messages until we're within the token limit
        while current_tokens > self.max_token_limit and len(self.buffer) > 0:
            removed_message = self.buffer.pop(0)
            # Subtract tokens of removed message
            removed_tokens = self.count_tokens(str(removed_message))
            current_tokens -= removed_tokens
    
    def get_buffer(self) -> List[Any]:
        """
        Get current buffer contents
        """
        return self.buffer.copy()  # Return a copy to prevent external modification
    
    def get_buffer_tokens(self) -> int:
        """
        Get current token count of buffer
        """
        return self.count_buffer_tokens()
    
    def clear_buffer(self):
        """
        Clear the buffer
        """
        self.buffer = []
    
    def summarize_buffer(self) -> str:
        """
        Generate summary of buffer contents
        """
        if not self.buffer:
            return ""
        
        # Convert buffer items to strings and join
        buffer_texts = [str(msg) for msg in self.buffer]
        return " | ".join(buffer_texts)
    
    def get_buffer_info(self) -> dict:
        """
        Get information about current buffer state
        """
        return {
            "message_count": len(self.buffer),
            "token_count": self.count_buffer_tokens(),
            "token_limit": self.max_token_limit,
            "token_usage_percentage": (self.count_buffer_tokens() / self.max_token_limit) * 100
        }
