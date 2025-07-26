#!/usr/bin/env python3
"""
Enhanced Claude Code Hooks with FULL CLAUDE VISIBILITY
This version uses exit code 2 + stderr to provide actionable feedback that Claude can see and act upon.

KEY PRINCIPLE: If Claude can't see the feedback, the hook is worthless for automated coding!
"""

import argparse
import json
import logging
import sys
import subprocess
import os
from pathlib import Path
from typing import Any, Dict

# Add the hooks directory to the path
hooks_dir = Path(__file__).parent
sys.path.insert(0, str(hooks_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Import processors (fallback gracefully)
try:
    from processors.user_prompt import (
        ProcessManager,
        create_process_manager,
        analyze_prompt_complexity,
        detect_claude_flow_swarm_needs,
        run_zen_consultation_functional,
        run_claude_flow_swarm_orchestration,
        generate_coordination_output,
        judge_and_spawn_agents_functional,
        create_zen_consultation_task,
        get_available_mcp_tools,
        generate_serena_project_context
    )
    from processors.proactive_guidance import (
        generate_proactive_suggestions,
        format_suggestions_for_output,
        should_provide_suggestions
    )
    from processors.continuous_insights import (
        format_continuous_insights,
        provide_decision_support,
        insight_state
    )
    PROCESSORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced processors not available: {e}")
    PROCESSORS_AVAILABLE = False

def handle_pre_bash_enhanced(json_input):
    """Enhanced pre-bash hook with actionable Claude feedback"""
    command = json_input.get('tool_input', {}).get('command', '')
    logger.info(f"Pre-bash hook: validating command: {command[:100]}...")
    
    # Critical: Check for Claude Flow coordination
    if 'claude-flow' in command.lower():
        # This is good - Claude is using coordination
        return 0
    
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
    if any(indicator in command for indicator in ['npm install', 'git clone', 'pip install', 'make', 'cargo build']):
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
    dangerous_patterns = ['rm -rf', 'rm -r', 'sudo rm', '>>', 'curl | bash', 'wget | sh']
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
    
    # Provide proactive suggestions that Claude can see
    if 'grep' in command and 'rg' not in command:
        claude_feedback(
            "💡 TOOL OPTIMIZATION SUGGESTION\n\n"
            "Consider using `rg` (ripgrep) instead of `grep` for better performance:\n"
            "• Faster search across files\n"
            "• Respects .gitignore by default\n"
            "• Better Unicode support\n\n"
            "Or use the `Grep` tool directly for structured output.\n\n"
            "Switch to optimized search tool?"
        )
    
    elif 'find' in command and '-name' in command:
        claude_feedback(
            "💡 SEARCH OPTIMIZATION SUGGESTION\n\n"
            "Consider using these optimized alternatives:\n"
            "• `Glob` tool for file pattern matching\n"
            "• `rg --files -g pattern` for faster file discovery\n"
            "• `mcp__serena__find_file` for project-aware search\n\n"
            "Use optimized search approach?"
        )
    
    # All good - proceed silently
    return 0

def handle_post_bash_enhanced(json_input):
    """Enhanced post-bash hook with actionable follow-up suggestions"""
    command = json_input.get('tool_input', {}).get('command', '')
    result = json_input.get('tool_result', {})
    exit_code = result.get('exitCode', 0)
    stdout = result.get('stdout', '')
    stderr = result.get('stderr', '')
    
    logger.info(f"Post-bash hook: command completed: {command[:100]}...")
    
    # Handle failures with actionable advice
    if exit_code != 0:
        claude_feedback(
            f"❌ COMMAND FAILED: {command}\n\n"
            f"Exit code: {exit_code}\n"
            f"Error: {stderr[:200] if stderr else 'No error details'}\n\n"
            "Troubleshooting suggestions:\n"
            "1. Check if dependencies are installed\n"
            "2. Verify file paths exist\n"
            "3. Check permissions\n"
            "4. Use mcp__zen__debug for systematic debugging\n\n"
            "Would you like me to analyze this failure and suggest fixes?"
        )
    
    # Suggest next steps for successful installations
    if exit_code == 0 and any(install in command for install in ['npm install', 'pip install', 'cargo install']):
        claude_feedback(
            "✅ INSTALLATION COMPLETE\n\n"
            "Recommended next steps:\n"
            "1. Run tests: npm test, pytest, or cargo test\n"
            "2. Check linting: npm run lint, flake8, or cargo clippy\n"
            "3. Update documentation if needed\n"
            "4. Consider adding to TodoWrite for tracking\n\n"
            "Would you like me to run these verification steps?"
        )
    
    # Handle test results
    if 'test' in command.lower() and exit_code == 0:
        if 'passed' in stdout.lower() or 'ok' in stdout.lower():
            claude_feedback(
                "✅ TESTS PASSED!\n\n"
                "Next steps:\n"
                "1. Update TodoWrite to mark testing complete\n"
                "2. Consider mcp__github__create_pr if ready\n"
                "3. Run coverage reports if available\n"
                "4. Deploy or merge changes\n\n"
                "Ready to proceed with next phase?"
            )
        else:
            claude_feedback(
                "🧪 TEST ISSUES DETECTED\n\n"
                "Follow-up actions:\n"
                "1. Review test output for specific failures\n"
                "2. Use mcp__zen__testgen for missing tests\n"
                "3. Fix failures with targeted edits\n"
                "4. Re-run tests to verify fixes\n\n"
                "Would you like me to analyze the test failures?"
            )
    
    # Handle git operations
    if 'git status' in command:
        claude_feedback(
            "📝 GIT STATUS CHECKED\n\n"
            "Common next steps:\n"
            "1. Stage files: git add [files]\n"
            "2. Commit changes: git commit -m 'message'\n"
            "3. Create PR: mcp__github__create_pr\n"
            "4. Use TodoWrite to track commit tasks\n\n"
            "Ready to commit changes?"
        )
    
    # All good - proceed silently
    return 0

def handle_pre_task_enhanced(json_input):
    """Enhanced pre-task hook ensures proper agent coordination"""
    task_desc = json_input.get('tool_input', {}).get('description', '')
    prompt = json_input.get('tool_input', {}).get('prompt', '')
    
    logger.info(f"Pre-task hook: preparing task: {task_desc[:100]}...")
    
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
    
    # All good - proceed
    return 0

def handle_post_edit_enhanced(json_input):
    """Enhanced post-edit hook with intelligent suggestions"""
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    
    if not file_path:
        return 0
    
    logger.info(f"Post-edit hook: file edited: {file_path}")
    
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
    
    elif file_path.endswith(('.md', '.rst', '.txt')):
        claude_feedback(
            f"📚 DOCUMENTATION MODIFIED: {file_path}\n\n"
            "Documentation updated! Consider:\n"
            "1. Check for broken links\n"
            "2. Verify code examples work\n"
            "3. Update table of contents if needed\n"
            "4. Consider mcp__github__create_pr for review\n\n"
            "Ready to publish documentation changes?"
        )
    
    # All good - proceed silently
    return 0

def handle_stop_enhanced(json_input):
    """Enhanced stop hook with session analysis and next steps"""
    logger.info("Stop hook: cleaning up session")
    
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
    
    return 0

def analyze_session_activity() -> Dict[str, Any]:
    """
    Analyze what happened during this session.
    In a real implementation, this would check logs, git status, etc.
    """
    # Placeholder implementation - in reality would check:
    # - Git status for modified files
    # - Log files for test runs
    # - TodoWrite status
    # - Memory for incomplete tasks
    return {
        'incomplete_todos': 0,
        'files_modified': 0,
        'tests_run': False,
        'commits_made': 0
    }

def handle_notification_enhanced(json_input):
    """Enhanced notification hook with context-aware responses"""
    message = json_input.get('message', '')
    logger.info(f"Notification hook: {message[:100]}...")
    
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
        # Don't block permission requests, just provide guidance
        print("""### 🔐 Permission Request Guidance

**Quick Review Checklist**:
- Is the file path correct?
- Is this a safe operation?
- Are there any alternatives?

**Auto-approve candidates**:
- Reading documentation files (.md, .txt)
- Status checking operations
- Memory retrieval (not storage)""")
        return 0
    
    # All other notifications proceed silently
    return 0

def handle_subagent_stop_enhanced(json_input):
    """Enhanced subagent-stop hook for agent coordination"""
    logger.info("Subagent-stop hook: task agent completed")
    
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

def handle_precompact_enhanced(json_input):
    """Enhanced precompact hook with preparation guidance"""
    trigger = json_input.get('trigger', 'unknown')
    logger.info(f"Precompact hook: about to compact (trigger: {trigger})")
    
    claude_feedback(
        f"📦 PRECOMPACT PREPARATION\n\n"
        f"About to compact (trigger: {trigger})\n\n"
        "Before compacting:\n"
        "1. Save important context with mcp__claude-flow__memory_usage\n"
        "2. Update TodoWrite with current progress\n"
        "3. Store any decisions or findings\n"
        "4. Ensure critical information is preserved\n\n"
        "Ready to proceed with compacting?"
    )

# Enhanced hook handlers that use the original handlers but with visibility improvements
def handle_pre_bash(json_input):
    """Wrapper that adds Claude visibility to original handler"""
    # Check for critical issues first (with Claude visibility)
    command = json_input.get('tool_input', {}).get('command', '')
    
    # Check for coordination and dangerous patterns with Claude feedback
    if any(bad in command for bad in ['rm -rf /', 'sudo rm -rf', 'curl | bash']):
        return handle_pre_bash_enhanced(json_input)
    
    if any(indicator in command for indicator in ['npm install', 'git clone', 'pip install']) and 'claude-flow' not in command:
        return handle_pre_bash_enhanced(json_input)
    
    # Otherwise use original handler (silent)
    logger.info(f"Pre-bash hook: validating command: {command[:100]}...")
    
    # Provide proactive suggestions (visible to user)
    if 'grep' in command and 'rg' not in command:
        print("""### 💡 Tool Suggestion

Consider using `rg` (ripgrep) instead of `grep` for better performance:
- Faster search across files
- Respects .gitignore by default
- Better Unicode support

Or use the `Grep` tool directly for structured output.
""")
    
    return 0

def handle_post_bash(json_input):
    """Wrapper that adds Claude visibility to original handler"""
    command = json_input.get('tool_input', {}).get('command', '')
    result = json_input.get('tool_result', {})
    exit_code = result.get('exitCode', 0)
    
    # Check for critical issues first (with Claude visibility)
    if exit_code != 0:
        return handle_post_bash_enhanced(json_input)
    
    if 'test' in command.lower() or 'git status' in command:
        return handle_post_bash_enhanced(json_input)
    
    # Otherwise use original handler (user-visible suggestions)
    logger.info(f"Post-bash hook: command completed: {command[:100]}...")
    
    # Track claude-flow orchestration commands
    if 'claude-flow' in command and 'hooks' in command:
        print("""### ✅ Coordination Hook Executed

Remember to:
- Store decisions with `mcp__claude-flow__memory_usage`
- Check swarm status periodically
- Use TodoWrite to track progress
""")
    
    return 0

def handle_pre_edit(json_input):
    """Enhanced pre-edit with coordination checks"""
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    logger.info(f"Pre-edit hook: preparing to edit {file_path}")
    return 0

def handle_post_edit(json_input):
    """Wrapper that adds Claude visibility to original handler"""
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    
    # Check for critical file types that need immediate action
    if file_path.endswith(('.py', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml')):
        return handle_post_edit_enhanced(json_input)
    
    # Otherwise use original handler
    logger.info(f"Post-edit hook: file edited: {file_path}")
    
    # Provide context-aware suggestions based on file type
    file_ext = file_path.split('.')[-1] if '.' in file_path else ''
    
    suggestions_map = {
        'py': "Consider running `python -m pytest` or `mcp__zen__testgen`",
        'js': "Consider running `npm test` or checking with ESLint",
        'ts': "Consider running `npm run typecheck` for type safety",
        'md': "Documentation updated - consider `mcp__github__create_pr`",
    }
    
    if file_ext in suggestions_map:
        print(f"\n💡 **Post-edit suggestion**: {suggestions_map[file_ext]}")
    
    return 0

def handle_pre_task(json_input):
    """Always use enhanced version for task coordination"""
    return handle_pre_task_enhanced(json_input)

def handle_post_task(json_input):
    """Handle post-task hook - process task completion"""
    logger.info("Post-task hook: task completed")
    return 0

def handle_pre_mcp(json_input):
    """Handle pre-MCP hook - provide context-aware MCP tool guidance"""
    tool_name = json_input.get('tool_input', {}).get('_tool_name', '')
    logger.info(f"Pre-MCP hook: preparing MCP tool: {tool_name}")
    
    # Provide tool-specific guidance (user-visible)
    tool_guidance = {
        'swarm_init': """### 🐝 Swarm Initialization Checklist

1. **Topology Selection**:
   - `hierarchical` - Best for structured tasks with clear dependencies
   - `mesh` - Best for collaborative tasks requiring peer communication
   - `ring` - Best for sequential processing pipelines
   - `star` - Best for centralized coordination

2. **Agent Count**: Base on task complexity (3-12 agents)
3. **Strategy**: `balanced`, `specialized`, or `adaptive`
4. **Next**: Spawn agents with `mcp__claude-flow__agent_spawn`
""",
        'agent_spawn': """### 🤖 Agent Spawning Best Practices

- **CRITICAL**: Spawn ALL agents in ONE BatchTool message
- **Agent Types**: researcher, coder, analyst, tester, coordinator
- **Naming**: Use descriptive names for tracking
- **Coordination**: Each agent MUST include hooks in their prompt
- **Next**: Use `Task` tool to assign work to agents
""",
    }
    
    # Extract tool type from full name
    tool_parts = tool_name.split('__')
    if len(tool_parts) >= 3:
        tool_type = tool_parts[2]
        if tool_type in tool_guidance:
            print(tool_guidance[tool_type])
    
    return 0

def handle_post_mcp(json_input):
    """Handle post-MCP hook - suggest follow-up tools and workflows"""
    tool_name = json_input.get('tool_input', {}).get('_tool_name', '')
    logger.info(f"Post-MCP hook: MCP tool completed: {tool_name}")
    
    # Tool-specific follow-up suggestions
    follow_ups = {
        'swarm_init': """### 🐝 Swarm Initialized!

**Immediate Next Steps**:
1. Spawn agents: `mcp__claude-flow__agent_spawn` (ALL in one BatchTool)
2. Use `Task` tool to assign work with coordination hooks
3. Store initial state: `mcp__claude-flow__memory_usage`
4. Monitor: `mcp__claude-flow__swarm_status`
""",
        'find_symbol': """### 🔍 Symbol Found!

**Explore Further**:
- `mcp__serena__read_file` - Read full implementation
- `mcp__serena__find_referencing_symbols` - Find usages
- `mcp__serena__replace_symbol_body` - Make edits
- Document findings with memory tools
""",
    }
    
    # Find matching follow-up
    for pattern, suggestion in follow_ups.items():
        if pattern in tool_name:
            print(suggestion)
            break
    
    return 0

def handle_stop(json_input):
    """Always use enhanced version for session cleanup"""
    return handle_stop_enhanced(json_input)

def handle_subagent_stop(json_input):
    """Always use enhanced version for agent coordination"""
    return handle_subagent_stop_enhanced(json_input)

def handle_precompact(json_input):
    """Always use enhanced version for compact preparation"""
    return handle_precompact_enhanced(json_input)

def handle_notification(json_input):
    """Always use enhanced version for notifications"""
    return handle_notification_enhanced(json_input)

def handle_prompt(json_input):
    """
    Handle prompt hook with FULL orchestration - KEEP ORIGINAL IMPLEMENTATION
    This is the most important hook and should maintain full functionality
    """
    logger.info("=" * 60)
    logger.info("🎯 PROMPT HOOK: Full Orchestration Pipeline")
    logger.info("=" * 60)
    
    # Extract the prompt from input
    prompt = json_input.get('prompt', '')
    
    if not prompt:
        logger.warning("No prompt provided in input")
        return 0
    
    logger.info(f"Processing prompt: {prompt[:100]}...")
    
    # Use advanced processor if available
    if PROCESSORS_AVAILABLE:
        try:
            # Create process manager for parallel execution
            process_manager = create_process_manager(logger, enhanced=True, max_workers=4)
            
            # Analyze prompt complexity
            logger.info("Step 1: Analyzing prompt complexity...")
            prompt_analysis = analyze_prompt_complexity(prompt, logger)
            
            # Detect if swarm orchestration is needed
            logger.info("Step 2: Detecting orchestration needs...")
            swarm_analysis = detect_claude_flow_swarm_needs(prompt, logger)
            
            # Get available MCP tools
            mcp_tools = get_available_mcp_tools()
            
            # Generate project context (if Serena available)
            project_context = generate_serena_project_context(logger, process_manager) or {}
            
            # Create Zen consultation task
            logger.info("Step 3: Creating Zen consultation task...")
            zen_task = create_zen_consultation_task(prompt, mcp_tools, project_context)
            
            # Generate Zen consultation instructions
            logger.info("Step 4: Generating Zen consultation instructions...")
            consultation_result = run_zen_consultation_functional(
                zen_task, prompt_analysis, logger, process_manager
            )
            
            if consultation_result.get('success'):
                logger.info("Zen consultation instructions generated")
                
                # Build comprehensive instructions
                output_parts = []
                output_parts.append("## 🎯 Task Orchestration Plan\n")
                output_parts.append(f"**Task**: {prompt}")
                output_parts.append(f"**Complexity**: {prompt_analysis.get('complexity', 'MEDIUM').upper()}")
                output_parts.append(f"**Needs Swarm**: {swarm_analysis.get('needs_swarm', False)}\n")
                
                # Add Zen consultation instructions
                output_parts.append(consultation_result.get('output', ''))
                
                # If complex task needing orchestration
                if swarm_analysis.get('needs_swarm'):
                    logger.info("Step 5: Generating Claude Flow swarm instructions...")
                    swarm_result = run_claude_flow_swarm_orchestration(
                        prompt, swarm_analysis, logger, process_manager
                    )
                    
                    if swarm_result and swarm_result.get('success'):
                        output_parts.append("\n" + swarm_result.get('output', ''))
                        logger.info("Swarm orchestration instructions generated")
                
                # Judge results and prepare final output
                logger.info("Step 6: Preparing final coordination output...")
                judgment = judge_and_spawn_agents_functional(
                    '\n'.join(output_parts),
                    prompt_analysis,
                    mcp_tools,
                    logger,
                    process_manager
                )
                
                # Generate final coordination output
                coordination_output = generate_coordination_output(judgment)
                
                # Output the enhanced prompt with coordination instructions
                print(coordination_output)
                
                logger.info("✅ Orchestration instructions complete - ready for Claude Code execution")
                
            else:
                logger.error(f"Zen consultation failed: {consultation_result.get('error')}")
                # Fallback to basic orchestration
                _provide_basic_orchestration(prompt, prompt_analysis, swarm_analysis)
            
            # Cleanup
            process_manager.cleanup_all()
            
        except Exception as e:
            logger.error(f"Advanced processing failed: {e}", exc_info=True)
            # Fallback to simple orchestration
            _provide_simple_orchestration(prompt)
    else:
        # Use simple fallback
        _provide_simple_orchestration(prompt)
    
    return 0

def _provide_basic_orchestration(prompt: str, prompt_analysis: dict, swarm_analysis: dict):
    """Provide basic orchestration when advanced tools fail"""
    output = f"""## 🎯 Task Orchestration (Basic Mode)

**Task**: {prompt[:200]}...
**Complexity**: {prompt_analysis.get('complexity', 'MEDIUM')}
**Needs Swarm**: {swarm_analysis.get('needs_swarm', False)}

### 📋 Coordination Plan

1. **Initialize coordination** using Claude Flow tools
2. **Spawn agents** based on task complexity
3. **Execute with hooks** for pre/post coordination
4. **Monitor progress** through shared memory

### 🚀 Ready to proceed with coordinated execution.

---
**Note**: Advanced analysis unavailable. Using basic coordination patterns."""
    
    print(output)

def _provide_simple_orchestration(prompt: str):
    """Provide simple orchestration when no processors available"""
    output = f"""## 🎯 Task Coordination

**Task**: {prompt[:100]}...

### 📋 Execution Plan

For complex tasks, consider:
1. Using `mcp__claude-flow__swarm_init` to set up coordination
2. Spawning specialized agents with Task tool
3. Ensuring all agents use coordination hooks
4. Monitoring progress with status tools

### 🚀 Ready to proceed.

---
**Note**: Enhanced orchestration unavailable. Manual coordination recommended."""
    
    print(output)

# Hook type mapping
HOOK_HANDLERS = {
    'pre-bash': handle_pre_bash,
    'pre-edit': handle_pre_edit,
    'post-bash': handle_post_bash,
    'post-edit': handle_post_edit,
    'pre-task': handle_pre_task,
    'post-task': handle_post_task,
    'pre-mcp': handle_pre_mcp,
    'post-mcp': handle_post_mcp,
    'stop': handle_stop,
    'subagent-stop': handle_subagent_stop,
    'precompact': handle_precompact,
    'notification': handle_notification,
    'prompt': handle_prompt
}

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Claude Code hooks with FULL CLAUDE VISIBILITY",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Hook types:
  pre-bash      PreToolUse hook for Bash commands (ENHANCED with Claude visibility)
  pre-edit      PreToolUse hook for Write|Edit|MultiEdit (ENHANCED)
  post-bash     PostToolUse hook for Bash commands (ENHANCED with Claude visibility)
  post-edit     PostToolUse hook for Write|Edit|MultiEdit (ENHANCED with Claude visibility)
  pre-task      PreToolUse hook for Task commands (ENHANCED with coordination checks)
  post-task     PostToolUse hook for Task commands
  pre-mcp       PreToolUse hook for MCP tools
  post-mcp      PostToolUse hook for MCP tools
  stop          Stop hook for session end (ENHANCED with session analysis)
  subagent-stop SubagentStop hook for Task completion (ENHANCED with coordination)
  precompact    PreCompact hook before compact operations (ENHANCED)
  notification  Notification hook for Claude Code notifications (ENHANCED)
  prompt        UserPromptSubmit hook (FULL ORCHESTRATION - unchanged)

🚨 KEY ENHANCEMENT: Critical hooks now use exit code 2 + stderr for Claude visibility!
        """
    )
    parser.add_argument(
        'hook_type',
        choices=list(HOOK_HANDLERS.keys()),
        help='Type of hook to execute'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Read JSON input from stdin
    json_input: Dict[str, Any] = {}
    try:
        if sys.stdin.isatty():
            logger.warning("No input provided via stdin")
            json_input = {}
        else:
            raw_input = sys.stdin.read()
            json_input = json.loads(raw_input) if raw_input.strip() else {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        json_input = {}
    
    # Get appropriate handler
    handler = HOOK_HANDLERS.get(args.hook_type)
    
    if not handler:
        logger.error(f"Unknown hook type: {args.hook_type}")
        return 1
    
    # Execute handler
    try:
        returncode = handler(json_input)
        return returncode
        
    except Exception as e:
        logger.error(f"Hook execution failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("🚀 Enhanced Claude Code Hook Orchestrator v2.0 - WITH CLAUDE VISIBILITY")
    sys.exit(main())