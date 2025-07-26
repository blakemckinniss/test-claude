#!/usr/bin/env python3
"""
Hook decision support for advanced permission control
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Decision patterns for different scenarios
DECISION_PATTERNS = {
    'auto_approve': {
        'safe_reads': {
            'tools': ['Read', 'mcp__filesystem__read_file', 'mcp__serena__read_file'],
            'condition': lambda ti: ti.get('file_path', '').endswith(('.md', '.txt', '.json', '.yml', '.yaml')),
            'reason': "Safe file type - documentation/config"
        },
        'memory_retrieve': {
            'tools': ['mcp__claude-flow__memory_usage'],
            'condition': lambda ti: ti.get('action') == 'retrieve',
            'reason': "Memory retrieval is safe"
        },
        'status_checks': {
            'tools': ['mcp__claude-flow__swarm_status', 'mcp__claude-flow__agent_list'],
            'condition': lambda ti: True,
            'reason': "Status monitoring is always safe"
        }
    },
    'require_confirmation': {
        'file_writes': {
            'tools': ['Write', 'mcp__filesystem__write_file'],
            'condition': lambda ti: True,
            'reason': "File creation/modification requires review"
        },
        'system_commands': {
            'tools': ['Bash'],
            'condition': lambda ti: any(cmd in ti.get('command', '') for cmd in ['rm', 'delete', 'install']),
            'reason': "System modification command"
        },
        'github_changes': {
            'tools': ['mcp__github__create_pr', 'mcp__github__merge_pr'],
            'condition': lambda ti: True,
            'reason': "GitHub repository changes"
        }
    },
    'suggest_alternatives': {
        'grep_usage': {
            'tools': ['Bash'],
            'condition': lambda ti: 'grep' in ti.get('command', '') and 'rg' not in ti.get('command', ''),
            'suggestion': "Consider using 'rg' (ripgrep) instead of grep for better performance",
            'alternative_tool': 'Grep'
        },
        'find_usage': {
            'tools': ['Bash'],
            'condition': lambda ti: 'find' in ti.get('command', '') and '-name' in ti.get('command', ''),
            'suggestion': "Consider using Glob tool or 'rg --files' for better performance",
            'alternative_tool': 'Glob'
        }
    }
}


def generate_hook_decision(
    hook_type: str,
    tool_name: str,
    tool_input: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate advanced hook decision with context"""
    
    # Default response
    response = {
        'continue': True,
        'suppressOutput': False
    }
    
    # Only process PreToolUse hooks
    if hook_type != 'PreToolUse':
        return response
    
    # Check auto-approval patterns
    for category, patterns in DECISION_PATTERNS['auto_approve'].items():
        if tool_name in patterns['tools'] and patterns['condition'](tool_input):
            response['hookSpecificOutput'] = {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'allow',
                'permissionDecisionReason': patterns['reason']
            }
            response['suppressOutput'] = True
            
            # Add contextual suggestions
            response['additionalContext'] = generate_tool_suggestions(tool_name, tool_input)
            return response
    
    # Check if confirmation required
    for category, patterns in DECISION_PATTERNS['require_confirmation'].items():
        if tool_name in patterns['tools'] and patterns['condition'](tool_input):
            response['hookSpecificOutput'] = {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'ask',
                'permissionDecisionReason': patterns['reason']
            }
            
            # Add helpful context
            response['additionalContext'] = generate_safety_context(tool_name, tool_input)
            return response
    
    # Check for suggested alternatives
    for category, patterns in DECISION_PATTERNS['suggest_alternatives'].items():
        if tool_name in patterns['tools'] and patterns['condition'](tool_input):
            response['hookSpecificOutput'] = {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': patterns['suggestion']
            }
            
            # Provide alternative
            response['alternativeSuggestion'] = f"Use {patterns['alternative_tool']} tool instead"
            return response
    
    return response


def generate_tool_suggestions(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Generate contextual suggestions for the approved tool"""
    suggestions = []
    
    tool_workflows = {
        'Read': [
            "After reading, consider:",
            "- `mcp__serena__find_symbol` to explore code structure",
            "- `Grep` to search for patterns",
            "- `Edit` to make improvements"
        ],
        'mcp__serena__get_symbols_overview': [
            "After overview, consider:",
            "- `mcp__serena__find_symbol` for specific symbols",
            "- `mcp__serena__search_pattern` for implementations",
            "- `TodoWrite` to plan exploration"
        ],
        'mcp__claude-flow__memory_usage': [
            "Memory operation complete. Next:",
            "- `mcp__claude-flow__swarm_status` to check coordination",
            "- `Task` to spawn agents based on memory",
            "- `mcp__claude-flow__agent_list` to see active agents"
        ]
    }
    
    if tool_name in tool_workflows:
        suggestions.extend(tool_workflows[tool_name])
    
    return '\n'.join(suggestions) if suggestions else ""


def generate_safety_context(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Generate safety context for tools requiring confirmation"""
    context_parts = []
    
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        context_parts.append(f"Command: `{command}`")
        
        # Analyze command for risks
        if 'rm' in command:
            context_parts.append("⚠️ Deletion command - verify targets")
        if 'install' in command:
            context_parts.append("📦 Package installation - check dependencies")
        if '>' in command or '>>' in command:
            context_parts.append("📝 Output redirection - check target file")
    
    elif tool_name in ['Write', 'mcp__filesystem__write_file']:
        file_path = tool_input.get('file_path', '')
        context_parts.append(f"Target: `{file_path}`")
        
        # Check for sensitive files
        if any(sensitive in file_path for sensitive in ['.env', '.git', 'secret', 'key']):
            context_parts.append("⚠️ Potentially sensitive file")
    
    elif tool_name.startswith('mcp__github__'):
        context_parts.append("🔗 GitHub operation - will affect repository")
    
    return '\n'.join(context_parts) if context_parts else ""


def format_decision_output(decision: Dict[str, Any]) -> str:
    """Format decision as JSON for stdout"""
    # Remove internal fields
    output = {
        k: v for k, v in decision.items()
        if k not in ['additionalContext', 'alternativeSuggestion']
    }
    
    # Add any context as a separate field
    if 'additionalContext' in decision:
        output['context'] = decision['additionalContext']
    
    return json.dumps(output, indent=2)