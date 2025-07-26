"""
Resilience module for Claude Code hooks.
Provides circuit breakers, retry mechanisms, and load balancing.
"""

import json
import logging
import random
import threading
import time
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

# Define LOGS_DIR
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket for rate limiting"""
    def __init__(self, capacity: int = 10, refill_rate: float = 2.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            # Refill tokens based on time elapsed
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for fault tolerance in hook operations"""
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, reset_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if operation can be executed based on circuit state"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if self.last_failure_time and time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
        return False

    def record_success(self) -> None:
        """Record successful operation"""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record failed operation"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened due to {self.failure_count} failures")


class RetryMechanism:
    """Implements retry logic with exponential backoff and jitter"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                result = operation(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    logger.error(f"Operation failed after {self.max_retries + 1} attempts: {e}")
                    break

                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)

                # Add jitter to prevent thundering herd
                if self.jitter:
                    delay *= (0.5 + random.random() * 0.5)

                logger.warning(f"Operation failed on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                time.sleep(delay)

        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Operation failed with unknown error")


class CheckpointManager:
    """Manages checkpoints for long-running operations"""
    def __init__(self, checkpoint_dir: str | None = None):
        self.checkpoint_dir = Path(checkpoint_dir or LOGS_DIR / "checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoints = {}

    def save_checkpoint(self, task_id: str, state: dict[str, Any]) -> None:
        """Save checkpoint state for a task"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.json"
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'state': state
                }, f, indent=2)
            logger.info(f"Checkpoint saved for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint for {task_id}: {e}")

    def load_checkpoint(self, task_id: str) -> dict[str, Any] | None:
        """Load checkpoint state for a task"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.json"
        try:
            if checkpoint_file.exists():
                with open(checkpoint_file) as f:
                    data = json.load(f)
                logger.info(f"Checkpoint loaded for task {task_id}")
                return data.get('state')
        except Exception as e:
            logger.error(f"Failed to load checkpoint for {task_id}: {e}")
        return None

    def clear_checkpoint(self, task_id: str) -> None:
        """Clear checkpoint after successful completion"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.json"
        try:
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                logger.info(f"Checkpoint cleared for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to clear checkpoint for {task_id}: {e}")


class LoadBalancer:
    """Smart load balancing for parallel hook operations"""
    def __init__(self, max_concurrent: int = 4, queue_threshold: int = 10):
        self.max_concurrent = max_concurrent
        self.queue_threshold = queue_threshold
        self.active_operations = 0
        self.queued_operations = 0
        self.operation_times = []
        self._lock = threading.Lock()

    def can_execute_now(self) -> bool:
        """Check if operation can execute immediately"""
        with self._lock:
            return self.active_operations < self.max_concurrent

    def should_queue(self) -> bool:
        """Check if operation should be queued"""
        with self._lock:
            return self.queued_operations < self.queue_threshold

    def start_operation(self) -> None:
        """Mark operation as started"""
        with self._lock:
            self.active_operations += 1

    def end_operation(self, duration: float | None = None) -> None:
        """Mark operation as completed"""
        with self._lock:
            self.active_operations = max(0, self.active_operations - 1)
            if duration is not None:
                self.operation_times.append(duration)
                # Keep only last 100 measurements
                if len(self.operation_times) > 100:
                    self.operation_times = self.operation_times[-100:]

    def get_avg_operation_time(self) -> float:
        """Get average operation time for planning"""
        with self._lock:
            if not self.operation_times:
                return 1.0  # Default estimate
            return sum(self.operation_times) / len(self.operation_times)

    def get_load_factor(self) -> float:
        """Get current load factor (0.0 to 1.0)"""
        with self._lock:
            return self.active_operations / self.max_concurrent


# Per-hook token buckets for better rate limiting
hook_buckets: dict[str, TokenBucket] = {}

# Global instances
retry_mechanism = RetryMechanism()
checkpoint_manager = CheckpointManager()
load_balancer = LoadBalancer()

# Global circuit breakers for different hook types
circuit_breakers = {
    'claude-flow': CircuitBreaker(failure_threshold=5, timeout=60, reset_timeout=300),
    'mcp': CircuitBreaker(failure_threshold=3, timeout=30, reset_timeout=180),
    'default': CircuitBreaker(failure_threshold=5, timeout=60, reset_timeout=300)
}


# Export main components
__all__ = [
    'TokenBucket', 'CircuitState', 'CircuitBreaker', 'RetryMechanism',
    'CheckpointManager', 'LoadBalancer', 'hook_buckets', 'retry_mechanism',
    'checkpoint_manager', 'load_balancer', 'circuit_breakers'
]
