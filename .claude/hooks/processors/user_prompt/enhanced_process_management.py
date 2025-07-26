#!/usr/bin/env python3
"""
Enhanced process management with parallel execution capabilities
Integrates ParallelHookExecutor for advanced concurrent process management
"""

import asyncio
import concurrent.futures
import contextlib
import logging
import multiprocessing
import os
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import psutil

# Add parent directory to path to import parallel_executor
sys.path.insert(0, str(Path(__file__).parent.parent))

# Initialize at module level
PARALLEL_EXECUTOR_AVAILABLE = False

# Type definitions for when parallel_executor is not available
if TYPE_CHECKING:
    from parallel_executor import (
        ContextSharedExecutor,
        ExecutionMode,
        ExecutionResult,
        HookCommand,
        ParallelHookExecutor,
        cleanup_executor,
    )
else:
    # Runtime imports with fallbacks
    try:
        from parallel_executor import (
            ContextSharedExecutor,
            ExecutionMode,
            ExecutionResult,
            HookCommand,
            ParallelHookExecutor,
            cleanup_executor,
        )
        PARALLEL_EXECUTOR_AVAILABLE = True
    except ImportError:
        PARALLEL_EXECUTOR_AVAILABLE = False

        # Create stub classes for type safety
        class ParallelHookExecutor:  # type: ignore
            def __init__(self, *args, **kwargs): pass

        class HookCommand:  # type: ignore
            def __init__(self, *args, **kwargs): pass

        class ExecutionResult:  # type: ignore
            def __init__(self, command: str = "", return_code: int = -1,
                        stdout: str = "", stderr: str = "",
                        execution_time: float = 0.0, success: bool = False,
                        error: str | None = None):
                self.command = command
                self.return_code = return_code
                self.stdout = stdout
                self.stderr = stderr
                self.execution_time = execution_time
                self.success = success
                self.error = error

        class ExecutionMode:  # type: ignore
            ADAPTIVE = "adaptive"

        class ContextSharedExecutor:  # type: ignore
            def __init__(self, *args, **kwargs): pass

        def cleanup_executor(*args, **kwargs): pass

# Constants
PROCESS_TERMINATE_TIMEOUT = 3  # seconds
DEFAULT_COMMAND_TIMEOUT = 60  # seconds
MAX_PARALLEL_PROCESSES = 8
CLEANUP_AGE_THRESHOLD = 900  # 15 minutes


@dataclass
class ProcessExecutionRequest:
    """Request for process execution with enhanced options"""
    command: str
    timeout: int = DEFAULT_COMMAND_TIMEOUT
    environment: dict[str, str] | None = None
    working_dir: str | None = None
    priority: int = 5
    parallel_eligible: bool = True
    retry_count: int = 0
    shell: bool = False


class EnhancedProcessManager:
    """
    Enhanced process manager with parallel execution capabilities
    Integrates ParallelHookExecutor for advanced concurrent process management
    """

    def __init__(self, logger: logging.Logger | None = None,
                 max_workers: int = 4, max_concurrent: int = MAX_PARALLEL_PROCESSES):
        self.logger = logger or logging.getLogger(__name__)
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent

        # Traditional executors
        self.active_processes: list[subprocess.Popen[str]] = []
        self._thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self._process_executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self._lock = threading.RLock()

        # Enhanced parallel execution with proper type annotations
        self.parallel_executor: ParallelHookExecutor | None = None
        self.context_executor: ContextSharedExecutor | None = None
        self.parallel_enabled = False

        if PARALLEL_EXECUTOR_AVAILABLE:
            try:
                self.parallel_executor = ParallelHookExecutor(
                    max_workers=max_workers,
                    max_concurrent=max_concurrent
                )
                self.context_executor = ContextSharedExecutor(self.parallel_executor)
                self.parallel_enabled = True
                self.logger.info(f"Enhanced process manager initialized with parallel execution ({max_workers} workers)")
            except Exception as e:
                self.logger.warning(f"Failed to initialize parallel executor: {e}")
                self.parallel_enabled = False
        else:
            self.logger.warning("Parallel executor not available, using traditional process management")

        # Performance tracking
        self.execution_stats = {
            'total_commands': 0,
            'parallel_commands': 0,
            'sequential_commands': 0,
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'parallel_efficiency_gain': 0.0
        }

    def log(self, level: str, message: str) -> None:
        """Log a message using the configured logger"""
        getattr(self.logger, level)(message)

    def kill_process_tree(self, pid: int) -> bool:
        """
        Kill a process and all its children with enhanced error handling
        Returns True if successful, False otherwise
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            self.log('debug', f"Killing process tree for PID {pid} with {len(children)} children")

            # Kill children first
            for child in children:
                with contextlib.suppress(psutil.NoSuchProcess):
                    child.terminate()

            # Give them time to terminate gracefully
            _, alive = psutil.wait_procs(children, timeout=PROCESS_TERMINATE_TIMEOUT)

            # Force kill any remaining
            for p in alive:
                with contextlib.suppress(psutil.NoSuchProcess):
                    p.kill()

            # Finally kill the parent
            try:
                parent.terminate()
                parent.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                with contextlib.suppress(psutil.NoSuchProcess):
                    parent.kill()

            self.log('info', f"Successfully killed process tree for PID {pid}")
            return True

        except Exception as e:
            self.log('warning', f"Error killing process tree for PID {pid}: {e}")
            return False

    async def execute_commands_parallel_advanced(self,
                                               requests: list[ProcessExecutionRequest],
                                               execution_mode: str | None = None,
                                               shared_context: dict[str, Any] | None = None) -> list[ExecutionResult]:
        """
        Execute multiple commands using advanced parallel execution
        """
        if not self.parallel_enabled or not requests or not self.parallel_executor:
            return await self._fallback_parallel_execution(requests)

        # Convert requests to HookCommands
        hook_commands = []
        for req in requests:
            env = os.environ.copy()
            if req.environment:
                env.update(req.environment)

            hook_command = HookCommand(
                command=req.command,
                timeout=req.timeout,
                parallel=req.parallel_eligible,
                environment=env,
                working_dir=req.working_dir,
                retry_count=req.retry_count,
                priority=req.priority
            )
            hook_commands.append(hook_command)

        try:
            start_time = time.time()

            # Execute with parallel executor
            if shared_context and self.context_executor:
                results = await self.context_executor.execute_with_context(
                    hook_commands, shared_context
                )
            else:
                # Check if ExecutionMode is available
                if ExecutionMode is None:
                    # Fallback when ExecutionMode is not available
                    return await self._fallback_parallel_execution(requests)

                # Convert string execution_mode to ExecutionMode enum
                if execution_mode:
                    try:
                        if hasattr(ExecutionMode, execution_mode.upper()):
                            mode = getattr(ExecutionMode, execution_mode.upper())
                        else:
                            mode = ExecutionMode.ADAPTIVE
                    except (AttributeError, TypeError):
                        mode = ExecutionMode.ADAPTIVE
                else:
                    mode = ExecutionMode.ADAPTIVE

                results = await self.parallel_executor.execute_hooks_parallel(
                    hook_commands, mode
                )

            execution_time = time.time() - start_time

            # Update statistics
            self._update_stats(len(requests), execution_time, results, parallel=True)

            self.log('info', f"Parallel execution completed: {len(results)} commands in {execution_time:.2f}s")

            return results

        except Exception as e:
            self.log('error', f"Advanced parallel execution failed: {e}")
            return await self._fallback_parallel_execution(requests)

    async def _fallback_parallel_execution(self,
                                         requests: list[ProcessExecutionRequest]) -> list[ExecutionResult]:
        """Fallback to basic parallel execution when advanced features fail"""
        results: list[ExecutionResult] = []
        start_time = time.time()

        # Use traditional ThreadPoolExecutor for fallback
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for req in requests:
                future = executor.submit(self._execute_single_request, req)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=max(req.timeout for req in requests) + 10)
                    results.append(result)
                except Exception as e:
                    error_result = ExecutionResult(
                        command="unknown",
                        return_code=-1,
                        stdout="",
                        stderr=str(e),
                        execution_time=0.0,
                        success=False,
                        error=str(e)
                    )
                    results.append(error_result)

        execution_time = time.time() - start_time
        self._update_stats(len(requests), execution_time, results, parallel=False)

        return results

    def _execute_single_request(self, request: ProcessExecutionRequest) -> ExecutionResult:
        """Execute a single process request and return ExecutionResult"""
        start_time = time.time()

        try:
            return_code, stdout, stderr = self.execute_command(
                request.command,
                timeout=request.timeout,
                shell=request.shell,
                env=request.environment,
                cwd=request.working_dir
            )

            execution_time = time.time() - start_time
            success = return_code == 0

            return ExecutionResult(
                command=request.command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                success=success
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                command=request.command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

    def execute_command(self, cmd: str, timeout: int = DEFAULT_COMMAND_TIMEOUT,
                       shell: bool = False, env: dict[str, str] | None = None,
                       cwd: str | None = None) -> tuple[int, str, str]:
        """
        Execute a command with enhanced process management
        Returns: (return_code, stdout, stderr)
        """
        self.log('debug', f"Executing command: {cmd}")

        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            # For shell commands, use process groups to ensure all children can be killed
            if shell:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=process_env,
                    cwd=cwd,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
            else:
                # Split command into list for non-shell execution
                cmd_list = cmd.split() if isinstance(cmd, str) else cmd
                process = subprocess.Popen(
                    cmd_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=process_env,
                    cwd=cwd
                )

            with self._lock:
                self.active_processes.append(process)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode

                self.log('debug', f"Command completed with return code: {return_code}")
                if stderr and return_code != 0:
                    self.log('warning', f"Command stderr: {stderr}")

                self._update_basic_stats(True)
                return return_code, stdout, stderr

            except subprocess.TimeoutExpired:
                self.log('error', f"Command timed out after {timeout} seconds: {cmd}")

                # Kill the entire process group if shell command
                if shell and os.name != 'nt':
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        time.sleep(2)
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    # Use enhanced process tree killing
                    self.kill_process_tree(process.pid)

                # Get any partial output
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", "Process timed out and was killed"

                self._update_basic_stats(False)
                return -1, stdout, f"Timeout after {timeout} seconds. {stderr}"

            finally:
                # Remove from active processes
                with self._lock:
                    if process in self.active_processes:
                        self.active_processes.remove(process)

        except Exception as e:
            self.log('error', f"Failed to execute command: {e}")
            self._update_basic_stats(False)
            return -1, "", str(e)

    def execute_batch_commands(self, commands: list[str],
                             timeout: int = DEFAULT_COMMAND_TIMEOUT,
                             shell: bool = False,
                             parallel: bool = True) -> list[tuple[int, str, str]]:
        """
        Execute a batch of commands with optional parallel execution
        """
        if parallel and len(commands) > 1:
            # Create execution requests
            requests = [
                ProcessExecutionRequest(
                    command=cmd,
                    timeout=timeout,
                    shell=shell,
                    parallel_eligible=True
                ) for cmd in commands
            ]

            # Use async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    self.execute_commands_parallel_advanced(requests)
                )
                # Convert ExecutionResults to tuples
                return [(r.return_code, r.stdout, r.stderr) for r in results]
            finally:
                loop.close()
        else:
            # Sequential execution
            results = []
            for cmd in commands:
                result = self.execute_command(cmd, timeout=timeout, shell=shell)
                results.append(result)
            return results

    def set_shared_context(self, key: str, value: Any) -> None:
        """Set a shared context value for parallel execution"""
        if hasattr(self, '_shared_context'):
            self._shared_context[key] = value
        else:
            self._shared_context = {key: value}

    def get_shared_context(self, key: str, default: Any = None) -> Any:
        """Get a shared context value"""
        return getattr(self, '_shared_context', {}).get(key, default)

    def update_shared_context(self, updates: dict[str, Any]) -> None:
        """Update multiple shared context values"""
        if hasattr(self, '_shared_context'):
            self._shared_context.update(updates)
        else:
            self._shared_context = updates.copy()

    def get_execution_stats(self) -> dict[str, Any]:
        """Get current execution statistics"""
        with self._lock:
            stats = self.execution_stats.copy()
            stats['active_processes'] = len(self.active_processes)
            stats['parallel_executor_available'] = self.parallel_enabled
            stats['max_workers'] = self.max_workers
            stats['max_concurrent'] = self.max_concurrent

            # Calculate success rate
            if stats['total_commands'] > 0:
                stats['success_rate'] = (
                    (stats['total_commands'] - stats.get('failed_commands', 0)) /
                    stats['total_commands']
                ) * 100

            return stats

    def _update_stats(self, command_count: int, execution_time: float,
                     results: list[ExecutionResult], parallel: bool) -> None:
        """Update execution statistics"""
        with self._lock:
            self.execution_stats['total_commands'] += command_count
            if parallel:
                self.execution_stats['parallel_commands'] += command_count
            else:
                self.execution_stats['sequential_commands'] += command_count

            # Update average execution time
            total_time = (
                self.execution_stats['average_execution_time'] *
                (self.execution_stats['total_commands'] - command_count)
            ) + execution_time
            self.execution_stats['average_execution_time'] = (
                total_time / self.execution_stats['total_commands']
            )

            # Count failures
            failed_count = sum(1 for r in results if not r.success)
            if 'failed_commands' not in self.execution_stats:
                self.execution_stats['failed_commands'] = 0
            self.execution_stats['failed_commands'] += failed_count

    def _update_basic_stats(self, success: bool) -> None:
        """Update basic statistics for single command execution"""
        with self._lock:
            self.execution_stats['total_commands'] += 1
            self.execution_stats['sequential_commands'] += 1

            if not success:
                if 'failed_commands' not in self.execution_stats:
                    self.execution_stats['failed_commands'] = 0
                self.execution_stats['failed_commands'] += 1

    def cleanup_all(self) -> None:
        """Clean up all active processes and executors"""
        self.log('info', "Cleaning up all active processes and executors")

        # Kill all active processes
        with self._lock:
            for process in self.active_processes[:]:
                try:
                    self.kill_process_tree(process.pid)
                except Exception as e:
                    self.log('warning', f"Error killing process {process.pid}: {e}")
            self.active_processes.clear()

        # Shutdown executors
        try:
            self._thread_executor.shutdown(wait=True)
        except Exception as e:
            self.log('warning', f"Error shutting down thread executor: {e}")

        try:
            self._process_executor.shutdown(wait=True)
        except Exception as e:
            self.log('warning', f"Error shutting down process executor: {e}")

        # Cleanup parallel executor if available
        if self.parallel_enabled and PARALLEL_EXECUTOR_AVAILABLE:
            try:
                cleanup_executor()
            except Exception as e:
                self.log('warning', f"Error cleaning up parallel executor: {e}")

        self.log('info', "Cleanup completed")

    def __del__(self) -> None:
        """Cleanup on destruction"""
        try:
            self.cleanup_all()
        except Exception:
            pass  # Ignore errors during cleanup in destructor


def enhanced_find_and_kill_zombie_processes(logger: logging.Logger | None = None) -> int:
    """
    Find and kill zombie processes with enhanced detection
    Returns the number of processes killed
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    killed_count = 0

    try:
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'status', 'create_time']):
            try:
                # Skip if process is not a zombie or if it's too new
                if proc.info['status'] != psutil.STATUS_ZOMBIE:
                    continue

                current_time = time.time()
                if current_time - proc.info['create_time'] < CLEANUP_AGE_THRESHOLD:
                    continue

                if logger:
                    logger.debug(f"Found zombie process: PID {proc.info['pid']}, "
                               f"name: {proc.info['name']}")

                # Get parent process
                try:
                    parent = psutil.Process(proc.info['ppid'])
                    parent_info = f"parent PID {parent.pid} ({parent.name()})"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    parent_info = f"parent PID {proc.info['ppid']} (unknown)"

                # Try to clean up zombie by signaling parent or killing directly
                try:
                    # First try to signal the parent to clean up
                    if proc.info['ppid'] > 1:  # Don't signal init
                        try:
                            parent = psutil.Process(proc.info['ppid'])
                            parent.send_signal(signal.SIGCHLD)
                            time.sleep(0.1)  # Give parent time to clean up
                        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                            pass

                    # If still exists, try to terminate it directly
                    try:
                        zombie_proc = psutil.Process(proc.info['pid'])
                        if zombie_proc.status() == psutil.STATUS_ZOMBIE:
                            zombie_proc.terminate()
                            killed_count += 1
                            if logger:
                                logger.info(f"Killed zombie process PID {proc.info['pid']} "
                                          f"({proc.info['name']}) with {parent_info}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process might have been cleaned up already
                        pass

                except Exception as e:
                    if logger:
                        logger.warning(f"Failed to kill zombie process PID {proc.info['pid']}: {e}")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process disappeared or access denied, continue
                continue

    except Exception as e:
        if logger:
            logger.error(f"Error during zombie process cleanup: {e}")

    if logger:
        logger.info(f"Zombie process cleanup completed, killed {killed_count} processes")

    return killed_count


def create_enhanced_process_manager(logger: logging.Logger | None = None,
                                  max_workers: int = 4,
                                  max_concurrent: int = MAX_PARALLEL_PROCESSES) -> EnhancedProcessManager:
    """Create and return a configured EnhancedProcessManager instance"""
    return EnhancedProcessManager(
        logger=logger,
        max_workers=max_workers,
        max_concurrent=max_concurrent
    )
