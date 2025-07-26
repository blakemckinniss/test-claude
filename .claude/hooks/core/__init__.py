"""
Core Claude Code hooks functionality - Organized structure
"""

from .alerting import AlertingSystem
from .async_operations import AsyncFileOperations
from .cache import CacheManager, cache_manager, cached_file_read, cached_function
from .handlers.hook_handlers import (
    handle_notification,
    handle_post_bash,
    handle_post_edit,
    handle_post_mcp,
    handle_post_task,
    handle_pre_bash,
    handle_pre_edit,
    handle_pre_mcp,
    handle_pre_task,
    handle_precompact,
    handle_prompt,
    handle_stop,
    handle_subagent_stop,
)
from .http_client import HTTPClientManager
from .monitoring.monitoring import initialize_monitoring, start_monitoring, stop_monitoring
from .process_management import ProcessManager
from .resilience import CheckpointManager, CircuitBreaker, LoadBalancer, RetryMechanism, TokenBucket
from .tracking import HookTracker, hook_tracker
from .utils.utils import extract_json_field, log_to_file, should_execute_hook

__all__ = [
    # Cache
    'CacheManager', 'cache_manager', 'cached_function', 'cached_file_read',
    # HTTP
    'HTTPClientManager',
    # Monitoring
    'initialize_monitoring', 'start_monitoring', 'stop_monitoring',
    # Process Management
    'ProcessManager',
    # Alerting
    'AlertingSystem',
    # Resilience
    'TokenBucket', 'CircuitBreaker', 'RetryMechanism', 'CheckpointManager', 'LoadBalancer',
    # Tracking
    'HookTracker', 'hook_tracker',
    # Async Operations
    'AsyncFileOperations',
    # Utils
    'log_to_file', 'extract_json_field', 'should_execute_hook',
    # Hook Handlers
    'handle_pre_bash', 'handle_post_bash', 'handle_pre_edit', 'handle_post_edit',
    'handle_pre_task', 'handle_post_task', 'handle_pre_mcp', 'handle_post_mcp',
    'handle_notification', 'handle_stop', 'handle_prompt', 'handle_subagent_stop',
    'handle_precompact'
]
