#!/usr/bin/env python3
"""
Unified cache management module for user prompt processing
Now uses orchestration_cache.py as backend with fallback compatibility
"""

import contextlib
import logging
import sys
import threading
from pathlib import Path
from typing import Any

# Enhanced caching imports (for fallback compatibility)
import diskcache
from cachetools import LRUCache, TTLCache
from joblib import Memory

# Add parent directory to path to import orchestration_cache
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from orchestration_cache import (
        ContextAwareCache,
        IntelligentCache,
        _context_cache,
        _global_cache,
        clear_cache,
        get_cache_stats,
        warm_cache,
    )
    HAS_ORCHESTRATION_CACHE = True
except ImportError:
    # Fallback if orchestration_cache is not available
    IntelligentCache = None
    ContextAwareCache = None
    HAS_ORCHESTRATION_CACHE = False

logger = logging.getLogger(__name__)


class UserPromptCacheManager:
    """Unified cache manager for user prompt processing using orchestration_cache backend"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

        # Use orchestration cache if available
        if HAS_ORCHESTRATION_CACHE:
            self.intelligent_cache = _global_cache
            self.context_cache_backend = _context_cache
            self.use_orchestration = True
            logger.info("UserPromptCacheManager using orchestration_cache backend")
        else:
            self.use_orchestration = False
            logger.warning("Orchestration cache not available, using fallback implementation")

            # Fallback: Original cache implementation
            self.prompt_cache = TTLCache(maxsize=500, ttl=600)  # 10 minutes
            self.context_cache = LRUCache(maxsize=100)
            self.file_analysis_cache = TTLCache(maxsize=200, ttl=300)  # 5 minutes
            self.command_cache = LRUCache(maxsize=300)
            self.disk_cache = diskcache.Cache(str(cache_dir / "user_prompt_cache"))
            self.joblib_memory = Memory(location=str(cache_dir / "user_prompt_joblib"), verbose=0)

            # Thread-safe locks
            self._prompt_lock = threading.RLock()
            self._context_lock = threading.RLock()
            self._file_lock = threading.RLock()
            self._command_lock = threading.RLock()

    def get_prompt_analysis(self, prompt_hash: str, default: Any = None) -> Any:
        """Get cached prompt analysis"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"prompt:{prompt_hash}")
            return value if hit else default
        else:
            with self._prompt_lock:
                return self.prompt_cache.get(prompt_hash, default)

    def set_prompt_analysis(self, prompt_hash: str, analysis: Any) -> None:
        """Cache prompt analysis"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"prompt:{prompt_hash}", analysis, ttl=600)
        else:
            with self._prompt_lock:
                self.prompt_cache[prompt_hash] = analysis

    def get_context(self, context_key: str, default: Any = None) -> Any:
        """Get cached context"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"context:{context_key}")
            return value if hit else default
        else:
            with self._context_lock:
                return self.context_cache.get(context_key, default)

    def set_context(self, context_key: str, context: Any) -> None:
        """Cache context"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"context:{context_key}", context, ttl=1800)  # 30 min for context
        else:
            with self._context_lock:
                self.context_cache[context_key] = context

    def get_file_analysis(self, file_path: str, default: Any = None) -> Any:
        """Get cached file analysis with context awareness"""
        if self.use_orchestration:
            # Use context-aware cache for file operations
            hit, value = self.context_cache_backend.get_file_based(
                f"file_analysis:{file_path}",
                [file_path],
                ttl=300
            )
            return value if hit else default
        else:
            with self._file_lock:
                return self.file_analysis_cache.get(file_path, default)

    def set_file_analysis(self, file_path: str, analysis: Any) -> None:
        """Cache file analysis with context awareness"""
        if self.use_orchestration:
            # Use context-aware cache for file operations
            self.context_cache_backend.put_file_based(
                f"file_analysis:{file_path}",
                analysis,
                [file_path],
                ttl=300
            )
        else:
            with self._file_lock:
                self.file_analysis_cache[file_path] = analysis

    def get_command_result(self, command_hash: str, default: Any = None) -> Any:
        """Get cached command result"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"cmd:{command_hash}")
            return value if hit else default
        else:
            with self._command_lock:
                return self.command_cache.get(command_hash, default)

    def set_command_result(self, command_hash: str, result: Any) -> None:
        """Cache command result"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"cmd:{command_hash}", result, ttl=1800)  # 30 min for commands
        else:
            with self._command_lock:
                self.command_cache[command_hash] = result

    def clear_all(self):
        """Clear all caches"""
        if self.use_orchestration:
            if clear_cache:
                clear_cache()  # Clear orchestration cache
                logger.info("Cleared orchestration cache for user prompt processing")
        else:
            # Fallback implementation
            with self._prompt_lock:
                self.prompt_cache.clear()
            with self._context_lock:
                self.context_cache.clear()
            with self._file_lock:
                self.file_analysis_cache.clear()
            with self._command_lock:
                self.command_cache.clear()

            with contextlib.suppress(Exception):
                self.disk_cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        if self.use_orchestration:
            # Get stats from orchestration cache
            stats = {'backend': 'orchestration_cache'}
            if get_cache_stats:
                stats.update(get_cache_stats())
            return stats
        else:
            # Fallback stats
            return {
                'backend': 'fallback_cache',
                'prompt_cache_size': len(self.prompt_cache),
                'context_cache_size': len(self.context_cache),
                'file_analysis_cache_size': len(self.file_analysis_cache),
                'command_cache_size': len(self.command_cache)
            }


# Utility functions for orchestration cache integration
def warm_user_prompt_cache():
    """Warm the user prompt cache with commonly used data"""
    if HAS_ORCHESTRATION_CACHE and warm_cache:
        try:
            warm_cache()
            logger.info("User prompt cache warmed using orchestration_cache")
        except Exception as e:
            logger.warning(f"Failed to warm user prompt cache: {e}")
    else:
        logger.info("User prompt cache warming skipped (orchestration cache not available)")

# Export main components
__all__ = [
    'UserPromptCacheManager',
    'warm_user_prompt_cache',
    'HAS_ORCHESTRATION_CACHE'
]
