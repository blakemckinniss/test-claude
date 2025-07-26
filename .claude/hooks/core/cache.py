"""
Unified cache management module for Claude Code hooks.
Provides multi-level caching using orchestration_cache.py as backend.
"""

import contextlib
import logging
import sys
import threading
from functools import wraps
from pathlib import Path
from typing import Any

# Enhanced caching imports (fallback compatibility)
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
        _performance_monitor,
        cached,
        clear_cache,
        get_cache_stats,
        get_performance_report,
        warm_cache,
    )
    HAS_ORCHESTRATION_CACHE = True
except ImportError:
    # Fallback if orchestration_cache is not available
    IntelligentCache = None
    ContextAwareCache = None
    HAS_ORCHESTRATION_CACHE = False

# Import lru_dict or provide fallback
try:
    from lru_dict import LRUDict  # type: ignore
    HAS_LRU_DICT = True
except ImportError:
    HAS_LRU_DICT = False
    # Fallback if lru_dict is not available
    class LRUDict(dict):
        """Simple LRU dict fallback implementation"""
        def __init__(self, maxsize: int):
            super().__init__()
            self.maxsize = maxsize

        def __setitem__(self, key, value):
            if len(self) >= self.maxsize and key not in self:
                # Remove oldest item (simple FIFO for fallback)
                oldest_key = next(iter(self))
                del self[oldest_key]
            super().__setitem__(key, value)

# Setup cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


class CacheManager:
    """Unified caching system using orchestration_cache.py as backend with fallback compatibility"""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir

        # Use orchestration cache if available
        if HAS_ORCHESTRATION_CACHE:
            self.intelligent_cache = _global_cache
            self.context_cache = _context_cache
            self.use_orchestration = True
            logger.info("Using orchestration_cache.py backend")
        else:
            self.use_orchestration = False
            logger.warning("Orchestration cache not available, using fallback implementation")

            # Fallback: Original cache implementation
            self.l1_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes TTL
            self.l2_cache = LRUCache(maxsize=5000)
            self.l3_cache = diskcache.Cache(str(cache_dir / "disk_cache"))
            self.lru_dict = LRUDict(2000)
            self.joblib_memory = Memory(location=str(cache_dir / "joblib_cache"), verbose=0)

            # Specialized caches
            self.command_cache = LRUCache(maxsize=500)
            self.file_cache = TTLCache(maxsize=200, ttl=60)
            self.json_cache = LRUCache(maxsize=1000)
            self.process_cache = TTLCache(maxsize=100, ttl=30)

            # Thread-safe locks
            self._l1_lock = threading.RLock()
            self._l2_lock = threading.RLock()
            self._lru_lock = threading.RLock()
            self._command_lock = threading.RLock()
            self._file_lock = threading.RLock()
            self._json_lock = threading.RLock()
            self._process_lock = threading.RLock()

    def get_multi_level(self, key: str, default=None):
        """Get from multi-level cache using orchestration backend or fallback"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(key)
            return value if hit else default
        else:
            # Fallback implementation
            # Try L1 first (fastest)
            with self._l1_lock:
                if key in self.l1_cache:
                    return self.l1_cache[key]

            # Try L2
            with self._l2_lock:
                if key in self.l2_cache:
                    value = self.l2_cache[key]
                    # Promote to L1
                    with self._l1_lock:
                        self.l1_cache[key] = value
                    return value

            # Try L3 (disk)
            try:
                value = self.l3_cache.get(key, default)
                if value != default:
                    # Promote to L2 and L1
                    with self._l2_lock:
                        self.l2_cache[key] = value
                    with self._l1_lock:
                        self.l1_cache[key] = value
                    return value
            except Exception:
                pass

            return default

    def set_multi_level(self, key: str, value, ttl: int | None = None):
        """Set in multi-level cache using orchestration backend or fallback"""
        if self.use_orchestration:
            self.intelligent_cache.put(key, value, ttl)
        else:
            # Fallback implementation
            # Set in all levels
            with self._l1_lock:
                self.l1_cache[key] = value
            with self._l2_lock:
                self.l2_cache[key] = value

            try:
                # Set in L3 with optional TTL
                if ttl:
                    self.l3_cache.set(key, value, expire=ttl)
                else:
                    self.l3_cache[key] = value
            except Exception:
                pass

    def get(self, key: str, default=None):
        """Get from cache using multi-level strategy"""
        return self.get_multi_level(key, default)

    def set(self, key: str, value, ttl: int | None = None):
        """Set in cache using multi-level strategy"""
        return self.set_multi_level(key, value, ttl)

    def get_command(self, key: str, default=None):
        """Get from command cache"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"cmd:{key}")
            return value if hit else default
        else:
            with self._command_lock:
                return self.command_cache.get(key, default)

    def set_command(self, key: str, value):
        """Set in command cache"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"cmd:{key}", value, ttl=1800)  # 30 min for commands
        else:
            with self._command_lock:
                self.command_cache[key] = value

    def get_file(self, key: str, default=None):
        """Get from file cache with context awareness"""
        if self.use_orchestration:
            # Use context-aware cache for file operations
            hit, value = self.context_cache.get_file_based(f"file:{key}", [key], ttl=60)
            return value if hit else default
        else:
            with self._file_lock:
                return self.file_cache.get(key, default)

    def set_file(self, key: str, value):
        """Set in file cache with context awareness"""
        if self.use_orchestration:
            # Use context-aware cache for file operations
            self.context_cache.put_file_based(f"file:{key}", value, [key], ttl=60)
        else:
            with self._file_lock:
                self.file_cache[key] = value

    def get_json(self, key: str, default=None):
        """Get from JSON cache"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"json:{key}")
            return value if hit else default
        else:
            with self._json_lock:
                return self.json_cache.get(key, default)

    def set_json(self, key: str, value):
        """Set in JSON cache"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"json:{key}", value, ttl=300)  # 5 min for JSON
        else:
            with self._json_lock:
                self.json_cache[key] = value

    def get_process(self, key: str, default=None):
        """Get from process cache"""
        if self.use_orchestration:
            hit, value = self.intelligent_cache.get(f"proc:{key}")
            return value if hit else default
        else:
            with self._process_lock:
                return self.process_cache.get(key, default)

    def set_process(self, key: str, value):
        """Set in process cache"""
        if self.use_orchestration:
            self.intelligent_cache.put(f"proc:{key}", value, ttl=30)  # 30 sec for processes
        else:
            with self._process_lock:
                self.process_cache[key] = value

    def clear_all(self):
        """Clear all caches"""
        if self.use_orchestration:
            if clear_cache:
                clear_cache()  # Clear orchestration cache
        else:
            # Fallback implementation
            with self._l1_lock:
                self.l1_cache.clear()
            with self._l2_lock:
                self.l2_cache.clear()
            with self._command_lock:
                self.command_cache.clear()
            with self._file_lock:
                self.file_cache.clear()
            with self._json_lock:
                self.json_cache.clear()
            with self._process_lock:
                self.process_cache.clear()
            with self._lru_lock:
                self.lru_dict.clear()

            with contextlib.suppress(Exception):
                self.l3_cache.clear()

    def _get_l3_cache_size(self) -> int | str:
        """Safely get L3 cache size avoiding type compatibility issues"""
        if self.use_orchestration:
            return 'unified_cache'
        try:
            # Use safe iteration method to count entries
            count = 0
            for _ in self.l3_cache:
                count += 1
            return count
        except Exception:
            # If any method fails, return 'unknown' to avoid type issues
            return 'unknown'

    def get_stats(self):
        """Get cache statistics"""
        if self.use_orchestration:
            # Get stats from orchestration cache
            stats = {'backend': 'orchestration_cache'}
            if get_cache_stats:
                stats.update(get_cache_stats())
            if get_performance_report:
                stats['performance'] = get_performance_report()
            return stats
        else:
            # Fallback stats
            return {
                'backend': 'fallback_cache',
                'l1_size': len(self.l1_cache),
                'l2_size': len(self.l2_cache),
                'l3_size': self._get_l3_cache_size(),
                'lru_size': len(self.lru_dict),
                'command_size': len(self.command_cache),
                'file_size': len(self.file_cache),
                'json_size': len(self.json_cache),
                'process_size': len(self.process_cache)
            }


# Global cache manager instance
cache_manager = CacheManager()


def cached_function(cache_type='lru', maxsize=128, ttl=None):
    """Enhanced caching decorator with orchestration backend support"""
    def decorator(func):
        # Use orchestration cache decorator if available
        if HAS_ORCHESTRATION_CACHE and cached and cache_type in ['multi', 'lru']:
            return cached(ttl=ttl or 300, key_prefix=cache_type)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"

            # Multi-level cache
            if cache_type == 'multi':
                result = cache_manager.get_multi_level(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_manager.set_multi_level(cache_key, result, ttl=ttl)
                return result

            # Command cache
            elif cache_type == 'command':
                result = cache_manager.get_command(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_manager.set_command(cache_key, result)
                return result

            # File cache
            elif cache_type == 'file':
                result = cache_manager.get_file(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_manager.set_file(cache_key, result)
                return result

            # JSON cache
            elif cache_type == 'json':
                result = cache_manager.get_json(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_manager.set_json(cache_key, result)
                return result

            # Process cache
            elif cache_type == 'process':
                result = cache_manager.get_process(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_manager.set_process(cache_key, result)
                return result

            # Default LRU cache (using lru_cache from functools)
            else:
                # For default case, just execute the function
                # The actual lru_cache decorator should be applied separately
                return func(*args, **kwargs)

        return wrapper
    return decorator


# Cache utility functions
@cached_function(cache_type='multi', ttl=300)
def cached_file_read(file_path: str) -> str:
    """Cached file reading with context-aware invalidation"""
    try:
        with open(file_path) as f:
            return f.read()
    except Exception:
        return ""

# Additional utility functions for orchestration cache integration
def warm_entry_cache():
    """Warm the cache with commonly used data"""
    if HAS_ORCHESTRATION_CACHE and warm_cache:
        try:
            warm_cache()
            logger.info("Entry cache warmed using orchestration_cache")
        except Exception as e:
            logger.warning(f"Failed to warm entry cache: {e}")
    else:
        logger.info("Entry cache warming skipped (orchestration cache not available)")

def get_unified_cache_performance() -> dict[str, Any]:
    """Get performance report from unified cache system"""
    if HAS_ORCHESTRATION_CACHE and get_performance_report:
        return get_performance_report()
    else:
        return {'status': 'orchestration_cache_not_available'}


# Export main components
__all__ = [
    'CacheManager',
    'cache_manager',
    'cached_function',
    'cached_file_read',
    'warm_entry_cache',
    'get_unified_cache_performance',
    'CACHE_DIR',
    'HAS_ORCHESTRATION_CACHE'
]
