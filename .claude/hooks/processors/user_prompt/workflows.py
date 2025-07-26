#!/usr/bin/env python3
"""
Workflow orchestration functions for user prompt processing
"""

import json
import logging
import time
from typing import Any

# MCP tool execution removed - hooks now return instructions only
from .process_management import ProcessManager

# Constants
CONSULTATION_TIMEOUT_SECONDS = 120


def create_zen_consultation_task(prompt, mcp_tools, project_context):
    """Create a task object for Zen consultation"""
    return {
        'prompt': prompt,
        'mcp_tools': mcp_tools,
        'project_context': project_context,
        'timestamp': time.time()
    }


def run_zen_consultation_functional(zen_task, prompt_analysis: dict[str, Any], logger, process_manager: ProcessManager):
    """
    Generate instructions for Zen consultation (no direct execution)
    """
    workflow = prompt_analysis.get('suggested_workflow', 'chat')

    if logger:
        logger.info(f"Generating Zen consultation instructions for workflow: {workflow}")

    # Prepare the consultation parameters
    consultation_params = {
        'prompt': zen_task['prompt'],
        'model': 'anthropic/claude-opus-4',  # Default to best model
        'thinking_mode': 'high' if prompt_analysis.get('complexity') == 'high' else 'medium',
        'use_websearch': True
    }

    # Add workflow-specific parameters
    if workflow == 'thinkdeep':
        consultation_params.update({
            'step': 'Initial analysis',
            'step_number': 1,
            'total_steps': 3,
            'next_step_required': True,
            'findings': 'Starting investigation'
        })
    elif workflow == 'debug':
        consultation_params.update({
            'confidence': 'exploring'
        })
    elif workflow == 'codereview':
        consultation_params.update({
            'review_type': 'full',
            'severity_filter': 'all'
        })

    # 🚨 CRITICAL: Return instructions that STRONGLY recommend Task() execution WITH THINKING KEYWORDS
    # Determine thinking keywords based on workflow complexity
    workflow_complexity = 'high' if workflow in ['thinkdeep', 'analyze', 'debug'] else 'medium'
    workflow_thinking = get_thinking_keywords_for_complexity(workflow_complexity)
    main_keyword = workflow_thinking['primary'][0]
    
    instructions = f"""### 🚨 MANDATORY: {main_keyword.title()} About Using Task() for Zen Consultation

**🎯 CRITICAL INSTRUCTION**: You MUST **{main_keyword}** and use the Task() tool to execute Zen consultation!

**REQUIRED PATTERN** - Think super hard about this execution:
```
Task("Please use mcp__zen__{workflow} tool with the following parameters: {json.dumps(consultation_params, indent=2)}")
```

**🚨 WHY YOU MUST {main_keyword.upper()} ABOUT Task() EXECUTION**:
- ✅ Enables **parallel execution** with other operations (think deeply about efficiency)
- ✅ Provides **expert analysis and validation** beyond Claude Code's capabilities (megathink required)
- ✅ **Systematic approach** ensures thorough investigation (think intensely about methodology)
- ✅ **Batch operations** - combine with file reads, bash commands, etc. (ultrathink about coordination)
- ✅ **Coordination** with swarm agents for comprehensive analysis (think super hard about collaboration)

**🔥 BATCH WITH OTHER OPERATIONS - Think Very Hard About Efficiency**: 
Combine your Task() call with file operations, bash commands, and swarm initialization in a SINGLE message for maximum efficiency! Think longer about optimization opportunities.

**Workflow**: {workflow} | **Tool**: `mcp__zen__{workflow}` | **Confidence**: 95% | **Thinking Mode**: {main_keyword}"""

    return {
        'success': True,
        'workflow': workflow,
        'output': instructions,
        'consultation_params': consultation_params
    }


def run_claude_flow_swarm_orchestration(prompt: str, swarm_analysis: dict[str, Any], logger, process_manager: ProcessManager):
    """
    Generate instructions for Claude Flow swarm orchestration (no direct execution)
    """
    if logger:
        logger.info("Generating Claude Flow swarm orchestration instructions")

    # Prepare swarm parameters
    topology = swarm_analysis.get('suggested_topology', 'hierarchical')
    max_agents = swarm_analysis.get('estimated_agents', 3)
    
    # Determine agent types based on task
    agent_types = ['coordinator', 'researcher', 'coder', 'analyst', 'tester']
    agents_to_spawn = agent_types[:max_agents]

    # Generate orchestration instructions
    instructions = f"""### 🐝 Claude Flow Swarm Orchestration

**Task**: {prompt[:200]}{"..." if len(prompt) > 200 else ""}
**Complexity**: HIGH - Requires coordinated execution
**Recommended Agents**: {max_agents}

#### Step 1: Initialize Swarm
```
Tool: mcp__claude-flow__swarm_init
Parameters: {{
  "topology": "{topology}",
  "maxAgents": {max_agents},
  "strategy": "balanced"
}}
```

#### Step 2: Spawn Specialized Agents
Use the Task tool to spawn the following agents in PARALLEL:

"""

    # Add agent spawning instructions
    agent_prompts = {
        'coordinator': "You are the Coordinator agent. Your role is to track overall progress and ensure integration between components.",
        'researcher': "You are the Researcher agent. Your role is to analyze requirements and gather necessary information.",
        'coder': "You are the Coder agent. Your role is to implement the core functionality with clean, efficient code.",
        'analyst': "You are the Analyst agent. Your role is to design data models and system architecture.",
        'tester': "You are the Tester agent. Your role is to ensure comprehensive test coverage and quality."
    }

    for i, agent_type in enumerate(agents_to_spawn, 1):
        instructions += f"""{i}. **{agent_type.capitalize()} Agent**
   ```
   Task("{agent_prompts.get(agent_type, 'Specialized agent')}
   
   MANDATORY COORDINATION:
   1. START: Run `npx claude-flow@alpha hooks pre-task --description \"{agent_type} starting\"`
   2. DURING: After EVERY file operation, run `npx claude-flow@alpha hooks post-edit --file \"[file]\"`
   3. SHARE: Use `npx claude-flow@alpha hooks notification --message \"[decision]\"`
   4. END: Run `npx claude-flow@alpha hooks post-task --task-id \"{agent_type}\"`
   
   Your specific task: [Assign based on main task requirements]")
   ```

"""

    instructions += f"""#### Step 3: Track Progress
```
Tool: mcp__claude-flow__memory_usage
Parameters: {{
  "action": "store",
  "key": "swarm/initialization",
  "value": {{
    "prompt": "{prompt[:100]}...",
    "agents": {json.dumps(agents_to_spawn)},
    "timestamp": "{{current_time}}"
  }}
}}
```

#### Step 4: Monitor Execution
Use `mcp__claude-flow__swarm_status` periodically to check progress.

**Note**: All operations should be executed in a single BatchTool message for maximum efficiency."""

    return {
        'success': True,
        'spawned_agents': agents_to_spawn,
        'output': instructions
    }


def run_github_claude_flow_orchestration(prompt: str, github_analysis: dict[str, Any], logger, process_manager: ProcessManager):
    """
    Generate instructions for GitHub-specific Claude Flow orchestration (no direct execution)
    """
    if logger:
        logger.info("Generating GitHub Claude Flow orchestration instructions")

    # GitHub-specific agent configurations
    github_agents = ['repo-manager', 'pr-reviewer', 'issue-triager']
    operations = github_analysis.get('suggested_operations', [])

    instructions = f"""### 🔗 GitHub-Specific Swarm Orchestration

**Task**: {prompt[:200]}{"..." if len(prompt) > 200 else ""}
**Focus**: GitHub repository management and collaboration

#### Step 1: Initialize GitHub-Aware Swarm
```
Tool: mcp__claude-flow__swarm_init
Parameters: {{
  "topology": "hierarchical",
  "maxAgents": 5,
  "strategy": "specialized"
}}
```

#### Step 2: Spawn GitHub Specialist Agents
Use the Task tool to spawn these GitHub-focused agents:

"""

    # GitHub agent descriptions
    agent_descriptions = {
        'repo-manager': "You are the Repository Manager. Focus on repository structure, dependencies, and overall health.",
        'pr-reviewer': "You are the PR Reviewer. Analyze pull requests, suggest improvements, and ensure code quality.",
        'issue-triager': "You are the Issue Triager. Categorize issues, assign priorities, and suggest resolutions."
    }

    for i, agent in enumerate(github_agents, 1):
        instructions += f"""{i}. **GitHub {agent.replace('-', ' ').title()}**
   ```
   Task("{agent_descriptions[agent]}
   
   MANDATORY: Use coordination hooks and GitHub MCP tools.
   Coordinate through npx claude-flow@alpha hooks.")
   ```

"""

    # Add suggested operations
    if operations:
        instructions += "#### Step 3: Execute GitHub Operations\n"
        instructions += "Based on the task, consider using these GitHub MCP tools:\n\n"
        for op in operations:
            instructions += f"- `mcp__github__{op}`\n"

    instructions += """
#### Step 4: Coordinate Results
Store findings and coordinate between agents using `mcp__claude-flow__memory_usage`.

**Note**: Execute all operations in parallel using BatchTool for efficiency."""

    return {
        'success': True,
        'spawned_agents': github_agents,
        'operations': operations,
        'output': instructions
    }


def run_github_mcp_integration(prompt: str, smart_triggers: dict[str, Any], logger, process_manager: ProcessManager):
    """
    Generate instructions for GitHub MCP integration (no direct execution)
    """
    if not smart_triggers.get('github_mcp'):
        return None

    if logger:
        logger.info("Generating GitHub MCP integration instructions")

    # Analyze what GitHub operations are needed
    prompt_lower = prompt.lower()
    instructions = "### 🔧 GitHub MCP Operations\n\n"

    if 'list issues' in prompt_lower or 'show issues' in prompt_lower:
        instructions += """**List Issues**:
```
Tool: mcp__github__list_issues
Parameters: {
  "owner": "[repository_owner]",
  "repo": "[repository_name]",
  "state": "open"
}
```\n\n"""

    if 'create pr' in prompt_lower or 'open pr' in prompt_lower:
        instructions += """**Create Pull Request**:
```
Tool: mcp__github__create_pull_request
Parameters: {
  "owner": "[repository_owner]",
  "repo": "[repository_name]",
  "title": "[PR title based on changes]",
  "head": "[feature_branch]",
  "base": "main",
  "body": "[Description of changes]"
}
```\n\n"""

    if 'notifications' in prompt_lower:
        instructions += """**Check Notifications**:
```
Tool: mcp__github__list_notifications
Parameters: {
  "filter": "default"
}
```\n\n"""

    instructions += "**Note**: Replace placeholders with actual values based on context."

    return [{
        'operation': 'github_instructions',
        'success': True,
        'output': instructions
    }]


def run_enhanced_mcp_orchestration(prompt: str, smart_triggers: dict[str, Any], logger, process_manager: ProcessManager):
    """
    Generate instructions for multiple MCP tools based on smart triggers (no direct execution)
    """
    instructions = "### 🛠️ MCP Tools Orchestration\n\n"
    tools_mentioned = []

    # Tavily web search instructions
    if smart_triggers.get('tavily_mcp'):
        if logger:
            logger.info("Adding Tavily web search instructions")
        
        tools_mentioned.append('tavily')
        instructions += """**Web Search with Tavily**:
```
Tool: mcp__tavily-remote__tavily_search
Parameters: {
  "query": "%s",
  "max_results": 5,
  "search_depth": "basic"
}
```

""" % prompt

    # Filesystem operations instructions
    if smart_triggers.get('filesystem_mcp'):
        if logger:
            logger.info("Adding filesystem MCP instructions")
        
        tools_mentioned.append('filesystem')
        instructions += """**Filesystem Operations**:
Consider using these filesystem MCP tools based on your task:
- `mcp__filesystem__read_file` - Read file contents
- `mcp__filesystem__write_file` - Create or overwrite files
- `mcp__filesystem__list_directory` - List directory contents
- `mcp__filesystem__search_files` - Search for files by pattern

"""

    # Playwright browser automation instructions
    if smart_triggers.get('playwright_mcp'):
        if logger:
            logger.info("Adding Playwright browser automation instructions")
        
        tools_mentioned.append('playwright')
        instructions += """**Browser Automation with Playwright**:
```
Tool: mcp__playwright__browser_navigate
Parameters: {
  "url": "[target_url]"
}
```

Additional browser tools available:
- `mcp__playwright__browser_snapshot` - Capture page state
- `mcp__playwright__browser_click` - Click elements
- `mcp__playwright__browser_type` - Type text

"""

    instructions += "**Note**: Execute all operations in parallel when possible for efficiency."

    return {
        'tools_used': tools_mentioned,
        'results': {
            'instructions': {
                'success': True,
                'output': instructions
            }
        }
    }


def extract_consultation_data(consultation_result: str, logger: logging.Logger | None) -> dict[str, Any]:
    """Extract structured data from consultation result"""
    try:
        # Try to parse as JSON first
        return json.loads(consultation_result)
    except json.JSONDecodeError:
        # Fallback to text extraction
        return {
            'raw_output': consultation_result,
            'extracted': True
        }


def merge_analysis_with_consultation(result_data: dict[str, Any],
                                   prompt_analysis: dict[str, Any],
                                   additional_context: dict[str, Any]) -> dict[str, Any]:
    """Merge all analysis results"""
    return {
        'prompt_analysis': prompt_analysis,
        'consultation_result': result_data,
        'additional_context': additional_context,
        'timestamp': time.time()
    }


def judge_and_spawn_agents_functional(consultation_result: str, prompt_analysis: dict[str, Any],
                                    mcp_tools: dict[str, Any], logger: logging.Logger | None,
                                    process_manager: ProcessManager) -> dict[str, Any]:
    """
    Judge the consultation result and determine agent spawning strategy
    """
    # Extract data from consultation
    result_data = extract_consultation_data(consultation_result, logger)

    # Merge with prompt analysis
    merged_data = merge_analysis_with_consultation(
        result_data,
        prompt_analysis,
        {'mcp_tools': mcp_tools}
    )

    # Determine judgment
    judgment = {
        'needs_agents': prompt_analysis.get('needs_swarm', False),
        'agent_count': prompt_analysis.get('estimated_agents', 3),
        'coordination_strategy': prompt_analysis.get('suggested_topology', 'hierarchical'),
        'reasoning': prompt_analysis.get('reasoning', []),
        'merged_data': merged_data
    }

    return judgment


def get_thinking_keywords_for_complexity(complexity: str) -> dict[str, list[str]]:
    """
    🚨 CRITICAL: Get appropriate thinking keywords based on task complexity
    Triggers extra reasoning time in Claude Code through strategic keyword placement
    """
    thinking_tiers = {
        'tier1': ['think'],
        'tier2': ['think deeply', 'think about it', 'think a lot', 'think hard', 'think more', 'megathink'],
        'tier3': ['think harder', 'think intensely', 'think longer', 'think really hard', 'think super hard', 'think very hard', 'ultrathink']
    }
    
    if complexity.lower() in ['high', 'complex']:
        return {
            'primary': thinking_tiers['tier3'][:3],  # Use top 3 Tier 3 keywords
            'secondary': thinking_tiers['tier2'][:2],  # Plus some Tier 2
            'basic': thinking_tiers['tier1']
        }
    elif complexity.lower() in ['medium', 'moderate']:
        return {
            'primary': thinking_tiers['tier2'][:3],  # Use top 3 Tier 2 keywords
            'secondary': thinking_tiers['tier1'],
            'basic': thinking_tiers['tier1']
        }
    else:  # low, unknown, etc.
        return {
            'primary': thinking_tiers['tier1'],
            'secondary': thinking_tiers['tier1'],
            'basic': thinking_tiers['tier1']
        }


def generate_coordination_output(judgment: dict[str, Any]) -> str:
    """
    Generate the final coordination output with instructions for Claude
    🚨 INCLUDES STRATEGIC THINKING KEYWORDS to trigger extra reasoning time
    """
    output_lines = []

    # Header
    output_lines.append("## 🎯 Task Coordination Analysis\n")

    # 🚨 CRITICAL: Get thinking keywords based on complexity
    complexity = judgment.get('merged_data', {}).get('prompt_analysis', {}).get('complexity', 'high')
    thinking_keywords = get_thinking_keywords_for_complexity(complexity)
    
    output_lines.append(f"**Task Complexity**: {complexity.upper()}")
    output_lines.append(f"**Confidence**: {judgment.get('merged_data', {}).get('prompt_analysis', {}).get('confidence', 0.5) * 100:.0f}%\n")

    # 🚨 STRATEGIC THINKING KEYWORD PLACEMENT - Tier-based reasoning trigger
    primary_keyword = thinking_keywords['primary'][0]  # Main keyword for this complexity
    output_lines.append(f"### 🚨 MANDATORY: {primary_keyword.title()} About Swarm Coordination\n")
    
    # 🚨 CRITICAL: ALWAYS recommend swarm coordination and Task() usage
    output_lines.append("🚨 **CRITICAL**: You must **think super hard** about this task coordination approach!\n")
    agent_count = judgment.get('agent_count', 6)  # Default to 6 agents
    topology = judgment.get('coordination_strategy', 'hierarchical')
    output_lines.append(f"**Recommended Agents**: {agent_count}")
    output_lines.append(f"**Topology**: {topology}")

    # 🚨 MANDATORY reasoning with embedded thinking keywords
    secondary_keyword = thinking_keywords['secondary'][0] if thinking_keywords['secondary'] else 'think'
    output_lines.append(f"\n**🚨 WHY YOU MUST {secondary_keyword.upper()} ABOUT SWARM COORDINATION**:")
    output_lines.append("- ✅ **Parallel execution** - 2.8-4.4x speed improvement (think about efficiency)")
    output_lines.append("- ✅ **Task() batching** - Combine multiple operations efficiently (think deeply about coordination)")
    output_lines.append("- ✅ **Expert validation** - Beyond Claude Code's native capabilities (megathink required)")
    output_lines.append("- ✅ **Memory coordination** - Persistent context across agents (think intensely about persistence)")
    output_lines.append("- ✅ **Error resilience** - Multiple perspectives prevent mistakes (ultrathink for safety)")

    # 🚨 Strategic keyword placement in approach steps
    output_lines.append(f"\n### 🚨 MANDATORY APPROACH - {thinking_keywords['primary'][1] if len(thinking_keywords['primary']) > 1 else 'Think Harder'} About Parallel Execution:\n")
    output_lines.append("**Step 1**: Initialize swarm with `mcp__claude-flow__swarm_init` (think about topology)")
    output_lines.append("**Step 2**: Spawn ALL agents with `mcp__claude-flow__agent_spawn` (think deeply about batching)")
    output_lines.append("**Step 3**: Use `Task()` tool to spawn agents with coordination instructions (megathink required)")
    output_lines.append("**Step 4**: Batch file operations, bash commands, and TodoWrite in ONE message (think super hard about efficiency)")
    output_lines.append("**Step 5**: Use `mcp__claude-flow__memory_usage` for coordination (ultrathink about persistence)")

    # 🚨 Add workflow suggestion with thinking keywords
    workflow = judgment.get('merged_data', {}).get('prompt_analysis', {}).get('suggested_workflow', 'analyze')
    output_lines.append(f"\n**Suggested Zen Workflow**: `{workflow}` (via Task() tool - think intensely about execution)")
    output_lines.append(f"**CRITICAL**: Use Task() to execute `mcp__zen__{workflow}` for expert analysis (think very hard about approach)")

    # MCP tool recommendations
    mcp_tools = judgment.get('merged_data', {}).get('additional_context', {}).get('mcp_tools', {})
    if mcp_tools:
        output_lines.append("\n### 🔧 Available MCP Tools:\n")
        for server, tools in mcp_tools.items():
            if tools:
                output_lines.append(f"**{server}**: {', '.join(tools[:5])}")

    # Task-specific recommendations
    task_type = judgment.get('merged_data', {}).get('prompt_analysis', {}).get('type', 'general')
    if task_type != 'general':
        output_lines.append(f"\n### 📌 Task Type: {task_type.upper()}\n")

        # Get appropriate thinking keywords for task-specific recommendations
        task_thinking_keywords = thinking_keywords['primary'] + thinking_keywords['secondary']
        
        recommendations = {
            'debugging': [
                f"🚨 MANDATORY: Use Task() to execute `mcp__zen__debug` for systematic investigation ({task_thinking_keywords[0]} about root causes)",
                f"🚨 BATCH: Combine Task() with log reading and error analysis in ONE message ({task_thinking_keywords[1] if len(task_thinking_keywords) > 1 else 'think deeply'} about efficiency)",
                f"🚨 PARALLEL: Use `TodoWrite` to track debugging steps alongside other operations (megathink about coordination)"
            ],
            'testing': [
                f"🚨 MANDATORY: Use Task() to execute `mcp__zen__testgen` for comprehensive test generation ({task_thinking_keywords[0]} about edge cases)",
                f"🚨 BATCH: Combine Task() with file operations and test execution in ONE message ({task_thinking_keywords[1] if len(task_thinking_keywords) > 1 else 'think deeply'} about coverage)",  
                f"🚨 PARALLEL: Consider edge cases through coordinated agent analysis (ultrathink about scenarios)"
            ],
            'research': [
                f"🚨 MANDATORY: Use Task() to execute `mcp__zen__analyze` for deep analysis ({task_thinking_keywords[0]} about methodology)",
                f"🚨 BATCH: Combine Task() with WebSearch and documentation lookup in ONE message ({task_thinking_keywords[1] if len(task_thinking_keywords) > 1 else 'think deeply'} about sources)",
                f"🚨 PARALLEL: Document findings through coordinated memory storage (think super hard about organization)"
            ],
            'documentation': [
                f"🚨 MANDATORY: Use Task() to execute `mcp__zen__docgen` for documentation generation ({task_thinking_keywords[0]} about clarity)",
                f"🚨 BATCH: Combine Task() with file reading and writing in ONE message ({task_thinking_keywords[1] if len(task_thinking_keywords) > 1 else 'think deeply'} about structure)",
                f"🚨 PARALLEL: Follow project standards through coordinated agent review (think intensely about consistency)"
            ]
        }

        if task_type in recommendations:
            output_lines.append("**Specific Recommendations**:")
            for rec in recommendations[task_type]:
                output_lines.append(f"- {rec}")

    # Add indicators if present
    indicators = judgment.get('merged_data', {}).get('prompt_analysis', {}).get('indicators', [])
    if indicators:
        output_lines.append("\n### 🔍 Detected Indicators:\n")
        output_lines.append(', '.join(indicators))

    # 🚨 CRITICAL: Final action prompt with mandatory Task() instructions and thinking keywords
    final_keyword = thinking_keywords['primary'][-1] if thinking_keywords['primary'] else 'think super hard'
    output_lines.append("\n---")
    output_lines.append(f"**🚨 MANDATORY EXECUTION PATTERN - {final_keyword.upper()} ABOUT IMPLEMENTATION**:")
    output_lines.append("1. ALWAYS start with `mcp__claude-flow__swarm_init` (think about topology selection)")
    output_lines.append("2. BATCH ALL operations in ONE message (Task(), TodoWrite, Read, Write, Bash) - think deeply about efficiency")
    output_lines.append("3. Use Task() for ALL Zen consultations - NEVER execute mcp__zen__ tools directly (megathink about delegation)")
    output_lines.append("4. Spawn agents with coordination hooks and memory storage (ultrathink about coordination)")
    
    # Add final strong thinking keyword based on complexity
    complexity_emphasis = {
        'high': 'think super hard',
        'medium': 'think deeply', 
        'low': 'think'
    }.get(complexity.lower(), 'think super hard')
    
    output_lines.append(f"\n**Ready to proceed with MANDATORY swarm coordination and Task() execution - {complexity_emphasis} about every step!**")

    return '\n'.join(output_lines)
