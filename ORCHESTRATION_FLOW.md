# Claude Code Orchestration Flow

This document describes the complete orchestration flow from user prompt to coordinated execution using Claude hooks, Zen consultation, and Claude Flow swarm coordination.

## 🎯 Complete Flow Overview

```
User Prompt
    ↓
UserPromptSubmit Hook (.claude/settings.json)
    ↓
main.py handle_prompt()
    ↓
Prompt Analysis & Complexity Detection
    ↓
Zen Consultation (via MCP tools)
    ↓
Claude Flow Swarm Init (if complex)
    ↓
Agent Spawning with Coordination
    ↓
Pre/Post Tool Hooks (continuous monitoring)
    ↓
Parallel Execution with Hook Coordination
```

## 📁 Key Files

1. **`.claude/settings.json`** - Defines all hooks including UserPromptSubmit
2. **`.claude/hooks/main.py`** - Main orchestrator entry point
3. **`.claude/hooks/processors/user_prompt_main.py`** - Advanced prompt processor
4. **`.claude/hooks/processors/user_prompt/workflows.py`** - Zen & swarm workflows

## 🔄 Detailed Flow Steps

### 1️⃣ User Types Prompt

When user enters a prompt in Claude Code, the UserPromptSubmit hook is triggered.

### 2️⃣ UserPromptSubmit Hook

```json
"UserPromptSubmit": [
    {
        "hooks": [
            {
                "type": "command",
                "command": "python /home/devcontainers/bench/test-game/.claude/hooks/main.py prompt",
                "timeout": 120
            }
        ]
    }
]
```

### 3️⃣ Prompt Analysis

`main.py handle_prompt()` performs:
- Complexity analysis via `analyze_prompt_complexity()`
- Swarm need detection via `detect_claude_flow_swarm_needs()`
- MCP tool availability check
- Project context generation

### 4️⃣ Zen Consultation

The system consults Zen tools to determine the best approach:
```python
consultation_result = run_zen_consultation_functional(
    zen_task, prompt_analysis, logger, process_manager
)
```

This uses MCP Zen tools like:
- `mcp__zen__chat` - For general consultation
- `mcp__zen__thinkdeep` - For complex investigation
- `mcp__zen__debug` - For debugging tasks
- `mcp__zen__codereview` - For code review

### 5️⃣ Claude Flow Orchestration

For complex tasks, initializes swarm coordination:
```python
if swarm_analysis.get('needs_swarm'):
    swarm_result = run_claude_flow_swarm_orchestration(
        prompt, swarm_analysis, logger, process_manager
    )
```

This executes:
- `mcp__claude-flow__swarm_init` - Initialize topology
- `mcp__claude-flow__agent_spawn` - Create specialized agents
- `mcp__claude-flow__task_orchestrate` - Coordinate execution

### 6️⃣ Agent Coordination Instructions

Each spawned agent receives coordination instructions:
```
You are the [Agent Type] agent in a coordinated swarm.

MANDATORY COORDINATION:
1. START: Run `npx claude-flow@alpha hooks pre-task --description "[your task]"`
2. DURING: After EVERY file operation, run `npx claude-flow@alpha hooks post-edit --file "[file]"`
3. MEMORY: Store ALL decisions using `npx claude-flow@alpha hooks notification --message "[decision]"`
4. END: Run `npx claude-flow@alpha hooks post-task --task-id "[task]"`
```

### 7️⃣ Pre/Post Tool Hooks

Continuous monitoring via hooks:

**PreToolUse Hooks:**
- `pre-bash` - Validates commands before execution
- `pre-edit` - Prepares for file operations
- `pre-task` - Ensures Task agents have coordination
- `pre-mcp` - Tracks MCP tool usage

**PostToolUse Hooks:**
- `post-bash` - Processes command results
- `post-edit` - Handles file changes
- `post-task` - Tracks task completion
- `post-mcp` - Records MCP results

### 8️⃣ Parallel Execution

All operations execute in parallel:
- Multiple agents work simultaneously
- Coordination through shared memory
- Progress tracking via hooks
- Real-time status monitoring

## 🛠️ Hook Control Points

### Command Validation (pre-bash)
```python
def handle_pre_bash(json_input):
    command = json_input.get('tool_input', {}).get('command', '')
    # Validate claude-flow commands
    if 'claude-flow' in command:
        logger.info("Claude Flow command detected - ensuring coordination")
```

### Agent Coordination (pre-task)
```python
def handle_pre_task(json_input):
    prompt = json_input.get('tool_input', {}).get('prompt', '')
    # Ensure coordination instructions
    if prompt and 'claude-flow' not in prompt.lower():
        logger.warning("Task agent missing coordination!")
```

### Progress Tracking (notification)
```python
def handle_notification(json_input):
    message = json_input.get('message', '')
    # Share coordination state between agents
```

## 🚀 Example Flow

For prompt: "Build a REST API with auth and tests"

1. **Prompt Hook** analyzes complexity → HIGH
2. **Zen Consultation** suggests thinkdeep workflow
3. **Claude Flow** initializes hierarchical swarm with 5 agents
4. **Agents Spawned**:
   - Architect (system design)
   - Coder (API implementation)
   - Coder (Auth implementation)
   - Analyst (database design)
   - Tester (test suite)
5. **Each Agent** runs coordination hooks:
   - `pre-task` before starting
   - `post-edit` after each file change
   - `notification` to share decisions
   - `post-task` when complete
6. **Orchestrator** monitors all via pre/post hooks
7. **Results** aggregated through shared memory

## 🔧 Configuration

Key environment variables in `.claude/settings.json`:
```json
{
    "env": {
        "CLAUDE_FLOW_HOOKS_ENABLED": "true",
        "CLAUDE_HOOK_CONTEXT_SHARING": "true",
        "CLAUDE_HOOK_PERFORMANCE_MONITORING": "true"
    }
}
```

## 📊 Monitoring & Control

The orchestration provides:
- Real-time progress tracking
- Performance monitoring
- Error handling and recovery
- Token usage optimization
- Parallel execution management
- Coordination state persistence

## 🎯 Benefits

1. **Automated Orchestration** - No manual swarm setup needed
2. **Intelligent Routing** - Right tool for each task
3. **Parallel Execution** - Maximum efficiency
4. **Full Coordination** - All agents stay in sync
5. **Progress Visibility** - Real-time status updates
6. **Error Recovery** - Self-healing workflows

This orchestration ensures every user prompt gets the optimal execution strategy with full coordination and monitoring throughout the process.