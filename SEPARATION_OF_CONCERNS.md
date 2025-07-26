# 🎯 Claude Code vs Claude Flow: Separation of Concerns

This document defines the CRITICAL separation between Claude Code (executor) and Claude Flow (coordinator).

## 🚨 GOLDEN RULE

**Claude Code EXECUTES, Claude Flow COORDINATES**

## 📊 Responsibility Matrix

| Action | Claude Code | Claude Flow | Notes |
|--------|-------------|-------------|-------|
| Write files | ✅ | ❌ | ONLY Claude Code writes files |
| Read files | ✅ | ❌ | ONLY Claude Code reads files |
| Execute bash | ✅ | ❌ | ONLY Claude Code runs commands |
| Generate code | ✅ | ❌ | ONLY Claude Code creates code |
| Run tests | ✅ | ❌ | ONLY Claude Code executes tests |
| Git operations | ✅ | ❌ | ONLY Claude Code does git |
| TodoWrite | ✅ | ❌ | ONLY Claude Code manages todos |
| Task spawning | ✅ | ❌ | Claude Code uses Task tool |
| Swarm topology | ❌ | ✅ | Claude Flow plans structure |
| Memory storage | ❌ | ✅ | Claude Flow manages memory |
| Agent coordination | ❌ | ✅ | Claude Flow coordinates |
| Performance tracking | ❌ | ✅ | Claude Flow monitors |
| Neural patterns | ❌ | ✅ | Claude Flow learns |

## 🔄 Correct Orchestration Flow

### 1️⃣ User Submits Prompt
```
User: "Build a REST API with auth and tests"
```

### 2️⃣ UserPromptSubmit Hook Analyzes
The hook returns INSTRUCTIONS, not executions:
```markdown
## 🎯 Task Orchestration Plan

I will execute this using:
1. MCP tools for swarm coordination (planning only)
2. Task tool for agent spawning (with instructions)
3. Native Claude Code tools for ALL actual work
```

### 3️⃣ Claude Code Executes Instructions
Claude Code reads the plan and executes in ONE message:
```javascript
[Single Message - BatchTool]:
  // Coordination setup
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 }
  
  // Spawn agents with coordination
  Task("You are Architect. MANDATORY: Use hooks. Design API.")
  Task("You are Developer. MANDATORY: Use hooks. Build endpoints.")
  Task("You are Tester. MANDATORY: Use hooks. Write tests.")
  
  // Track with todos
  TodoWrite { todos: [complete list] }
  
  // Execute work
  Write("api/server.js", serverCode)
  Write("api/routes/auth.js", authCode)
  Bash("npm install express")
```

### 4️⃣ Agents Coordinate Through Hooks
Each agent runs coordination commands:
```bash
npx claude-flow@alpha hooks pre-task --description "Design API"
# ... do work with Claude Code tools ...
npx claude-flow@alpha hooks post-edit --file "api/schema.js"
npx claude-flow@alpha hooks notification --message "Schema complete"
npx claude-flow@alpha hooks post-task --task-id "design"
```

### 5️⃣ Claude Flow Tracks Progress
MCP tools monitor and coordinate:
- `mcp__claude-flow__swarm_status` - Check progress
- `mcp__claude-flow__memory_usage` - Store decisions
- `mcp__claude-flow__agent_metrics` - Track performance

## ❌ WRONG Patterns (Never Do This)

### Wrong: Claude Flow Writing Files
```javascript
// ❌ NEVER: Claude Flow doesn't write files
mcp__claude-flow__create_file { path: "server.js", content: "..." }
```

### Wrong: Sequential Operations
```javascript
// ❌ NEVER: Multiple messages
Message 1: mcp__claude-flow__swarm_init
Message 2: Task("Agent 1")
Message 3: Task("Agent 2")
```

### Wrong: Direct Hook Execution
```python
// ❌ NEVER: Hooks shouldn't execute tools
def handle_prompt():
    run_mcp_tool('zen', 'chat')  # Wrong!
    subprocess.run(['mcp', 'tool'])  # Wrong!
```

## ✅ CORRECT Patterns

### Correct: Claude Code Executes Everything
```javascript
// ✅ CORRECT: Claude Code does all work
Write("api/server.js", content)
Edit("api/routes.js", changes)
Bash("npm test")
TodoWrite({ todos: [...] })
```

### Correct: Parallel Execution
```javascript
// ✅ CORRECT: Everything in ONE message
[BatchTool]:
  mcp__claude-flow__swarm_init
  Task("Agent 1 with instructions")
  Task("Agent 2 with instructions")
  Task("Agent 3 with instructions")
  TodoWrite { todos: [all todos] }
  Write("file1.js", content1)
  Write("file2.js", content2)
```

### Correct: Hook Returns Instructions
```python
// ✅ CORRECT: Hook provides guidance
def handle_prompt():
    print("""
    ## Task Plan
    Use mcp__claude-flow__swarm_init for coordination
    Spawn agents with Task tool
    Execute with native tools
    """)
```

## 🎯 Key Principles

1. **Claude Code is the ONLY executor** - All file operations, commands, and code generation
2. **Claude Flow is ONLY coordination** - Planning, memory, performance tracking
3. **Hooks provide instructions** - They guide Claude Code, not execute directly
4. **Parallel execution always** - Single message with all operations
5. **Agents coordinate via hooks** - npx claude-flow commands for synchronization

## 📋 Validation Checklist

Before executing any task, verify:

- [ ] All file operations use Claude Code tools (Read, Write, Edit)
- [ ] All bash commands use Claude Code's Bash tool
- [ ] Task tool spawns agents with coordination instructions
- [ ] MCP tools used only for coordination setup
- [ ] Everything executes in parallel (one message)
- [ ] Agents include mandatory hook commands
- [ ] TodoWrite batches all todos together
- [ ] No direct subprocess calls in hooks

## 🚀 Example: Correct Full Flow

```javascript
// Single BatchTool message in Claude Code:
[
  // 1. Setup coordination
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 },
  
  // 2. Spawn agents with full instructions
  Task("You are the Architect agent. Your role is to design the system architecture. MANDATORY COORDINATION: Run `npx claude-flow@alpha hooks pre-task` before starting, `npx claude-flow@alpha hooks post-edit` after each file, `npx claude-flow@alpha hooks notification` to share decisions, and `npx claude-flow@alpha hooks post-task` when complete. Design a scalable REST API architecture."),
  
  Task("You are the Developer agent. Your role is to implement the core functionality. MANDATORY COORDINATION: [same hooks]. Build the REST endpoints with Express."),
  
  Task("You are the Database agent. Your role is to design data models. MANDATORY COORDINATION: [same hooks]. Create PostgreSQL schemas."),
  
  // 3. Track all work
  TodoWrite { todos: [
    { id: "1", content: "Design architecture", status: "in_progress", priority: "high" },
    { id: "2", content: "Create database schema", status: "pending", priority: "high" },
    { id: "3", content: "Implement auth", status: "pending", priority: "high" },
    { id: "4", content: "Build API endpoints", status: "pending", priority: "high" },
    { id: "5", content: "Write tests", status: "pending", priority: "medium" }
  ]},
  
  // 4. Execute actual work
  Bash("mkdir -p api/{src,tests,docs}"),
  Write("api/package.json", packageJson),
  Write("api/src/server.js", serverCode),
  Write("api/src/db/schema.sql", schemaSQL),
  
  // 5. Store coordination state
  mcp__claude-flow__memory_usage { action: "store", key: "project/init", value: {...} }
]
```

This ensures perfect separation: Claude Code executes, Claude Flow coordinates!