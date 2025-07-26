#!/usr/bin/env python3
"""
Enhanced Claude Hook Handlers with Full Claude Visibility
These handlers use exit code 2 + stderr to provide actionable feedback that Claude can see and act upon.

KEY PRINCIPLE: If Claude can't see the feedback, the hook is worthless for automated coding!
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple

def claude_feedback(message: str, block: bool = True) -> None:
    """
    Send feedback directly to Claude that it can see and act upon.
    
    Args:
        message: Actionable feedback for Claude
        block: If True, uses exit code 2 (Claude sees stderr). If False, uses exit code 0.
    """
    if block:
        print(message, file=sys.stderr)
        sys.exit(2)  # Claude sees this feedback and can act on it!
    else:
        print(message)  # Goes to user only
        sys.exit(0)

def claude_json_feedback(decision: str, reason: str) -> None:
    """
    Send structured JSON feedback to Claude with decision control.
    
    Args:
        decision: "block" to provide feedback Claude can act on, or None
        reason: Explanation that Claude will see
    """
    if decision == "block":
        output = {
            "decision": "block",
            "reason": reason
        }
        print(json.dumps(output))
        sys.exit(0)
    else:
        print(reason)
        sys.exit(0)

# Enhanced Hook Handlers with Claude Visibility

def handle_pre_bash_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced PreToolUse:Bash hook with actionable Claude feedback.
    Validates commands and provides suggestions Claude can act upon.
    """
    command = json_input.get('tool_input', {}).get('command', '')
    
    # Critical: Check for Claude Flow coordination
    if 'claude-flow' in command.lower():
        # This is good - Claude is using coordination
        sys.exit(0)
    
    # Check for sequential anti-patterns
    if any(bad in command for bad in ['sleep', 'wait', 'pause']):
        claude_feedback(
            "❌ SEQUENTIAL EXECUTION DETECTED!\n\n"
            "Instead of waiting, use PARALLEL execution:\n"
            "• Batch multiple operations in ONE message\n"
            "• Use mcp__claude-flow__swarm_init for coordination\n"
            "• Spawn multiple Task agents simultaneously\n\n"
            "Example: Instead of 'sleep 5 && command', use BatchTool with multiple operations.\n\n"
            "Would you like me to restructure this for parallel execution?"
        )
    
    # Suggest coordination for complex operations
    if any(indicator in command for indicator in ['npm install', 'git clone', 'pip install']):
        claude_feedback(
            "💡 COMPLEX OPERATION DETECTED\n\n"
            "Consider using swarm coordination for this operation:\n"
            "1. Initialize: mcp__claude-flow__swarm_init\n"
            "2. Spawn agents: Task tools with coordination instructions\n"
            "3. Track progress: TodoWrite with all steps\n\n"
            "This will enable parallel execution and better error handling.\n\n"
            "Proceed with coordination setup?"
        )
    
    # Warning for potentially destructive commands
    dangerous_patterns = ['rm -rf', 'rm -r', 'sudo rm', '>>', 'curl | bash']
    if any(pattern in command for pattern in dangerous_patterns):
        claude_feedback(
            "🚨 POTENTIALLY DANGEROUS COMMAND\n\n"
            f"Command: {command}\n\n"
            "This command could be destructive. Please:\n"
            "1. Verify the command is correct\n"
            "2. Consider using safer alternatives\n"
            "3. Ensure you have backups if needed\n\n"
            "Continue with this command?"
        )
    
    # All good - proceed
    sys.exit(0)

def handle_post_bash_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced PostToolUse:Bash hook with actionable follow-up suggestions.
    """
    command = json_input.get('tool_input', {}).get('command', '')
    response = json_input.get('tool_response', {})
    success = response.get('success', False)
    
    if not success:
        claude_feedback(
            f"❌ COMMAND FAILED: {command}\n\n"
            "Troubleshooting suggestions:\n"
            "1. Check if dependencies are installed\n"
            "2. Verify file paths exist\n"
            "3. Check permissions\n"
            "4. Use mcp__zen__debug for systematic debugging\n\n"
            "Would you like me to analyze this failure and suggest fixes?"
        )
    
    # Suggest next steps for successful installations
    if success and any(install in command for install in ['npm install', 'pip install']):
        claude_feedback(
            "✅ INSTALLATION COMPLETE\n\n"
            "Recommended next steps:\n"
            "1. Run tests: npm test or pytest\n"
            "2. Check linting: npm run lint or flake8\n"
            "3. Update documentation if needed\n"
            "4. Consider adding to TodoWrite for tracking\n\n"
            "Would you like me to run these verification steps?"
        )
    
    sys.exit(0)

def handle_pre_task_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced PreToolUse:Task hook ensures proper agent coordination.
    """
    prompt = json_input.get('tool_input', {}).get('prompt', '')
    
    # Critical: Check if agent has coordination instructions
    required_hooks = [
        'npx claude-flow@alpha hooks pre-task',
        'npx claude-flow@alpha hooks post-edit',
        'npx claude-flow@alpha hooks notification',
        'npx claude-flow@alpha hooks post-task'
    ]
    
    missing_hooks = [hook for hook in required_hooks if hook not in prompt]
    
    if missing_hooks:
        missing_list = '\n'.join(f"• {hook}" for hook in missing_hooks)
        claude_feedback(
            "🚨 AGENT MISSING COORDINATION INSTRUCTIONS!\n\n"
            f"This Task agent is missing required coordination hooks:\n{missing_list}\n\n"
            "MANDATORY: Every Task agent MUST include:\n"
            "1. START: npx claude-flow@alpha hooks pre-task --description '[task]'\n"
            "2. DURING: npx claude-flow@alpha hooks post-edit --file '[file]'\n"
            "3. SHARE: npx claude-flow@alpha hooks notification --message '[decision]'\n"
            "4. END: npx claude-flow@alpha hooks post-task --task-id '[task]'\n\n"
            "Please add these coordination instructions to the Task prompt!"
        )
    
    # Check for parallel execution violation
    if 'wait for' in prompt.lower() or 'after' in prompt.lower():
        claude_feedback(
            "⚠️ SEQUENTIAL EXECUTION DETECTED IN TASK\n\n"
            "Task agents should work in PARALLEL, not sequentially.\n\n"
            "Instead of: 'Wait for X then do Y'\n"
            "Use: 'Do Y with coordination via hooks'\n\n"
            "Agents coordinate through Claude Flow memory, not by waiting.\n\n"
            "Restructure this task for parallel execution?"
        )
    
    sys.exit(0)

def handle_post_edit_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced PostToolUse:Edit hook with intelligent suggestions.
    """
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    
    if not file_path:
        sys.exit(0)
    
    # Check file type and suggest next steps
    if file_path.endswith(('.js', '.ts', '.tsx')):
        claude_feedback(
            f"📝 JAVASCRIPT FILE MODIFIED: {file_path}\n\n"
            "Recommended actions:\n"
            "1. Run linting: npm run lint\n"
            "2. Run tests: npm test\n"
            "3. Check TypeScript: npm run type-check\n"
            "4. Consider adding tests if this is new functionality\n\n"
            "Use mcp__zen__testgen for comprehensive test generation.\n\n"
            "Run these validations now?"
        )
    
    elif file_path.endswith(('.py',)):
        claude_feedback(
            f"🐍 PYTHON FILE MODIFIED: {file_path}\n\n"
            "Recommended actions:\n"
            "1. Run linting: flake8 or black\n"
            "2. Run tests: pytest\n"
            "3. Check typing: mypy\n"
            "4. Update requirements if dependencies changed\n\n"
            "Use mcp__zen__testgen for test coverage analysis.\n\n"
            "Run these validations now?"
        )
    
    elif file_path.endswith(('.json', '.yaml', '.yml')):
        claude_feedback(
            f"⚙️ CONFIG FILE MODIFIED: {file_path}\n\n"
            "Config changes detected. Consider:\n"
            "1. Validate syntax\n"
            "2. Restart relevant services\n"
            "3. Update documentation\n"
            "4. Test configuration changes\n\n"
            "Would you like me to validate this configuration?"
        )
    
    sys.exit(0)

def handle_stop_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced Stop hook with session analysis and next steps.
    """
    # Analyze what was accomplished this session
    session_data = analyze_session_activity()
    
    if session_data['incomplete_todos'] > 0:
        claude_feedback(
            f"📋 SESSION INCOMPLETE\n\n"
            f"You have {session_data['incomplete_todos']} incomplete todos.\n"
            f"Files modified: {session_data['files_modified']}\n"
            f"Tests run: {session_data['tests_run']}\n\n"
            "Recommended actions:\n"
            "1. Continue with pending todos\n"
            "2. Run tests if files were modified\n"
            "3. Commit changes if work is complete\n"
            "4. Use mcp__claude-flow__memory_usage to save progress\n\n"
            "Continue working on incomplete tasks?"
        )
    
    if session_data['files_modified'] > 0 and not session_data['tests_run']:
        claude_feedback(
            "🧪 FILES MODIFIED BUT NO TESTS RUN\n\n"
            f"{session_data['files_modified']} files were modified but no tests were executed.\n\n"
            "Critical for automated coding:\n"
            "1. Run relevant tests: npm test, pytest, etc.\n"
            "2. Check linting and formatting\n"
            "3. Validate changes work as expected\n\n"
            "Run tests before finishing?"
        )
    
    sys.exit(0)

def analyze_session_activity() -> Dict[str, Any]:
    """
    Analyze what happened during this session.
    In a real implementation, this would check logs, git status, etc.
    """
    # Placeholder implementation
    return {
        'incomplete_todos': 0,
        'files_modified': 0,
        'tests_run': False,
        'commits_made': 0
    }

def handle_notification_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced Notification hook with context-aware responses.
    """
    message = json_input.get('message', '')
    
    if 'waiting for input' in message.lower():
        claude_feedback(
            "⏳ CLAUDE IS WAITING - SUGGESTED ACTIONS\n\n"
            "Consider these next steps:\n"
            "1. Continue with current task implementation\n"
            "2. Use mcp__zen__chat to explore approaches\n"
            "3. Review and test recent changes\n"
            "4. Initialize swarm coordination for complex tasks\n"
            "5. Ask specific questions about the implementation\n\n"
            "Use mcp__claude-flow__swarm_status to check coordination state.\n\n"
            "What would you like to focus on next?"
        )
    
    if 'permission' in message.lower():
        # Don't block permission requests, just log
        sys.exit(0)
    
    sys.exit(0)

def handle_subagent_stop_enhanced(json_input: Dict[str, Any]) -> None:
    """
    Enhanced SubagentStop hook for agent coordination.
    """
    # Check if other agents are still working
    # In real implementation, would check Claude Flow swarm status
    
    claude_feedback(
        "🤖 SUBAGENT COMPLETED\n\n"
        "Agent coordination checkpoint:\n"
        "1. Storing results in Claude Flow memory\n"
        "2. Notifying other agents of completion\n"
        "3. Checking for dependent tasks\n"
        "4. Updating coordination state\n\n"
        "Use mcp__claude-flow__swarm_status to check overall progress.\n\n"
        "Continue with coordinated execution?"
    )

# Main enhanced hook router
def main_enhanced():
    """
    Enhanced main function that routes to appropriate handlers with Claude visibility.
    """
    if len(sys.argv) < 2:
        print("Usage: enhanced_claude_visibility.py <hook_type>", file=sys.stderr)
        sys.exit(1)
    
    hook_type = sys.argv[1]
    
    try:
        # Read JSON input from stdin
        raw_input = sys.stdin.read()
        json_input = json.loads(raw_input) if raw_input.strip() else {}
    except json.JSONDecodeError as e:
        claude_feedback(f"❌ Invalid JSON input: {e}")
    
    # Route to enhanced handlers
    handlers = {
        'pre-bash': handle_pre_bash_enhanced,
        'post-bash': handle_post_bash_enhanced,
        'pre-task': handle_pre_task_enhanced,
        'post-edit': handle_post_edit_enhanced,
        'stop': handle_stop_enhanced,
        'notification': handle_notification_enhanced,
        'subagent-stop': handle_subagent_stop_enhanced,
    }
    
    handler = handlers.get(hook_type)
    if handler:
        handler(json_input)
    else:
        claude_feedback(f"❌ Unknown hook type: {hook_type}")

if __name__ == '__main__':
    main_enhanced()