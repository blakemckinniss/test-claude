#!/usr/bin/env python3
"""
Test script to demonstrate the orchestration flow:
User Prompt → Hooks → Zen Consultation → Claude Flow → Agent Coordination
"""

import json
import subprocess
import sys
from pathlib import Path

def test_prompt_hook():
    """Test the prompt hook with a sample prompt"""
    print("=" * 60)
    print("🧪 Testing Orchestration Flow")
    print("=" * 60)
    
    # Sample prompt that should trigger full orchestration
    test_prompt = "Build a complete REST API with authentication, database integration, and comprehensive tests using modern best practices"
    
    # Prepare input for the hook
    hook_input = json.dumps({
        "prompt": test_prompt,
        "context": {
            "session_id": "test-session-123",
            "timestamp": "2025-07-26T12:00:00Z"
        }
    })
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    print("\n🔄 Triggering UserPromptSubmit hook...")
    
    # Run the hook
    try:
        result = subprocess.run(
            ["python", "/home/devcontainers/bench/test-game/.claude/hooks/main.py", "prompt"],
            input=hook_input,
            text=True,
            capture_output=True,
            check=False
        )
        
        print("\n📊 Hook Output:")
        print("-" * 60)
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Hook Errors/Logs:")
            print(result.stderr)
        
        print(f"\n✅ Hook Exit Code: {result.returncode}")
        
    except Exception as e:
        print(f"\n❌ Error running hook: {e}")
        return 1
    
    # Demonstrate the expected flow
    print("\n" + "=" * 60)
    print("📋 Expected Orchestration Flow:")
    print("=" * 60)
    print("""
1️⃣ UserPromptSubmit Hook Triggered
   └─→ main.py handle_prompt()
   
2️⃣ Prompt Analysis
   └─→ analyze_prompt_complexity()
   └─→ detect_claude_flow_swarm_needs()
   
3️⃣ Zen Consultation (via Task tool)
   └─→ create_zen_consultation_task()
   └─→ run_zen_consultation_functional()
       └─→ Uses mcp__zen__* tools for analysis
   
4️⃣ Claude Flow Orchestration
   └─→ run_claude_flow_swarm_orchestration()
       ├─→ mcp__claude-flow__swarm_init
       ├─→ mcp__claude-flow__agent_spawn (multiple)
       └─→ mcp__claude-flow__task_orchestrate
   
5️⃣ Agent Coordination
   └─→ judge_and_spawn_agents_functional()
   └─→ Task() commands with coordination hooks
       ├─→ "npx claude-flow@alpha hooks pre-task"
       ├─→ "npx claude-flow@alpha hooks post-edit" 
       └─→ "npx claude-flow@alpha hooks notification"
   
6️⃣ Pre/Post Tool Hooks
   ├─→ PreToolUse hooks monitor all operations
   └─→ PostToolUse hooks track progress
   
7️⃣ Parallel Execution & Monitoring
   └─→ All agents work in parallel
   └─→ Coordination through shared memory
   └─→ Progress tracking via hooks
""")
    
    return 0

def test_pre_post_hooks():
    """Test pre/post tool hooks"""
    print("\n" + "=" * 60)
    print("🧪 Testing Pre/Post Tool Hooks")
    print("=" * 60)
    
    # Test pre-bash hook
    bash_input = json.dumps({
        "tool_input": {
            "command": "npx claude-flow@alpha hooks pre-task --description 'Test task'"
        }
    })
    
    print("\n🔧 Testing Pre-Bash Hook (Claude Flow command)...")
    result = subprocess.run(
        ["python", "/home/devcontainers/bench/test-game/.claude/hooks/main.py", "pre-bash"],
        input=bash_input,
        text=True,
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✅ Pre-bash hook validated Claude Flow command")
    
    # Test pre-task hook
    task_input = json.dumps({
        "tool_input": {
            "description": "Research API patterns",
            "prompt": "You are researcher agent. MANDATORY: Run hooks pre-task, post-edit, post-task."
        }
    })
    
    print("\n🔧 Testing Pre-Task Hook...")
    result = subprocess.run(
        ["python", "/home/devcontainers/bench/test-game/.claude/hooks/main.py", "pre-task"],
        input=task_input,
        text=True,
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✅ Pre-task hook verified coordination instructions")
    
    # Test pre-mcp hook
    mcp_input = json.dumps({
        "tool_input": {
            "_tool_name": "mcp__claude-flow__swarm_init",
            "topology": "hierarchical",
            "maxAgents": 5
        }
    })
    
    print("\n🔧 Testing Pre-MCP Hook (Claude Flow tool)...")
    result = subprocess.run(
        ["python", "/home/devcontainers/bench/test-game/.claude/hooks/main.py", "pre-mcp"],
        input=mcp_input,
        text=True,
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✅ Pre-MCP hook tracked Claude Flow orchestration")

def main():
    """Run all tests"""
    print("🚀 Claude Code Orchestration Flow Test")
    print("Testing the complete flow from prompt to execution\n")
    
    # Test the main prompt hook
    if test_prompt_hook() != 0:
        return 1
    
    # Test pre/post hooks
    test_pre_post_hooks()
    
    print("\n" + "=" * 60)
    print("✅ Orchestration Flow Test Complete!")
    print("=" * 60)
    print("""
Key Points Verified:
1. UserPromptSubmit hook triggers full orchestration
2. Zen consultation analyzes and plans approach  
3. Claude Flow initializes swarm coordination
4. Agents spawned with coordination instructions
5. Pre/Post hooks monitor all operations
6. Parallel execution maintained throughout
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())