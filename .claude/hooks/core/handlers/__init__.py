"""
Hook handlers for Claude Code
"""

from .hook_handlers import (
    handle_notification,
    handle_post_bash,
    handle_post_edit,
    handle_post_mcp,
    handle_post_task,
    handle_pre_bash,
    handle_pre_edit,
    handle_pre_mcp,
    handle_pre_task,
    handle_precompact,
    handle_prompt,
    handle_stop,
    handle_subagent_stop,
)

__all__ = [
    'handle_pre_bash', 'handle_post_bash',
    'handle_pre_edit', 'handle_post_edit',
    'handle_pre_task', 'handle_post_task',
    'handle_pre_mcp', 'handle_post_mcp',
    'handle_notification', 'handle_stop',
    'handle_prompt', 'handle_subagent_stop',
    'handle_precompact'
]
