# Agent Lifecycle Coordination Fix

## Critical Issue: API Error Due to Orphaned Agents

The API error occurs when Task agents are spawned without proper lifecycle management, causing them to remain in memory without completion tracking.

## PHASE 1: The 4 Mandatory Hooks for All Task Agents

Every Task agent MUST implement these 4 coordination hooks:

### 1. PRE-TASK HOOK (Required at Start)
```bash
npx claude-flow@alpha hooks pre-task --description "[specific task]" --auto-spawn-agents false
```
- **Purpose**: Initialize agent context and load coordination data
- **When**: BEFORE any work begins
- **Critical**: Sets up proper lifecycle tracking

### 2. POST-EDIT HOOK (Required After Each Operation)
```bash
npx claude-flow@alpha hooks post-edit --file "[filepath]" --memory-key "agent/[name]/[step]"
```
- **Purpose**: Store progress and coordinate with other agents
- **When**: AFTER every file operation or major step
- **Critical**: Prevents agent state from becoming stale

### 3. NOTIFICATION HOOK (Required for Decisions)
```bash
npx claude-flow@alpha hooks notification --message "[decision/finding]" --telemetry true
```
- **Purpose**: Share decisions and findings with the swarm
- **When**: After making important decisions or discoveries
- **Critical**: Enables proper coordination between agents

### 4. POST-TASK HOOK (Required at End)
```bash
npx claude-flow@alpha hooks post-task --task-id "[task]" --analyze-performance true
```
- **Purpose**: Complete lifecycle and cleanup agent resources
- **When**: AFTER all work is finished
- **Critical**: Prevents orphaned agents and memory leaks

## Why These Hooks Prevent API Errors

1. **Proper Initialization**: Pre-task hooks ensure agents start with valid context
2. **State Management**: Post-edit hooks maintain consistent agent state
3. **Coordination**: Notification hooks prevent conflicts between agents
4. **Cleanup**: Post-task hooks properly terminate agents and free resources

## Current Problem: Incomplete Lifecycles

Without these hooks, agents:
- Start work without proper context loading
- Make changes without coordination
- Never properly terminate
- Accumulate in memory causing API errors
- Cannot be tracked or managed by the swarm

## Solution: Mandatory Hook Implementation

All Task agents must follow the complete lifecycle pattern to prevent API errors and orphaned processes.