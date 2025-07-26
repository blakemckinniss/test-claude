#!/usr/bin/env python3
"""
Tests for the unified cache system
"""

import time
import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.unified_cache import (
    InMemoryCache,
    UnifiedCache,
    create_cache,
    get_global_cache,
    get_command_cache,
    clear_all_caches,
    get_all_stats
)


class TestInMemoryCache(unittest.TestCase):
    """Test the in-memory cache backend"""
    
    def setUp(self):
        self.cache = InMemoryCache(max_size=3, default_ttl=1)
    
    def test_basic_operations(self):
        """Test basic get/set operations"""
        # Test miss
        hit, value = self.cache.get("key1")
        self.assertFalse(hit)
        self.assertIsNone(value)
        
        # Test set and hit
        self.cache.set("key1", "value1")
        hit, value = self.cache.get("key1")
        self.assertTrue(hit)
        self.assertEqual(value, "value1")
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        self.cache.set("key1", "value1")
        time.sleep(1.1)  # Wait for expiration
        
        hit, value = self.cache.get("key1")
        self.assertFalse(hit)
        self.assertIsNone(value)
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        # Fill cache
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        self.cache.get("key1")
        
        # Add new key, should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        # Check key2 was evicted
        hit, _ = self.cache.get("key2")
        self.assertFalse(hit)
        
        # Check others still exist
        hit, _ = self.cache.get("key1")
        self.assertTrue(hit)
        hit, _ = self.cache.get("key3")
        self.assertTrue(hit)
        hit, _ = self.cache.get("key4")
        self.assertTrue(hit)
    
    def test_delete(self):
        """Test delete operation"""
        self.cache.set("key1", "value1")
        
        # Delete existing key
        deleted = self.cache.delete("key1")
        self.assertTrue(deleted)
        
        # Verify it's gone
        hit, _ = self.cache.get("key1")
        self.assertFalse(hit)
        
        # Delete non-existent key
        deleted = self.cache.delete("key2")
        self.assertFalse(deleted)
    
    def test_clear(self):
        """Test clear operation"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        # Verify all gone
        hit, _ = self.cache.get("key1")
        self.assertFalse(hit)
        hit, _ = self.cache.get("key2")
        self.assertFalse(hit)
    
    def test_stats(self):
        """Test statistics"""
        # Initial stats
        stats = self.cache.stats()
        self.assertEqual(stats['size'], 0)
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        
        # Add some activity
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.stats()
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], 0.5)


class TestUnifiedCache(unittest.TestCase):
    """Test the unified cache interface"""
    
    def test_namespace_isolation(self):
        """Test that namespaces are isolated"""
        cache1 = create_cache(namespace="ns1")
        cache2 = create_cache(namespace="ns2")
        
        cache1.set("key", "value1")
        cache2.set("key", "value2")
        
        # Each namespace should have its own value
        hit, value = cache1.get("key")
        self.assertEqual(value, "value1")
        
        hit, value = cache2.get("key")
        self.assertEqual(value, "value2")
    
    def test_prefixed_cache(self):
        """Test prefixed cache views"""
        cache = create_cache()
        
        # Create prefixed views
        user_cache = cache.with_prefix("user")
        session_cache = cache.with_prefix("session")
        
        # Set values with same key but different prefixes
        user_cache.set("123", {"name": "Alice"})
        session_cache.set("123", {"token": "abc"})
        
        # Verify isolation
        hit, user_data = user_cache.get("123")
        self.assertEqual(user_data["name"], "Alice")
        
        hit, session_data = session_cache.get("123")
        self.assertEqual(session_data["token"], "abc")


class TestGlobalCaches(unittest.TestCase):
    """Test the global cache instances"""
    
    def setUp(self):
        clear_all_caches()
    
    def test_global_cache_instances(self):
        """Test that global caches are properly configured"""
        global_cache = get_global_cache()
        cmd_cache = get_command_cache()
        
        # Test they're different namespaces
        global_cache.set("test", "global_value")
        cmd_cache.set("test", "cmd_value")
        
        hit, value = global_cache.get("test")
        self.assertEqual(value, "global_value")
        
        hit, value = cmd_cache.get("test")
        self.assertEqual(value, "cmd_value")
    
    def test_clear_all_caches(self):
        """Test clearing all caches"""
        get_global_cache().set("key1", "value1")
        get_command_cache().set("key2", "value2")
        
        clear_all_caches()
        
        # Verify all cleared
        hit, _ = get_global_cache().get("key1")
        self.assertFalse(hit)
        
        hit, _ = get_command_cache().get("key2")
        self.assertFalse(hit)
    
    def test_get_all_stats(self):
        """Test getting stats for all caches"""
        # Add some data
        get_global_cache().set("key1", "value1")
        get_command_cache().set("key2", "value2")
        
        stats = get_all_stats()
        
        # Verify structure
        self.assertIn('global', stats)
        self.assertIn('command', stats)
        self.assertIn('file', stats)
        self.assertIn('process', stats)
        
        # Verify some data
        self.assertEqual(stats['global']['size'], 1)
        self.assertEqual(stats['command']['size'], 1)


if __name__ == '__main__':
    unittest.main()