"""
Claude Flow integration module for Claude Code hooks.
Provides swarm orchestration, MCP command execution, and GitHub integration.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

# Import with fallbacks for missing modules
try:
    from ...core.cache import CacheManager
except ImportError:
    # Fallback cache manager
    class CacheManager:
        def get(self, key): return None
        def set(self, key, value, ttl=None): pass

try:
    from ...core.resilience import CircuitBreaker, RetryMechanism, circuit_breakers, retry_mechanism
except ImportError:
    # Fallback resilience components
    class CircuitBreaker:
        def can_execute(self): return True
        def record_success(self): pass
        def record_failure(self): pass

    class RetryMechanism:
        def execute_with_retry(self, func): return func()

    circuit_breakers = {'claude-flow': CircuitBreaker(), 'default': CircuitBreaker()}
    retry_mechanism = RetryMechanism()

try:
    from ...core.utils.utils import extract_json_field, log_to_file
except ImportError:
    # Fallback utilities
    def log_to_file(message):
        logging.info(message)

    def extract_json_field(data, field_path):
        try:
            keys = field_path.split('.')
            value = data
            for key in keys:
                value = value.get(key, {})
            return value if value != {} else None
        except (AttributeError, KeyError, TypeError):
            return None

logger = logging.getLogger(__name__)

# Initialize cache for Claude Flow operations
claude_flow_cache = CacheManager()


def run_serena_mcp_command(request_data: dict[str, Any]) -> dict[str, Any]:
    """Run Serena MCP command if requested"""
    # Check if this is a Serena MCP command
    serena_pattern = extract_json_field(request_data, 'tool.server_name') or ''
    if 'serena' not in serena_pattern:
        return {}

    tool_name = extract_json_field(request_data, 'tool.tool_name') or ''

    # Load command mappings from config
    config_path = Path(__file__).parent.parent.parent / "config" / "command_mappings.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
            serena_commands = config.get('serena', {}).get('mcp_commands', {})
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded if config not available
        serena_commands = {
            'find_symbol': 'serena find',
            'replace_symbol_body': 'serena replace',
            'get_symbols_overview': 'serena overview',
            'search_for_pattern': 'serena search',
            'restart_language_server': 'serena restart',
            'write_memory': 'serena memory write',
            'read_memory': 'serena memory read',
            'list_memories': 'serena memory list',
            'activate_project': 'serena project activate',
            'switch_modes': 'serena mode'
        }

    if tool_name in serena_commands:
        cli_command = serena_commands[tool_name]
        log_to_file(f"📚 Mapping Serena MCP tool '{tool_name}' to CLI command: {cli_command}")

        # Add intelligent context hints
        hints = {
            'find_symbol': "Tip: Use wildcards for flexible symbol search",
            'replace_symbol_body': "Tip: Preview changes before replacing",
            'search_for_pattern': "Tip: Use regex for powerful pattern matching"
        }

        if tool_name in hints:
            log_to_file(f"💡 {hints[tool_name]}")

        return {
            'command': cli_command,
            'tool': tool_name,
            'context': 'serena_mcp_integration'
        }

    return {}


def run_claude_flow_mcp_command(request_data: dict[str, Any]) -> dict[str, Any]:
    """Run Claude Flow MCP command if requested"""
    # Check if this is a Claude Flow MCP command
    flow_pattern = extract_json_field(request_data, 'tool.server_name') or ''
    if 'claude-flow' not in flow_pattern:
        return {}

    tool_name = extract_json_field(request_data, 'tool.tool_name') or ''

    # Load command mappings from config
    config_path = Path(__file__).parent.parent.parent / "config" / "command_mappings.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
            flow_commands = config.get('claude_flow', {}).get('mcp_commands', {})
            hints = config.get('claude_flow', {}).get('hints', {})
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded if config not available
        flow_commands = {
            'swarm_init': 'npx claude-flow@alpha swarm init',
            'agent_spawn': 'npx claude-flow@alpha agent spawn',
            'task_orchestrate': 'npx claude-flow@alpha task orchestrate',
            'swarm_status': 'npx claude-flow@alpha swarm status',
            'memory_usage': 'npx claude-flow@alpha memory',
            'neural_train': 'npx claude-flow@alpha neural train',
            'github_swarm': 'npx claude-flow@alpha github swarm',
            'repo_analyze': 'npx claude-flow@alpha github analyze',
            'workflow_create': 'npx claude-flow@alpha workflow create',
            'benchmark_run': 'npx claude-flow@alpha benchmark',
            'daa_agent_create': 'npx claude-flow@alpha daa create',
            'sparc_mode': 'npx claude-flow@alpha sparc'
        }
        hints = {
            'swarm_init': "🧠 Auto-selecting optimal topology based on task complexity",
            'agent_spawn': "🤖 Spawning specialized agent with cognitive patterns",
            'task_orchestrate': "🎯 Breaking down complex task for parallel execution",
            'neural_train': "🧠 Training neural patterns for improved coordination"
        }

    if tool_name in flow_commands:
        cli_command = flow_commands[tool_name]
        log_to_file(f"🐝 Mapping Claude Flow MCP tool '{tool_name}' to CLI command: {cli_command}")

        # Extract parameters for smart command building
        params = extract_json_field(request_data, 'tool.parameters') or {}

        # Build intelligent command with parameters
        if params:
            param_str = ' '.join([f'--{k} {v}' for k, v in params.items() if v is not None])
            cli_command = f"{cli_command} {param_str}"

        # Add intelligent context hints
        if tool_name in hints:
            log_to_file(f"💡 {hints[tool_name]}")

        return {
            'command': cli_command,
            'tool': tool_name,
            'context': 'claude_flow_mcp_integration',
            'parameters': params
        }

    return {}


def detect_complex_task_and_spawn_swarm(
    request_data: dict[str, Any],
    hook_type: str,
    cache_key_prefix: str = "swarm_detection"
) -> dict[str, Any]:
    """
    Detect complex tasks that benefit from swarm orchestration
    """
    # Check cache first
    cache_key = f"{cache_key_prefix}_{hook_type}_{hash(str(request_data))}"
    cached_result = claude_flow_cache.get(cache_key)
    if cached_result and isinstance(cached_result, dict):
        return cached_result

    # Complex task indicators
    indicators = {
        'multi_file': False,
        'multi_component': False,
        'needs_research': False,
        'needs_testing': False,
        'needs_deployment': False,
        'complexity_score': 0
    }

    # Analyze request for complexity indicators
    if hook_type == 'pre-task':
        task_desc = extract_json_field(request_data, 'description') or ''

        # Multi-file operations
        if any(word in task_desc.lower() for word in ['multiple', 'all', 'entire', 'whole', 'across']):
            indicators['multi_file'] = True
            indicators['complexity_score'] += 2

        # Multi-component tasks
        if any(word in task_desc.lower() for word in ['frontend', 'backend', 'database', 'api', 'ui']):
            indicators['multi_component'] = True
            indicators['complexity_score'] += 3

        # Research tasks
        if any(word in task_desc.lower() for word in ['research', 'analyze', 'investigate', 'explore']):
            indicators['needs_research'] = True
            indicators['complexity_score'] += 2

        # Testing tasks
        if any(word in task_desc.lower() for word in ['test', 'verify', 'validate', 'check']):
            indicators['needs_testing'] = True
            indicators['complexity_score'] += 2

        # Deployment tasks
        if any(word in task_desc.lower() for word in ['deploy', 'release', 'publish', 'ship']):
            indicators['needs_deployment'] = True
            indicators['complexity_score'] += 3

    # Recommend swarm if complexity score is high
    recommendation = {
        'should_use_swarm': indicators['complexity_score'] >= 4,
        'recommended_agents': [],
        'topology': 'mesh',
        'indicators': indicators,
        'recommend_swarm': indicators['complexity_score'] >= 4,
        'complexity_score': indicators['complexity_score']
    }

    if recommendation['should_use_swarm']:
        # Build agent recommendations
        if indicators['multi_component']:
            recommendation['recommended_agents'].extend(['architect', 'coder', 'analyst'])
            recommendation['topology'] = 'hierarchical'

        if indicators['needs_research']:
            recommendation['recommended_agents'].append('researcher')

        if indicators['needs_testing']:
            recommendation['recommended_agents'].append('tester')

        if indicators['needs_deployment']:
            recommendation['recommended_agents'].append('coordinator')

        # Ensure we have a balanced team
        if len(recommendation['recommended_agents']) < 3:
            recommendation['recommended_agents'].append('optimizer')

        log_to_file(f"🧠 Complex task detected! Recommending swarm with {len(recommendation['recommended_agents'])} agents")
        log_to_file(f"   Complexity score: {indicators['complexity_score']}/10")
        log_to_file(f"   Recommended topology: {recommendation['topology']}")

    # Cache the result
    claude_flow_cache.set(cache_key, recommendation, ttl=300)

    return recommendation


def integrate_claude_flow_memory(
    operation: str,
    key: str,
    value: Any | None = None,
    namespace: str = "default"
) -> Any | None:
    """
    Integrate with Claude Flow's persistent memory system
    """
    try:
        if operation == "store":
            # Store in persistent memory
            cmd = [
                "npx", "claude-flow@alpha", "memory", "store",
                "--key", f"{namespace}/{key}",
                "--value", json.dumps(value) if value else "{}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                log_to_file(f"💾 Stored in Claude Flow memory: {namespace}/{key}")
                return True
            else:
                log_to_file(f"❌ Failed to store in memory: {result.stderr}")
                return False

        elif operation == "retrieve":
            # Retrieve from persistent memory
            cmd = [
                "npx", "claude-flow@alpha", "memory", "get",
                "--key", f"{namespace}/{key}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return result.stdout
            else:
                return None

        elif operation == "list":
            # List memory keys
            cmd = [
                "npx", "claude-flow@alpha", "memory", "list",
                "--namespace", namespace
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return []

    except Exception as e:
        log_to_file(f"❌ Memory operation failed: {e}")
        return None


def detect_github_repository_context(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Detect if we're working with a GitHub repository and extract context
    """
    context = {
        'is_github_repo': False,
        'repo_path': None,
        'remote_url': None,
        'current_branch': None,
        'has_uncommitted_changes': False,
        'owner': None,
        'repo': None
    }

    # Check if we're in a git repository
    try:
        # Get repository root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            check=False
        )

        if result.returncode == 0:
            context['is_github_repo'] = True
            context['repo_path'] = result.stdout.strip()

            # Get remote URL
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                cwd=context['repo_path'],
                check=False
            )

            if remote_result.returncode == 0:
                context['remote_url'] = remote_result.stdout.strip()

                # Extract owner and repo from URL
                import re
                match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', context['remote_url'])
                if match:
                    context['owner'] = match.group(1)
                    context['repo'] = match.group(2)

            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=context['repo_path'],
                check=False
            )

            if branch_result.returncode == 0:
                context['current_branch'] = branch_result.stdout.strip()

            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=context['repo_path'],
                check=False
            )

            if status_result.returncode == 0 and status_result.stdout.strip():
                context['has_uncommitted_changes'] = True

    except Exception as e:
        log_to_file(f"⚠️ Error detecting GitHub context: {e}")

    return context


def recommend_github_swarm_orchestration(
    github_context: dict[str, Any],
    task_context: dict[str, Any]
) -> dict[str, Any]:
    """
    Recommend GitHub-specific swarm orchestration based on context
    """
    recommendations = {
        'recommended': False,
        'swarm_type': None,
        'suggested_agents': [],
        'workflow': []
    }

    if not github_context.get('is_github_repo'):
        return recommendations

    # Get task description from task_context
    task_description = task_context.get('command', '') or task_context.get('file_path', '')

    # Analyze task for GitHub operations
    github_keywords = {
        'pr': ['pull request', 'pr', 'merge', 'review'],
        'issue': ['issue', 'bug', 'feature request', 'ticket'],
        'release': ['release', 'tag', 'version', 'deploy'],
        'maintenance': ['cleanup', 'refactor', 'update dependencies', 'maintenance']
    }

    task_lower = str(task_description).lower()

    for swarm_type, keywords in github_keywords.items():
        if any(keyword in task_lower for keyword in keywords):
            recommendations['recommended'] = True
            recommendations['swarm_type'] = swarm_type

            # Build agent recommendations
            if swarm_type == 'pr':
                recommendations['suggested_agents'] = [
                    'pr-reviewer',
                    'test-runner',
                    'merge-coordinator'
                ]
                recommendations['workflow'] = [
                    'analyze_pr_changes',
                    'run_tests',
                    'review_code',
                    'suggest_improvements',
                    'coordinate_merge'
                ]

            elif swarm_type == 'issue':
                recommendations['suggested_agents'] = [
                    'issue-triager',
                    'bug-investigator',
                    'solution-architect'
                ]
                recommendations['workflow'] = [
                    'triage_issue',
                    'investigate_root_cause',
                    'propose_solution',
                    'create_implementation_plan'
                ]

            elif swarm_type == 'release':
                recommendations['suggested_agents'] = [
                    'release-coordinator',
                    'changelog-generator',
                    'deployment-manager'
                ]
                recommendations['workflow'] = [
                    'prepare_release_branch',
                    'generate_changelog',
                    'run_release_tests',
                    'create_release_tag',
                    'deploy_release'
                ]

            elif swarm_type == 'maintenance':
                recommendations['suggested_agents'] = [
                    'dependency-updater',
                    'code-analyzer',
                    'refactor-specialist'
                ]
                recommendations['workflow'] = [
                    'analyze_codebase',
                    'identify_improvements',
                    'update_dependencies',
                    'refactor_code',
                    'run_comprehensive_tests'
                ]

            log_to_file(f"🐙 GitHub swarm recommended: {swarm_type}")
            log_to_file(f"   Agents: {', '.join(recommendations['suggested_agents'])}")

            break

    return recommendations


def initialize_github_swarm(
    swarm_type: str,
    repo_path: str,
    agents: list[str]
) -> dict[str, Any]:
    """
    Initialize a GitHub-specific swarm with the Claude Flow GitHub integration
    """
    try:
        # Build the command
        cmd = [
            "npx", "claude-flow@alpha", "github", "swarm",
            "--type", swarm_type,
            "--repo", repo_path,
            "--agents", str(len(agents))
        ]

        # Add agent types
        for agent in agents:
            cmd.extend(["--agent-type", agent])

        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            log_to_file(f"✅ GitHub swarm initialized: {swarm_type}")

            # Parse the output for swarm details
            try:
                swarm_details = json.loads(result.stdout)
                return {
                    'success': True,
                    'swarm_id': swarm_details.get('swarm_id'),
                    'agents': swarm_details.get('agents', []),
                    'status': 'initialized'
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'output': result.stdout,
                    'status': 'initialized'
                }
        else:
            log_to_file(f"❌ Failed to initialize GitHub swarm: {result.stderr}")
            return {
                'success': False,
                'error': result.stderr
            }

    except Exception as e:
        log_to_file(f"❌ Error initializing GitHub swarm: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_claude_flow_command(command_parts: list[str]) -> tuple[int, str, str]:
    """
    Run a Claude Flow command with circuit breaker and retry logic
    """
    # Get appropriate circuit breaker
    breaker = circuit_breakers.get('claude-flow', circuit_breakers['default'])

    if not breaker.can_execute():
        log_to_file("❌ Claude Flow circuit breaker is OPEN - skipping command")
        return 1, "", "Circuit breaker open"

    def execute_command():
        cmd = ["npx", "claude-flow@alpha"] + command_parts

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")

        return result

    try:
        # Execute with retry
        result = retry_mechanism.execute_with_retry(execute_command)
        breaker.record_success()
        return result.returncode, result.stdout, result.stderr

    except Exception as e:
        breaker.record_failure()
        log_to_file(f"❌ Claude Flow command failed: {e}")
        return 1, "", str(e)


async def run_claude_flow_command_async(command_parts: list[str]) -> tuple[int, str, str]:
    """
    Run a Claude Flow command asynchronously with circuit breaker
    """
    # Get appropriate circuit breaker
    breaker = circuit_breakers.get('claude-flow', circuit_breakers['default'])

    if not breaker.can_execute():
        log_to_file("❌ Claude Flow circuit breaker is OPEN - skipping async command")
        return 1, "", "Circuit breaker open"

    try:
        cmd = ["npx", "claude-flow@alpha"] + command_parts

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Async command failed: {stderr.decode()}")

        breaker.record_success()
        return process.returncode, stdout.decode(), stderr.decode()

    except Exception as e:
        breaker.record_failure()
        log_to_file(f"❌ Claude Flow async command failed: {e}")
        return 1, "", str(e)


def run_neural_training(training_data: dict[str, Any]) -> dict[str, Any]:
    """
    Run neural network training with Claude Flow WASM
    """
    try:
        pattern_type = training_data.get('pattern_type', 'coordination')
        epochs = training_data.get('epochs', 100)
        model_name = training_data.get('model_name', 'auto-generated')
        
        cmd = [
            "npx", "claude-flow@alpha", "neural", "train",
            "--pattern-type", pattern_type,
            "--epochs", str(epochs),
            "--model-name", model_name,
            "--real-time-monitoring", "true"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            log_to_file(f"🧠 Neural training started: {model_name}")
            return {
                'success': True,
                'model_name': model_name,
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        log_to_file(f"❌ Neural training failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_memory_operations(operation: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Run memory operations with enhanced persistence
    """
    try:
        if operation == "backup":
            cmd = [
                "npx", "claude-flow@alpha", "memory", "backup",
                "--destination", params.get('destination', './backups/auto-backup')
            ]
        elif operation == "search":
            cmd = [
                "npx", "claude-flow@alpha", "memory", "search",
                "--pattern", params.get('pattern', '*'),
                "--namespace", params.get('namespace', 'default'),
                "--limit", str(params.get('limit', 10))
            ]
        elif operation == "sync":
            cmd = [
                "npx", "claude-flow@alpha", "memory", "sync",
                "--force", str(params.get('force', False)).lower()
            ]
        else:
            return {'success': False, 'error': f'Unknown memory operation: {operation}'}
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def run_daa_operations(operation: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Run DAA (Dynamic Agent Architecture) operations
    """
    try:
        if operation == "create_agent":
            cmd = [
                "npx", "claude-flow@alpha", "daa", "create",
                "--id", params.get('agent_id', 'auto'),
                "--cognitive-pattern", params.get('pattern', 'adaptive'),
                "--enable-memory", str(params.get('enable_memory', True)).lower()
            ]
        elif operation == "adapt_agent":
            cmd = [
                "npx", "claude-flow@alpha", "daa", "adapt",
                "--agent-id", params.get('agent_id'),
                "--feedback", params.get('feedback', ''),
                "--performance-score", str(params.get('score', 0.5))
            ]
        elif operation == "knowledge_share":
            cmd = [
                "npx", "claude-flow@alpha", "daa", "knowledge-share",
                "--source", params.get('source_agent'),
                "--targets", ','.join(params.get('target_agents', []))
            ]
        else:
            return {'success': False, 'error': f'Unknown DAA operation: {operation}'}
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def run_performance_monitoring(metrics_type: str = "all") -> dict[str, Any]:
    """
    Run performance monitoring and bottleneck analysis
    """
    try:
        cmd = [
            "npx", "claude-flow@alpha", "performance", "report",
            "--metrics", metrics_type,
            "--format", "json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            try:
                metrics = json.loads(result.stdout)
                
                # Check for performance issues
                if metrics.get('response_time', 0) > 1000:  # 1 second
                    log_to_file("⚠️ High response time detected")
                
                if metrics.get('memory_usage', 0) > 500 * 1024 * 1024:  # 500MB
                    log_to_file("⚠️ High memory usage detected")
                
                return {
                    'success': True,
                    'metrics': metrics
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'output': result.stdout
                }
        else:
            return {
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def run_workflow_automation(workflow_type: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Run workflow automation with Claude Flow
    """
    try:
        if workflow_type == "create":
            cmd = [
                "npx", "claude-flow@alpha", "workflow", "create",
                "--id", params.get('workflow_id', 'auto'),
                "--name", params.get('name', 'Automated Workflow'),
                "--steps", json.dumps(params.get('steps', []))
            ]
        elif workflow_type == "execute":
            cmd = [
                "npx", "claude-flow@alpha", "workflow", "execute",
                "--workflow-id", params.get('workflow_id'),
                "--parallel", str(params.get('parallel', True)).lower()
            ]
        else:
            return {'success': False, 'error': f'Unknown workflow type: {workflow_type}'}
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Export main components
__all__ = [
    'run_serena_mcp_command',
    'run_claude_flow_mcp_command',
    'detect_complex_task_and_spawn_swarm',
    'integrate_claude_flow_memory',
    'detect_github_repository_context',
    'recommend_github_swarm_orchestration',
    'initialize_github_swarm',
    'run_claude_flow_command',
    'run_claude_flow_command_async',
    'claude_flow_cache',
    # Advanced Claude Flow features
    'run_neural_training',
    'run_memory_operations',
    'run_daa_operations',
    'run_performance_monitoring',
    'run_workflow_automation'
]
