#!/usr/bin/env python3
"""
Async utilities for Claude Code hooks
Provides async versions of common I/O operations
"""

import asyncio
import aiofiles
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def read_file_async(file_path: str | Path) -> str:
    """
    Read a file asynchronously
    
    Args:
        file_path: Path to the file
        
    Returns:
        File contents as string
    """
    try:
        async with aiofiles.open(file_path, mode='r') as f:
            contents = await f.read()
        return contents
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return ""


async def write_file_async(file_path: str | Path, content: str) -> bool:
    """
    Write to a file asynchronously
    
    Args:
        file_path: Path to the file
        content: Content to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, mode='w') as f:
            await f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        return False


async def append_file_async(file_path: str | Path, content: str) -> bool:
    """
    Append to a file asynchronously
    
    Args:
        file_path: Path to the file
        content: Content to append
        
    Returns:
        True if successful, False otherwise
    """
    try:
        async with aiofiles.open(file_path, mode='a') as f:
            await f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to append to file {file_path}: {e}")
        return False


async def file_exists_async(file_path: str | Path) -> bool:
    """
    Check if a file exists asynchronously
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file exists, False otherwise
    """
    return await asyncio.to_thread(Path(file_path).exists)


async def list_directory_async(dir_path: str | Path) -> list[str]:
    """
    List directory contents asynchronously
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        List of file/directory names
    """
    try:
        path = Path(dir_path)
        if not path.is_dir():
            return []
        
        # Use asyncio.to_thread for I/O bound operation
        return await asyncio.to_thread(
            lambda: [item.name for item in path.iterdir()]
        )
    except Exception as e:
        logger.error(f"Failed to list directory {dir_path}: {e}")
        return []


async def get_file_size_async(file_path: str | Path) -> int:
    """
    Get file size asynchronously
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or 0 if error
    """
    try:
        return await asyncio.to_thread(
            lambda: Path(file_path).stat().st_size
        )
    except Exception:
        return 0


async def run_async_tasks(tasks: list[asyncio.Task]) -> list[Any]:
    """
    Run multiple async tasks concurrently
    
    Args:
        tasks: List of asyncio tasks
        
    Returns:
        List of results in the same order as tasks
    """
    return await asyncio.gather(*tasks, return_exceptions=True)


# Export main components
__all__ = [
    'read_file_async',
    'write_file_async',
    'append_file_async',
    'file_exists_async',
    'list_directory_async',
    'get_file_size_async',
    'run_async_tasks'
]