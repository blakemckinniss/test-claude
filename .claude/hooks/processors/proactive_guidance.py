#!/usr/bin/env python3
"""
Proactive guidance system for suggesting MCP tools and coordination strategies
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

# Get logger
logger = logging.getLogger(__name__)

# MCP Tool Knowledge Base
MCP_TOOL_PATTERNS = {
    # Claude Flow patterns
    'swarm_coordination': {
        'patterns': [
            r'\b(complex|multiple|parallel|coordinate|orchestrate)\b',
            r'\b(build|create|develop|implement).*\b(system|api|app|service)\b',
            r'\b(full[- ]stack|microservice|distributed)\b',
            r'\btask[s]?\s+(that|requiring|with)\s+\w+\s+(component|part|step)s?\b'
        ],
        'tools': ['mcp__claude-flow__swarm_init', 'mcp__claude-flow__agent_spawn', 'mcp__claude-flow__task_orchestrate'],
        'suggestion': "Consider using Claude Flow swarm coordination for this complex task"
    },
    
    # Zen consultation patterns
    'zen_analysis': {
        'patterns': [
            r'\b(analyze|investigate|debug|troubleshoot|understand)\b',
            r'\b(why|how|what).*\b(wrong|issue|problem|bug|error)\b',
            r'\b(research|explore|study|examine)\b',
            r'\b(optimize|improve|refactor|enhance)\b'
        ],
        'tools': ['mcp__zen__analyze', 'mcp__zen__debug', 'mcp__zen__thinkdeep'],
        'suggestion': "Zen tools can provide deep analysis and strategic guidance"
    },
    
    # GitHub patterns
    'github_operations': {
        'patterns': [
            r'\b(pr|pull request|issue|notification|repository|github)\b',
            r'\b(merge|commit|push|branch|fork)\b',
            r'\b(review|approve|comment)\b',
            r'\bgit\s+(status|diff|log|add|commit)\b'
        ],
        'tools': ['mcp__github__list_issues', 'mcp__github__create_pr', 'mcp__github__list_notifications'],
        'suggestion': "GitHub MCP tools available for repository operations"
    },
    
    # Web search patterns
    'web_search': {
        'patterns': [
            r'\b(search|find|look up|research).*\b(online|web|internet)\b',
            r'\b(latest|current|recent|up[- ]to[- ]date)\b',
            r'\b(documentation|docs|reference|api)\s+for\b',
            r'\bwhat\s+is\s+(the\s+)?(latest|current|new)\b'
        ],
        'tools': ['mcp__tavily-remote__tavily_search', 'mcp__tavily-remote__tavily_extract'],
        'suggestion': "Web search tools can find current information"
    },
    
    # Code analysis patterns
    'code_analysis': {
        'patterns': [
            r'\b(find|search|locate)\s+(function|class|method|symbol)\b',
            r'\b(where|which)\s+(file|code|implementation)\b',
            r'\b(understand|analyze|review)\s+(code|codebase|implementation)\b',
            r'\bcode\s+(structure|organization|architecture)\b'
        ],
        'tools': ['mcp__serena__find_symbol', 'mcp__serena__search_pattern', 'mcp__serena__get_symbols_overview'],
        'suggestion': "Serena MCP tools excel at code analysis and navigation"
    },
    
    # Documentation lookup patterns
    'documentation': {
        'patterns': [
            r'\b(how|what|docs?|documentation|reference)\s+(to|for|about)?\s*\w+\.(js|py|ts|go)\b',
            r'\b(react|vue|angular|django|flask|express|next\.?js)\b',
            r'\blibrary\s+(docs?|documentation|reference)\b',
            r'\bapi\s+(reference|documentation|docs?)\b'
        ],
        'tools': ['mcp__context7__resolve-library-id', 'mcp__context7__get-library-docs'],
        'suggestion': "Context7 can provide up-to-date library documentation"
    },
    
    # File operations patterns
    'file_operations': {
        'patterns': [
            r'\b(read|write|edit|create|delete)\s+(file|directory|folder)\b',
            r'\b(list|show|display)\s+(files?|directories|folders?)\b',
            r'\b(search|find|grep)\s+(in\s+)?files?\b',
            r'\bfile\s+(content|contents|structure)\b'
        ],
        'tools': ['mcp__filesystem__read_file', 'mcp__filesystem__write_file', 'mcp__filesystem__list_directory'],
        'suggestion': "Filesystem MCP tools for file operations"
    },
    
    # Browser automation patterns
    'browser_automation': {
        'patterns': [
            r'\b(browse|navigate|visit|open)\s+(website|page|url)\b',
            r'\b(click|type|fill|submit)\s+(button|form|input)\b',
            r'\b(screenshot|capture|snapshot)\s+(page|website)\b',
            r'\bweb\s+(scraping|automation|testing)\b'
        ],
        'tools': ['mcp__playwright__browser_navigate', 'mcp__playwright__browser_click', 'mcp__playwright__browser_snapshot'],
        'suggestion': "Playwright MCP tools for browser automation"
    },
    
    # Testing patterns
    'testing': {
        'patterns': [
            r'\b(test|testing|unit test|integration test)\b',
            r'\b(write|create|generate)\s+test[s]?\b',
            r'\b(coverage|test coverage|code coverage)\b',
            r'\btest\s+(suite|cases?|scenarios?)\b'
        ],
        'tools': ['mcp__zen__testgen', 'Task'],
        'suggestion': "Use test generation tools for comprehensive testing"
    },
    
    # Performance patterns
    'performance': {
        'patterns': [
            r'\b(performance|optimize|speed up|slow|fast)\b',
            r'\b(benchmark|profile|measure)\b',
            r'\b(memory|cpu|resource)\s+(usage|consumption)\b',
            r'\bbottleneck[s]?\b'
        ],
        'tools': ['mcp__claude-flow__benchmark_run', 'mcp__zen__analyze'],
        'suggestion': "Performance analysis tools available"
    }
}

# Coordination strategy patterns
COORDINATION_STRATEGIES = {
    'parallel_execution': {
        'indicators': ['multiple', 'parallel', 'concurrent', 'simultaneously', 'at the same time'],
        'strategy': "Use BatchTool to execute multiple operations in parallel"
    },
    'sequential_workflow': {
        'indicators': ['step by step', 'one by one', 'then', 'after', 'before'],
        'strategy': "Create a TodoWrite list with proper dependencies"
    },
    'distributed_work': {
        'indicators': ['different parts', 'components', 'modules', 'services'],
        'strategy': "Spawn specialized agents for different components"
    },
    'iterative_development': {
        'indicators': ['iterate', 'improve', 'refine', 'evolve', 'feedback'],
        'strategy': "Use memory tools to track iterations and improvements"
    }
}


def analyze_context_for_tools(prompt: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze prompt and context to suggest relevant MCP tools
    """
    suggestions = []
    prompt_lower = prompt.lower()
    
    # Check each tool pattern
    for category, config in MCP_TOOL_PATTERNS.items():
        for pattern in config['patterns']:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                suggestions.append({
                    'category': category,
                    'tools': config['tools'],
                    'suggestion': config['suggestion'],
                    'confidence': 0.8
                })
                break
    
    # Analyze context for additional clues
    if context.get('has_error_context'):
        suggestions.append({
            'category': 'debugging',
            'tools': ['mcp__zen__debug', 'mcp__zen__thinkdeep'],
            'suggestion': "Debug tools recommended for error investigation",
            'confidence': 0.9
        })
    
    if context.get('file_count', 0) > 10:
        suggestions.append({
            'category': 'complex_project',
            'tools': ['mcp__claude-flow__swarm_init', 'mcp__serena__get_symbols_overview'],
            'suggestion': "Large project detected - consider swarm coordination",
            'confidence': 0.7
        })
    
    return suggestions


def generate_coordination_advice(prompt: str, tool_suggestions: List[Dict[str, Any]]) -> str:
    """
    Generate specific coordination advice based on the task
    """
    advice_parts = []
    
    # Check coordination strategies
    prompt_lower = prompt.lower()
    for strategy_name, config in COORDINATION_STRATEGIES.items():
        if any(indicator in prompt_lower for indicator in config['indicators']):
            advice_parts.append(f"**{strategy_name.replace('_', ' ').title()}**: {config['strategy']}")
    
    # Add tool-specific advice
    if any(s['category'] == 'swarm_coordination' for s in tool_suggestions):
        advice_parts.append("""
**Swarm Orchestration Pattern**:
1. Initialize swarm with appropriate topology
2. Spawn ALL agents in ONE BatchTool message
3. Each agent MUST use coordination hooks
4. Track progress with memory tools
""")
    
    if any(s['category'] == 'code_analysis' for s in tool_suggestions):
        advice_parts.append("""
**Code Analysis Pattern**:
1. Start with `get_symbols_overview` for structure
2. Use `find_symbol` for specific elements
3. Search patterns for implementation details
4. Document findings in memory
""")
    
    return '\n'.join(advice_parts) if advice_parts else ""


def generate_proactive_suggestions(
    hook_type: str,
    input_data: Dict[str, Any],
    transcript_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate proactive MCP tool suggestions based on current context
    """
    suggestions = {
        'mcp_tools': [],
        'coordination_advice': '',
        'next_steps': [],
        'warnings': []
    }
    
    # Extract relevant information based on hook type
    if hook_type == 'UserPromptSubmit':
        prompt = input_data.get('prompt', '')
        tool_suggestions = analyze_context_for_tools(prompt, transcript_context or {})
        suggestions['mcp_tools'] = tool_suggestions
        suggestions['coordination_advice'] = generate_coordination_advice(prompt, tool_suggestions)
        
        # Add next steps based on suggestions
        if tool_suggestions:
            suggestions['next_steps'] = [
                f"Consider using {s['tools'][0]} for {s['category'].replace('_', ' ')}"
                for s in tool_suggestions[:3]
            ]
    
    elif hook_type == 'PreToolUse':
        tool_name = input_data.get('tool_name', '')
        
        # Suggest coordination for Task tool
        if tool_name == 'Task':
            suggestions['warnings'].append("Ensure Task includes coordination hooks!")
            suggestions['next_steps'].append("Add 'npx claude-flow@alpha hooks' to agent instructions")
        
        # Suggest parallel execution for multiple operations
        elif tool_name in ['Read', 'Write', 'Edit']:
            suggestions['coordination_advice'] = "Consider batching multiple file operations"
            suggestions['next_steps'].append("Use BatchTool for parallel file operations")
    
    elif hook_type == 'PostToolUse':
        tool_name = input_data.get('tool_name', '')
        tool_response = input_data.get('tool_response', {})
        
        # Suggest follow-up tools based on results
        if tool_name == 'Grep' and tool_response.get('matches'):
            suggestions['next_steps'].append("Use mcp__serena__find_symbol to explore found code")
        
        elif tool_name == 'mcp__github__list_issues' and tool_response.get('issues'):
            suggestions['next_steps'].append("Consider mcp__github__create_pr for fixes")
            suggestions['mcp_tools'].append({
                'category': 'github_workflow',
                'tools': ['mcp__github__create_pr', 'mcp__github__add_issue_comment'],
                'suggestion': "GitHub workflow tools for issue resolution"
            })
    
    elif hook_type == 'Notification':
        message = input_data.get('message', '')
        
        # Provide guidance based on notification content
        if 'waiting' in message.lower():
            suggestions['next_steps'].append("Use mcp__claude-flow__swarm_status to check progress")
            suggestions['next_steps'].append("Consider mcp__claude-flow__memory_usage to review state")
    
    return suggestions


def format_suggestions_for_output(suggestions: Dict[str, Any]) -> str:
    """
    Format suggestions into readable output for Claude Code
    """
    output_parts = []
    
    if suggestions.get('mcp_tools'):
        output_parts.append("### 🔧 Relevant MCP Tools\n")
        for tool_suggestion in suggestions['mcp_tools'][:5]:  # Limit to top 5
            output_parts.append(f"**{tool_suggestion['category'].replace('_', ' ').title()}**")
            output_parts.append(f"- {tool_suggestion['suggestion']}")
            output_parts.append(f"- Tools: `{', '.join(tool_suggestion['tools'][:3])}`")
            output_parts.append("")
    
    if suggestions.get('coordination_advice'):
        output_parts.append("### 📋 Coordination Strategy\n")
        output_parts.append(suggestions['coordination_advice'])
        output_parts.append("")
    
    if suggestions.get('next_steps'):
        output_parts.append("### 🚀 Suggested Next Steps\n")
        for i, step in enumerate(suggestions['next_steps'][:5], 1):
            output_parts.append(f"{i}. {step}")
        output_parts.append("")
    
    if suggestions.get('warnings'):
        output_parts.append("### ⚠️ Important Reminders\n")
        for warning in suggestions['warnings']:
            output_parts.append(f"- {warning}")
        output_parts.append("")
    
    return '\n'.join(output_parts)


def should_provide_suggestions(hook_type: str, input_data: Dict[str, Any]) -> bool:
    """
    Determine if suggestions should be provided for this hook call
    """
    # Always provide for UserPromptSubmit
    if hook_type == 'UserPromptSubmit':
        return True
    
    # Provide for Task tool to ensure coordination
    if hook_type == 'PreToolUse' and input_data.get('tool_name') == 'Task':
        return True
    
    # Provide for MCP tool usage
    if hook_type in ['PreToolUse', 'PostToolUse']:
        tool_name = input_data.get('tool_name', '')
        if tool_name.startswith('mcp__'):
            return True
    
    # Provide for notifications about waiting/idle
    if hook_type == 'Notification':
        message = input_data.get('message', '').lower()
        if any(word in message for word in ['waiting', 'idle', 'stuck']):
            return True
    
    return False