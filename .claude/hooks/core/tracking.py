"""
Hook tracking module for Claude Code hooks.
Provides tracking and lifecycle logging for hook executions.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)
lifecycle_logger = logging.getLogger("lifecycle")


class HookTracker:
    """Track hook execution lifecycle and performance"""

    def __init__(self):
        self.start_time = None
        self.hook_type = None
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    def start(self, hook_type: str, context: dict[str, Any]):
        """Start tracking a hook execution"""
        self.start_time = time.time()
        self.hook_type = hook_type
        lifecycle_logger.info(f"🚀 HOOK START: {hook_type} | Session: {self.session_id}")
        logger.debug(f"Hook context: {json.dumps(context, indent=2)}")

    def end(self, success: bool, duration: float, result: Any = None):
        """End tracking with success/failure status"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        lifecycle_logger.info(
            f"{status}: {self.hook_type} | Duration: {duration:.2f}s | Session: {self.session_id}"
        )
        if result:
            logger.debug(f"Hook result: {result}")


# Global hook tracker instance
hook_tracker = HookTracker()


# Export main components
__all__ = ['HookTracker', 'hook_tracker']
