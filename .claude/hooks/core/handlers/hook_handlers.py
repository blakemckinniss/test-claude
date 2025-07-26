"""
Hook handlers module for Claude Code hooks.
Contains all the handle_* functions for different hook types.
"""

import io
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Setup logger first
logger = logging.getLogger(__name__)

# Import utilities with fallbacks
try:
    from ..utils.utils import extract_json_field, log_to_file, should_execute_hook
except ImportError:
    # Fallback utilities
    def log_to_file(message):
        logger.info(message)
        print(f"[HOOK] {message}", file=sys.stderr)

    def extract_json_field(data, field_path):
        try:
            keys = field_path.split('.')
            value = data
            for key in keys:
                value = value.get(key, {})
            return value if value != {} else None
        except (AttributeError, KeyError, TypeError):
            return None

    def should_execute_hook(hook_type):
        return True  # Default to allowing execution

# Import Claude Flow integration functions
try:
    # Use absolute import by adding the hooks directory to the path
    hooks_dir = Path(__file__).parent.parent.parent
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))

    from integrations.claude_flow.claude_flow_integration import (
        detect_complex_task_and_spawn_swarm,
        detect_github_repository_context,
        initialize_github_swarm,
        integrate_claude_flow_memory,
        recommend_github_swarm_orchestration,
        run_claude_flow_command,
        run_claude_flow_command_async,
        run_claude_flow_mcp_command,
        run_serena_mcp_command,
        # Advanced Claude Flow features
        run_neural_training,
        run_memory_operations,
        run_daa_operations,
        run_performance_monitoring,
        run_workflow_automation,
    )
    CLAUDE_FLOW_AVAILABLE = True
    logger.info("Claude Flow integration loaded successfully")
except ImportError as e:
    # Proper fallback implementations that return correct types
    CLAUDE_FLOW_AVAILABLE = False
    logger.warning(f"Claude Flow integration not available: {e}, using fallbacks")

    def run_claude_flow_command(command_parts):
        """Fallback that returns correct tuple format"""
        return (0, "", "")  # (returncode, stdout, stderr)

    def run_serena_mcp_command(json_input):
        """Fallback that returns empty dict"""
        return {}

    def run_claude_flow_mcp_command(json_input):
        """Fallback that returns empty dict"""
        return {}

    def detect_complex_task_and_spawn_swarm(operation_context, hook_type):
        """Fallback that returns proper analysis dict"""
        return {
            "recommend_swarm": False,
            "complexity_score": 0,
            "should_use_swarm": False,
            "recommended_agents": [],
            "topology": "mesh",
            "indicators": {}
        }

    def integrate_claude_flow_memory(operation, key, value=None, namespace="default"):
        """Fallback that returns None"""
        return None

    def detect_github_repository_context(json_input):
        """Fallback that returns proper context dict"""
        return {
            "is_github_repo": False,
            "repo_path": None,
            "remote_url": None,
            "current_branch": None,
            "has_uncommitted_changes": False,
            "owner": None,
            "repo": None
        }

    def recommend_github_swarm_orchestration(github_context, task_context):
        """Fallback that returns proper recommendation dict"""
        return {
            "recommended": False,
            "swarm_type": None,
            "suggested_agents": [],
            "workflow": []
        }

    def initialize_github_swarm(swarm_type, repo_path, agents):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "Claude Flow not available"
        }

    def run_neural_training(training_data):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "Neural training not available"
        }

    def run_memory_operations(operation, params):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "Memory operations not available"
        }

    def run_daa_operations(operation, params):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "DAA operations not available"
        }

    def run_performance_monitoring(metrics_type="all"):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "Performance monitoring not available"
        }

    def run_workflow_automation(workflow_type, params):
        """Fallback that returns proper result dict"""
        return {
            "success": False,
            "error": "Workflow automation not available"
        }

# Import process management with fallbacks
try:
    from ..process_management import ProcessManager
    process_manager = ProcessManager()
except ImportError:
    # Fallback process manager
    class ProcessManager:
        def cleanup(self): pass
    process_manager = ProcessManager()

# Import the user_prompt_processor module for 'prompt' hook type
user_prompt_processor = None
try:
    # Try primary path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import user_prompt_processor_unified as user_prompt_processor
except ImportError:
    try:
        # Try alternative path
        processors_dir = Path(__file__).parent.parent.parent / 'processors'
        sys.path.insert(0, str(processors_dir))
        import user_prompt_main as user_prompt_processor
    except ImportError:
        user_prompt_processor = None
        logger.warning("user_prompt_processor module not found")


def handle_pre_bash(json_input: dict[str, Any]) -> int:
    """Handle PreToolUse hook for Bash commands"""
    # Rate limiting check
    if not should_execute_hook("pre-bash"):
        return 0

    command = extract_json_field(json_input, "tool_input.command")
    if not command:
        log_to_file("❌ PRE-BASH: No command found in input")
        logger.error("No command found in tool_input.command")
        error_output = {
            "success": False,
            "message": "No command found in tool_input.command",
            "returncode": 1
        }
        print(json.dumps(error_output), file=sys.stderr)
        return 1

    # Skip hooks on log directory operations to prevent loops
    skip_patterns = ('.claude/logs', '.log', 'hooks_', 'session_')
    if any(pattern in command for pattern in skip_patterns):
        return 0  # Silent skip for performance

    log_to_file(f"🔧 PRE-BASH: {command[:50]}...")
    logger.debug(f"Full command: {command}")

    # Advanced: Check if command needs neural pattern recognition
    if CLAUDE_FLOW_AVAILABLE and any(pattern in command for pattern in ['test', 'build', 'deploy']):
        try:
            # Use neural network to predict command outcome
            neural_result = run_neural_training({
                'pattern_type': 'command_prediction',
                'input_command': command,
                'epochs': 1,  # Quick inference
                'model_name': 'command-predictor'
            })
            if neural_result.get('success'):
                log_to_file(f"🧠 Neural prediction: {neural_result.get('prediction', 'unknown')}")
        except Exception as e:
            logger.debug(f"Neural prediction skipped: {e}")

    # Run the claude-flow pre-command hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "pre-command",
        "--command", command,
        "--validate-safety", "true",
        "--prepare-resources", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Pre-command hook failed: {stderr}",
            "command": command,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Pre-command hook completed successfully",
            "output": stdout,
            "command": command
        }
        print(json.dumps(success_output))

    return returncode


def handle_pre_edit(json_input: dict[str, Any]) -> int:
    """Handle PreToolUse hook for Write|Edit|MultiEdit"""
    # Rate limiting check
    if not should_execute_hook("pre-edit"):
        return 0

    # Try different possible field paths for file path
    file_path = (extract_json_field(json_input, "tool_input.file_path") or
                 extract_json_field(json_input, "tool_input.path"))

    if not file_path:
        log_to_file("❌ PRE-EDIT: No file path found in input")
        logger.error("No file path found in tool_input")
        error_output = {
            "success": False,
            "message": "No file path found in tool_input",
            "returncode": 1
        }
        print(json.dumps(error_output), file=sys.stderr)
        return 1

    # Skip hooks on log files to prevent loops
    file_str = str(file_path)
    skip_patterns = ('.claude/logs', '.log', 'hooks_', 'session_')
    if any(pattern in file_str for pattern in skip_patterns):
        return 0  # Silent skip for performance

    log_to_file(f"📝 PRE-EDIT: {file_path}")
    logger.debug(f"Edit operation on: {file_path}")

    # Run the claude-flow pre-edit hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "pre-edit",
        "--file", str(file_path),
        "--auto-assign-agents", "true",
        "--load-context", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Pre-edit hook failed: {stderr}",
            "file_path": str(file_path),
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Pre-edit hook completed successfully",
            "output": stdout,
            "file_path": str(file_path)
        }
        print(json.dumps(success_output))

    return returncode


def handle_post_bash(json_input: dict[str, Any]) -> int:
    """Handle PostToolUse hook for Bash commands"""
    # Rate limiting check
    if not should_execute_hook("post-bash"):
        return 0

    command = extract_json_field(json_input, "tool_input.command")
    if not command:
        log_to_file("❌ POST-BASH: No command found in input")
        logger.error("No command found in tool_input.command")
        error_output = {
            "success": False,
            "message": "No command found in tool_input.command",
            "returncode": 1
        }
        print(json.dumps(error_output), file=sys.stderr)
        return 1

    # Skip hooks on log directory operations to prevent loops
    skip_patterns = ('.claude/logs', '.log', 'hooks_', 'session_')
    if any(pattern in command for pattern in skip_patterns):
        return 0  # Silent skip for performance

    log_to_file(f"🔨 POST-BASH: {command[:50]}...")
    logger.debug(f"Post-processing command: {command}")

    # Advanced: Performance monitoring for commands
    if CLAUDE_FLOW_AVAILABLE:
        try:
            # Monitor command performance
            perf_result = run_performance_monitoring("command_execution")
            if perf_result.get('success'):
                metrics = perf_result.get('metrics', {})
                if metrics.get('response_time', 0) > 1000:  # 1 second
                    log_to_file(f"⚠️ Slow command detected: {metrics.get('response_time')}ms")
                    # Store in memory for pattern analysis
                    integrate_claude_flow_memory(
                        "store",
                        f"slow_command/{hash(command)}",
                        {"command": command, "time": metrics.get('response_time')},
                        "performance"
                    )
        except Exception as e:
            logger.debug(f"Performance monitoring skipped: {e}")

    # Run the claude-flow post-command hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "post-command",
        "--command", command,
        "--track-metrics", "true",
        "--store-results", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Post-command hook failed: {stderr}",
            "command": command,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Post-command hook completed successfully",
            "output": stdout,
            "command": command
        }
        print(json.dumps(success_output))

    return returncode


def handle_post_edit(json_input: dict[str, Any]) -> int:
    """Handle PostToolUse hook for Write|Edit|MultiEdit with Serena and Claude Flow integration"""
    # Rate limiting check
    if not should_execute_hook("post-edit"):
        return 0

    # Try different possible field paths for file path
    file_path = (extract_json_field(json_input, "tool_input.file_path") or
                 extract_json_field(json_input, "tool_input.path"))

    if not file_path:
        log_to_file("❌ POST-EDIT: No file path found in input")
        logger.error("No file path found in tool_input")
        error_output = {
            "success": False,
            "message": "No file path found in tool_input",
            "returncode": 1
        }
        print(json.dumps(error_output), file=sys.stderr)
        return 1

    # Skip hooks on log files to prevent loops
    file_str = str(file_path)
    skip_patterns = ('.claude/logs', '.log', 'hooks_', 'session_')
    if any(pattern in file_str for pattern in skip_patterns):
        return 0  # Silent skip for performance

    log_to_file(f"📄 POST-EDIT: {file_path}")
    logger.debug(f"Post-edit processing: {file_path}")

    # Enhanced with Serena MCP and Claude Flow integration
    serena_success = False
    claude_flow_analysis = {"recommend_swarm": False, "complexity_score": 0}

    if CLAUDE_FLOW_AVAILABLE:
        try:
            # 1. Check for Serena MCP operations
            serena_context = extract_json_field(json_input, "tool")
            if serena_context and 'serena' in str(serena_context).lower():
                serena_result = run_serena_mcp_command(json_input)
                if serena_result:
                    log_to_file(f"📚 Serena MCP integration detected for {file_path}")
                    serena_success = True

            # 2. Check for Claude Flow MCP operations
            flow_context = extract_json_field(json_input, "tool")
            if flow_context and 'claude-flow' in str(flow_context).lower():
                flow_result = run_claude_flow_mcp_command(json_input)
                if flow_result:
                    log_to_file(f"🐝 Claude Flow MCP integration detected for {file_path}")

            # 3. Claude Flow: Detect if this edit suggests complex task coordination
            operation_context = {
                "tool_name": "post-edit",
                "file_path": str(file_path),
                "command": ""
            }
            claude_flow_analysis = detect_complex_task_and_spawn_swarm(operation_context, "post-edit")

            # 4. GitHub Integration: Check for GitHub-specific operations
            github_context = detect_github_repository_context(json_input)
            if github_context.get("is_github_repo"):
                github_swarm_analysis = recommend_github_swarm_orchestration(github_context, operation_context)

                # Initialize GitHub swarm if recommended
                if github_swarm_analysis.get("recommended"):
                    github_swarm_result = initialize_github_swarm(
                        github_swarm_analysis.get("swarm_type", "maintenance"),
                        github_context.get("repo_path", "."),
                        github_swarm_analysis.get("suggested_agents", [])
                    )
                    if github_swarm_result.get("success"):
                        log_to_file(f"🐙 GitHub swarm initialized for {github_context.get('owner')}/{github_context.get('repo')}")

        except Exception as e:
            logger.warning(f"Serena/Claude Flow integration failed for {file_path}: {e}")

    # Run the claude-flow post-edit hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "post-edit",
        "--file", str(file_path),
        "--format", "true",
        "--update-memory", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Post-edit hook failed: {stderr}",
            "file_path": str(file_path),
            "returncode": returncode,
            "serena_analysis": serena_success,
            "claude_flow_swarm_recommended": claude_flow_analysis.get("recommend_swarm", False)
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Post-edit hook completed successfully",
            "output": stdout,
            "file_path": str(file_path),
            "serena_analysis": serena_success,
            "claude_flow_swarm_recommended": claude_flow_analysis.get("recommend_swarm", False),
            "complexity_score": claude_flow_analysis.get("complexity_score", 0)
        }
        print(json.dumps(success_output))

    return returncode


def handle_subagent_stop(json_input: dict[str, Any]) -> int:
    """Handle SubagentStop hook for Task tool completion"""
    log_to_file("🤖 SUBAGENT-STOP: Task subagent finished, processing cleanup...")

    session_id = extract_json_field(json_input, "session_id") or "unknown"
    stop_hook_active = extract_json_field(json_input, "stop_hook_active") or False

    # Skip if already processing stop hooks to prevent infinite loops
    if stop_hook_active:
        success_output = {
            "success": True,
            "message": "Subagent stop hook skipped - stop hook already active",
            "session_id": session_id
        }
        print(json.dumps(success_output))
        return 0

    # Run the claude-flow subagent-end hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "post-task",
        "--task-id", f"subagent-{session_id}",
        "--analyze-performance", "true",
        "--generate-insights", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Subagent-stop hook failed: {stderr}",
            "session_id": session_id,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Subagent-stop hook completed successfully",
            "output": stdout,
            "session_id": session_id
        }
        print(json.dumps(success_output))

    return returncode


def handle_precompact(json_input: dict[str, Any]) -> int:
    """Handle PreCompact hook before compact operations"""
    trigger = extract_json_field(json_input, "trigger") or "unknown"
    custom_instructions = extract_json_field(json_input, "custom_instructions") or ""

    log_to_file(f"📦 PRECOMPACT: About to compact (trigger: {trigger})")

    # Run the claude-flow pre-compact hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "pre-task",
        "--description", f"Compact operation ({trigger})",
        "--task-id", f"compact-{trigger}",
        "--auto-spawn-agents", "false"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Pre-compact hook failed: {stderr}",
            "trigger": trigger,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Pre-compact hook completed successfully",
            "output": stdout,
            "trigger": trigger,
            "custom_instructions": custom_instructions
        }
        print(json.dumps(success_output))

    return returncode


def handle_notification(json_input: dict[str, Any]) -> int:
    """Handle Notification hook for Claude Code notifications"""
    # Rate limiting check
    if not should_execute_hook("notification"):
        return 0

    message = extract_json_field(json_input, "message") or "No message"
    session_id = extract_json_field(json_input, "session_id") or "unknown"

    log_to_file(f"🔔 NOTIFICATION: {message[:50]}...")

    # Run the claude-flow notification hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "notification",
        "--message", message,
        "--session-id", session_id,
        "--telemetry", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Notification hook failed: {stderr}",
            "notification_message": message,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Notification hook completed successfully",
            "output": stdout,
            "notification_message": message
        }
        print(json.dumps(success_output))

    return returncode


def handle_stop(json_input: dict[str, Any]) -> int:
    """Handle Stop hook for session end"""
    log_to_file("🛑 STOP: Session ending, generating summary...")

    # Run the claude-flow session-end hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "session-end",
        "--generate-summary", "true",
        "--persist-state", "true",
        "--export-metrics", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Session-end hook failed: {stderr}",
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Session-end hook completed successfully",
            "output": stdout
        }
        print(json.dumps(success_output))

    # Clean up any remaining processes
    if process_manager:
        process_manager.cleanup()

    return returncode


def handle_pre_task(json_input: dict[str, Any]) -> int:
    """Handle PreToolUse hook for Task commands"""
    # Rate limiting check
    if not should_execute_hook("pre-task"):
        return 0

    task_description = extract_json_field(json_input, "tool_input.description") or "Task execution"

    log_to_file(f"🎯 PRE-TASK: {task_description[:50]}...")

    # Run the claude-flow pre-task hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "pre-task",
        "--description", task_description,
        "--auto-spawn-agents", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Pre-task hook failed: {stderr}",
            "task_description": task_description,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Pre-task hook completed successfully",
            "output": stdout,
            "task_description": task_description
        }
        print(json.dumps(success_output))

    return returncode


def handle_post_task(json_input: dict[str, Any]) -> int:
    """Handle PostToolUse hook for Task commands"""
    # Rate limiting check
    if not should_execute_hook("post-task"):
        return 0

    task_description = extract_json_field(json_input, "tool_input.description") or "Task execution"

    log_to_file(f"✅ POST-TASK: {task_description[:50]}...")

    # Run the claude-flow post-task hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "post-task",
        "--task-id", f"task-{task_description[:20]}",
        "--analyze-performance", "true"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Post-task hook failed: {stderr}",
            "task_description": task_description,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Post-task hook completed successfully",
            "output": stdout,
            "task_description": task_description
        }
        print(json.dumps(success_output))

    return returncode


def handle_pre_mcp(json_input: dict[str, Any]) -> int:
    """Handle PreToolUse hook for MCP tools"""
    # Rate limiting check
    if not should_execute_hook("pre-mcp"):
        return 0

    tool_name = extract_json_field(json_input, "tool_name") or "unknown"

    log_to_file(f"🔗 PRE-MCP: {tool_name}")

    # Special handling for Tavily tools
    if "tavily" in tool_name.lower():
        log_to_file(f"🌐 TAVILY: Preparing web search/extraction tool: {tool_name}")

    # Special handling for Context7 tools
    if "context7" in tool_name.lower():
        log_to_file(f"📚 CONTEXT7: Preparing documentation lookup tool: {tool_name}")

    # Run the claude-flow pre-mcp hook - simplified for MCP coordination
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "pre-task",
        "--description", f"MCP tool: {tool_name}",
        "--auto-spawn-agents", "false"
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Pre-MCP hook failed: {stderr}",
            "tool_name": tool_name,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Pre-MCP hook completed successfully",
            "output": stdout,
            "tool_name": tool_name
        }
        print(json.dumps(success_output))

    return returncode


def handle_post_mcp(json_input: dict[str, Any]) -> int:
    """Handle PostToolUse hook for MCP tools"""
    # Rate limiting check
    if not should_execute_hook("post-mcp"):
        return 0

    tool_name = extract_json_field(json_input, "tool_name") or "unknown"

    log_to_file(f"🔗 POST-MCP: {tool_name}")

    # Run the claude-flow post-mcp hook
    returncode, stdout, stderr = run_claude_flow_command([
        "hooks", "post-task",
        "--task-id", f"mcp-{tool_name}",
        "--analyze-performance", "false"  # Lightweight for MCP tools
    ])

    if returncode != 0:
        error_output = {
            "success": False,
            "message": f"Post-MCP hook failed: {stderr}",
            "tool_name": tool_name,
            "returncode": returncode
        }
        print(json.dumps(error_output), file=sys.stderr)
    else:
        success_output = {
            "success": True,
            "message": "Post-MCP hook completed successfully",
            "output": stdout,
            "tool_name": tool_name
        }
        print(json.dumps(success_output))

    return returncode


def handle_prompt(json_input: dict[str, Any]) -> int:
    """Handle UserPromptSubmit hook by delegating to user_prompt_processor"""
    # Rate limiting check
    if not should_execute_hook("prompt"):
        return 0

    prompt_text = extract_json_field(json_input, "prompt") or "<no prompt>"
    
    # Advanced: Check if prompt needs DAA agents or workflow automation
    if CLAUDE_FLOW_AVAILABLE:
        try:
            # Analyze prompt for complexity
            prompt_lower = prompt_text.lower()
            
            # Check if we need DAA agents
            if any(keyword in prompt_lower for keyword in ['complex', 'multi-step', 'coordinate', 'orchestrate']):
                daa_result = run_daa_operations("create_agent", {
                    'agent_id': f'prompt-agent-{hash(prompt_text)}',
                    'pattern': 'adaptive',
                    'enable_memory': True
                })
                if daa_result.get('success'):
                    log_to_file("🤖 DAA agent created for complex prompt processing")
            
            # Check if we need workflow automation
            if any(keyword in prompt_lower for keyword in ['automate', 'workflow', 'pipeline', 'process']):
                workflow_result = run_workflow_automation("create", {
                    'workflow_id': f'prompt-workflow-{hash(prompt_text)}',
                    'name': 'Automated Prompt Workflow',
                    'steps': [
                        {'name': 'analyze', 'type': 'analysis'},
                        {'name': 'plan', 'type': 'planning'},
                        {'name': 'execute', 'type': 'execution'}
                    ]
                })
                if workflow_result.get('success'):
                    log_to_file("🔄 Workflow automation created for prompt")
            
            # Store prompt in memory for cross-session learning
            integrate_claude_flow_memory(
                "store",
                f"prompt_history/{hash(prompt_text)}",
                {
                    "prompt": prompt_text[:500],
                    "timestamp": os.environ.get('TIMESTAMP', 'N/A'),
                    "complexity": 'high' if len(prompt_text.split()) > 50 else 'medium'
                },
                "prompts"
            )
        except Exception as e:
            logger.debug(f"Advanced prompt processing skipped: {e}")

    if user_prompt_processor is None:
        log_to_file("❌ PROMPT: user_prompt_processor module not found")
        logger.error("user_prompt_processor module not found")

        # Provide a basic fallback response
        print(f"## 🎯 Basic Task Analysis\n\n**Prompt**: {prompt_text[:200]}...\n\n**Status**: Ready to proceed with direct execution.\n\n---\n**Note**: Advanced prompt analysis unavailable, proceeding with basic coordination.")

        success_output = {
            "success": True,
            "message": "Basic prompt processing completed (advanced analysis unavailable)",
            "prompt_length": len(prompt_text)
        }
        print(json.dumps(success_output))
        return 0

    log_to_file(f"💬 PROMPT: Processing user prompt: {prompt_text[:100]}...")
    logger.debug(f"Full prompt: {prompt_text}")

    # Restore stdin for the user_prompt_processor to read
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(json_input))

    try:
        # Run the user_prompt_processor main function
        user_prompt_processor.main()
        # Output success message in expected format
        success_output = {
            "success": True,
            "message": "User prompt processing completed successfully",
            "prompt_length": len(prompt_text)
        }
        print(json.dumps(success_output))
        return 0
    except SystemExit as e:
        return int(str(e.code)) if e.code is not None else 0
    except Exception as e:
        logger.error(f"Error running user_prompt_processor: {e}")
        error_output = {
            "success": False,
            "message": f"Error running user_prompt_processor: {e}",
            "returncode": 1
        }
        print(json.dumps(error_output), file=sys.stderr)
        return 1
    finally:
        sys.stdin = old_stdin


# Export all handlers
__all__ = [
    'handle_pre_bash',
    'handle_pre_edit',
    'handle_post_bash',
    'handle_post_edit',
    'handle_subagent_stop',
    'handle_precompact',
    'handle_notification',
    'handle_stop',
    'handle_pre_task',
    'handle_post_task',
    'handle_pre_mcp',
    'handle_post_mcp',
    'handle_prompt'
]
