# Enhanced Claude Hook Properties with Full Claude Visibility

## 🚨 CRITICAL: Hooks Now Provide Actionable Feedback Claude Can See!

The enhanced hook system transforms Claude Code hooks from **passive validators** into **active coordination agents** that provide actionable feedback Claude can see and act upon.

### Key Enhancement: Exit Code 2 + stderr = Claude Visibility

**Before (Invisible to Claude):**
```python
print("Suggestion for user")  # Claude can't see this
sys.exit(0)  # Exit code 0 = stdout goes to user only
```

**After (Visible to Claude):**
```python
print("Actionable feedback for Claude", file=sys.stderr)  # Claude sees this!
sys.exit(2)  # Exit code 2 = stderr goes to Claude for action
```

## Enhanced Hook Properties

### 🔧 PreToolUse Hooks (Enhanced with Claude Visibility)

#### PreToolUse:Bash - Proactive Command Optimization
- **Detects sequential anti-patterns** → Suggests parallel execution
- **Identifies complex operations** → Recommends swarm coordination  
- **Warns about dangerous commands** → Requests confirmation
- **Suggests tool optimizations** → Proposes better alternatives

**Example Claude-Visible Feedback:**
```
❌ SEQUENTIAL EXECUTION DETECTED!

Instead of waiting, use PARALLEL execution:
• Batch multiple operations in ONE message
• Use mcp__claude-flow__swarm_init for coordination
• Spawn multiple Task agents simultaneously

Would you like me to restructure this for parallel execution?
```

#### PreToolUse:Task - Mandatory Coordination Enforcement
- **Validates coordination instructions** → Blocks incomplete agents
- **Checks for parallel execution** → Prevents sequential patterns
- **Ensures hook requirements** → Mandates proper coordination

**Example Claude-Visible Feedback:**
```
🚨 AGENT MISSING COORDINATION INSTRUCTIONS!

This Task agent is missing required coordination hooks:
• npx claude-flow@alpha hooks pre-task
• npx claude-flow@alpha hooks post-edit

MANDATORY: Every Task agent MUST include these hooks!
Please add coordination instructions to the Task prompt!
```

### 🔨 PostToolUse Hooks (Enhanced with Claude Visibility)

#### PostToolUse:Bash - Intelligent Follow-up Actions
- **Analyzes command failures** → Provides debugging guidance
- **Detects successful installations** → Suggests verification steps
- **Handles test results** → Recommends next actions
- **Tracks git operations** → Guides workflow progression

**Example Claude-Visible Feedback:**
```
❌ COMMAND FAILED: npm test

Exit code: 1
Error: Test suite failed - 3 tests failing

Troubleshooting suggestions:
1. Check if dependencies are installed
2. Use mcp__zen__debug for systematic debugging
3. Review test output for specific failures

Would you like me to analyze this failure and suggest fixes?
```

#### PostToolUse:Edit - Context-Aware File Actions
- **JavaScript/TypeScript files** → Suggests linting and testing
- **Python files** → Recommends pytest and type checking
- **Config files** → Proposes validation and service restarts
- **Documentation** → Suggests PR creation

**Example Claude-Visible Feedback:**
```
📝 JAVASCRIPT FILE MODIFIED: src/api/auth.js

Recommended actions:
1. Run linting: npm run lint
2. Run tests: npm test
3. Check TypeScript: npm run type-check
4. Use mcp__zen__testgen for comprehensive test generation

Run these validations now?
```

### 🔔 Notification Hook (Enhanced with Context Awareness)

#### Notification - Proactive Assistance When Claude Waits
- **Detects waiting states** → Provides action menus
- **Handles permission requests** → Offers approval guidance
- **Suggests status checking** → Recommends monitoring tools

**Example Claude-Visible Feedback:**
```
⏳ CLAUDE IS WAITING - SUGGESTED ACTIONS

Consider these next steps:
1. Continue with current task implementation
2. Use mcp__zen__chat to explore approaches
3. Initialize swarm coordination for complex tasks
4. Check coordination state: mcp__claude-flow__swarm_status

What would you like to focus on next?
```

### 🛑 Stop Hook (Enhanced with Session Analysis)

#### Stop - Session Completion Validation
- **Analyzes incomplete work** → Suggests continuation
- **Detects untested changes** → Mandates test execution
- **Reviews session progress** → Provides completion guidance

**Example Claude-Visible Feedback:**
```
🧪 FILES MODIFIED BUT NO TESTS RUN

3 files were modified but no tests were executed.

Critical for automated coding:
1. Run relevant tests: npm test, pytest, etc.
2. Check linting and formatting
3. Validate changes work as expected

Run tests before finishing?
```

### 🤖 SubagentStop Hook (Enhanced with Coordination)

#### SubagentStop - Agent Completion Checkpoint
- **Coordinates agent completion** → Updates swarm state
- **Stores agent results** → Preserves work context
- **Notifies other agents** → Maintains coordination
- **Checks dependent tasks** → Ensures workflow continuity

**Example Claude-Visible Feedback:**
```
🤖 SUBAGENT COMPLETED

Agent coordination checkpoint:
1. Storing results in Claude Flow memory
2. Notifying other agents of completion
3. Checking for dependent tasks
4. Updating coordination state

Use mcp__claude-flow__swarm_status to check progress.
Continue with coordinated execution?
```

### 📦 PreCompact Hook (Enhanced with Preparation)

#### PreCompact - Context Preservation Before Compacting
- **Saves critical context** → Preserves important information
- **Updates progress tracking** → Maintains TodoWrite state
- **Stores decisions** → Preserves coordination history

**Example Claude-Visible Feedback:**
```
📦 PRECOMPACT PREPARATION

About to compact (trigger: context_limit)

Before compacting:
1. Save important context with mcp__claude-flow__memory_usage
2. Update TodoWrite with current progress
3. Store any decisions or findings
4. Ensure critical information is preserved

Ready to proceed with compacting?
```

## Implementation Details

### Core Enhancement Functions

```python
def claude_feedback(message: str, block: bool = True) -> None:
    """
    Send feedback directly to Claude that it can see and act upon.
    
    Args:
        message: Actionable feedback for Claude
        block: If True, uses exit code 2 (Claude sees stderr)
    """
    if block:
        print(message, file=sys.stderr)
        sys.exit(2)  # Claude sees this feedback and can act on it!
    else:
        print(message)  # Goes to user only
        sys.exit(0)
```

### Enhanced Hook Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Enhanced Hook Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Hook Triggered → Enhanced Handler                       │
│  2. Analyze Context → Detect Issues/Opportunities           │
│  3. Generate Actionable Feedback                            │
│  4. Use exit code 2 + stderr → Claude Sees Feedback        │
│  5. Claude Acts on Feedback → Takes Suggested Actions       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Usage Patterns

### Pattern 1: Command Optimization
```
User runs: grep "pattern" *.js
Hook detects: Suboptimal search tool
Claude sees: "Use rg instead for better performance?"
Claude acts: Suggests Grep or rg alternatives
```

### Pattern 2: Coordination Enforcement
```
User spawns: Task without coordination hooks
Hook detects: Missing coordination instructions
Claude sees: "Agent missing required hooks!"
Claude acts: Adds coordination instructions to Task
```

### Pattern 3: Workflow Guidance
```
User modifies: Python file
Hook detects: Code change without testing
Claude sees: "Run pytest and linting now?"
Claude acts: Executes tests and validation
```

### Pattern 4: Session Management
```
User ends session: With incomplete todos
Hook detects: Unfinished work
Claude sees: "3 incomplete todos remain!"
Claude acts: Continues with pending tasks
```

## Configuration

The enhanced hooks are automatically activated through `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/main_enhanced_visibility.py pre-bash",
        "timeout": 15
      }]
    }],
    // ... all hooks updated to use enhanced version
  }
}
```

## Benefits for Automated Coding

### 🚀 Proactive Coordination
- Hooks actively guide Claude toward optimal tool usage
- Prevent common mistakes before they happen
- Ensure proper swarm coordination is maintained

### 🔧 Intelligent Workflow Management
- Context-aware suggestions based on file types and operations
- Automatic detection of complex tasks requiring coordination
- Smart follow-up actions after tool completion

### 🛡️ Safety and Validation
- Warning system for potentially dangerous operations
- Mandatory validation for critical workflows
- Session completion analysis prevents incomplete work

### ⚡ Performance Optimization
- Tool suggestions for better performance (rg vs grep)
- Parallel execution enforcement over sequential patterns
- Efficient coordination patterns through proper hooks

## Troubleshooting

### Hook Not Providing Feedback?
1. Check if enhanced version is configured in settings.json
2. Verify Python path and permissions
3. Look for processor import errors in logs
4. Test with --debug flag for detailed output

### Claude Not Responding to Feedback?
1. Ensure hooks are using exit code 2 for critical feedback
2. Verify stderr output is properly formatted
3. Check timeout settings allow sufficient processing time
4. Confirm hook matchers are correctly configured

## Backup and Recovery

Original hooks are preserved:
- `main.py` → Original implementation (backup)
- `main_enhanced_visibility.py` → Enhanced implementation (active)
- `settings.json.backup` → Original configuration (backup)

To revert to original hooks:
```bash
cp .claude/settings.json.backup .claude/settings.json
```

## Summary

The enhanced hook system transforms Claude Code hooks from passive validators into **active AI assistants** that:

- 🔧 **Provide actionable feedback Claude can see and act upon**
- 📋 **Enforce proper coordination patterns for swarms**
- 🚀 **Suggest optimal tools and workflows proactively**
- ⚠️ **Prevent mistakes through intelligent validation**
- 🧠 **Enable truly automated coding with minimal human intervention**

**Key Principle: If Claude can't see the feedback, the hook is worthless for automated coding!**

The enhanced hooks ensure Claude is **always aware** of the best tools, approaches, and next steps for any given task, making automated coding more effective and reliable.