# Enhanced Claude Code Hooks - Continuous MCP Tool Guidance

## Overview

The enhanced hook system provides **constant, proactive MCP tool suggestions** throughout your Claude Code sessions. Hooks now actively guide Claude Code by:

1. **Suggesting relevant MCP tools** based on context
2. **Providing workflow recommendations** for complex tasks
3. **Reminding about coordination requirements** for swarms
4. **Offering follow-up actions** after tool completion
5. **Warning about sensitive operations**
6. **Sharing best practices** and performance tips

## Key Features

### 🎯 Proactive Tool Suggestions

Hooks analyze the current context and suggest the most relevant MCP tools:

```python
# Example: When working with multiple files
"Working with multiple files? Use parallel execution"
- Tools: BatchTool, mcp__claude-flow__swarm_init, TodoWrite
```

### 🔄 Workflow Guidance

Complete workflow patterns are suggested based on task type:

```python
# Example: Debugging workflow
"Debug workflow: Analyze issue → Search patterns → Find references"
- Tools: mcp__zen__debug → Grep → mcp__serena__find_referencing_symbols
```

### 🐝 Swarm Coordination Reminders

Every Task spawn includes mandatory coordination instructions:

```
MANDATORY COORDINATION:
1. START: Run `npx claude-flow@alpha hooks pre-task --description "[task]"`
2. DURING: After EVERY file operation, run hooks
3. SHARE: Use memory tools for decisions
4. END: Run post-task hooks
```

### 📊 Context-Aware Insights

Hooks track session state and provide timely suggestions:

- **Early session**: Basic tips and memory checking
- **Mid-session**: Workflow optimization suggestions
- **Long session**: Progress saving and PR creation reminders

### 🔧 Tool-Specific Guidance

Each MCP tool gets contextual help:

```python
# Example: swarm_init guidance
"Topology Selection:
- hierarchical: Best for structured tasks
- mesh: Best for collaborative tasks
- ring: Best for sequential pipelines
- star: Best for centralized coordination"
```

## Hook Enhancements by Type

### UserPromptSubmit

- Analyzes task complexity
- Suggests Zen consultation workflows
- Recommends swarm coordination for complex tasks
- Provides initial MCP tool inventory
- Offers task-specific recommendations

### Pre-Tool Hooks

#### PreToolUse (Bash)
- Suggests better alternatives (rg instead of grep)
- Warns about dangerous commands
- Provides command-specific tips

#### PreToolUse (Task)
- **Always** shows coordination requirements
- Suggests agent-specific MCP tools
- Provides role-based tool recommendations

#### PreToolUse (MCP)
- Tool-specific checklists and guides
- Next-step recommendations
- Best practices for each tool

### Post-Tool Hooks

#### PostToolUse (Bash)
- Analyzes command results
- Suggests debugging tools for failures
- Provides next-step guidance based on output

#### PostToolUse (Edit/Write)
- File-type specific suggestions
- Testing reminders for code changes
- Documentation update hints

#### PostToolUse (MCP)
- Immediate follow-up actions
- Workflow continuation guidance
- Result-based recommendations

### Notification Hook

- Helps when Claude Code is waiting
- Suggests status checking tools
- Provides quick action menus
- Offers context-aware assistance

## Implementation Details

### Core Modules

1. **proactive_guidance.py**
   - Pattern matching for tool suggestions
   - Coordination strategy detection
   - Context analysis

2. **continuous_insights.py**
   - Session state tracking
   - Periodic reminders
   - Tool sequence recommendations

3. **hook_decisions.py**
   - Auto-approval patterns
   - Safety warnings
   - Alternative suggestions

### Configuration

Enhanced hooks are automatically enabled in `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/main.py prompt",
        "timeout": 120
      }]
    }],
    // ... other hooks
  }
}
```

## Usage Examples

### Complex Task → Swarm Suggestion

**Input**: "Build a REST API with authentication and tests"

**Hook Output**:
```
🐝 Swarm Coordination Recommended
- Recommended Agents: 5
- Topology: hierarchical

1. Initialize swarm with `mcp__claude-flow__swarm_init`
2. Spawn specialized agents with `mcp__claude-flow__agent_spawn`
3. Use `Task` tool to assign work to each agent
4. Coordinate results with `mcp__claude-flow__memory_usage`
```

### File Edit → Testing Reminder

**Input**: Edit Python file

**Hook Output**:
```
💡 Post-edit suggestion: Consider running `python -m pytest` or `mcp__zen__testgen`
```

### Waiting State → Action Menu

**Input**: Claude is waiting notification

**Hook Output**:
```
💡 While Claude Code is Waiting

Quick Actions:
1. Check swarm progress: `mcp__claude-flow__swarm_status`
2. Review memory state: `mcp__claude-flow__memory_usage`
3. Monitor agents: `mcp__claude-flow__agent_list`
4. Check todos: Review your TodoWrite list
```

## Best Practices

1. **Pay attention to hook suggestions** - They provide optimal tool sequences
2. **Use suggested workflows** - They're based on proven patterns
3. **Follow coordination requirements** - Essential for swarm operations
4. **Consider alternatives** - Hooks suggest better tools when available
5. **Track with TodoWrite** - Hooks remind you to maintain task lists

## Advanced Features

### Decision Support

Hooks can auto-approve safe operations:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe file type - documentation"
  }
}
```

### Tool Combination Patterns

Hooks understand common tool sequences:
- `find_symbol` → `read_file` → `find_referencing_symbols`
- `list_issues` → `create_branch` → `create_pr`
- `swarm_init` → `agent_spawn` → `Task`

### Memory Integration

Hooks remind about memory operations:
- Store decisions after major steps
- Retrieve context before operations
- Share state between agents

## Troubleshooting

If hooks aren't providing suggestions:

1. Check logs with `--debug` flag
2. Verify processors are loaded
3. Ensure settings.json is configured
4. Test with `test_enhanced_hooks.py`

## Summary

The enhanced hook system transforms Claude Code hooks from passive validators into **active AI assistants** that constantly guide you with:

- 🔧 Relevant MCP tool suggestions
- 📋 Complete workflow patterns
- 🐝 Swarm coordination requirements
- 🚀 Next-step recommendations
- ⚠️ Safety warnings and best practices

Hooks now ensure you're always aware of the best tools and approaches for your current task!