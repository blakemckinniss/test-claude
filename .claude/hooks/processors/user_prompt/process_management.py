#!/usr/bin/env python3
"""
Process management module for user prompt processing
Enhanced with parallel execution capabilities
"""

import concurrent.futures
import contextlib
import logging
import multiprocessing
import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import psutil

# Import the enhanced process manager
try:
    from .enhanced_process_management import (
        EnhancedProcessManager,
        ProcessExecutionRequest,
        create_enhanced_process_manager,
        enhanced_find_and_kill_zombie_processes,
    )
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Constants
PROCESS_TERMINATE_TIMEOUT = 3  # seconds


class ProcessManager:
    """Enhanced process manager with concurrent execution support"""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger
        self.active_processes: list[subprocess.Popen] = []
        self._thread_executor = ThreadPoolExecutor(max_workers=4)
        self._process_executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self._lock = threading.Lock()

    def log(self, level: str, message: str):
        """Log a message if logger is available"""
        if self.logger:
            getattr(self.logger, level)(message)

    def kill_process_tree(self, pid: int):
        """Kill a process and all its children"""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

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

        except Exception as e:
            self.log('warning', f"Error killing process tree for PID {pid}: {e}")

    def execute_command(self, cmd: str, timeout: int = 60, shell: bool = False) -> tuple[int, str, str]:
        """
        Execute a command with proper process management
        Returns: (return_code, stdout, stderr)
        """
        self.log('info', f"Executing command: {cmd}")

        try:
            # For shell commands, use process groups to ensure all children can be killed
            if shell:
                # Create new process group
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
            else:
                # Split command into list for non-shell execution
                cmd_list = cmd.split() if isinstance(cmd, str) else cmd
                process = subprocess.Popen(
                    cmd_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            with self._lock:
                self.active_processes.append(process)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode

                self.log('info', f"Command completed with return code: {return_code}")
                if stderr:
                    self.log('warning', f"Command stderr: {stderr}")

                return return_code, stdout, stderr

            except subprocess.TimeoutExpired:
                self.log('error', f"Command timed out after {timeout} seconds")

                # Kill the entire process group if shell command
                if shell and os.name != 'nt':
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        time.sleep(2)
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    # Use psutil to kill process tree
                    self.kill_process_tree(process.pid)

                # Get any partial output
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", "Process timed out and was killed"

                return -1, stdout, f"Timeout after {timeout} seconds. {stderr}"

            finally:
                # Remove from active processes
                with self._lock:
                    if process in self.active_processes:
                        self.active_processes.remove(process)

        except Exception as e:
            self.log('error', f"Failed to execute command: {e}")
            return -1, "", str(e)

    def execute_command_with_executor(self, cmd: str, timeout: int = 60,
                                    shell: bool = False, use_thread_pool: bool = True) -> concurrent.futures.Future:
        """Execute command using thread or process pool executor"""
        executor = self._thread_executor if use_thread_pool else self._process_executor
        return executor.submit(self.execute_command, cmd, timeout, shell)

    def execute_commands_parallel(self, commands: list[str], timeout: int = 60,
                                 shell: bool = False, max_workers: int | None = None) -> list[tuple[int, str, str]]:
        """Execute multiple commands in parallel using ThreadPoolExecutor"""
        with ThreadPoolExecutor(max_workers=max_workers or min(len(commands), 4)) as executor:
            futures = [executor.submit(self.execute_command, cmd, timeout, shell) for cmd in commands]
            results = []

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=timeout + 10)  # Add buffer time
                    results.append(result)
                except Exception as e:
                    self.log('error', f"Parallel command execution failed: {e}")
                    results.append((-1, "", str(e)))

            return results

    def execute_cpu_intensive_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Execute CPU-intensive task using ProcessPoolExecutor"""
        return self._process_executor.submit(func, *args, **kwargs)

    def execute_io_intensive_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Execute I/O-intensive task using ThreadPoolExecutor"""
        return self._thread_executor.submit(func, *args, **kwargs)

    def cleanup_all(self):
        """Clean up all active processes and executors"""
        with self._lock:
            for process in self.active_processes[:]:  # Copy list to avoid modification during iteration
                try:
                    if process.poll() is None:  # Process still running
                        self.kill_process_tree(process.pid)
                except Exception as e:
                    self.log('warning', f"Error cleaning up process: {e}")

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

    def __del__(self):
        """Cleanup on destruction"""
        with contextlib.suppress(Exception):
            self.cleanup_all()


def find_and_kill_zombie_processes(logger: logging.Logger | None = None):
    """Find and kill zombie processes with enhanced logging"""
    # Use enhanced version if available
    if ENHANCED_AVAILABLE:
        return enhanced_find_and_kill_zombie_processes(logger)

    # Fallback to original implementation
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
            try:
                # Check for zombie status
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    if logger:
                        logger.warning(f"Found zombie process: PID={proc.info['pid']}, Name={proc.info['name']}")
                    # Zombie processes need parent to reap them
                    try:
                        parent = proc.parent()
                        if parent:
                            os.kill(parent.pid, signal.SIGCHLD)
                    except Exception:
                        pass

                # Check for long-running Claude Flow processes
                elif proc.info['cmdline'] and any('claude-flow' in str(arg) for arg in proc.info['cmdline']):
                    try:
                        create_time = proc.create_time()
                        age = time.time() - create_time

                        # Kill if older than 15 minutes (900 seconds)
                        if age > 900:
                            if logger:
                                logger.warning(f"Killing old Claude Flow process: PID={proc.info['pid']}, Age={age:.0f}s")
                            proc.terminate()
                            proc.wait(timeout=3)
                            killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        try:
                            proc.kill()
                            killed_count += 1
                        except Exception:
                            pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as e:
        if logger:
            logger.error(f"Error in zombie process cleanup: {e}")

    return killed_count


# Enhanced factory functions
def create_process_manager(logger: logging.Logger | None = None,
                          enhanced: bool = True,
                          max_workers: int = 4,
                          max_concurrent: int = 8) -> ProcessManager:
    """
    Create a process manager instance with optional enhanced capabilities

    Args:
        logger: Optional logger instance
        enhanced: Whether to use enhanced parallel capabilities (if available)
        max_workers: Maximum number of worker threads
        max_concurrent: Maximum number of concurrent processes

    Returns:
        ProcessManager instance (enhanced if available and requested)
    """
    if enhanced and ENHANCED_AVAILABLE:
        return create_enhanced_process_manager(logger, max_workers, max_concurrent)
    else:
        return ProcessManager(logger)


# Export enhanced classes if available
if ENHANCED_AVAILABLE:
    # Make enhanced classes available at module level
    globals()['ProcessExecutionRequest'] = ProcessExecutionRequest
    globals()['EnhancedProcessManager'] = EnhancedProcessManager

    # Override the default ProcessManager with enhanced version
    ProcessManager = EnhancedProcessManager
