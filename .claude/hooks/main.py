#!/usr/bin/env python3
"""
Enhanced unified entry point for all Claude Code hooks
Orchestrates prompt processing through Zen consultation and Claude Flow coordination
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

# Import processors
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

# Simple hook handlers for non-prompt hooks
def handle_pre_bash(json_input):
    """Handle pre-bash hook - validate commands and provide suggestions"""
    command = json_input.get('tool_input', {}).get('command', '')
    logger.info(f"Pre-bash hook: validating command: {command[:100]}...")
    
    # Check for claude-flow commands to ensure coordination
    if 'claude-flow' in command:
        logger.info("Claude Flow command detected - ensuring coordination hooks")
    
    # Provide proactive suggestions
    if PROCESSORS_AVAILABLE:
        try:
            # Check for common patterns that could be improved
            if 'grep' in command and 'rg' not in command:
                print("""### 💡 Tool Suggestion

Consider using `rg` (ripgrep) instead of `grep` for better performance:
- Faster search across files
- Respects .gitignore by default
- Better Unicode support

Or use the `Grep` tool directly for structured output.
""")
            
            elif 'find' in command and '-name' in command:
                print("""### 💡 Tool Suggestion

Consider using:
- `Glob` tool for file pattern matching
- `rg --files -g pattern` for faster file discovery
- `mcp__serena__find_file` for project-aware search
""")
            
            # General suggestions
            suggestions = generate_proactive_suggestions('PreToolUse', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
        except Exception as e:
            logger.debug(f"Failed to generate suggestions: {e}")
    
    return 0

def handle_pre_edit(json_input):
    """Handle pre-edit hook - prepare for file operations"""
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    logger.info(f"Pre-edit hook: preparing to edit {file_path}")
    
    # Could add file backup or validation here
    return 0

def handle_post_bash(json_input):
    """Handle post-bash hook - analyze results and suggest next steps"""
    command = json_input.get('tool_input', {}).get('command', '')
    result = json_input.get('tool_result', {})
    exit_code = result.get('exitCode', 0)
    stdout = result.get('stdout', '')
    
    logger.info(f"Post-bash hook: command completed: {command[:100]}...")
    
    # Track claude-flow orchestration commands
    if 'claude-flow' in command and 'hooks' in command:
        logger.info("Claude Flow hook command completed - updating orchestration state")
        print("""### ✅ Coordination Hook Executed

Remember to:
- Store decisions with `mcp__claude-flow__memory_usage`
- Check swarm status periodically
- Use TodoWrite to track progress
""")
    
    # Provide context-based suggestions
    if exit_code != 0:
        print(f"""### ⚠️ Command Failed (exit code: {exit_code})

**Debugging Tools**:
- `mcp__zen__debug` - Systematic error investigation
- `Grep` - Search for error patterns
- `mcp__serena__find_symbol` - Locate problematic code
- Check logs and error messages in output
""")
    
    # Command-specific suggestions
    elif 'npm test' in command or 'pytest' in command:
        if 'passed' in stdout.lower() or 'ok' in stdout.lower():
            print("""### ✅ Tests Passed!

**Next Steps**:
- Update TodoWrite to mark testing complete
- Consider `mcp__github__create_pr` if ready
- Run coverage reports if available
""")
        else:
            print("""### 🧪 Test Results

**Follow-up Actions**:
- Review test output for failures
- Use `mcp__zen__testgen` for missing tests
- Fix failures with targeted edits
""")
    
    elif 'git status' in command:
        print("""### 📝 Git Status Checked

**Common Next Steps**:
- `git add` files for staging
- `mcp__github__create_pr` for pull requests
- Use TodoWrite to track commit tasks
- Review changes with `git diff`
""")
    
    elif 'npm install' in command or 'pip install' in command:
        print("""### 📦 Dependencies Installed

**Post-Install Checklist**:
- Run tests to verify installation
- Check for security vulnerabilities
- Update documentation if needed
- Commit lock files (package-lock.json, etc.)
""")
    
    # General suggestions
    if PROCESSORS_AVAILABLE:
        try:
            suggestions = generate_proactive_suggestions('PostToolUse', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
        except Exception as e:
            logger.debug(f"Failed to generate post-bash suggestions: {e}")
    
    return 0

def handle_post_edit(json_input):
    """Handle post-edit hook - suggest related actions"""
    file_path = json_input.get('tool_input', {}).get('file_path', '')
    logger.info(f"Post-edit hook: file edited: {file_path}")
    
    # Provide context-aware suggestions based on file type
    if PROCESSORS_AVAILABLE:
        try:
            file_ext = file_path.split('.')[-1] if '.' in file_path else ''
            
            suggestions_map = {
                'py': "Consider running `python -m pytest` or `mcp__zen__testgen`",
                'js': "Consider running `npm test` or checking with ESLint",
                'ts': "Consider running `npm run typecheck` for type safety",
                'md': "Documentation updated - consider `mcp__github__create_pr`",
                'json': "Config changed - validate with appropriate schema tools"
            }
            
            if file_ext in suggestions_map:
                print(f"\n💡 **Post-edit suggestion**: {suggestions_map[file_ext]}")
                
            # Special handling for test files
            if 'test' in file_path.lower():
                print("""\n### 🧪 Test File Modified

Recommended actions:
1. Run the test suite to verify changes
2. Check code coverage with appropriate tools
3. Consider `mcp__zen__testgen` for additional test cases
""")
        except Exception as e:
            logger.debug(f"Failed to generate post-edit suggestions: {e}")
    
    return 0

def handle_pre_task(json_input):
    """Handle pre-task hook - ensure coordination and provide guidance"""
    task_desc = json_input.get('tool_input', {}).get('description', '')
    prompt = json_input.get('tool_input', {}).get('prompt', '')
    
    logger.info(f"Pre-task hook: preparing task: {task_desc[:100]}...")
    
    # Always provide coordination reminder
    print("""### ⚠️ Task Agent Coordination Required

Ensure your Task agent includes these MANDATORY coordination hooks:

1. **START**: `npx claude-flow@alpha hooks pre-task --description "[task]"`
2. **DURING**: After EVERY file operation:
   - `npx claude-flow@alpha hooks post-edit --file "[file]"`
   - `npx claude-flow@alpha hooks notification --message "[decision]"`
3. **MEMORY**: Store decisions with:
   - `mcp__claude-flow__memory_usage` (action: "store")
4. **END**: `npx claude-flow@alpha hooks post-task --task-id "[task]"`

This enables proper swarm coordination and shared decision-making.
""")
    
    # Additional task-specific suggestions
    if PROCESSORS_AVAILABLE:
        try:
            suggestions = generate_proactive_suggestions('PreToolUse', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
            
            # Suggest relevant MCP tools based on task type
            task_lower = (task_desc + ' ' + prompt).lower()
            if 'research' in task_lower or 'analyze' in task_lower:
                print("""\n### 🔍 Research Agent Tools:
- `mcp__zen__analyze` - Deep analysis
- `mcp__serena__get_symbols_overview` - Code structure
- `WebSearch` - Current information
- `mcp__context7__get-library-docs` - Library docs
""")
            elif 'test' in task_lower:
                print("""\n### 🧪 Testing Agent Tools:
- `mcp__zen__testgen` - Generate tests
- `Bash` - Run test suites
- `mcp__zen__codereview` - Review quality
""")
            elif 'implement' in task_lower or 'code' in task_lower:
                print("""\n### 💻 Coding Agent Tools:
- `Write` / `Edit` - File operations
- `mcp__serena__find_symbol` - Find code
- `mcp__zen__refactor` - Improve code
- `TodoWrite` - Track subtasks
""")
                    
        except Exception as e:
            logger.debug(f"Failed to generate task suggestions: {e}")
    
    return 0

def handle_post_task(json_input):
    """Handle post-task hook - process task completion"""
    logger.info("Post-task hook: task completed")
    return 0

def handle_pre_mcp(json_input):
    """Handle pre-MCP hook - provide context-aware MCP tool guidance"""
    tool_name = json_input.get('tool_input', {}).get('_tool_name', '')
    logger.info(f"Pre-MCP hook: preparing MCP tool: {tool_name}")
    
    # Provide tool-specific guidance
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
        
        'task_orchestrate': """### 🎯 Task Orchestration Guide

1. **Strategy Options**:
   - `parallel` - All tasks run simultaneously
   - `sequential` - Tasks run in order
   - `adaptive` - Dynamic task allocation

2. **Priority Levels**: critical, high, medium, low
3. **Memory**: Store task breakdown for agents
4. **Monitor**: Use `swarm_status` to track progress
""",
        
        'memory_usage': """### 💾 Memory Operation Guide

**Actions**:
- `store` - Save coordination state/decisions
- `retrieve` - Get previous context
- `list` - See all memory keys

**Key Patterns**:
- `swarm/{id}/init` - Swarm configuration
- `agent/{name}/state` - Agent-specific data
- `task/{id}/progress` - Task tracking
- `decision/{timestamp}` - Decision history
""",
        
        'find_symbol': """### 🔍 Symbol Search Tips

1. **Name Path Format**:
   - Simple: `method_name`
   - Nested: `class/method`
   - Absolute: `/module/class/method`

2. **Options**:
   - `depth`: Include child symbols
   - `include_body`: Get full implementation
   - `substring_matching`: Partial name match

3. **Next**: Use `read_file` or `find_referencing_symbols`
""",
        
        'github': """### 🔗 GitHub Operation Guide

**Common Workflows**:
1. Issues → Branch → Edit → PR
2. PR Review → Comments → Merge
3. Notifications → Triage → Action

**Best Practices**:
- Always check existing issues first
- Create descriptive branch names
- Add comprehensive PR descriptions
"""
    }
    
    # Extract tool type from full name
    tool_parts = tool_name.split('__')
    if len(tool_parts) >= 3:
        tool_type = tool_parts[2]
        if tool_type in tool_guidance:
            print(tool_guidance[tool_type])
        elif 'github' in tool_parts[1]:
            print(tool_guidance.get('github', ''))
    
    # General MCP tool suggestions
    if PROCESSORS_AVAILABLE:
        try:
            suggestions = generate_proactive_suggestions('PreToolUse', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
        except Exception as e:
            logger.debug(f"Failed to generate suggestions: {e}")
    
    return 0

def handle_post_mcp(json_input):
    """Handle post-MCP hook - suggest follow-up tools and workflows"""
    tool_name = json_input.get('tool_input', {}).get('_tool_name', '')
    tool_result = json_input.get('tool_result', {})
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
        
        'agent_spawn': """### 🤖 Agent Spawned!

**Now**:
1. Assign work with `Task` tool (include coordination hooks!)
2. Track with TodoWrite for each agent's responsibilities
3. Monitor progress: `mcp__claude-flow__agent_metrics`
""",
        
        'find_symbol': """### 🔍 Symbol Found!

**Explore Further**:
- `mcp__serena__read_file` - Read full implementation
- `mcp__serena__find_referencing_symbols` - Find usages
- `mcp__serena__replace_symbol_body` - Make edits
- Document findings with memory tools
""",
        
        'list_issues': """### 📝 Issues Retrieved!

**Issue Management**:
1. Prioritize with TodoWrite
2. Create branch: `mcp__github__create_branch`
3. Comment updates: `mcp__github__add_issue_comment`
4. Create PR when ready: `mcp__github__create_pr`
""",
        
        'get-library-docs': """### 📚 Documentation Retrieved!

**Using the Docs**:
- Reference in your implementation
- Create examples based on docs
- Test against documented behavior
- Share insights via memory tools
""",
        
        'tavily_search': """### 🔍 Search Complete!

**Process Results**:
- Extract key information
- Verify with additional searches if needed
- Store findings: `mcp__claude-flow__memory_usage`
- Use `mcp__tavily-remote__tavily_extract` for full content
"""
    }
    
    # Find matching follow-up
    for pattern, suggestion in follow_ups.items():
        if pattern in tool_name:
            print(suggestion)
            break
    
    # Result-based suggestions
    if tool_result:
        if tool_name.endswith('_list') or tool_name.endswith('list_issues'):
            count = len(tool_result) if isinstance(tool_result, list) else 0
            if count > 0:
                print(f"\n📊 Found {count} items. Consider using TodoWrite to track them.")
        
        elif tool_name.endswith('status'):
            print("\n📋 Status checked. Update your approach based on current state.")
    
    # General MCP follow-up suggestions
    if PROCESSORS_AVAILABLE:
        try:
            suggestions = generate_proactive_suggestions('PostToolUse', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
        except Exception as e:
            logger.debug(f"Failed to generate post-MCP suggestions: {e}")
    
    return 0

def handle_stop(json_input):
    """Handle stop hook - cleanup session"""
    logger.info("Stop hook: cleaning up session")
    return 0

def handle_subagent_stop(json_input):
    """Handle subagent-stop hook - cleanup after Task completion"""
    logger.info("Subagent-stop hook: task agent completed")
    return 0

def handle_precompact(json_input):
    """Handle precompact hook"""
    logger.info("Precompact hook executed")
    return 0

def handle_notification(json_input):
    """Handle notification hook - provide context-aware assistance"""
    message = json_input.get('message', '')
    logger.info(f"Notification hook: {message[:100]}...")
    
    # Provide proactive help based on notification type
    if 'waiting' in message.lower() or 'idle' in message.lower():
        print("""### 💡 While Claude Code is Waiting

**Quick Actions**:
1. Check swarm progress: `mcp__claude-flow__swarm_status`
2. Review memory state: `mcp__claude-flow__memory_usage` (action: "retrieve")
3. Monitor agents: `mcp__claude-flow__agent_list`
4. Check todos: Review your TodoWrite list

**Common Next Steps**:
- If debugging: Try `mcp__zen__debug` for systematic investigation
- If implementing: Use `mcp__serena__find_symbol` to locate code
- If testing: Run `mcp__zen__testgen` for test generation
- If reviewing: Use `mcp__github__list_notifications`
""")
    
    elif 'permission' in message.lower():
        print("""### 🔐 Permission Request Guidance

**Quick Review Checklist**:
- Is the file path correct?
- Is this a safe operation?
- Are there any alternatives?

**Auto-approve candidates**:
- Reading documentation files (.md, .txt)
- Status checking operations
- Memory retrieval (not storage)
""")
    
    # General notification handling
    if PROCESSORS_AVAILABLE:
        try:
            suggestions = generate_proactive_suggestions('Notification', json_input)
            if suggestions and any(suggestions.values()):
                output = format_suggestions_for_output(suggestions)
                if output:
                    print("\n" + output)
        except Exception as e:
            logger.debug(f"Failed to generate notification suggestions: {e}")
    
    return 0

def handle_prompt(json_input):
    """
    Handle prompt hook with FULL orchestration:
    1. Analyze prompt complexity
    2. Consult Zen tools for approach
    3. Initialize Claude Flow swarm if needed
    4. Spawn coordinated agents
    5. Set up pre/post tool hooks for coordination
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
        description="Enhanced unified entry point for all Claude Code hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Hook types:
  pre-bash      PreToolUse hook for Bash commands
  pre-edit      PreToolUse hook for Write|Edit|MultiEdit
  post-bash     PostToolUse hook for Bash commands
  post-edit     PostToolUse hook for Write|Edit|MultiEdit
  pre-task      PreToolUse hook for Task commands
  post-task     PostToolUse hook for Task commands
  pre-mcp       PreToolUse hook for MCP tools
  post-mcp      PostToolUse hook for MCP tools
  stop          Stop hook for session end
  subagent-stop SubagentStop hook for Task completion
  precompact    PreCompact hook before compact operations
  notification  Notification hook for Claude Code notifications
  prompt        UserPromptSubmit hook (FULL ORCHESTRATION)
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
    logger.info("🚀 Claude Code Hook Orchestrator v2.0")
    sys.exit(main())