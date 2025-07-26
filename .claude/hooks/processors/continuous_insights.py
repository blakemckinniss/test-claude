#!/usr/bin/env python3
"""
Continuous insights system for providing constant MCP tool guidance
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# State tracking for continuous insights
class InsightState:
    """Track conversation state for contextual suggestions"""
    def __init__(self):
        self.session_id: str = ""
        self.recent_tools: List[str] = []
        self.pending_tasks: Set[str] = set()
        self.active_agents: Set[str] = set()
        self.file_operations: Dict[str, int] = {}
        self.error_count: int = 0
        self.last_suggestion_time: float = 0
        self.conversation_context: Dict[str, Any] = {}
    
    def update_tool_usage(self, tool_name: str):
        """Track tool usage patterns"""
        self.recent_tools.append(tool_name)
        if len(self.recent_tools) > 10:
            self.recent_tools.pop(0)
    
    def should_suggest(self, min_interval: float = 30.0) -> bool:
        """Determine if we should provide suggestions"""
        return time.time() - self.last_suggestion_time > min_interval

# Global state instance
insight_state = InsightState()

# Contextual MCP tool suggestions
CONTEXTUAL_SUGGESTIONS = {
    'startup': {
        'tools': ['mcp__serena__get_symbols_overview', 'mcp__serena__list_memories'],
        'message': "Starting a new session? Use these tools to understand the project"
    },
    'error_detected': {
        'tools': ['mcp__zen__debug', 'mcp__zen__thinkdeep', 'Grep'],
        'message': "Error detected - these tools can help investigate"
    },
    'multiple_files': {
        'tools': ['BatchTool', 'mcp__claude-flow__swarm_init', 'TodoWrite'],
        'message': "Working with multiple files? Use parallel execution"
    },
    'testing_needed': {
        'tools': ['mcp__zen__testgen', 'Bash', 'mcp__serena__find_symbol'],
        'message': "Don't forget to test your changes"
    },
    'documentation': {
        'tools': ['mcp__context7__get-library-docs', 'WebSearch', 'mcp__zen__docgen'],
        'message': "Need documentation? These tools can help"
    },
    'performance': {
        'tools': ['mcp__claude-flow__benchmark_run', 'mcp__zen__analyze'],
        'message': "Performance concerns? Profile and analyze"
    }
}

# Tool combination patterns
TOOL_COMBINATIONS = {
    'code_exploration': [
        ('mcp__serena__get_symbols_overview', 'mcp__serena__find_symbol', 'mcp__serena__read_file'),
        "For code exploration: Overview → Find symbols → Read details"
    ],
    'debugging_workflow': [
        ('mcp__zen__debug', 'Grep', 'mcp__serena__find_referencing_symbols'),
        "Debug workflow: Analyze issue → Search patterns → Find references"
    ],
    'testing_workflow': [
        ('mcp__zen__testgen', 'Write', 'Bash'),
        "Testing workflow: Generate tests → Write files → Run tests"
    ],
    'github_workflow': [
        ('mcp__github__list_issues', 'mcp__github__create_branch', 'mcp__github__create_pr'),
        "GitHub workflow: Check issues → Create branch → Submit PR"
    ],
    'refactoring_workflow': [
        ('mcp__zen__analyze', 'mcp__zen__refactor', 'mcp__zen__testgen'),
        "Refactoring workflow: Analyze → Refactor → Test"
    ]
}

def analyze_conversation_state(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current conversation state for insights"""
    analysis = {
        'needs_swarm': False,
        'needs_testing': False,
        'needs_documentation': False,
        'complexity_level': 'low',
        'suggested_workflows': []
    }
    
    # Check recent tool usage patterns
    recent_tools = insight_state.recent_tools[-5:]
    
    # Detect patterns
    if len(set(recent_tools)) > 3:
        analysis['complexity_level'] = 'high'
        analysis['needs_swarm'] = True
    
    if any('edit' in t.lower() or 'write' in t.lower() for t in recent_tools):
        analysis['needs_testing'] = True
    
    if insight_state.error_count > 0:
        analysis['suggested_workflows'].append('debugging_workflow')
    
    # File operation patterns
    if len(insight_state.file_operations) > 5:
        analysis['needs_swarm'] = True
        analysis['suggested_workflows'].append('code_exploration')
    
    return analysis

def generate_contextual_insights(
    hook_type: str,
    input_data: Dict[str, Any],
    analysis: Dict[str, Any]
) -> str:
    """Generate contextual insights based on current state"""
    insights = []
    
    # Header
    insights.append("### 🎯 Contextual MCP Tool Insights\n")
    
    # Workflow suggestions
    if analysis['suggested_workflows']:
        insights.append("**Recommended Workflows:**")
        for workflow_name in analysis['suggested_workflows']:
            if workflow_name in TOOL_COMBINATIONS:
                tools, description = TOOL_COMBINATIONS[workflow_name]
                insights.append(f"- {description}")
                insights.append(f"  Tools: `{' → '.join(tools)}`")
        insights.append("")
    
    # Complexity-based suggestions
    if analysis['needs_swarm']:
        insights.append("**🐝 High Complexity Detected**")
        insights.append("Consider initializing a swarm for parallel execution:")
        insights.append("```")
        insights.append("mcp__claude-flow__swarm_init")
        insights.append("mcp__claude-flow__agent_spawn (multiple agents)")
        insights.append("Task (with coordination hooks)")
        insights.append("```")
        insights.append("")
    
    # Testing reminders
    if analysis['needs_testing']:
        insights.append("**🧪 Testing Reminder**")
        insights.append("Recent edits detected. Consider:")
        insights.append("- `mcp__zen__testgen` - Generate comprehensive tests")
        insights.append("- `Bash` - Run existing test suites")
        insights.append("- `mcp__zen__codereview` - Review changes")
        insights.append("")
    
    # Tool combination suggestions
    if len(insight_state.recent_tools) >= 2:
        last_tool = insight_state.recent_tools[-1]
        suggestions = get_next_tool_suggestions(last_tool)
        if suggestions:
            insights.append(f"**After `{last_tool}`, consider:**")
            for tool, reason in suggestions:
                insights.append(f"- `{tool}` - {reason}")
            insights.append("")
    
    # Memory and state management
    if insight_state.active_agents:
        insights.append("**📊 Active Coordination**")
        insights.append(f"Agents active: {len(insight_state.active_agents)}")
        insights.append("Use these tools to coordinate:")
        insights.append("- `mcp__claude-flow__memory_usage` - Share state")
        insights.append("- `mcp__claude-flow__swarm_status` - Check progress")
        insights.append("- `npx claude-flow@alpha hooks notification` - Send updates")
        insights.append("")
    
    return '\n'.join(insights)

def get_next_tool_suggestions(last_tool: str) -> List[tuple[str, str]]:
    """Suggest next tools based on the last tool used"""
    suggestions = []
    
    tool_sequences = {
        'mcp__serena__get_symbols_overview': [
            ('mcp__serena__find_symbol', 'Locate specific symbols'),
            ('mcp__serena__search_pattern', 'Search for patterns')
        ],
        'mcp__serena__find_symbol': [
            ('mcp__serena__read_file', 'Read full implementation'),
            ('mcp__serena__find_referencing_symbols', 'Find usages')
        ],
        'mcp__github__list_issues': [
            ('mcp__github__create_branch', 'Start working on issue'),
            ('TodoWrite', 'Plan implementation steps')
        ],
        'mcp__zen__debug': [
            ('Grep', 'Search for error patterns'),
            ('mcp__serena__find_symbol', 'Locate problematic code')
        ],
        'Write': [
            ('mcp__zen__testgen', 'Generate tests for new code'),
            ('Bash', 'Run linters and formatters')
        ],
        'mcp__claude-flow__swarm_init': [
            ('mcp__claude-flow__agent_spawn', 'Spawn specialized agents'),
            ('Task', 'Assign work to agents')
        ]
    }
    
    return tool_sequences.get(last_tool, [])

def generate_periodic_reminder(session_time: float) -> Optional[str]:
    """Generate periodic reminders based on session duration"""
    reminders = []
    
    # Early session reminders (< 5 minutes)
    if session_time < 300:
        reminders.append("💡 **Quick Tips:**")
        reminders.append("- Use `mcp__serena__list_memories` to check project knowledge")
        reminders.append("- `BatchTool` enables parallel operations")
        reminders.append("- Include coordination hooks in Task agents")
    
    # Mid-session reminders (5-15 minutes)
    elif session_time < 900:
        reminders.append("🔄 **Workflow Optimization:**")
        reminders.append("- Consider `mcp__claude-flow__swarm_init` for complex tasks")
        reminders.append("- Use `TodoWrite` to track progress")
        reminders.append("- `mcp__zen__analyze` for architectural insights")
    
    # Long session reminders (> 15 minutes)
    else:
        reminders.append("📊 **Session Management:**")
        reminders.append("- Save progress with `mcp__claude-flow__memory_usage`")
        reminders.append("- Review changes with `git diff` and `mcp__zen__codereview`")
        reminders.append("- Consider creating a PR with `mcp__github__create_pr`")
    
    return '\n'.join(reminders) if reminders else None

def format_continuous_insights(
    hook_type: str,
    input_data: Dict[str, Any],
    force: bool = False
) -> Optional[str]:
    """Generate and format continuous insights"""
    # Check if we should provide insights
    if not force and not insight_state.should_suggest():
        return None
    
    # Update state
    if hook_type == 'PreToolUse':
        tool_name = input_data.get('tool_name', '')
        insight_state.update_tool_usage(tool_name)
        
        # Track file operations
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = input_data.get('tool_input', {}).get('file_path', '')
            insight_state.file_operations[file_path] = insight_state.file_operations.get(file_path, 0) + 1
    
    # Analyze current state
    analysis = analyze_conversation_state(input_data)
    
    # Generate insights
    insights = generate_contextual_insights(hook_type, input_data, analysis)
    
    # Add periodic reminders
    session_time = time.time() - float(input_data.get('session_start_time', time.time()))
    reminder = generate_periodic_reminder(session_time)
    if reminder:
        insights += f"\n\n{reminder}"
    
    # Update last suggestion time
    insight_state.last_suggestion_time = time.time()
    
    return insights

def provide_decision_support(
    hook_type: str,
    input_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Provide decision support for permission requests"""
    if hook_type != 'PreToolUse':
        return None
    
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})
    
    # Auto-approve patterns
    auto_approve_patterns = {
        'Read': lambda ti: ti.get('file_path', '').endswith(('.md', '.txt', '.json')),
        'mcp__serena__list_memories': lambda ti: True,
        'mcp__claude-flow__swarm_status': lambda ti: True,
        'mcp__claude-flow__memory_usage': lambda ti: ti.get('action') == 'retrieve'
    }
    
    # Check for auto-approval
    if tool_name in auto_approve_patterns:
        if auto_approve_patterns[tool_name](tool_input):
            return {
                'decision': 'approve',
                'reason': f"Auto-approved: {tool_name} for safe operation",
                'suggestions': get_next_tool_suggestions(tool_name)
            }
    
    # Provide context for manual decisions
    context_messages = {
        'Bash': "Review command for safety before approving",
        'Write': "New file creation - ensure path is correct",
        'mcp__github__create_pr': "PR will be visible publicly",
        'mcp__claude-flow__swarm_init': "Swarm will spawn multiple agents"
    }
    
    if tool_name in context_messages:
        return {
            'context': context_messages[tool_name],
            'suggestions': get_next_tool_suggestions(tool_name)
        }
    
    return None