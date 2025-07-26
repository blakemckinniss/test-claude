#!/usr/bin/env python3
"""
User Prompt Processor module for Claude Code hooks
"""

from .analysis import (
    analyze_prompt_complexity,
    cached_prompt_hash,
    detect_claude_flow_swarm_needs,
    detect_github_claude_flow_needs,
    detect_github_repository_context_prompt,
    detect_library_documentation_needs,
    detect_serena_code_analysis_needs,
    detect_smart_mcp_triggers,
    determine_zen_workflow,
    expensive_prompt_analysis,
)
from .async_ops import AsyncFileOperations, AsyncProcessManager
from .cache import HAS_ORCHESTRATION_CACHE, UserPromptCacheManager, warm_user_prompt_cache
from .http_client import UserPromptHTTPClientManager
from .mcp_tools import (
    generate_code2prompt_context,
    generate_serena_project_context,
    get_available_mcp_tools,
    run_claude_flow_mcp_command,
    run_context7_documentation_lookup,
    run_mcp_tool_command,
    run_serena_mcp_command,
)
from .monitoring import UserPromptMonitor, log_prompt_event
from .parallel_integration import (
    MCPToolExecution,
    ParallelMCPExecutor,
    ParallelWorkflowOrchestrator,
    create_parallel_mcp_executor,
    create_workflow_orchestrator,
    run_parallel_analysis,
)
from .process_management import ProcessManager, create_process_manager, find_and_kill_zombie_processes
from .workflows import (
    create_zen_consultation_task,
    extract_consultation_data,
    generate_coordination_output,
    judge_and_spawn_agents_functional,
    merge_analysis_with_consultation,
    run_claude_flow_swarm_orchestration,
    run_enhanced_mcp_orchestration,
    run_github_claude_flow_orchestration,
    run_github_mcp_integration,
    run_zen_consultation_functional,
)

__all__ = [
    # Cache
    'UserPromptCacheManager',
    'warm_user_prompt_cache',
    'HAS_ORCHESTRATION_CACHE',

    # Parallel Execution
    'ParallelMCPExecutor',
    'ParallelWorkflowOrchestrator',
    'MCPToolExecution',
    'create_parallel_mcp_executor',
    'create_workflow_orchestrator',
    'run_parallel_analysis',

    # HTTP Client
    'UserPromptHTTPClientManager',

    # Monitoring
    'UserPromptMonitor',
    'log_prompt_event',

    # Async Operations
    'AsyncFileOperations',
    'AsyncProcessManager',

    # Process Management
    'ProcessManager',
    'find_and_kill_zombie_processes',
    'create_process_manager',

    # Analysis Functions
    'analyze_prompt_complexity',
    'determine_zen_workflow',
    'detect_claude_flow_swarm_needs',
    'detect_serena_code_analysis_needs',
    'detect_smart_mcp_triggers',
    'detect_library_documentation_needs',
    'detect_github_repository_context_prompt',
    'detect_github_claude_flow_needs',
    'cached_prompt_hash',
    'expensive_prompt_analysis',

    # MCP Tools
    'get_available_mcp_tools',
    'run_claude_flow_mcp_command',
    'run_serena_mcp_command',
    'generate_serena_project_context',
    'generate_code2prompt_context',
    'run_context7_documentation_lookup',
    'run_mcp_tool_command',

    # Workflows
    'create_zen_consultation_task',
    'run_zen_consultation_functional',
    'run_claude_flow_swarm_orchestration',
    'run_github_claude_flow_orchestration',
    'run_github_mcp_integration',
    'run_enhanced_mcp_orchestration',
    'extract_consultation_data',
    'merge_analysis_with_consultation',
    'judge_and_spawn_agents_functional',
    'generate_coordination_output'
]
