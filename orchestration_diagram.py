#!/usr/bin/env python3
"""
Generate an ASCII diagram of the orchestration flow
"""

def generate_flow_diagram():
    """Generate ASCII art diagram of the orchestration flow"""
    
    diagram = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │                     🎯 CLAUDE CODE ORCHESTRATION FLOW                │
    └─────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────┐
    │   User Prompt   │ ◀── "Build a REST API with auth and tests"
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────┐
    │        UserPromptSubmit Hook            │
    │    (.claude/settings.json line 136)     │
    └────────┬────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────────┐
    │         main.py handle_prompt()         │
    │  ┌─────────────────────────────────┐   │
    │  │ • Analyze prompt complexity     │   │
    │  │ • Detect orchestration needs    │   │
    │  │ • Check available MCP tools     │   │
    │  │ • Generate project context      │   │
    │  └─────────────────────────────────┘   │
    └────────┬────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────────┐
    │      Zen Consultation (Task Tool)       │
    │  ┌─────────────────────────────────┐   │
    │  │ mcp__zen__chat                  │   │
    │  │ mcp__zen__thinkdeep             │   │
    │  │ mcp__zen__analyze               │   │
    │  └─────────────────────────────────┘   │
    └────────┬────────────────────────────────┘
             │
             ├─── [Complex Task Detected] ───┐
             │                               │
             ▼                               ▼
    ┌─────────────────────┐       ┌────────────────────┐
    │   Simple Execution  │       │  Claude Flow Init  │
    │  (Direct approach)  │       │ mcp__claude-flow__ │
    └─────────────────────┘       │    swarm_init      │
                                  └─────────┬──────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │    Spawn Agents          │
                              │ ┌──────────────────────┐ │
                              │ │ • Architect Agent    │ │
                              │ │ • Coder Agent(s)     │ │
                              │ │ • Analyst Agent      │ │
                              │ │ • Tester Agent       │ │
                              │ │ • Coordinator Agent  │ │
                              │ └──────────────────────┘ │
                              └────────────┬─────────────┘
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 │                                                   │
                 ▼                                                   ▼
    ┌──────────────────────────────┐                   ┌──────────────────────────┐
    │   Agent Coordination Hooks   │                   │  Pre/Post Tool Hooks     │
    │ ┌────────────────────────┐  │                   │ ┌──────────────────────┐ │
    │ │ npx claude-flow hooks:  │  │                   │ │ • pre-bash           │ │
    │ │ • pre-task              │  │ ◀── Monitor ───▶ │ │ • pre-edit           │ │
    │ │ • post-edit             │  │                   │ │ • pre-task           │ │
    │ │ • notification          │  │                   │ │ • pre-mcp            │ │
    │ │ • post-task             │  │                   │ │ • post-*             │ │
    │ └────────────────────────┘  │                   │ └──────────────────────┘ │
    └──────────────┬───────────────┘                   └──────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────┐
    │         Parallel Execution              │
    │  ┌─────────────────────────────────┐   │
    │  │ • All agents work concurrently  │   │
    │  │ • Shared memory coordination    │   │
    │  │ • Real-time progress tracking   │   │
    │  │ • Hook-based synchronization    │   │
    │  └─────────────────────────────────┘   │
    └────────┬────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────────┐
    │           Execution Results              │
    │  • Code generated and tested            │
    │  • All tasks completed                  │
    │  • Coordination state preserved         │
    └─────────────────────────────────────────┘
    
    
    🔄 KEY COORDINATION POINTS:
    
    1. UserPromptSubmit → Triggers entire flow
    2. Zen Consultation → Determines approach  
    3. Claude Flow Init → Sets up orchestration
    4. Agent Hooks → Maintain coordination
    5. Pre/Post Hooks → Monitor all operations
    
    
    📊 HOOK TYPES & PURPOSES:
    
    ┌─────────────────┬──────────────────────────────────────┐
    │   Hook Type     │            Purpose                   │
    ├─────────────────┼──────────────────────────────────────┤
    │ UserPromptSubmit│ Main orchestration entry point       │
    │ pre-bash        │ Validate commands before execution   │
    │ pre-edit        │ Prepare for file operations          │
    │ pre-task        │ Ensure agent coordination            │
    │ pre-mcp         │ Track MCP tool usage                 │
    │ post-bash       │ Process command results              │
    │ post-edit       │ Handle file changes                  │
    │ post-task       │ Track task completion                │
    │ post-mcp        │ Record MCP results                   │
    │ notification    │ Share coordination state             │
    │ stop            │ Cleanup session                      │
    └─────────────────┴──────────────────────────────────────┘
    """
    
    return diagram

if __name__ == "__main__":
    print(generate_flow_diagram())