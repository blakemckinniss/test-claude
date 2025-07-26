"""
Async operations module for Claude Code hooks.
Provides async file operations and utilities.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

try:
    import aiofiles
except ImportError:
    aiofiles = None

logger = logging.getLogger(__name__)


class AsyncFileOperations:
    """Async file operations for better I/O performance"""

    @staticmethod
    async def read_file_async(file_path: str) -> str:
        """Read file asynchronously"""
        if not aiofiles:
            # Fallback to sync read
            try:
                with open(file_path, encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Sync file read error for {file_path}: {e}")
                return ""

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Async file read error for {file_path}: {e}")
            return ""

    @staticmethod
    async def write_file_async(file_path: str, content: str) -> bool:
        """Write file asynchronously"""
        if not aiofiles:
            # Fallback to sync write
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                logger.error(f"Sync file write error for {file_path}: {e}")
                return False

        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return True
        except Exception as e:
            logger.error(f"Async file write error for {file_path}: {e}")
            return False

    @staticmethod
    async def read_files_batch_async(file_paths: list[str]) -> dict[str, str]:
        """Read multiple files asynchronously in batch"""
        tasks = [AsyncFileOperations.read_file_async(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        file_contents = {}
        for path, result in zip(file_paths, results, strict=False):
            if isinstance(result, Exception):
                logger.error(f"Error reading {path}: {result}")
                file_contents[path] = ""
            else:
                file_contents[path] = result

        return file_contents

    @staticmethod
    async def write_files_batch_async(file_data: dict[str, str]) -> dict[str, bool]:
        """Write multiple files asynchronously in batch"""
        tasks = []
        paths = []

        for path, content in file_data.items():
            tasks.append(AsyncFileOperations.write_file_async(path, content))
            paths.append(path)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        write_results = {}
        for path, result in zip(paths, results, strict=False):
            if isinstance(result, Exception):
                logger.error(f"Error writing {path}: {result}")
                write_results[path] = False
            else:
                write_results[path] = result

        return write_results

    @staticmethod
    async def process_files_concurrent(
        file_paths: list[str],
        process_func: Callable[[str, str], Any],
        max_concurrent: int = 10
    ) -> list[Any]:
        """Process multiple files concurrently with a given function"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(path: str):
            async with semaphore:
                content = await AsyncFileOperations.read_file_async(path)
                # Run the processing function in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, process_func, path, content)

        tasks = [process_with_semaphore(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Export main components
__all__ = ['AsyncFileOperations']
