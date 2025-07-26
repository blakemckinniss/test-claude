# Agent Completion Tracking System

## PHASE 3: Completion Tracking to Prevent Orphaned Agents

This system ensures all Task agents complete their lifecycle properly and no agents remain orphaned.

## The Orphaned Agent Problem

**Root Cause**: Task agents that don't complete their post-task hook remain in memory, causing:
- API errors when memory limits are reached
- Resource leaks from unclosed processes
- Swarm coordination failures
- Performance degradation

## Completion Tracking Implementation

### 1. Agent Registry System

Every spawned agent must be registered and tracked:

```bash
# When spawning an agent, register it
npx claude-flow@alpha hooks agent-spawned --name "[agent-name]" --type "[agent-type]"

# This creates a registry entry for tracking
```

### 2. Progress Tracking Pattern

Each agent reports progress using consistent memory keys:

```bash
# Step 1: Register start
npx claude-flow@alpha hooks pre-task --description "Task description"
# Creates: agent/[id]/lifecycle/started

# Step 2: Report progress
npx claude-flow@alpha hooks post-edit --file "progress" --memory-key "agent/[id]/lifecycle/progress-[N]"
# Creates: agent/[id]/lifecycle/progress-1, progress-2, etc.

# Step 3: Report completion
npx claude-flow@alpha hooks post-task --task-id "[task-id]" --analyze-performance true
# Creates: agent/[id]/lifecycle/completed
```

### 3. Completion Verification System

Before any new agents are spawned, verify all previous agents completed:

```bash
# Check for orphaned agents
npx claude-flow@alpha hooks session-restore --session-id "current" --load-memory true

# This will show any agents that started but never completed
```

### 4. Automatic Cleanup Pattern

Implement automatic cleanup for orphaned agents:

```javascript
// In Task agent template, add timeout completion:
setTimeout(() => {
  console.log("Agent timeout reached, forcing completion...");
  npx claude-flow@alpha hooks post-task --task-id "[task-id]" --analyze-performance true;
  process.exit(0);
}, 300000); // 5 minute timeout
```

## Agent Lifecycle States

Track agents through these states:

1. **REGISTERED**: Agent spawned and recorded
2. **STARTED**: Pre-task hook completed
3. **WORKING**: Post-edit hooks being called
4. **COMPLETING**: Post-task hook initiated
5. **COMPLETED**: All cleanup finished

## Memory Key Structure

Organize agent tracking with consistent keys:

```
agent/[agent-id]/lifecycle/registered    - Agent spawn timestamp
agent/[agent-id]/lifecycle/started       - Pre-task completion
agent/[agent-id]/lifecycle/progress-N    - Work step N completed
agent/[agent-id]/lifecycle/completing    - Post-task initiated
agent/[agent-id]/lifecycle/completed     - Full cleanup done
```

## Orphan Detection Algorithm

```bash
# 1. Get all registered agents
REGISTERED=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/registered")

# 2. Check for completed agents
COMPLETED=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/completed")

# 3. Find orphans (registered but not completed)
ORPHANS=$(comm -23 <(echo "$REGISTERED") <(echo "$COMPLETED"))

# 4. Report orphaned agents
if [ -n "$ORPHANS" ]; then
  echo "🚨 ORPHANED AGENTS DETECTED:"
  echo "$ORPHANS"
  echo "These agents may be causing API errors!"
fi
```

## Prevention Strategies

### Strategy 1: Mandatory Completion Checks
Before spawning new agents, verify previous ones completed:

```javascript
// In orchestration code:
const checkOrphans = `
  npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/registered" > registered.txt
  npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/completed" > completed.txt
  ORPHANS=$(comm -23 registered.txt completed.txt)
  if [ -n "$ORPHANS" ]; then
    echo "❌ Cannot spawn new agents - orphans detected: $ORPHANS"
    exit 1
  fi
`;
```

### Strategy 2: Automatic Timeout Handling
Add to every Task agent:

```javascript
// Auto-completion after timeout
const AGENT_TIMEOUT = 5 * 60 * 1000; // 5 minutes
setTimeout(() => {
  console.log("🚨 Agent timeout - forcing completion to prevent orphaning");
  exec("npx claude-flow@alpha hooks post-task --task-id " + taskId + " --analyze-performance true");
  process.exit(0);
}, AGENT_TIMEOUT);
```

### Strategy 3: Health Check Pattern
Regular verification of agent states:

```bash
# Health check script
npx claude-flow@alpha hooks notify --message "Running agent health check" --level "info"

# Count active vs completed agents
ACTIVE=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/started" | wc -l)
COMPLETED=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/completed" | wc -l)

if [ $ACTIVE -gt $COMPLETED ]; then
  ORPHANS=$((ACTIVE - COMPLETED))
  npx claude-flow@alpha hooks notify --message "⚠️ $ORPHANS potential orphaned agents detected" --level "warning"
fi
```

## Implementation Checklist

To prevent orphaned agents:
- ✅ Register every spawned agent
- ✅ Track lifecycle states in memory
- ✅ Implement timeout handling
- ✅ Add completion verification
- ✅ Run health checks periodically
- ✅ Clean up resources properly

This system ensures no Task agents become orphaned and cause API errors.