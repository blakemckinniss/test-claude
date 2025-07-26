# Cache Migration Guide

## Overview

This guide helps migrate from the complex multi-cache system to the new unified cache backend.

## Key Changes

### 1. Unified Cache Interface

**Old System:**
- Multiple cache implementations (L1/L2/L3, TTL, LRU, orchestration)
- Redundant fallback mechanisms
- Complex interdependencies

**New System:**
- Single `UnifiedCache` interface
- Configurable backends
- Namespace support
- Simplified API

### 2. Migration Steps

#### Step 1: Update Imports

```python
# Old
from ..core.cache import CacheManager
from ..core.orchestration_cache import IntelligentCache

# New
from ..core.unified_cache import get_global_cache, get_command_cache, get_file_cache
```

#### Step 2: Replace Cache Usage

```python
# Old
cache_manager = CacheManager()
result = cache_manager.get_multi_level(key)
cache_manager.set_multi_level(key, value, ttl=300)

# New
cache = get_global_cache()
hit, value = cache.get(key)
cache.set(key, value, ttl=300)
```

#### Step 3: Use Namespaced Caches

```python
# Command caching
cmd_cache = get_command_cache()
hit, result = cmd_cache.get(command_hash)

# File caching
file_cache = get_file_cache()
hit, content = file_cache.get(file_path)

# Process caching
proc_cache = get_process_cache()
hit, status = proc_cache.get(process_id)
```

### 3. Prefixed Cache Views

```python
# Create a prefixed view for specific features
cache = get_global_cache()
prompt_cache = cache.with_prefix("prompt")
prompt_cache.set("analysis_123", analysis_result)
```

### 4. Cache Statistics

```python
# Get stats for all caches
from ..core.unified_cache import get_all_stats
stats = get_all_stats()
print(f"Global cache hit rate: {stats['global']['hit_rate']}")
```

### 5. Configuration

The new system uses sensible defaults:
- Global cache: 2000 entries, 600s TTL
- Command cache: 500 entries, 1800s TTL  
- File cache: 200 entries, 60s TTL
- Process cache: 100 entries, 30s TTL

### 6. Backward Compatibility

The unified cache provides a simpler API while maintaining compatibility:
- `get()` returns `(hit: bool, value: Any)`
- `set()` accepts optional TTL
- `delete()` returns success boolean
- `clear()` clears all entries

## Benefits

1. **Reduced Complexity**: Single interface instead of 6+ cache implementations
2. **Better Performance**: No redundant cache lookups
3. **Easier Testing**: Mock a single interface
4. **Clear Dependencies**: No circular imports
5. **Maintainability**: Less code to maintain

## Example Migration

### Before (Complex)
```python
class MyProcessor:
    def __init__(self):
        self.cache_manager = CacheManager()
        self.l1_cache = TTLCache(maxsize=1000, ttl=300)
        self.l2_cache = LRUCache(maxsize=5000)
        self.orchestration_cache = IntelligentCache()
        
    def process(self, data):
        # Check multiple cache levels
        result = self.cache_manager.get_multi_level(key)
        if not result:
            result = self.orchestration_cache.get(key)
        # ... complex logic
```

### After (Simple)
```python
class MyProcessor:
    def __init__(self):
        self.cache = get_global_cache()
        
    def process(self, data):
        # Simple cache check
        hit, result = self.cache.get(key)
        if not hit:
            result = self._compute(data)
            self.cache.set(key, result)
        return result
```

## Testing

Run the test suite to ensure cache behavior is preserved:

```bash
pytest .claude/hooks/tests/test_unified_cache.py
```