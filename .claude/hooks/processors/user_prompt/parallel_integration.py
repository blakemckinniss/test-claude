#!/usr/bin/env python3
"""
Integration layer for parallel_executor.py with user prompt processor
Provides parallel execution capabilities for MCP tools and workflow orchestration
"""

import logging
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add async_ops directory to path to import parallel_executor
async_ops_dir = Path(__file__).parent.parent / 'async_ops'
sys.path.insert(0, str(async_ops_dir))

# Runtime imports
try:
    from parallel_executor import ExecutionMode, ExecutionResult, HookCommand, ParallelHookExecutor
    PARALLEL_EXECUTOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Failed to import parallel_executor: {e}")
    PARALLEL_EXECUTOR_AVAILABLE = False
    ParallelHookExecutor = None
    HookCommand = None
    ExecutionResult = None
    ExecutionMode = None


@dataclass
class MCPToolExecution:
    """Represents an MCP tool execution request"""
    server: str
    tool: str
    params: dict[str, Any] | None = None
    timeout: int = 60
    priority: int = 5


class ParallelMCPExecutor:
    """
    Parallel executor specifically designed for MCP tool operations
    Integrates with the existing user prompt processor workflow
    """

    def __init__(self, max_workers: int = 4, max_concurrent: int = 6):
        self.logger = logging.getLogger(__name__)

        if PARALLEL_EXECUTOR_AVAILABLE and ParallelHookExecutor is not None:
            self.executor = ParallelHookExecutor(max_workers=max_workers, max_concurrent=max_concurrent)
            self.enabled = True
            self.logger.info(f"Parallel MCP executor initialized with {max_workers} workers, {max_concurrent} max concurrent")
        else:
            self.executor = None
            self.enabled = False
            self.logger.warning("Parallel executor not available, falling back to sequential execution")

    async def execute_mcp_tools_parallel(self, tool_executions: list[MCPToolExecution]) -> dict[str, Any]:
        """
        Execute multiple MCP tools in parallel and return aggregated results
        """
        if not self.enabled or not tool_executions:
            return await self._execute_sequential_fallback(tool_executions)

        # Convert MCP tool executions to HookCommands
        hook_commands = []
        for execution in tool_executions:
            command = self._build_mcp_command(execution)
            if HookCommand is None:
                # Fallback when HookCommand is not available
                return await self._execute_sequential_fallback(tool_executions)
            hook_command = HookCommand(
                command=command,
                timeout=execution.timeout,
                parallel=True,
                priority=execution.priority,
                environment=self._get_mcp_environment()
            )
            hook_commands.append(hook_command)

        try:
            # Execute in parallel
            if self.executor is None or ExecutionMode is None:
                # Fallback when executor or ExecutionMode is not available
                return await self._execute_sequential_fallback(tool_executions)
            results = await self.executor.execute_hooks_parallel(
                hook_commands,
                ExecutionMode.ADAPTIVE
            )

            # Process and aggregate results
            return self._process_mcp_results(tool_executions, results)

        except Exception as e:
            self.logger.error(f"Parallel MCP execution failed: {e}")
            return await self._execute_sequential_fallback(tool_executions)

    def _build_mcp_command(self, execution: MCPToolExecution) -> str:
        """Build MCP command string from execution request"""
        cmd_parts = []  # Initialize cmd_parts to ensure it's always defined

        if execution.server == 'claude-flow':
            cmd_parts = ['npx', 'claude-flow@alpha', 'mcp', execution.tool]
            # Add parameters for claude-flow
            if execution.params:
                for key, value in execution.params.items():
                    if isinstance(value, bool):
                        if value:
                            cmd_parts.append(f'--{key}')
                    else:
                        cmd_parts.extend([f'--{key}', str(value)])
        elif execution.server == 'serena':
            cmd_parts = ['serena', 'mcp', execution.tool]
            # Add parameters for serena
            if execution.params:
                for key, value in execution.params.items():
                    if isinstance(value, bool):
                        if value:
                            cmd_parts.append(f'--{key}')
                    else:
                        cmd_parts.extend([f'--{key}', str(value)])
        else:
            # Generic MCP command
            cmd_parts = ['mcp', 'call', execution.server, execution.tool]
            if execution.params:
                import json
                # Create temp file for params (would need proper cleanup)
                cmd_parts.extend(['--params', json.dumps(execution.params)])

        return ' '.join(cmd_parts)

    def _get_mcp_environment(self) -> dict[str, str]:
        """Get environment variables for MCP execution"""
        env = {
            'CLAUDE_PROJECT_DIR': os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()),
            'NODE_ENV': 'production',
            'PATH': os.environ.get('PATH', '')
        }
        return env

    def _process_mcp_results(self, executions: list[MCPToolExecution], results: list[Any]) -> dict[str, Any]:
        """Process parallel MCP execution results"""
        processed_results = {
            'success': True,
            'total_executed': len(results),
            'successful': 0,
            'failed': 0,
            'results': {},
            'errors': [],
            'execution_summary': {
                'total_time': 0.0,
                'parallel_efficiency': 0.0
            }
        }

        total_time = 0.0
        sequential_time_estimate = 0.0

        for _i, (execution, result) in enumerate(zip(executions, results, strict=False)):
            tool_key = f"{execution.server}.{execution.tool}"

            exec_time = getattr(result, 'execution_time', 0.0) if result else 0.0
            total_time = max(total_time, exec_time)  # Parallel time is the max
            sequential_time_estimate += exec_time

            if result and hasattr(result, 'success') and result.success:
                processed_results['successful'] += 1
                processed_results['results'][tool_key] = {
                    'success': True,
                    'stdout': getattr(result, 'stdout', ''),
                    'execution_time': getattr(result, 'execution_time', 0.0)
                }
            else:
                processed_results['failed'] += 1
                processed_results['success'] = False
                error_msg = ''
                return_code = -1
                if result:
                    error_msg = getattr(result, 'stderr', '') or getattr(result, 'error', '')
                    return_code = getattr(result, 'return_code', -1)
                processed_results['results'][tool_key] = {
                    'success': False,
                    'error': error_msg,
                    'return_code': return_code
                }
                processed_results['errors'].append({
                    'tool': tool_key,
                    'error': error_msg
                })

        # Calculate efficiency
        if sequential_time_estimate > 0:
            efficiency = (sequential_time_estimate - total_time) / sequential_time_estimate * 100
            processed_results['execution_summary']['parallel_efficiency'] = efficiency

        processed_results['execution_summary']['total_time'] = total_time
        processed_results['execution_summary']['estimated_sequential_time'] = sequential_time_estimate

        return processed_results

    async def _execute_sequential_fallback(self, tool_executions: list[MCPToolExecution]) -> dict[str, Any]:
        """Fallback to sequential execution when parallel is not available"""
        self.logger.info("Using sequential fallback execution")

        results = {
            'success': True,
            'total_executed': len(tool_executions),
            'successful': 0,
            'failed': 0,
            'results': {},
            'errors': [],
            'execution_summary': {
                'total_time': 0.0,
                'parallel_efficiency': 0.0,
                'fallback_used': True
            }
        }

        import subprocess
        import time

        start_time = time.time()

        for execution in tool_executions:
            tool_key = f"{execution.server}.{execution.tool}"
            command = self._build_mcp_command(execution)

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=execution.timeout,
                    env=self._get_mcp_environment(),
                    check=False
                )

                if result.returncode == 0:
                    results['successful'] += 1
                    results['results'][tool_key] = {
                        'success': True,
                        'stdout': result.stdout,
                        'execution_time': 0.0  # Not measured in fallback
                    }
                else:
                    results['failed'] += 1
                    results['success'] = False
                    results['results'][tool_key] = {
                        'success': False,
                        'error': result.stderr,
                        'return_code': result.returncode
                    }
                    if hasattr(results['errors'], 'append'):
                        results['errors'].append({
                            'tool': tool_key,
                            'error': result.stderr
                        })

            except Exception as e:
                results['failed'] += 1
                results['success'] = False
                results['results'][tool_key] = {
                    'success': False,
                    'error': str(e),
                    'return_code': -1
                }
                if hasattr(results['errors'], 'append'):
                    results['errors'].append({
                        'tool': tool_key,
                        'error': str(e)
                    })

        results['execution_summary']['total_time'] = time.time() - start_time

        return results


class ParallelWorkflowOrchestrator:
    """
    Orchestrator for parallel workflow execution in user prompt processing
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_executor = ParallelMCPExecutor()

    async def orchestrate_analysis_workflow(self, prompt: str, analysis: dict[str, Any]) -> dict[str, Any]:
        """
        Orchestrate parallel analysis workflow based on prompt complexity
        """
        workflow_results = {
            'prompt_analysis': analysis,
            'parallel_executions': {},
            'recommendations': [],
            'performance_metrics': {}
        }

        # Determine what parallel operations to run based on analysis
        parallel_operations = self._plan_parallel_operations(prompt, analysis)

        if parallel_operations:
            self.logger.info(f"Executing {len(parallel_operations)} operations in parallel")

            # Execute operations in parallel
            parallel_results = await self.mcp_executor.execute_mcp_tools_parallel(parallel_operations)
            workflow_results['parallel_executions'] = parallel_results

            # Process results into recommendations
            recommendations = self._generate_recommendations_from_results(parallel_results, analysis)
            workflow_results['recommendations'] = recommendations

            # Add performance metrics
            workflow_results['performance_metrics'] = parallel_results.get('execution_summary', {})

        return workflow_results

    def _plan_parallel_operations(self, prompt: str, analysis: dict[str, Any]) -> list[MCPToolExecution]:
        """
        Plan which operations to execute in parallel based on prompt analysis
        """
        operations = []

        # Always get project context in parallel
        operations.append(MCPToolExecution(
            server='serena',
            tool='get_symbols_overview',
            params={'relative_path': '.'},
            priority=8,
            timeout=30
        ))

        # If needs swarm coordination
        if analysis.get('needs_swarm', False):
            operations.extend([
                MCPToolExecution(
                    server='claude-flow',
                    tool='swarm_init',
                    params={'topology': 'hierarchical', 'maxAgents': 5},
                    priority=9,
                    timeout=15
                ),
                MCPToolExecution(
                    server='claude-flow',
                    tool='agent_spawn',
                    params={'type': 'coordinator'},
                    priority=8,
                    timeout=15
                )
            ])

        # If has code analysis needs
        if analysis.get('has_code', False):
            operations.append(MCPToolExecution(
                server='serena',
                tool='search_for_pattern',
                params={'substring_pattern': r'def |class |function '},
                priority=7,
                timeout=20
            ))

        # If needs consultation
        if analysis.get('needs_consultation', False):
            operations.append(MCPToolExecution(
                server='zen',
                tool='chat',
                params={'prompt': prompt[:500], 'model': 'openai/o3-mini'},
                priority=6,
                timeout=45
            ))

        return operations

    def _generate_recommendations_from_results(self, parallel_results: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """
        Generate recommendations based on parallel execution results
        """
        recommendations = []

        if parallel_results.get('success', False):
            efficiency = parallel_results.get('execution_summary', {}).get('parallel_efficiency', 0)
            if efficiency > 50:
                recommendations.append(f"✅ Parallel execution achieved {efficiency:.1f}% efficiency gain")

            # Process specific tool results
            results = parallel_results.get('results', {})

            if 'serena.get_symbols_overview' in results:
                recommendations.append("📁 Project structure analyzed for context")

            if 'claude-flow.swarm_init' in results:
                recommendations.append("🐝 Swarm coordination initialized for complex task")

            if 'zen.chat' in results:
                recommendations.append("💬 Expert consultation completed")

        else:
            recommendations.append("⚠️ Some parallel operations failed, but core functionality maintained")

        return recommendations


# Factory functions for easy integration
def create_parallel_mcp_executor(max_workers: int = 4) -> ParallelMCPExecutor:
    """Create a parallel MCP executor instance"""
    return ParallelMCPExecutor(max_workers=max_workers)


def create_workflow_orchestrator() -> ParallelWorkflowOrchestrator:
    """Create a parallel workflow orchestrator instance"""
    return ParallelWorkflowOrchestrator()


# Async utility functions
async def run_parallel_analysis(prompt: str, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Convenience function to run parallel analysis workflow
    """
    orchestrator = create_workflow_orchestrator()
    return await orchestrator.orchestrate_analysis_workflow(prompt, analysis)
