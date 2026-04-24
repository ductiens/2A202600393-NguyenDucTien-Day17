"""
Episodic memory module
Handles JSON file operations for past trajectories
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

class EpisodicMemory:
    def __init__(self, storage_path: str = "data/episodic_memory.json"):
        self.storage_path = storage_path
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def save_trajectory(self, user_id: str, trajectory: Dict[str, Any]):
        """Save a trajectory to JSON storage"""
        try:
            # Load existing data
            data = self.load_all_trajectories()
            
            # Add new trajectory
            if user_id not in data:
                data[user_id] = []
            
            trajectory_entry = {
                "timestamp": datetime.now().isoformat(),
                "trajectory": trajectory
            }
            data[user_id].append(trajectory_entry)
            
            # Save back to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Failed to save trajectory: {e}")
            return False
    
    def get_trajectories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trajectories for a user"""
        try:
            data = self.load_all_trajectories()
            user_trajectories = data.get(user_id, [])
            # Return most recent trajectories
            return sorted(user_trajectories, key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            print(f"Failed to get trajectories: {e}")
            return []
    
    def load_all_trajectories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all trajectories from JSON file"""
        if not os.path.exists(self.storage_path):
            return {}
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load trajectories: {e}")
            return {}
    
    def clear_trajectories(self, user_id: str):
        """Clear all trajectories for a user"""
        try:
            data = self.load_all_trajectories()
            if user_id in data:
                data[user_id] = []
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to clear trajectories: {e}")
            return False
