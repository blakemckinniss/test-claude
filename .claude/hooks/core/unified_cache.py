#!/usr/bin/env python3
"""
Unified Cache Backend for Claude Code Hooks
Consolidates all caching implementations into a single, configurable backend
"""

import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    def get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache. Returns (hit, value)"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if key existed"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        pass


class InMemoryCache(CacheBackend):
    """Simple in-memory LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if entry is expired"""
        return time.time() - timestamp > ttl
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.cache:
            self.cache.popitem(last=False)
    
    def get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return False, None
            
            value, timestamp = self.cache[key]
            if self._is_expired(timestamp, self.default_ttl):
                del self.cache[key]
                self.misses += 1
                return False, None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return True, value
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache"""
        with self.lock:
            # Evict if at capacity
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = (value, time.time())
            self.cache.move_to_end(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': max(0, total - len(self.cache))
            }


class UnifiedCache:
    """
    Unified cache interface that delegates to a configurable backend
    Provides namespace support and key prefixing
    """
    
    def __init__(self, backend: CacheBackend | None = None, namespace: str = "default"):
        self.backend = backend or InMemoryCache()
        self.namespace = namespace
        self.lock = threading.RLock()
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"
    
    def get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache"""
        return self.backend.get(self._make_key(key))
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache"""
        self.backend.set(self._make_key(key), value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self.backend.delete(self._make_key(key))
    
    def clear(self) -> None:
        """Clear all cache entries in this namespace"""
        # For now, clear all (namespace filtering would require backend support)
        self.backend.clear()
    
    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        stats = self.backend.stats()
        stats['namespace'] = self.namespace
        return stats
    
    def with_prefix(self, prefix: str) -> 'PrefixedCache':
        """Create a prefixed view of this cache"""
        return PrefixedCache(self, prefix)


class PrefixedCache:
    """Cache view with automatic key prefixing"""
    
    def __init__(self, cache: UnifiedCache, prefix: str):
        self.cache = cache
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache"""
        return self.cache.get(self._make_key(key))
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache"""
        self.cache.set(self._make_key(key), value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self.cache.delete(self._make_key(key))


def create_cache(
    backend_type: str = "memory",
    max_size: int = 1000,
    default_ttl: int = 300,
    namespace: str = "default"
) -> UnifiedCache:
    """
    Factory function to create cache instances
    
    Args:
        backend_type: Type of cache backend ("memory" for now)
        max_size: Maximum number of entries
        default_ttl: Default TTL in seconds
        namespace: Cache namespace
    
    Returns:
        UnifiedCache instance
    """
    if backend_type == "memory":
        backend = InMemoryCache(max_size=max_size, default_ttl=default_ttl)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
    
    return UnifiedCache(backend=backend, namespace=namespace)


# Global cache instances with sensible defaults
_global_cache = create_cache(max_size=2000, default_ttl=600, namespace="global")
_command_cache = create_cache(max_size=500, default_ttl=1800, namespace="command")
_file_cache = create_cache(max_size=200, default_ttl=60, namespace="file")
_process_cache = create_cache(max_size=100, default_ttl=30, namespace="process")


def get_global_cache() -> UnifiedCache:
    """Get the global cache instance"""
    return _global_cache


def get_command_cache() -> UnifiedCache:
    """Get the command cache instance"""
    return _command_cache


def get_file_cache() -> UnifiedCache:
    """Get the file cache instance"""
    return _file_cache


def get_process_cache() -> UnifiedCache:
    """Get the process cache instance"""
    return _process_cache


def clear_all_caches() -> None:
    """Clear all cache instances"""
    _global_cache.clear()
    _command_cache.clear()
    _file_cache.clear()
    _process_cache.clear()
    logger.info("All caches cleared")


def get_all_stats() -> dict[str, dict[str, Any]]:
    """Get statistics for all caches"""
    return {
        'global': _global_cache.stats(),
        'command': _command_cache.stats(),
        'file': _file_cache.stats(),
        'process': _process_cache.stats()
    }


# Backwards compatibility helpers
def cached_hash(data: str) -> str:
    """Generate cache key from string data"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


# Export main components
__all__ = [
    'CacheBackend',
    'InMemoryCache', 
    'UnifiedCache',
    'PrefixedCache',
    'create_cache',
    'get_global_cache',
    'get_command_cache',
    'get_file_cache',
    'get_process_cache',
    'clear_all_caches',
    'get_all_stats',
    'cached_hash'
]