"""
Utility functions for Claude Code hooks.
Provides common helper functions and utilities.
"""

import hashlib
import logging
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create cache directory if it doesn't exist
CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def log_to_file(message: str):
    """Log monitoring events to file and stderr"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_message = f"[{timestamp}] MONITOR: {message}"

    # Log to stderr for immediate visibility
    print(log_message, file=sys.stderr)

    # Also log to monitoring log file
    try:
        monitoring_log = LOGS_DIR / "monitoring.log"
        with open(monitoring_log, 'a') as f:
            f.write(f"{log_message}\n")
    except Exception:
        pass  # Don't fail if logging fails


def should_execute_hook(hook_type: str) -> bool:
    """
    Rate limiting check for hooks.
    Returns True if hook should execute, False if rate limited.
    """
    # Simple rate limiting without circular imports
    # Always allow execution for now - rate limiting can be added separately
    return True


@lru_cache(maxsize=512)
def _cached_field_path_split(field_path: str) -> tuple:
    """Cache field path splits for performance"""
    return tuple(field_path.split('.'))


def extract_json_field(json_data: dict[str, Any], field_path: str) -> Any | None:
    """Extract a field from JSON data using dot notation"""
    if not json_data or not field_path:
        return None

    # Split field path using cached function
    fields = _cached_field_path_split(field_path)

    # Navigate through the JSON structure
    current = json_data
    for field in fields:
        if isinstance(current, dict) and field in current:
            current = current[field]
        elif isinstance(current, list) and field.isdigit():
            index = int(field)
            if 0 <= index < len(current):
                current = current[index]
            else:
                return None
        else:
            return None

    return current


def cached_command_hash(command: str) -> str:
    """Generate cached hash for commands"""
    return hashlib.sha256(command.encode()).hexdigest()[:16]


def cpu_intensive_analysis(data_chunk):
    """Analyze data chunk and return analysis results"""
    # Simple analysis without artificial delays
    return {
        'analyzed': True,
        'score': len(str(data_chunk)) / 1000.0,  # Score based on data size
        'data_size': len(str(data_chunk))
    }


def enhance_hook_with_data_science(hook_type: str, command: str | None = None, file_paths: list[str] | None = None) -> dict[str, Any]:
    """
    Enhanced hook with data science capabilities
    """
    enhancements = {
        'hook_type': hook_type,
        'timestamp': datetime.now().isoformat(),
        'features': {}
    }

    # Import data science libraries if available
    try:
        import numpy as np
        import pandas as pd
        enhancements['features']['numpy_available'] = True
        enhancements['features']['pandas_available'] = True
    except ImportError:
        enhancements['features']['numpy_available'] = False
        enhancements['features']['pandas_available'] = False

    # Add command analysis if provided
    if command:
        enhancements['command_analysis'] = {
            'length': len(command),
            'hash': cached_command_hash(command),
            'contains_pipe': '|' in command,
            'contains_redirect': any(op in command for op in ['>', '<', '>>']),
            'is_dangerous': any(cmd in command.lower() for cmd in ['rm -rf', 'sudo', 'chmod 777'])
        }

    # Add file analysis if provided
    if file_paths:
        enhancements['file_analysis'] = {
            'count': len(file_paths),
            'extensions': list({Path(f).suffix for f in file_paths if Path(f).suffix}),
            'total_size': sum(Path(f).stat().st_size if Path(f).exists() else 0 for f in file_paths)
        }

    return enhancements


# Export main components
__all__ = [
    'log_to_file',
    'should_execute_hook',
    'extract_json_field',
    'cached_command_hash',
    'cpu_intensive_analysis',
    'enhance_hook_with_data_science',
    'LOGS_DIR',
    'CACHE_DIR'
]
