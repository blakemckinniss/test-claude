#!/usr/bin/env python3
"""
Async operations module for user prompt processing
"""

import asyncio
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import aiofiles


class AsyncFileOperations:
    """Async file operations using aiofiles"""

    @staticmethod
    async def read_file_async(file_path: str | Path) -> str:
        """Read file asynchronously"""
        try:
            async with aiofiles.open(file_path, encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            return f"Error reading {file_path}: {e}"

    @staticmethod
    async def write_file_async(file_path: str | Path, content: str) -> bool:
        """Write file asynchronously"""
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return True
        except Exception:
            return False

    @staticmethod
    async def append_file_async(file_path: str | Path, content: str) -> bool:
        """Append to file asynchronously"""
        try:
            async with aiofiles.open(file_path, 'a', encoding='utf-8') as f:
                await f.write(content)
            return True
        except Exception:
            return False


class AsyncProcessManager:
    """Async-enabled process manager with concurrent execution support"""

    def __init__(self, logger: logging.Logger | None = None, max_concurrent: int = 5):
        self.logger = logger
        self.active_processes: list[asyncio.subprocess.Process] = []
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._thread_executor = ThreadPoolExecutor(max_workers=4)
        self._process_executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self._lock = asyncio.Lock()

    def log(self, level: str, message: str):
        """Log a message if logger is available"""
        if self.logger:
            getattr(self.logger, level)(message)

    async def run_command_async(self, cmd: str | list[str], timeout: int | None = None) -> tuple[int, str, str]:
        """Run command asynchronously with proper resource management"""
        async with self._semaphore:
            try:
                self.log('info', f"Executing async command: {cmd}")

                # Use asyncio subprocess for better async support
                if isinstance(cmd, str):
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                else:
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )

                async with self._lock:
                    self.active_processes.append(process)

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )

                    return_code = process.returncode
                    stdout_text = stdout.decode('utf-8') if stdout else ""
                    stderr_text = stderr.decode('utf-8') if stderr else ""

                    self.log('info', f"Async command completed with return code: {return_code}")
                    return return_code, stdout_text, stderr_text

                except TimeoutError:
                    self.log('error', f"Async command timed out after {timeout} seconds")
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=3)
                    except TimeoutError:
                        process.kill()
                        await process.wait()

                    return -1, "", f"Timeout after {timeout} seconds"

                finally:
                    async with self._lock:
                        if process in self.active_processes:
                            self.active_processes.remove(process)

            except Exception as e:
                self.log('error', f"Failed to execute async command: {e}")
                return -1, "", str(e)

    async def run_commands_parallel(self, commands: list[str | list[str]], timeout: int | None = None) -> list[tuple[int, str, str]]:
        """Run multiple commands in parallel"""
        tasks = [self.run_command_async(cmd, timeout) for cmd in commands]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def cleanup_all_async(self):
        """Clean up all active async processes"""
        cleanup_tasks = []
        async with self._lock:
            for process in self.active_processes[:]:
                if process.returncode is None:
                    cleanup_tasks.append(self._cleanup_process_async(process))
            self.active_processes.clear()

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

    async def _cleanup_process_async(self, process: asyncio.subprocess.Process):
        """Clean up a single async process"""
        try:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            except TimeoutError:
                process.kill()
                await process.wait()
        except Exception as e:
            self.log('warning', f"Error cleaning up async process: {e}")

    def __del__(self):
        """Cleanup on destruction"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup_all_async())
            else:
                loop.run_until_complete(self.cleanup_all_async())
        except Exception:
            pass
