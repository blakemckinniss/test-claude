#!/usr/bin/env python3
"""
Parallel Hook Execution System for Claude Code
Enables concurrent execution of hooks with proper synchronization and error handling
"""

import asyncio
import builtins
import concurrent.futures
import contextlib
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"

@dataclass
class HookCommand:
    """Represents a hook command to execute"""
    command: str
    timeout: int = 60
    parallel: bool = True
    environment: dict[str, str] | None = None
    working_dir: str | None = None
    retry_count: int = 0
    priority: int = 0  # Higher numbers = higher priority

@dataclass
class ExecutionResult:
    """Result of hook execution"""
    command: str
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    error: str | None = None

class ParallelHookExecutor:
    """Executes hooks in parallel with intelligent coordination"""

    def __init__(self, max_workers: int = 4, max_concurrent: int = 8):
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_commands: dict[str, subprocess.Popen] = {}
        self.results_cache: dict[str, ExecutionResult] = {}
        self.execution_stats = {
            'total_executed': 0,
            'parallel_executed': 0,
            'average_time': 0.0,
            'success_rate': 0.0
        }
        self.lock = threading.RLock()
        self._closed = False

        # Setup logging
        self.logger = logging.getLogger(__name__)

    async def execute_hooks_parallel(self, commands: list[HookCommand],
                                   execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE) -> list[ExecutionResult]:
        """Execute multiple hooks with optimal parallelization"""

        if not commands:
            return []

        # Determine execution strategy
        if execution_mode == ExecutionMode.ADAPTIVE:
            execution_mode = self._determine_optimal_mode(commands)

        if execution_mode == ExecutionMode.SEQUENTIAL:
            return await self._execute_sequential(commands)
        else:
            return await self._execute_parallel(commands)

    def _determine_optimal_mode(self, commands: list[HookCommand]) -> ExecutionMode:
        """Determine optimal execution mode based on command characteristics"""

        # Analyze commands
        total_commands = len(commands)
        parallel_eligible = sum(1 for cmd in commands if cmd.parallel)
        avg_timeout = sum(cmd.timeout for cmd in commands) / total_commands if total_commands > 0 else 60

        # Decision logic
        if total_commands <= 2:
            return ExecutionMode.SEQUENTIAL
        elif parallel_eligible / total_commands > 0.7 and avg_timeout < 30 or total_commands > 5:
            return ExecutionMode.PARALLEL
        else:
            return ExecutionMode.SEQUENTIAL

    async def _execute_sequential(self, commands: list[HookCommand]) -> list[ExecutionResult]:
        """Execute commands sequentially"""
        results = []

        for command in commands:
            result = await self._execute_single_command(command)
            results.append(result)

            # Stop on critical failures
            if not result.success and command.priority > 8:
                self.logger.error(f"Critical command failed: {command.command}")
                break

        return results

    async def _execute_parallel(self, commands: list[HookCommand]) -> list[ExecutionResult]:
        """Execute commands in parallel with coordination"""

        # Sort by priority (higher first)
        sorted_commands = sorted(commands, key=lambda x: x.priority, reverse=True)

        # Create execution tasks
        tasks = []
        for command in sorted_commands:
            task = self._create_execution_task(command)
            tasks.append(task)

        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ExecutionResult(
                    command=sorted_commands[i].command,
                    return_code=-1,
                    stdout="",
                    stderr=str(result),
                    execution_time=0.0,
                    success=False,
                    error=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)

        return processed_results

    async def _create_execution_task(self, command: HookCommand) -> ExecutionResult:
        """Create an async task for command execution"""
        async with self.semaphore:  # Control concurrency
            return await self._execute_single_command(command)

    async def _execute_single_command(self, command: HookCommand) -> ExecutionResult:
        """Execute a single command asynchronously"""
        start_time = time.time()

        try:
            # Prepare environment
            env = os.environ.copy()
            if command.environment:
                env.update(command.environment)

            # Execute command
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool,
                self._run_subprocess,
                command.command,
                command.timeout,
                env,
                command.working_dir
            )

            execution_time = time.time() - start_time

            return_code, stdout, stderr = result
            success = return_code == 0

            # Update statistics
            self._update_stats(execution_time, success)

            return ExecutionResult(
                command=command.command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                success=success
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command execution failed: {command.command}, Error: {e}")

            return ExecutionResult(
                command=command.command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

    def _run_subprocess(self, command: str, timeout: int, env: dict[str, str],
                       working_dir: str | None) -> tuple[int, str, str]:
        """Run subprocess synchronously (called from thread pool)"""

        try:
            # Create process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=working_dir,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )

            # Track active process
            with self.lock:
                self.active_commands[command] = process

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return process.returncode, stdout, stderr

            except subprocess.TimeoutExpired:
                # Kill process group on timeout
                try:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), 9)
                    else:
                        process.kill()
                except (OSError, ProcessLookupError) as e:
                    logger.debug(f"Error killing process group: {e}")

                # Get partial output
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", "Process timed out"

                return -1, stdout, f"Timeout after {timeout}s: {stderr}"

            finally:
                # Remove from active commands
                with self.lock:
                    self.active_commands.pop(command, None)

        except Exception as e:
            return -1, "", str(e)

    def _update_stats(self, execution_time: float, success: bool):
        """Update execution statistics"""
        with self.lock:
            self.execution_stats['total_executed'] += 1

            # Update average time
            total = self.execution_stats['total_executed']
            current_avg = self.execution_stats['average_time']
            self.execution_stats['average_time'] = (current_avg * (total - 1) + execution_time) / total

            # Update success rate
            if success:
                current_successes = self.execution_stats['success_rate'] * (total - 1)
                self.execution_stats['success_rate'] = (current_successes + 1) / total
            else:
                current_successes = self.execution_stats['success_rate'] * (total - 1)
                self.execution_stats['success_rate'] = current_successes / total

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics"""
        with self.lock:
            return {
                **self.execution_stats,
                'active_commands': len(self.active_commands),
                'thread_pool_workers': self.max_workers,
                'max_concurrent': self.max_concurrent
            }

    def cleanup(self):
        """Clean up resources and kill active processes"""
        with self.lock:
            if self._closed:
                return
            self._closed = True
            # Kill active processes
            for command, process in self.active_commands.items():
                try:
                    if process.poll() is None:
                        if os.name != 'nt':
                            os.killpg(os.getpgid(process.pid), 9)
                        else:
                            process.kill()
                        self.logger.info(f"Killed active process: {command}")
                except Exception as e:
                    self.logger.warning(f"Failed to kill process {command}: {e}")

            self.active_commands.clear()

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

    def __del__(self):
        """Cleanup on destruction"""
        with contextlib.suppress(builtins.BaseException):
            self.cleanup()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup"""
        self.cleanup()
        return False


class ContextSharedExecutor:
    """Executor that shares context between hooks"""

    def __init__(self, executor: ParallelHookExecutor):
        self.executor = executor
        self.shared_context: dict[str, Any] = {}
        self.context_lock = threading.RLock()

    def set_context(self, key: str, value: Any):
        """Set shared context value"""
        with self.context_lock:
            self.shared_context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get shared context value"""
        with self.context_lock:
            return self.shared_context.get(key, default)

    def update_context(self, updates: dict[str, Any]):
        """Update multiple context values"""
        with self.context_lock:
            self.shared_context.update(updates)

    async def execute_with_context(self, commands: list[HookCommand],
                                 initial_context: dict[str, Any] | None = None) -> list[ExecutionResult]:
        """Execute commands with shared context"""

        if initial_context:
            self.update_context(initial_context)

        # Add context to command environments
        with self.context_lock:
            context_snapshot = self.shared_context.copy()
        
        for command in commands:
            if command.environment is None:
                command.environment = {}

            # Add shared context as environment variables
            for key, value in context_snapshot.items():
                env_key = f"CLAUDE_CONTEXT_{key.upper()}"
                command.environment[env_key] = str(value)

        return await self.executor.execute_hooks_parallel(commands)


# Global executor instance
_global_executor = ParallelHookExecutor(
    max_workers=int(os.environ.get('CLAUDE_HOOK_MAX_CONCURRENT', '4')),
    max_concurrent=8
)

_context_executor = ContextSharedExecutor(_global_executor)

# Public API functions
async def execute_hooks(commands: list[HookCommand],
                       execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE,
                       shared_context: dict[str, Any] | None = None) -> list[ExecutionResult]:
    """Execute hooks with optimal parallelization"""
    if shared_context:
        return await _context_executor.execute_with_context(commands, shared_context)
    else:
        return await _global_executor.execute_hooks_parallel(commands, execution_mode)

def create_hook_command(command: str, **kwargs) -> HookCommand:
    """Create a hook command with sensible defaults"""
    return HookCommand(command=command, **kwargs)

def get_execution_stats() -> dict[str, Any]:
    """Get global execution statistics"""
    return _global_executor.get_stats()

def set_shared_context(key: str, value: Any):
    """Set shared context for all hook executions"""
    _context_executor.set_context(key, value)

def get_shared_context(key: str, default: Any = None) -> Any:
    """Get shared context value"""
    return _context_executor.get_context(key, default)

def cleanup_executor():
    """Cleanup global executor resources"""
    _global_executor.cleanup()

# Performance monitoring
class HookPerformanceAnalyzer:
    """Analyze hook performance and provide optimization suggestions"""

    def __init__(self):
        self.execution_history: list[ExecutionResult] = []
        self.lock = threading.Lock()

    def record_execution(self, result: ExecutionResult):
        """Record hook execution result"""
        with self.lock:
            self.execution_history.append(result)

            # Keep only recent history (last 1000 executions)
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]

    def analyze_performance(self) -> dict[str, Any]:
        """Analyze performance and provide recommendations"""
        with self.lock:
            if not self.execution_history:
                return {'recommendations': ['No execution history available']}

            # Calculate metrics
            total_executions = len(self.execution_history)
            successful = [r for r in self.execution_history if r.success]
            failed = [r for r in self.execution_history if not r.success]

            avg_execution_time = sum(r.execution_time for r in self.execution_history) / total_executions
            success_rate = len(successful) / total_executions

            # Identify slow commands
            slow_commands = [r for r in self.execution_history if r.execution_time > 5.0]
            common_failures = {}

            for result in failed:
                cmd_base = result.command.split()[0] if result.command else 'unknown'
                common_failures[cmd_base] = common_failures.get(cmd_base, 0) + 1

            # Generate recommendations
            recommendations = []

            if success_rate < 0.9:
                recommendations.append(f"Low success rate ({success_rate:.1%}) - investigate failing commands")

            if avg_execution_time > 2.0:
                recommendations.append(f"High average execution time ({avg_execution_time:.1f}s) - consider optimization")

            if slow_commands:
                slow_cmd_names = list({r.command.split()[0] for r in slow_commands})[:3]
                recommendations.append(f"Slow commands detected: {', '.join(slow_cmd_names)}")

            if common_failures:
                most_failed = max(common_failures.items(), key=lambda x: x[1])
                recommendations.append(f"Most failing command: {most_failed[0]} ({most_failed[1]} failures)")

            return {
                'total_executions': total_executions,
                'success_rate': success_rate,
                'avg_execution_time': avg_execution_time,
                'slow_commands_count': len(slow_commands),
                'most_common_failures': dict(list(common_failures.items())[:5]),
                'recommendations': recommendations or ['Performance is optimal']
            }

# Global performance analyzer
_performance_analyzer = HookPerformanceAnalyzer()

def get_performance_analysis() -> dict[str, Any]:
    """Get performance analysis and recommendations"""
    return _performance_analyzer.analyze_performance()

def record_hook_execution(result: ExecutionResult):
    """Record hook execution for performance analysis"""
    _performance_analyzer.record_execution(result)
