"""
Async operations and parallel execution for Claude Code hooks
"""

# Re-export from parallel_executor if it exists
try:
    from .parallel_executor import *
except ImportError:
    # Module might not exist yet
    pass

__all__ = []
