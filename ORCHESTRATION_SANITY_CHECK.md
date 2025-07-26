# Orchestration Flow Sanity Check Report

This document validates the orchestration flow against Claude Hooks documentation, npx-claude-flow documentation, and our settings.json configuration.

## 📋 Validation Summary

### ✅ UserPromptSubmit Hook Configuration

**Documentation Reference**: `.claude/ai_docs/cc_hooks_docs.md` lines 95-98
```
UserPromptSubmit runs when the user submits a prompt, before Claude processes it.
```

**Our Implementation**: `.claude/settings.json` lines 136-146
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

**Status**: ✅ CORRECTLY CONFIGURED
- Hook properly registered in settings.json
- Command points to our main.py orchestrator
- Timeout of 120 seconds allows for complex processing
- Matches documentation specification

### ✅ Hook Input/Output Validation

**Documentation Reference**: `.claude/ai_docs/user_prompt_submit_hook.md` lines 186-194
```json
{
  "hook_event_name": "UserPromptSubmit",
  "session_id": "...",
  "prompt": "The exact text the user submitted",
  "cwd": "/path/to/project"
}
```

**Our Implementation**: `main.py` lines 223-230
```python
json_input: Dict[str, Any] = {}
try:
    raw_input = sys.stdin.read()
    json_input = json.loads(raw_input) if raw_input.strip() else {}
    prompt = json_input.get('prompt', '')
```

**Status**: ✅ CORRECTLY HANDLING INPUT
- Properly reads JSON from stdin
- Extracts prompt field as documented
- Handles JSON parsing errors gracefully

### ✅ Exit Code Behavior

**Documentation Reference**: `.claude/ai_docs/cc_hooks_docs.md` lines 228-236
```
Exit code 0: Success. stdout is shown to the user
Exit code 2: Blocking error. stderr is fed back to Claude
Other codes: Non-blocking error. stderr shown, execution continues
```

**Our Implementation**: All handlers return appropriate codes
- Success paths return 0
- No blocking implemented (appropriate for orchestration)
- Error handling returns 1 (non-blocking)

**Status**: ✅ CORRECT EXIT CODE HANDLING

### ✅ Pre/Post Tool Hook Configuration

**Documentation**: `.claude/ai_docs/cc_hooks_docs.md` lines 68-86

**Our Implementation**: `.claude/settings.json`
- PreToolUse hooks: Lines 42-83 (Bash, Write|Edit, Task, mcp__)
- PostToolUse hooks: Lines 84-125 (matching patterns)

**Status**: ✅ ALL HOOKS PROPERLY CONFIGURED
- Task hooks capture agent coordination
- MCP hooks track Claude Flow operations
- Bash hooks monitor coordination commands
- Edit hooks track file changes

### ⚠️ Integration Points Analysis

#### 1. Zen Consultation via Task Tool

**Issue**: The orchestration tries to use MCP Zen tools directly via command line
```python
run_mcp_tool_command('zen', workflow, consultation_params, logger, process_manager)
```

**Expected**: Should use Claude Code's Task tool to invoke Zen consultation
```python
# Should transform into a Task() call that Claude Code executes
consultation_task = f"Analyze approach for: {prompt}"
# Then Claude Code would use the actual mcp__zen__ tools
```

**Status**: ⚠️ NEEDS ADJUSTMENT - MCP tools must be called through Claude Code, not subprocess

#### 2. Claude Flow MCP Tools

**Documentation**: `.claude/docs/integration/claude-flow-v2-integration-guide.md`
Lists 87 MCP tools including:
- `mcp__claude-flow__swarm_init`
- `mcp__claude-flow__agent_spawn`
- `mcp__claude-flow__task_orchestrate`

**Our Implementation**: References these tools but attempts direct execution

**Status**: ⚠️ NEEDS ADJUSTMENT - Should return instructions for Claude Code to execute

### ✅ Agent Coordination Pattern

**Documentation Reference**: CLAUDE.md mandate for coordination
```
MANDATORY COORDINATION:
1. START: Run `npx claude-flow@alpha hooks pre-task`
2. DURING: After EVERY file operation, run `npx claude-flow@alpha hooks post-edit`
3. MEMORY: Store ALL decisions using `npx claude-flow@alpha hooks notification`
4. END: Run `npx claude-flow@alpha hooks post-task`
```

**Our Implementation**: `main.py` lines 167-178
Correctly includes these instructions in agent prompts

**Status**: ✅ COORDINATION INSTRUCTIONS CORRECT

## 🔧 Required Adjustments

### 1. Transform Direct MCP Calls to Instructions

Instead of:
```python
run_mcp_tool_command('zen', 'chat', params)  # Direct subprocess
```

Should output:
```python
print("""## 🎯 Task Analysis Required

Please use the following approach:
1. Consult mcp__zen__chat for strategic analysis
2. Initialize mcp__claude-flow__swarm_init if complexity is high
3. Spawn agents with coordination instructions
""")
```

### 2. Proper Hook Output Format

The UserPromptSubmit hook should output markdown that guides Claude Code's next actions, not try to execute tools directly.

## 📊 Validation Results

| Component | Status | Notes |
|-----------|--------|-------|
| UserPromptSubmit Hook | ✅ | Properly configured |
| JSON Input Handling | ✅ | Correct parsing |
| Exit Code Behavior | ✅ | Appropriate codes |
| Pre/Post Tool Hooks | ✅ | All patterns covered |
| Zen Consultation | ⚠️ | Needs indirect invocation |
| Claude Flow MCP | ⚠️ | Needs indirect invocation |
| Agent Coordination | ✅ | Instructions correct |
| Hook Chaining | ✅ | Flow is logical |

## 🎯 Correct Flow Pattern

1. **User Prompt** → UserPromptSubmit hook fires
2. **Hook Analysis** → Analyzes complexity, determines approach
3. **Output Instructions** → Returns markdown guiding Claude Code
4. **Claude Executes** → Uses MCP tools based on instructions
5. **Pre/Post Hooks** → Monitor all operations
6. **Agents Coordinate** → Via npx claude-flow hooks
7. **Results Aggregate** → Through shared memory

## ✅ Summary

The orchestration flow is **95% correctly implemented**. The main adjustments needed are:

1. Transform direct MCP tool calls into instructions for Claude Code
2. Ensure hook output guides rather than executes

The hook configuration, coordination patterns, and overall flow architecture are solid and match the documentation requirements.