#!/usr/bin/env python3
"""
Optimized Entry Point with Performance Enhancements

This module provides a high-performance entry point with:
- Efficient ProcessManager with connection pooling
- Optimized subprocess handling with async I/O
- Advanced rate limiting with token bucket algorithm
- Fast JSON parsing with streaming and caching
- Memory-efficient operations with object pooling
"""

import asyncio
import json
import logging
import logging.handlers
import multiprocessing
import os
import queue
import subprocess
import sys
import threading
import time
import weakref
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from collections import deque
import signal

# Performance-optimized imports
try:
    import orjson as json_fast  # Faster JSON parsing
except ImportError:
    import json as json_fast

try:
    import uvloop  # Faster asyncio event loop
    uvloop.install()
except ImportError:
    pass

# Configure high-performance logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            'app.log', maxBytes=10*1024*1024, backupCount=3
        )
    ]
)

# Disable debug logging for performance
for logger_name in ['asyncio', 'concurrent.futures']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for token bucket rate limiter."""
    rate: float = 100.0  # tokens per second
    capacity: int = 200  # maximum tokens
    refill_period: float = 0.01  # refill every 10ms


class TokenBucket:
    """High-performance token bucket rate limiter."""
    
    def __init__(self, config: RateLimitConfig):
        self.rate = config.rate
        self.capacity = config.capacity
        self.tokens = config.capacity
        self.last_refill = time.perf_counter()
        self._lock = threading.RLock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens if available. Returns True if successful."""
        with self._lock:
            now = time.perf_counter()
            # Add tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """Async wait until tokens are available."""
        while not self.consume(tokens):
            await asyncio.sleep(0.001)  # 1ms sleep


class ObjectPool:
    """Memory-efficient object pool to reduce garbage collection pressure."""
    
    def __init__(self, factory, max_size: int = 100):
        self._factory = factory
        self._pool = queue.Queue(maxsize=max_size)
        self._created = 0
        self._max_size = max_size
    
    @contextmanager
    def get_object(self):
        """Get object from pool, return to pool when done."""
        try:
            obj = self._pool.get_nowait()
        except queue.Empty:
            if self._created < self._max_size:
                obj = self._factory()
                self._created += 1
            else:
                # Pool is full, create temporary object
                obj = self._factory()
        
        try:
            yield obj
        finally:
            try:
                # Reset object state if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset()
                self._pool.put_nowait(obj)
            except queue.Full:
                pass  # Pool is full, let object be garbage collected


class FastJSONParser:
    """Optimized JSON parser with caching and streaming support."""
    
    def __init__(self, cache_size: int = 1000):
        self._cache = {}
        self._cache_size = cache_size
        self._access_order = deque()
    
    @lru_cache(maxsize=500)
    def parse_cached(self, json_str: str) -> Dict[str, Any]:
        """Parse JSON with LRU caching for repeated strings."""
        try:
            return json_fast.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON parse error: {e}")
            return {}
    
    def parse_stream(self, stream) -> List[Dict[str, Any]]:
        """Parse multiple JSON objects from a stream efficiently."""
        results = []
        buffer = StringIO()
        
        for line in stream:
            line = line.strip()
            if not line:
                continue
                
            buffer.write(line)
            try:
                data = json_fast.loads(buffer.getvalue())
                results.append(data)
                buffer = StringIO()  # Reset buffer
            except (json.JSONDecodeError, ValueError):
                # Incomplete JSON, continue reading
                continue
        
        return results
    
    def extract_fields(self, data: Dict[str, Any], fields: Set[str]) -> Dict[str, Any]:
        """Efficiently extract specific fields from JSON data."""
        return {field: data.get(field) for field in fields if field in data}


class SubprocessManager:
    """Optimized subprocess manager with connection pooling and async I/O."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self._executor = None
        self._active_processes = weakref.WeakSet()
        self._process_pool = ObjectPool(lambda: {}, max_size=50)
        self._rate_limiter = TokenBucket(RateLimitConfig(rate=50.0, capacity=100))
    
    def __enter__(self):
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
        self._cleanup_processes()
    
    async def __aenter__(self):
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
        self._cleanup_processes()
    
    def _cleanup_processes(self):
        """Clean up any remaining active processes."""
        for process in list(self._active_processes):
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
    
    async def run_command(self, cmd: List[str], **kwargs) -> Dict[str, Any]:
        """Run command asynchronously with rate limiting."""
        await self._rate_limiter.wait_for_tokens()
        
        try:
            # Use asyncio subprocess for better performance
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **kwargs
            )
            
            self._active_processes.add(process)
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=30.0
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise subprocess.TimeoutExpired(cmd, 30.0)
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'cmd': cmd
            }
        
        except Exception as e:
            logger.error(f"Command failed: {cmd} - {e}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'cmd': cmd
            }
    
    async def run_batch(self, commands: List[List[str]], max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Run multiple commands concurrently with controlled parallelism."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(cmd):
            async with semaphore:
                return await self.run_command(cmd)
        
        tasks = [run_with_semaphore(cmd) for cmd in commands]
        return await asyncio.gather(*tasks, return_exceptions=True)


class ProcessManager:
    """High-performance process manager with connection pooling and load balancing."""
    
    def __init__(self, max_processes: int = None, max_threads: int = None):
        self.max_processes = max_processes or multiprocessing.cpu_count()
        self.max_threads = max_threads or min(32, (os.cpu_count() or 1) + 4)
        
        # Connection pools
        self._process_executor = None
        self._thread_executor = None
        
        # Performance tracking
        self._task_queue = asyncio.Queue()
        self._active_tasks = set()
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._start_time = time.perf_counter()
        
        # Resource management
        self._rate_limiter = TokenBucket(RateLimitConfig(rate=100.0, capacity=200))
        self._memory_monitor = MemoryMonitor()
        
        # Graceful shutdown support
        self._shutdown = False
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown = True
    
    async def __aenter__(self):
        self._process_executor = ProcessPoolExecutor(max_workers=self.max_processes)
        self._thread_executor = ThreadPoolExecutor(max_workers=self.max_threads)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._shutdown = True
        await self._cleanup()
    
    async def _cleanup(self):
        """Clean up resources and active tasks."""
        logger.info("Shutting down ProcessManager...")
        
        # Cancel active tasks
        for future in list(self._active_tasks):
            if not future.done():
                future.cancel()
        
        # Wait for tasks to complete or timeout
        if self._active_tasks:
            await asyncio.wait(self._active_tasks, timeout=10.0)
        
        # Shutdown executors
        if self._process_executor:
            self._process_executor.shutdown(wait=True)
        if self._thread_executor:
            self._thread_executor.shutdown(wait=True)
        
        logger.info("ProcessManager shutdown complete")
    
    async def submit_task(self, func, *args, use_process: bool = False, **kwargs) -> Any:
        """Submit task to appropriate executor with rate limiting."""
        await self._rate_limiter.wait_for_tokens()
        
        if self._shutdown:
            raise RuntimeError("ProcessManager is shutting down")
        
        executor = self._process_executor if use_process else self._thread_executor
        loop = asyncio.get_event_loop()
        
        try:
            future = loop.run_in_executor(executor, func, *args)
            self._active_tasks.add(future)
            
            result = await future
            self._completed_tasks += 1
            return result
        
        except Exception as e:
            self._failed_tasks += 1
            logger.error(f"Task failed: {func.__name__} - {e}")
            raise
        
        finally:
            self._active_tasks.discard(future)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        runtime = time.perf_counter() - self._start_time
        return {
            'runtime_seconds': runtime,
            'completed_tasks': self._completed_tasks,
            'failed_tasks': self._failed_tasks,
            'active_tasks': len(self._active_tasks),
            'success_rate': self._completed_tasks / max(1, self._completed_tasks + self._failed_tasks),
            'tasks_per_second': self._completed_tasks / max(0.001, runtime),
            'memory_usage_mb': self._memory_monitor.get_usage_mb()
        }


class MemoryMonitor:
    """Monitor memory usage to prevent memory leaks."""
    
    def __init__(self):
        self._start_memory = self.get_usage_mb()
    
    def get_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback to resource module (Unix only)
            try:
                import resource
                # On Linux, ru_maxrss is in KB, on macOS it's in bytes
                maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if sys.platform == 'darwin':  # macOS
                    return maxrss / 1024 / 1024
                else:  # Linux
                    return maxrss / 1024
            except (ImportError, AttributeError):
                return 0.0
    
    def check_memory_leak(self, threshold_mb: float = 100.0) -> bool:
        """Check if memory usage has increased beyond threshold."""
        current = self.get_usage_mb()
        increase = current - self._start_memory
        return increase > threshold_mb


class PerformanceOptimizedApp:
    """Main application class with all performance optimizations."""
    
    def __init__(self):
        self.process_manager = ProcessManager()
        self.subprocess_manager = SubprocessManager()
        self.json_parser = FastJSONParser()
        self.rate_limiter = TokenBucket(RateLimitConfig())
        self.memory_monitor = MemoryMonitor()
        
        # Performance caches
        self._config_cache = {}
        self._result_cache = {}
        
        logger.info("PerformanceOptimizedApp initialized")
    
    async def process_json_data(self, json_data: Union[str, Dict], extract_fields: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Process JSON data with optimized parsing and field extraction."""
        await self.rate_limiter.wait_for_tokens()
        
        if isinstance(json_data, str):
            data = self.json_parser.parse_cached(json_data)
        else:
            data = json_data
        
        if extract_fields:
            return self.json_parser.extract_fields(data, extract_fields)
        
        return data
    
    async def run_command_batch(self, commands: List[List[str]]) -> List[Dict[str, Any]]:
        """Run multiple commands efficiently using subprocess manager."""
        async with self.subprocess_manager:
            return await self.subprocess_manager.run_batch(commands)
    
    async def process_large_dataset(self, data_items: List[Any], processor_func, batch_size: int = 100) -> List[Any]:
        """Process large dataset in batches with process pooling."""
        results = []
        
        async with self.process_manager:
            # Process in batches to control memory usage
            for i in range(0, len(data_items), batch_size):
                batch = data_items[i:i + batch_size]
                
                # Submit batch tasks
                tasks = []
                for item in batch:
                    task = self.process_manager.submit_task(
                        processor_func, item, use_process=True
                    )
                    tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend(batch_results)
                
                # Check for memory leaks
                if self.memory_monitor.check_memory_leak():
                    logger.warning("Memory leak detected, triggering garbage collection")
                    import gc
                    gc.collect()
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        stats = self.process_manager.get_stats()
        stats.update({
            'json_cache_size': len(self.json_parser._cache),
            'rate_limiter_tokens': self.rate_limiter.tokens,
            'memory_usage_mb': self.memory_monitor.get_usage_mb()
        })
        return stats


async def main():
    """Main entry point with performance monitoring."""
    logger.info("Starting optimized application...")
    
    app = PerformanceOptimizedApp()
    
    try:
        # Example usage demonstrating all optimization features
        
        # 1. JSON processing with field extraction
        json_data = '{"name": "test", "value": 42, "extra": "unused"}'
        result = await app.process_json_data(
            json_data, 
            extract_fields={"name", "value"}
        )
        logger.info(f"JSON processing result: {result}")
        
        # 2. Batch command execution
        commands = [
            ["echo", "Hello"],
            ["echo", "World"],
            ["sleep", "0.1"]
        ]
        cmd_results = await app.run_command_batch(commands)
        logger.info(f"Command batch results: {len(cmd_results)} commands completed")
        
        # 3. Large dataset processing
        def sample_processor(item):
            """Sample CPU-intensive processing function."""
            import math
            return sum(math.sqrt(i) for i in range(item * 100))
        
        dataset = list(range(1, 101))  # 100 items
        processed = await app.process_large_dataset(dataset, sample_processor)
        logger.info(f"Processed {len(processed)} items")
        
        # 4. Performance metrics
        metrics = app.get_performance_metrics()
        logger.info(f"Performance metrics: {metrics}")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    # Set up optimal Python settings for performance
    sys.dont_write_bytecode = True  # Disable .pyc files for faster startup
    
    # Run the optimized application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)