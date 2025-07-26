#!/usr/bin/env python3
"""
Test and demonstrate PROPER orchestration with correct separation of concerns
"""

import json
import subprocess
import sys

def test_orchestration_separation():
    """Test that demonstrates proper separation between Claude Code and Claude Flow"""
    
    print("=" * 80)
    print("🎯 TESTING PROPER ORCHESTRATION - SEPARATION OF CONCERNS")
    print("=" * 80)
    
    # Test prompt that should trigger swarm orchestration
    test_prompt = "Build a complete REST API with authentication, database, and tests"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    print("\n" + "=" * 80)
    print("EXPECTED BEHAVIOR:")
    print("=" * 80)
    
    print("""
1️⃣ UserPromptSubmit Hook:
   - Analyzes prompt complexity
   - Returns INSTRUCTIONS (not executions)
   
2️⃣ Claude Code Receives Instructions:
   - Reads the orchestration plan
   - Uses MCP tools for coordination setup
   - Uses Task tool to spawn agents
   
3️⃣ Task Tool Spawns Agents:
   Each agent receives coordination instructions:
   ```
   You are the [Role] agent.
   
   MANDATORY COORDINATION:
   - START: npx claude-flow@alpha hooks pre-task
   - DURING: npx claude-flow@alpha hooks post-edit
   - SHARE: npx claude-flow@alpha hooks notification
   - END: npx claude-flow@alpha hooks post-task
   
   Your task: [Specific work]
   ```
   
4️⃣ Agents Execute with Claude Code Tools:
   - Read() for file analysis
   - Write() for file creation
   - Edit() for modifications
   - Bash() for commands
   - TodoWrite() for task tracking
   
5️⃣ Coordination Through Hooks:
   - pre-task: Agent initialization
   - post-edit: After each file change
   - notification: Share decisions
   - post-task: Completion tracking
   
6️⃣ Claude Flow MCP Tools (Coordination Only):
   - mcp__claude-flow__swarm_init → Setup topology
   - mcp__claude-flow__agent_spawn → Track agents
   - mcp__claude-flow__memory_usage → Share state
   - mcp__claude-flow__swarm_status → Monitor progress
""")
    
    print("\n" + "=" * 80)
    print("CRITICAL DISTINCTIONS:")
    print("=" * 80)
    
    print("""
✅ CLAUDE CODE DOES:
- ALL file operations (Read, Write, Edit)
- ALL code generation
- ALL bash commands
- ALL testing
- ALL git operations
- Task() to spawn agents
- TodoWrite() for tracking

❌ CLAUDE CODE DOESN'T:
- Direct swarm management
- Neural network operations
- Cross-agent memory sync

✅ CLAUDE FLOW DOES:
- Coordination planning
- Memory management
- Performance tracking
- Swarm topology
- Agent communication
- Learning patterns

❌ CLAUDE FLOW DOESN'T:
- Write files
- Execute commands
- Generate code
- Run tests
- Make commits
""")
    
    # Run the hook to see output
    print("\n" + "=" * 80)
    print("RUNNING ORCHESTRATION HOOK:")
    print("=" * 80)
    
    hook_input = json.dumps({
        "prompt": test_prompt,
        "session_id": "test-proper-separation",
        "hook_event_name": "UserPromptSubmit"
    })
    
    try:
        result = subprocess.run(
            ["python", "/home/devcontainers/bench/test-game/.claude/hooks/main_orchestrator.py", "prompt"],
            input=hook_input,
            text=True,
            capture_output=True,
            check=False
        )
        
        if result.stdout:
            print("\n📋 ORCHESTRATION OUTPUT (Instructions for Claude Code):")
            print("-" * 80)
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Hook Logs:")
            print(result.stderr)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Demonstrate the execution pattern
    print("\n" + "=" * 80)
    print("PARALLEL EXECUTION PATTERN (What Claude Code Should Do):")
    print("=" * 80)
    
    print("""
# Single message with ALL operations:

[BatchTool Message]:
  # 1. Initialize Swarm (Coordination)
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 }
  
  # 2. Spawn ALL Agents (with full instructions)
  Task("You are the Architect agent. MANDATORY: Use hooks pre-task, post-edit, notification, post-task. Design the API architecture.")
  Task("You are the Lead Developer. MANDATORY: Use hooks. Implement core API endpoints.")
  Task("You are the Database Specialist. MANDATORY: Use hooks. Design data models.")
  Task("You are the Test Engineer. MANDATORY: Use hooks. Create comprehensive tests.")
  Task("You are the Coordinator. MANDATORY: Use hooks. Track progress and integration.")
  
  # 3. TodoWrite (ALL todos at once)
  TodoWrite { todos: [
    { id: "1", content: "Design API architecture", status: "in_progress", priority: "high" },
    { id: "2", content: "Create database schema", status: "pending", priority: "high" },
    { id: "3", content: "Implement auth system", status: "pending", priority: "high" },
    { id: "4", content: "Build REST endpoints", status: "pending", priority: "high" },
    { id: "5", content: "Write unit tests", status: "pending", priority: "medium" },
    { id: "6", content: "Write integration tests", status: "pending", priority: "medium" },
    { id: "7", content: "Create API documentation", status: "pending", priority: "low" },
    { id: "8", content: "Setup deployment", status: "pending", priority: "medium" }
  ]}
  
  # 4. Create project structure
  Bash("mkdir -p api/{src,tests,docs,config}")
  Write("api/package.json", packageContent)
  Write("api/README.md", readmeContent)
  Write("api/.env.example", envContent)
""")
    
    print("\n" + "=" * 80)
    print("✅ ORCHESTRATION TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_orchestration_separation()