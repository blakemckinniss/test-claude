"""
Claude Flow integration for Claude Code hooks
"""

from .claude_flow_integration import (
    detect_complex_task_and_spawn_swarm,
    detect_github_repository_context,
    initialize_github_swarm,
    integrate_claude_flow_memory,
    recommend_github_swarm_orchestration,
    run_claude_flow_command,
    run_claude_flow_mcp_command,
)

__all__ = [
    'detect_complex_task_and_spawn_swarm',
    'integrate_claude_flow_memory',
    'detect_github_repository_context',
    'recommend_github_swarm_orchestration',
    'initialize_github_swarm',
    'run_claude_flow_command',
    'run_claude_flow_mcp_command'
]
