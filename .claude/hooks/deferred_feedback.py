#!/usr/bin/env python3
"""
Deferred Feedback System for Claude Code Hooks
Safely queues feedback from post-edit hooks and delivers it during pre-tool-use hooks
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Feedback queue file location
FEEDBACK_QUEUE_FILE = Path.home() / '.claude' / 'hooks_feedback_queue.json'
FEEDBACK_QUEUE_FILE.parent.mkdir(exist_ok=True)

class DeferredFeedbackManager:
    """Manages deferred feedback delivery to prevent API breaks"""
    
    def __init__(self):
        self.queue_file = FEEDBACK_QUEUE_FILE
    
    def store_feedback(self, message: str, priority: str = "normal", source: str = "post-edit") -> None:
        """Store feedback for later delivery during pre-tool-use"""
        feedback_item = {
            "message": message,
            "timestamp": time.time(),
            "priority": priority,
            "source": source,
            "id": f"{source}_{int(time.time())}_{hash(message) % 10000}"
        }
        
        queue = self._load_queue()
        queue.append(feedback_item)
        self._save_queue(queue)
    
    def get_pending_feedback(self, clear_after: bool = True) -> List[Dict[str, Any]]:
        """Get all pending feedback items"""
        queue = self._load_queue()
        
        if clear_after:
            self._clear_queue()
        
        return queue
    
    def has_pending_feedback(self) -> bool:
        """Check if there's any pending feedback"""
        queue = self._load_queue()
        return len(queue) > 0
    
    def format_feedback_for_claude(self) -> str:
        """Format all pending feedback for Claude delivery"""
        queue = self.get_pending_feedback(clear_after=True)
        
        if not queue:
            return ""
        
        # Sort by priority and timestamp
        priority_order = {"high": 0, "normal": 1, "low": 2}
        queue.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["timestamp"]))
        
        messages = []
        for item in queue:
            priority_emoji = "🔴" if item["priority"] == "high" else "🟡" if item["priority"] == "normal" else "🟢"
            messages.append(f"{priority_emoji} {item['message']}")
        
        combined = "\n\n".join(messages)
        
        return (
            f"📢 DEFERRED FEEDBACK FROM PREVIOUS OPERATIONS:\n\n"
            f"{combined}\n\n"
            f"💡 These suggestions were safely queued to prevent API errors.\n"
            f"Consider these recommendations for your next actions!"
        )
    
    def _load_queue(self) -> List[Dict[str, Any]]:
        """Load feedback queue from file"""
        if not self.queue_file.exists():
            return []
        
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_queue(self, queue: List[Dict[str, Any]]) -> None:
        """Save feedback queue to file"""
        try:
            # Keep only last 50 items to prevent unbounded growth
            queue = queue[-50:]
            
            with open(self.queue_file, 'w') as f:
                json.dump(queue, f, indent=2)
        except Exception:
            pass  # Fail silently to not break hook execution
    
    def _clear_queue(self) -> None:
        """Clear the feedback queue"""
        try:
            if self.queue_file.exists():
                self.queue_file.unlink()
        except Exception:
            pass

# Global instance
deferred_feedback = DeferredFeedbackManager()

# Convenience functions
def queue_feedback(message: str, priority: str = "normal", source: str = "post-edit") -> None:
    """Queue feedback for later delivery"""
    deferred_feedback.store_feedback(message, priority, source)

def deliver_queued_feedback() -> str:
    """Get formatted feedback for Claude delivery"""
    return deferred_feedback.format_feedback_for_claude()

def has_queued_feedback() -> bool:
    """Check if there's queued feedback waiting"""
    return deferred_feedback.has_pending_feedback()