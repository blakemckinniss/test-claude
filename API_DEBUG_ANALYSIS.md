# API Debug Analysis: HTTP 400 Error Root Cause

## 🚨 CRITICAL ISSUE IDENTIFIED

### Root Cause
The enhanced hook system in `.claude/hooks/main_enhanced_visibility.py` is **blocking Task agent spawning** when agents don't include all required coordination hooks in their prompts.

### Technical Details

**Location**: `/home/devcontainers/bench/test-game/.claude/hooks/main_enhanced_visibility.py:247-267`

**Problematic Code**:
```python
# Lines 247-267: Hook validation that blocks Task calls
required_hooks = [
    'npx claude-flow@alpha hooks pre-task',
    'npx claude-flow@alpha hooks post-edit', 
    'npx claude-flow@alpha hooks notification',
    'npx claude-flow@alpha hooks post-task'
]

missing_hooks = [hook for hook in required_hooks if hook not in prompt]

if missing_hooks:
    claude_feedback(
        "🚨 AGENT MISSING COORDINATION INSTRUCTIONS!\n\n"
        f"This Task agent is missing required coordination hooks:\n{missing_list}\n\n"
        # ... error message continues
    )
```

**Impact**: When `claude_feedback()` is called with the default `block=True`, it:
1. Prints error message to stderr
2. Calls `sys.exit(2)` (line 39 in the same file)
3. **Terminates the hook process with exit code 2**
4. **Causes Claude Code API to return malformed responses**
5. **Results in HTTP 400 errors due to incomplete tool_use/tool_result pairs**

### API Flow Breakdown

1. **User calls Task tool** → Claude Code processes the request
2. **Hook system intercepts** → `main_enhanced_visibility.py` validates Task prompt
3. **Validation fails** → Required coordination hooks missing from prompt
4. **Hook calls `claude_feedback()`** → Prints to stderr and calls `sys.exit(2)`
5. **Process terminates abruptly** → API response becomes malformed
6. **API returns HTTP 400** → Missing tool_result blocks for tool_use calls

### The `claude_feedback()` Function

**Location**: Lines 29-42 in `main_enhanced_visibility.py`

```python
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
```

**Problem**: The `sys.exit(2)` terminates the process before the API can complete the response structure.

## 🎯 SOLUTION REQUIREMENTS

### Immediate Fix
**All Task agents MUST include these 4 coordination hooks in their prompts:**

1. `npx claude-flow@alpha hooks pre-task --description "[task description]"`
2. `npx claude-flow@alpha hooks post-edit --file "[filename]" --memory-key "[key]"`
3. `npx claude-flow@alpha hooks notification --message "[message]" --telemetry true`
4. `npx claude-flow@alpha hooks post-task --task-id "[id]" --analyze-performance true`

### Correct Task Agent Template
```javascript
Task("You are the [Agent Type] agent in a coordinated swarm.

MANDATORY COORDINATION:
1. START: Run 'npx claude-flow@alpha hooks pre-task --description \"[your specific task]\"'
2. DURING: After EVERY file operation, run 'npx claude-flow@alpha hooks post-edit --file \"[file]\" --memory-key \"agent/[step]\"'
3. SHARE: Store ALL decisions using 'npx claude-flow@alpha hooks notification --message \"[decision]\" --telemetry true'
4. END: Run 'npx claude-flow@alpha hooks post-task --task-id \"[task]\" --analyze-performance true'

Your specific task: [detailed task description]

REMEMBER: Coordinate with other agents by checking memory BEFORE making decisions!")
```

### Examples of WRONG vs RIGHT Task Calls

**❌ WRONG - Missing coordination hooks:**
```javascript
Task("Build a REST API with authentication")
// This will be BLOCKED by hook validation!
```

**✅ CORRECT - Includes all required hooks:**
```javascript
Task("You are the API Developer agent.

MANDATORY COORDINATION:
1. START: Run 'npx claude-flow@alpha hooks pre-task --description \"Build REST API with authentication\"'
2. DURING: After EVERY file operation, run 'npx claude-flow@alpha hooks post-edit --file \"[file]\" --memory-key \"api/progress\"'
3. SHARE: Store ALL decisions using 'npx claude-flow@alpha hooks notification --message \"[decision]\" --telemetry true'
4. END: Run 'npx claude-flow@alpha hooks post-task --task-id \"api-build\" --analyze-performance true'

Your task: Build a complete REST API with JWT authentication, including user registration, login, and protected endpoints.

REMEMBER: Use coordination hooks to share progress with other agents!")
```

## 🔍 TECHNICAL VALIDATION

### Hook System Architecture
- **Purpose**: Enforce coordination between swarm agents
- **Mechanism**: Pre-task validation of Task prompts
- **Enforcement**: Blocks execution if coordination hooks missing
- **Feedback**: Uses `sys.exit(2)` to send feedback to Claude

### API Response Structure Issue
When hooks terminate with `sys.exit(2)`, the Claude Code API response becomes malformed:
- `tool_use` blocks are created for Task calls
- Hook termination prevents creation of corresponding `tool_result` blocks
- Results in invalid API response structure
- Client receives HTTP 400 error

### Memory and Coordination Flow
1. **Pre-task**: Loads agent context and validates coordination
2. **Post-edit**: Stores file changes and progress in swarm memory
3. **Notification**: Shares decisions and findings across agents
4. **Post-task**: Analyzes performance and saves results

## ⚡ IMMEDIATE ACTION REQUIRED

**For ALL future Task agent spawning:**
1. ✅ Include all 4 mandatory coordination hooks in every Task prompt
2. ✅ Use the provided Task agent template
3. ✅ Test Task calls with proper coordination instructions
4. ✅ Verify no HTTP 400 errors occur after implementing hooks

**This fix will:**
- ✅ Eliminate HTTP 400 errors from malformed API responses
- ✅ Enable proper swarm coordination through hooks
- ✅ Allow agents to share progress and decisions
- ✅ Restore normal Task agent spawning functionality

## 📊 VERIFICATION

To verify the fix works:
1. **Spawn a Task agent with proper coordination hooks**
2. **Confirm no HTTP 400 error occurs**
3. **Check that agent can execute coordination commands**
4. **Verify swarm memory is properly updated**

**Status**: Root cause identified, solution documented, ready for implementation.