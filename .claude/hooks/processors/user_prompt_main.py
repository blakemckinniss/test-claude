#!/usr/bin/env python3
"""
Unified UserPromptSubmit Hook for Claude Code - Main processor entry point
Processes user prompts through analysis and provides appropriate coordination recommendations
"""

import json
import logging
import os
import signal
import sys
from pathlib import Path

# Add the hooks directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from our organized structure
from processors.user_prompt import (
    ProcessManager,
    # Core managers
    UserPromptCacheManager,
    UserPromptHTTPClientManager,
    UserPromptMonitor,
    # Analysis functions
    analyze_prompt_complexity,
    cached_prompt_hash,
    create_process_manager,
    # Workflows
    create_zen_consultation_task,
    detect_claude_flow_swarm_needs,
    detect_github_repository_context_prompt,
    detect_library_documentation_needs,
    detect_smart_mcp_triggers,
    determine_zen_workflow,
    find_and_kill_zombie_processes,
    generate_coordination_output,
    generate_serena_project_context,
    # MCP tools
    get_available_mcp_tools,
    judge_and_spawn_agents_functional,
    # Parallel execution
    log_prompt_event,
    run_claude_flow_swarm_orchestration,
    run_context7_documentation_lookup,
    run_enhanced_mcp_orchestration,
    run_zen_consultation_functional,
    warm_user_prompt_cache,
)

# Constants
PROCESS_TIMEOUT_SECONDS = 300  # 5 minutes
CONSULTATION_TIMEOUT_SECONDS = 120  # 2 minutes

# Setup cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Global instances
user_prompt_cache = UserPromptCacheManager(CACHE_DIR)
warm_user_prompt_cache()
user_prompt_http_client = UserPromptHTTPClientManager(user_prompt_cache)
user_prompt_monitor = UserPromptMonitor()


def setup_logging():
    """Set up logging for the user prompt processor with enhanced configuration"""
    log_level = os.environ.get('CLAUDE_LOG_LEVEL', 'INFO')

    # Create logs directory
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_dir / 'user_prompt_processor.log', mode='a')
        ]
    )

    # Create logger
    logger = logging.getLogger('UserPromptProcessor')

    # Suppress some noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    return logger


def initialize_system(logger: logging.Logger | None) -> int:
    """Initialize the system and clean up any zombie processes"""
    try:
        # Clean up zombie processes
        killed_count = find_and_kill_zombie_processes(logger)
        if killed_count > 0 and logger:
            logger.info(f"Cleaned up {killed_count} zombie processes")

        # Start monitoring
        user_prompt_monitor.start_monitoring(interval=10)

        return 0
    except Exception as e:
        if logger:
            logger.error(f"System initialization failed: {e}")
        return 1


def parse_input() -> str:
    """Parse input from stdin"""
    try:
        input_data = json.load(sys.stdin)
        return input_data.get('prompt', '')
    except Exception as e:
        log_prompt_event(f"Failed to parse input: {e}")
        return ''


def run_consultation_workflow(prompt: str, prompt_analysis: dict,
                            mcp_tools: dict, project_context: dict,
                            logger: logging.Logger | None,
                            process_manager: ProcessManager) -> str | None:
    """Run the consultation workflow based on prompt analysis"""
    try:
        # Determine workflow
        workflow = determine_zen_workflow(prompt_analysis, logger)
        prompt_analysis['suggested_workflow'] = workflow

        # Create consultation task
        zen_task = create_zen_consultation_task(prompt, mcp_tools, project_context)

        # Run consultation
        consultation_result = run_zen_consultation_functional(
            zen_task, prompt_analysis, logger, process_manager
        )

        if consultation_result.get('success'):
            return consultation_result.get('output', '')
        else:
            if logger:
                logger.error(f"Consultation failed: {consultation_result.get('error')}")
            return None

    except Exception as e:
        if logger:
            logger.error(f"Consultation workflow error: {e}")
        return None


def main():
    """Main entry point for the user prompt processor"""
    # Set up logging
    logger = setup_logging()

    # Initialize enhanced process manager
    process_manager = create_process_manager(logger, enhanced=True, max_workers=4, max_concurrent=8)

    # Set up signal handlers for cleanup
    def cleanup_handler(signum, frame):
        logger.info(f"Received signal {signum}, cleaning up...")
        process_manager.cleanup_all()
        user_prompt_monitor.stop_monitoring()
        user_prompt_http_client.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)

    try:
        # Initialize system
        init_result = initialize_system(logger)
        if init_result != 0:
            logger.error("System initialization failed")
            sys.exit(1)

        # Parse input
        prompt = parse_input()
        if not prompt:
            logger.error("No prompt provided")
            print(json.dumps({"error": "No prompt provided"}))
            sys.exit(1)

        logger.info(f"Processing prompt: {prompt[:100]}...")

        # Generate prompt hash for caching
        prompt_hash = cached_prompt_hash(prompt)

        # Check cache first
        cached_result = user_prompt_cache.get_prompt_analysis(prompt_hash)
        if cached_result:
            logger.info("Using cached prompt analysis")
            prompt_analysis = cached_result
        else:
            # Analyze prompt complexity
            prompt_analysis = analyze_prompt_complexity(prompt, logger)

            # Cache the analysis
            user_prompt_cache.set_prompt_analysis(prompt_hash, prompt_analysis)

        # Get available MCP tools
        mcp_tools = get_available_mcp_tools()

        # Generate project context
        project_context = {}

        # Try Serena first
        serena_context = generate_serena_project_context(logger, process_manager)
        if serena_context:
            project_context.update(serena_context)

        # 🚨 CRITICAL: ALWAYS run swarm orchestration FIRST
        logger.info("🚨 MANDATORY: Initializing Claude Flow swarm orchestration for ALL tasks")
        swarm_analysis = detect_claude_flow_swarm_needs(prompt, logger)
        smart_triggers = detect_smart_mcp_triggers(prompt)
        detect_github_repository_context_prompt(logger)

        # 🚨 MANDATORY: ALWAYS run Claude Flow swarm orchestration FIRST
        logger.info("🚨 RUNNING: Claude Flow swarm orchestration (ALWAYS REQUIRED)")
        swarm_result = run_claude_flow_swarm_orchestration(
            prompt, swarm_analysis, logger, process_manager
        )
        if swarm_result:
            project_context['swarm_orchestration'] = swarm_result
        else:
            # 🚨 FALLBACK: Even if swarm orchestration fails, provide basic instructions
            project_context['swarm_orchestration'] = {
                'instructions': '🚨 MANDATORY: Initialize claude-flow swarm with mcp__claude-flow__swarm_init before proceeding',
                'topology': swarm_analysis.get('suggested_topology', 'hierarchical'),
                'agents': swarm_analysis.get('estimated_agents', 6)
            }

        # Check for library documentation needs
        library_analysis = detect_library_documentation_needs(prompt)
        if library_analysis.get('needs_docs'):
            doc_result = run_context7_documentation_lookup(
                prompt, library_analysis, logger, process_manager
            )
            if doc_result:
                project_context['documentation'] = doc_result

        # Run enhanced MCP orchestration if triggers detected
        if any(smart_triggers.values()):
            mcp_result = run_enhanced_mcp_orchestration(
                prompt, smart_triggers, logger, process_manager
            )
            if mcp_result:
                project_context['mcp_orchestration'] = mcp_result

        # Run consultation workflow
        consultation_result = run_consultation_workflow(
            prompt, prompt_analysis, mcp_tools, project_context,
            logger, process_manager
        )

        # Judge and prepare final output
        if consultation_result:
            judgment = judge_and_spawn_agents_functional(
                consultation_result, prompt_analysis, mcp_tools,
                logger, process_manager
            )

            # Generate coordination output
            coordination_output = generate_coordination_output(judgment)

            # Record metrics
            processing_time = float(os.environ.get('ELAPSED_TIME', '0'))
            user_prompt_monitor.record_prompt_processing(
                processing_time,
                had_error=False,
                cache_hit=cached_result is not None
            )

            # Output the result
            print(coordination_output)

            # Log summary
            logger.info(f"Successfully processed prompt in {processing_time:.2f}s")
            logger.info(f"Complexity: {prompt_analysis.get('complexity')}, "
                       f"Needs swarm: {swarm_analysis.get('needs_swarm')}")
        else:
            # Fallback output
            logger.warning("Consultation failed, providing fallback guidance")

            # 🚨 CRITICAL: Add thinking keywords to fallback output based on complexity
            fallback_complexity = prompt_analysis.get('complexity', 'high')
            fallback_keywords = get_thinking_keywords_for_complexity(fallback_complexity)
            fallback_primary = fallback_keywords['primary'][0] if fallback_keywords['primary'] else 'think super hard'
            
            fallback_output = f"""## 🚨 MANDATORY: {fallback_primary.title()} About Task Coordination Analysis

**Task Complexity**: {fallback_complexity.upper()}
**Confidence**: {max(prompt_analysis.get('confidence', 0.8), 0.8) * 100:.0f}%

### 🚨 MANDATORY: {fallback_primary.title()} About Swarm Coordination Required

🚨 **CRITICAL**: Even with consultation failure, you MUST **{fallback_primary}** and use swarm coordination!

### 🚨 MANDATORY APPROACH - Think Super Hard About Implementation:
1. **Initialize**: `mcp__claude-flow__swarm_init` with hierarchical topology (think about configuration)
2. **Spawn Agents**: Use `mcp__claude-flow__agent_spawn` for 6 agents minimum (think deeply about coordination)
3. **Task() Execution**: ALWAYS use Task() tool for Zen consultations (megathink about delegation)
4. **Batch Operations**: Combine all operations in ONE message for efficiency (ultrathink about optimization)

**Detected indicators**: {', '.join(prompt_analysis.get('indicators', ['swarm_forced', 'task_required', 'thinking_required']))}

---
**🚨 MANDATORY: Proceed with swarm coordination and Task() execution - {fallback_primary} about every step - NO EXCEPTIONS.**"""

            print(fallback_output)

            # Record error metric
            user_prompt_monitor.record_prompt_processing(
                float(os.environ.get('ELAPSED_TIME', '0')),
                had_error=True,
                cache_hit=False
            )

    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    finally:
        # Cleanup
        try:
            process_manager.cleanup_all()
            user_prompt_monitor.stop_monitoring()
            user_prompt_http_client.close()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


if __name__ == "__main__":
    main()
