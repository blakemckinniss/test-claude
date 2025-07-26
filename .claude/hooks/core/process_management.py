"""
Process management module for Claude Code hooks.
Provides subprocess execution with proper cleanup and monitoring.
"""

import asyncio
import logging
import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    import aiofiles
except ImportError:
    aiofiles = None

import builtins
import contextlib

from .cache import cache_manager
from .utils.utils import cached_command_hash, log_to_file

logger = logging.getLogger(__name__)


class ProcessSupervisor:
    """Process supervision and health monitoring"""

    def __init__(self):
        self.supervised_processes = {}
        self.health_checks = {}
        self.supervisor_thread = None
        self.supervising = False

    def add_process(self, name: str, pid: int, health_check_func=None) -> None:
        """Add a process to supervision"""
        if not psutil:
            log_to_file("L psutil not available for process supervision")
            return

        try:
            process = psutil.Process(pid)
            self.supervised_processes[name] = {
                'process': process,
                'pid': pid,
                'start_time': time.time(),
                'restart_count': 0,
                'last_health_check': time.time(),
                'status': 'running'
            }

            if health_check_func:
                self.health_checks[name] = health_check_func

            log_to_file(f"👀 Added process to supervision: {name} (PID: {pid})")
        except (psutil.NoSuchProcess, AttributeError):
            log_to_file(f"L Cannot supervise non-existent process: {name} (PID: {pid})")

    def start_supervision(self, check_interval: int = 10) -> None:
        """Start process supervision"""
        if self.supervising:
            return

        self.supervising = True
        self.supervisor_thread = threading.Thread(
            target=self._supervision_loop,
            args=(check_interval,),
            daemon=True
        )
        self.supervisor_thread.start()
        log_to_file(f"👮 Process supervision started (interval: {check_interval}s)")

    def stop_supervision(self) -> None:
        """Stop process supervision"""
        self.supervising = False
        if self.supervisor_thread and self.supervisor_thread.is_alive():
            self.supervisor_thread.join(timeout=2)
        log_to_file("🛑 Process supervision stopped")

    def _supervision_loop(self, interval: int) -> None:
        """Supervision monitoring loop"""
        while self.supervising:
            try:
                self._check_processes()
                time.sleep(interval)
            except Exception as e:
                log_to_file(f"L Supervision error: {e}")
                time.sleep(interval)

    def _check_processes(self) -> None:
        """Check health of supervised processes"""
        if not psutil:
            return

        for name, info in list(self.supervised_processes.items()):
            try:
                process = info['process']

                # Check if process is still running
                if not process.is_running():
                    log_to_file(f"⚠️ Supervised process died: {name} (PID: {info['pid']})")
                    info['status'] = 'dead'
                    continue

                # Check process status
                status = process.status()
                if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                    log_to_file(f"⚠️ Supervised process in bad state: {name} (status: {status})")
                    info['status'] = status
                    continue

                # Run custom health check if available
                if name in self.health_checks:
                    try:
                        health_ok = self.health_checks[name](process)
                        if not health_ok:
                            log_to_file(f"⚠️ Health check failed for: {name}")
                            info['status'] = 'unhealthy'
                        else:
                            info['status'] = 'healthy'
                            info['last_health_check'] = time.time()
                    except Exception as e:
                        log_to_file(f"L Health check error for {name}: {e}")
                        info['status'] = 'health_check_error'

            except (psutil.NoSuchProcess, AttributeError):
                log_to_file(f"⚠️ Supervised process no longer exists: {name}")
                info['status'] = 'missing'
            except Exception as e:
                log_to_file(f"L Error checking process {name}: {e}")

    def get_supervision_status(self) -> dict[str, Any]:
        """Get status of all supervised processes"""
        status = {
            'supervising': self.supervising,
            'process_count': len(self.supervised_processes),
            'processes': {}
        }

        for name, info in self.supervised_processes.items():
            try:
                process = info['process']
                status['processes'][name] = {
                    'pid': info['pid'],
                    'status': info['status'],
                    'uptime': time.time() - info['start_time'],
                    'restart_count': info['restart_count'],
                    'last_health_check': info['last_health_check'],
                    'memory_mb': process.memory_info().rss / (1024 * 1024) if process.is_running() else 0,
                    'cpu_percent': process.cpu_percent() if process.is_running() else 0
                }
            except Exception as e:
                status['processes'][name] = {
                    'error': str(e),
                    'status': 'error'
                }

        return status


class AsyncProcessManager:
    """Async-enabled process manager with concurrent execution support"""

    def __init__(self, timeout: int = 60, max_processes: int = 10):
        self.timeout = timeout
        self.max_processes = max_processes
        self.processes = []
        self._lock = asyncio.Lock()
        self._process_count = 0
        self.executor = ThreadPoolExecutor(max_workers=max_processes)
        self.process_executor = ProcessPoolExecutor(max_workers=max_processes // 2)
        self._semaphore = asyncio.Semaphore(max_processes)
        self._closed = False

    async def run_command_async(self, cmd: list, timeout: int | None = None) -> tuple[int, str, str]:
        """Run command asynchronously with proper resource management"""
        async with self._semaphore:
            timeout = timeout or self.timeout

            try:
                # Use asyncio subprocess for better async support
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                async with self._lock:
                    self.processes.append(process)
                    self._process_count += 1

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=timeout
                    )
                    return process.returncode, stdout.decode(), stderr.decode()

                except TimeoutError:
                    logger.warning(f"Async command timed out after {timeout} seconds: {' '.join(cmd)}")
                    process.terminate()
                    await asyncio.sleep(0.5)
                    if process.returncode is None:
                        process.kill()

                    try:
                        stdout, stderr = await asyncio.wait_for(
                            process.communicate(), timeout=1
                        )
                    except TimeoutError:
                        stdout, stderr = b"", b"Process timed out and was terminated"

                    return -1, stdout.decode(), f"Timeout after {timeout} seconds: {stderr.decode()}"

            except Exception as e:
                logger.error(f"Async process error: {type(e).__name__}")
                return -1, "", str(e)
            finally:
                async with self._lock:
                    if process in self.processes:
                        self.processes.remove(process)
                    self._process_count = max(0, self._process_count - 1)

    async def run_commands_concurrent(self, commands: list, timeout: int | None = None) -> list:
        """Run multiple commands concurrently"""
        tasks = [self.run_command_async(cmd, timeout) for cmd in commands]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def run_cpu_intensive_task(self, func: Callable, *args, **kwargs) -> Any:
        """Run CPU-intensive task in process pool"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.process_executor, func, *args, **kwargs)

    def run_io_intensive_task(self, func: Callable, *args, **kwargs) -> Any:
        """Run I/O-intensive task in thread pool"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, func, *args, **kwargs)

    async def cleanup_async(self) -> None:
        """Async cleanup of processes"""
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            processes_to_clean = self.processes[:]

        cleanup_tasks = []
        for process in processes_to_clean:
            if process.returncode is None:
                cleanup_tasks.append(self._terminate_process_async(process))

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        self.executor.shutdown(wait=False)
        self.process_executor.shutdown(wait=False)

    async def _terminate_process_async(self, process) -> None:
        """Terminate process asynchronously"""
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=3)
        except TimeoutError:
            process.kill()
            await process.wait()
        except Exception as e:
            logger.error(f"Error terminating async process: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensure cleanup"""
        await self.cleanup_async()
        return False


class ProcessManager:
    """Manages subprocess execution with proper cleanup and zombie prevention"""

    def __init__(self, timeout: int = 60, max_processes: int = 10):
        self.timeout = timeout
        self.max_processes = max_processes
        self.processes = []
        self._lock = threading.Lock()
        self._process_count = 0
        self.async_manager = AsyncProcessManager(timeout, max_processes)

    def run_command(self, cmd: list, timeout: int | None = None) -> tuple[int, str, str]:
        """
        Run a command with proper process management, resource limits, and caching.

        Args:
            cmd: Command list to execute
            timeout: Optional timeout override

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        # Create cache key for command
        cmd_str = ' '.join(cmd)
        cmd_hash = cached_command_hash(cmd_str)
        cache_key = f"cmd:{cmd_hash}"

        # Check cache for idempotent commands (read-only operations)
        if any(readonly in cmd_str.lower() for readonly in ['status', 'log', 'show', 'list', 'get', 'cat', 'ls', 'pwd', 'which']):
            cached_result = cache_manager.get_process(cache_key)
            if cached_result is not None:
                logger.debug(f"Using cached result for command: {cmd_str[:50]}...")
                return cached_result

        # Check process limits
        with self._lock:
            if self._process_count >= self.max_processes:
                logger.warning(f"Process limit reached ({self.max_processes}), waiting...")
                # Wait for a process to finish
                time.sleep(0.1)
                if self._process_count >= self.max_processes:
                    return -1, "", "Process limit exceeded"
            self._process_count += 1
        timeout = timeout or self.timeout
        process = None

        try:
            # Create new process group for easier cleanup
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )

            with self._lock:
                self.processes.append(process)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result = (process.returncode, stdout, stderr)

                # Cache successful read-only commands
                if result[0] == 0 and any(readonly in cmd_str.lower() for readonly in
                                        ['status', 'log', 'show', 'list', 'get', 'cat', 'ls', 'pwd', 'which']):
                    cache_manager.set_process(cache_key, result)

                return result
            except subprocess.TimeoutExpired:
                logger.warning(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
                self._terminate_process_group(process)

                # Wait a bit for graceful termination
                time.sleep(0.5)

                # Force kill if still alive
                if process.poll() is None:
                    self._kill_process_group(process)

                # Collect any output that was produced
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", "Process timed out and was terminated"

                return -1, stdout, f"Timeout after {timeout} seconds: {stderr}"

        except Exception as e:
            # Improved error handling with context
            error_msg = f"Process error: {type(e).__name__}"
            logger.error(error_msg)
            if process and process.poll() is None:
                self._terminate_process_group(process)
            return -1, "", error_msg
        finally:
            # Clean up with thread safety
            with self._lock:
                if process in self.processes:
                    self.processes.remove(process)
                self._process_count = max(0, self._process_count - 1)

            # Ensure process is reaped
            if process:
                with contextlib.suppress(builtins.BaseException):
                    process.wait(timeout=1)

    def run_commands_parallel(self, commands: list, timeout: int | None = None) -> list:
        """Run multiple commands in parallel using ThreadPoolExecutor"""
        results = []
        with ThreadPoolExecutor(max_workers=min(len(commands), self.max_processes)) as executor:
            future_to_cmd = {executor.submit(self.run_command, cmd, timeout): cmd for cmd in commands}

            for future in as_completed(future_to_cmd):
                cmd = future_to_cmd[future]
                try:
                    result = future.result()
                    results.append((cmd, result))
                except Exception as exc:
                    logger.error(f"Command {cmd} generated an exception: {exc}")
                    results.append((cmd, (-1, "", str(exc))))

        return results

    def _terminate_process_group(self, process) -> None:
        """Terminate process group gracefully"""
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
        except (OSError, ProcessLookupError) as e:
            logger.debug(f"Error terminating process group: {e}")

    def _kill_process_group(self, process) -> None:
        """Force kill process group"""
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            else:
                process.kill()
        except (OSError, ProcessLookupError) as e:
            logger.debug(f"Error terminating process group: {e}")

    def cleanup(self) -> None:
        """Clean up any remaining processes with improved efficiency"""
        with self._lock:
            processes_to_clean = self.processes[:]

        for process in processes_to_clean:
            if process.poll() is None:
                logger.debug(f"Cleaning up process {process.pid}")
                self._terminate_process_group(process)

        # Wait briefly for graceful termination
        time.sleep(0.2)

        # Force kill any remaining processes
        with self._lock:
            for process in self.processes[:]:
                if process.poll() is None:
                    logger.warning(f"Force killing process {process.pid}")
                    self._kill_process_group(process)
                self.processes.remove(process)
            self._process_count = 0


# Global process manager instances
process_manager = ProcessManager(timeout=60)
async_process_manager = AsyncProcessManager(timeout=60)


# Export main components
__all__ = ['ProcessSupervisor', 'ProcessManager', 'AsyncProcessManager',
           'process_manager', 'async_process_manager']
