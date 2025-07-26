#!/usr/bin/env python3
"""
Intelligent Caching System for Claude Code Hooks
Provides high-performance caching with TTL, LRU eviction, and context awareness
"""

import hashlib
import json
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar


class IntelligentCache:
    """Thread-safe LRU cache with TTL and context awareness"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: dict[str, float] = {}
        self.access_counts: dict[str, int] = {}
        self.lock = threading.RLock()

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from function arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()[:16]

    def _is_expired(self, key: str, ttl: int | None = None) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True

        ttl = ttl or self.default_ttl
        return time.time() - self.timestamps[key] > ttl

    def _evict_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if current_time - timestamp > self.default_ttl
        ]

        for key in expired_keys:
            self._remove_entry(key)

    def _remove_entry(self, key: str) -> None:
        """Remove entry from all tracking structures"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        self.access_counts.pop(key, None)

    def _evict_lru(self) -> None:
        """Evict least recently used entries if over capacity"""
        while len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            self._remove_entry(oldest_key)

    def get(self, key: str, ttl: int | None = None) -> tuple[bool, Any]:
        """Get value from cache, returns (hit, value)"""
        with self.lock:
            if key not in self.cache or self._is_expired(key, ttl):
                return False, None

            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.access_counts[key] = self.access_counts.get(key, 0) + 1

            return True, value

    def put(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store value in cache"""
        with self.lock:
            self._evict_expired()
            self._evict_lru()

            # Store new entry
            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.access_counts[key] = 1

    def invalidate(self, pattern: str | None = None) -> None:
        """Invalidate cache entries matching pattern"""
        with self.lock:
            if pattern is None:
                # Clear all
                self.cache.clear()
                self.timestamps.clear()
                self.access_counts.clear()
            else:
                # Remove matching keys
                keys_to_remove = [k for k in self.cache if pattern in k]
                for key in keys_to_remove:
                    self._remove_entry(key)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_access = sum(self.access_counts.values())
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': total_access / max(len(self.access_counts), 1),
                'memory_usage_mb': self._estimate_memory_usage(),
                'expired_count': len([k for k in self.timestamps if self._is_expired(k)])
            }

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            import sys
            total_size = sys.getsizeof(self.cache) + sys.getsizeof(self.timestamps) + sys.getsizeof(self.access_counts)
            for key, value in self.cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

# Global cache instance
_global_cache = IntelligentCache(max_size=2000, default_ttl=600)

F = TypeVar('F', bound=Callable[..., Any])

def cached(ttl: int = 300, key_prefix: str = "") -> Callable[[F], F]:
    """Decorator for caching function results"""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{_global_cache._generate_key(*args, **kwargs)}"

            # Try to get from cache
            hit, result = _global_cache.get(cache_key, ttl)
            if hit:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _global_cache.put(cache_key, result, ttl)

            return result

        wrapper._cache_key_prefix = key_prefix  # type: ignore
        wrapper._cache_ttl = ttl  # type: ignore
        return wrapper  # type: ignore

    return decorator

class ContextAwareCache:
    """Cache that's aware of file modifications and project context"""

    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.file_mtimes: dict[str, float] = {}
        self.project_context_hash: str | None = None
        self.lock = threading.RLock()

    def get_file_based(self, key: str, file_paths: list[str], ttl: int = 300) -> tuple[bool, Any]:
        """Get cached value, invalidating if any tracked files changed"""
        with self.lock:
            # Check if any files have been modified
            for file_path in file_paths:
                try:
                    current_mtime = Path(file_path).stat().st_mtime
                    if file_path not in self.file_mtimes or self.file_mtimes[file_path] != current_mtime:
                        # File changed, invalidate related cache entries
                        self.cache.invalidate(f"file:{file_path}")
                        self.file_mtimes[file_path] = current_mtime
                        return False, None
                except (OSError, FileNotFoundError):
                    # File doesn't exist or can't be accessed
                    continue

            return self.cache.get(key, ttl)

    def put_file_based(self, key: str, value: Any, file_paths: list[str], ttl: int = 300) -> None:
        """Store value with file dependency tracking"""
        with self.lock:
            # Update file modification times
            for file_path in file_paths:
                try:
                    self.file_mtimes[file_path] = Path(file_path).stat().st_mtime
                except (OSError, FileNotFoundError):
                    continue

            # Use file-aware key
            file_key = f"file:{':'.join(file_paths)}:{key}"
            self.cache.put(file_key, value, ttl)

# Global context-aware cache
_context_cache = ContextAwareCache(_global_cache)

# Cache management functions
def get_cache_stats() -> dict[str, Any]:
    """Get comprehensive cache statistics"""
    return _global_cache.stats()

def clear_cache(pattern: str | None = None) -> None:
    """Clear cache entries"""
    _global_cache.invalidate(pattern)

def warm_cache():
    """Pre-populate cache with commonly used data"""
    import os

    # Cache project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    _global_cache.put('project_dir', project_dir, ttl=3600)

    # Cache common file paths
    common_paths = [
        '.claude/settings.json',
        'package.json',
        'requirements.txt',
        'Cargo.toml',
        'go.mod'
    ]

    for path in common_paths:
        full_path = Path(project_dir) / path
        if full_path.exists():
            try:
                with open(full_path) as f:
                    content = f.read()
                _global_cache.put(f'file_content:{path}', content, ttl=300)
            except OSError:
                continue

# Performance monitoring
class CachePerformanceMonitor:
    """Monitor cache performance and provide optimization recommendations"""

    def __init__(self):
        self.hit_history = []
        self.miss_history = []
        self.lock = threading.Lock()

    def record_hit(self, key: str, response_time_ms: float) -> None:
        """Record cache hit"""
        with self.lock:
            self.hit_history.append({
                'timestamp': time.time(),
                'key': key,
                'response_time_ms': response_time_ms
            })

            # Keep only recent history
            cutoff = time.time() - 3600  # 1 hour
            self.hit_history = [h for h in self.hit_history if h['timestamp'] > cutoff]

    def record_miss(self, key: str, computation_time_ms: float) -> None:
        """Record cache miss"""
        with self.lock:
            self.miss_history.append({
                'timestamp': time.time(),
                'key': key,
                'computation_time_ms': computation_time_ms
            })

            # Keep only recent history
            cutoff = time.time() - 3600  # 1 hour
            self.miss_history = [m for m in self.miss_history if m['timestamp'] > cutoff]

    def get_performance_report(self) -> dict[str, Any]:
        """Generate performance report with optimization recommendations"""
        with self.lock:
            total_hits = len(self.hit_history)
            total_misses = len(self.miss_history)
            total_requests = total_hits + total_misses

            if total_requests == 0:
                return {'hit_rate': 0, 'recommendations': ['No cache activity recorded']}

            hit_rate = total_hits / total_requests
            avg_hit_time = sum(h['response_time_ms'] for h in self.hit_history) / max(total_hits, 1)
            avg_miss_time = sum(m['computation_time_ms'] for m in self.miss_history) / max(total_misses, 1)

            recommendations = []
            if hit_rate < 0.6:
                recommendations.append('Consider increasing cache TTL - low hit rate detected')
            if avg_miss_time > 1000:  # > 1 second
                recommendations.append('High computation time on misses - consider pre-warming cache')
            if total_requests > 10000:  # High volume
                recommendations.append('High cache volume - consider distributed caching')

            return {
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                'avg_hit_time_ms': avg_hit_time,
                'avg_miss_time_ms': avg_miss_time,
                'time_saved_ms': total_hits * (avg_miss_time - avg_hit_time),
                'recommendations': recommendations or ['Cache performance is optimal']
            }

# Global performance monitor
_performance_monitor = CachePerformanceMonitor()

def get_performance_report() -> dict[str, Any]:
    """Get cache performance report"""
    return _performance_monitor.get_performance_report()

# Example usage functions
@cached(ttl=600, key_prefix="project_analysis")
def analyze_project_structure(project_dir: str) -> dict[str, Any]:
    """Analyze project structure with caching"""
    # This would be cached for 10 minutes
    return {
        'languages': ['python', 'typescript'],
        'frameworks': ['react', 'flask'],
        'complexity': 'medium'
    }

@cached(ttl=180, key_prefix="command_validation")
def validate_command_safety(command: str) -> dict[str, Any]:
    """Validate command safety with caching"""
    # This would be cached for 3 minutes
    dangerous_patterns = ['rm -rf', 'curl | bash', 'wget | sh']
    is_safe = not any(pattern in command for pattern in dangerous_patterns)

    return {
        'is_safe': is_safe,
        'risk_level': 'low' if is_safe else 'high',
        'suggestions': [] if is_safe else ['Use safer alternatives']
    }
