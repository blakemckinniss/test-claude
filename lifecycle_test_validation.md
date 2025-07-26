# Agent Lifecycle Test Validation

## PHASE 4: Testing Agent Lifecycle Completion

This phase validates that agents complete their full lifecycle properly and don't become orphaned.

## Test Agent Creation

Let's create a test agent that follows the complete lifecycle:

### Test Agent Script

```bash
#!/bin/bash
# Test agent that demonstrates proper lifecycle

AGENT_ID="test-agent-$(date +%s)"
TASK_ID="lifecycle-test-$(date +%s)"

echo "🧪 Starting Agent Lifecycle Test"
echo "Agent ID: $AGENT_ID"
echo "Task ID: $TASK_ID"

# Phase 1: Initialize (PRE-TASK HOOK)
echo "1️⃣ PHASE 1: Initializing agent..."
npx claude-flow@alpha hooks pre-task --description "Test agent lifecycle completion" --auto-spawn-agents false
echo "✅ Pre-task hook completed"

# Phase 2: Register agent
echo "2️⃣ PHASE 2: Registering agent..."
npx claude-flow@alpha hooks agent-spawned --name "$AGENT_ID" --type "test"
echo "✅ Agent registered"

# Phase 3: Simulate work with progress tracking
echo "3️⃣ PHASE 3: Simulating work..."
for i in {1..3}; do
  echo "  📝 Work step $i..."
  npx claude-flow@alpha hooks post-edit --file "test-work-step-$i" --memory-key "agent/$AGENT_ID/step-$i"
  sleep 1
done
echo "✅ Work phases completed"

# Phase 4: Share findings
echo "4️⃣ PHASE 4: Sharing findings..."
npx claude-flow@alpha hooks notify --message "Test agent completed all work steps successfully" --level "success"
echo "✅ Findings shared"

# Phase 5: Complete lifecycle (POST-TASK HOOK)
echo "5️⃣ PHASE 5: Completing lifecycle..."
npx claude-flow@alpha hooks post-task --task-id "$TASK_ID" --analyze-performance true
echo "✅ Post-task hook completed"

echo "🎉 Agent lifecycle test completed successfully!"
echo "Agent ID: $AGENT_ID should NOT be orphaned"
```

## Lifecycle Validation Test

### Test 1: Single Agent Completion

Create a test to verify single agent completes properly:

```javascript
// Test agent using Task tool with proper lifecycle
Task(`
You are a Test Agent for lifecycle validation.

AGENT ID: lifecycle-test-agent-001

MANDATORY LIFECYCLE COORDINATION:

1. INITIALIZE:
   npx claude-flow@alpha hooks pre-task --description "Validate agent lifecycle completion" --auto-spawn-agents false
   
2. REGISTER:
   npx claude-flow@alpha hooks agent-spawned --name "lifecycle-test-agent-001" --type "validator"
   
3. WORK SIMULATION:
   npx claude-flow@alpha hooks post-edit --file "validation-step-1" --memory-key "agent/lifecycle-test-agent-001/step-1"
   npx claude-flow@alpha hooks post-edit --file "validation-step-2" --memory-key "agent/lifecycle-test-agent-001/step-2"
   npx claude-flow@alpha hooks post-edit --file "validation-step-3" --memory-key "agent/lifecycle-test-agent-001/step-3"
   
4. REPORT FINDINGS:
   npx claude-flow@alpha hooks notify --message "Lifecycle test agent completed validation successfully" --level "success"
   
5. COMPLETE:
   npx claude-flow@alpha hooks post-task --task-id "lifecycle-test-validation" --analyze-performance true

YOUR TASK: Validate that you can complete a full lifecycle without becoming orphaned.

COMPLETION CRITERIA: When all 5 coordination steps are finished, you are complete.

CRITICAL: You MUST complete step 5 or you will become an orphaned agent!
`)
```

### Test 2: Multiple Agent Coordination

Test multiple agents completing in parallel:

```javascript
// Spawn 3 test agents simultaneously
const agents = [
  'lifecycle-multi-test-001',
  'lifecycle-multi-test-002', 
  'lifecycle-multi-test-003'
];

agents.forEach((agentId, index) => {
  Task(`
  You are Test Agent ${agentId} for multi-agent lifecycle validation.
  
  MANDATORY LIFECYCLE:
  1. npx claude-flow@alpha hooks pre-task --description "Multi-agent test ${index + 1}" --auto-spawn-agents false
  2. npx claude-flow@alpha hooks agent-spawned --name "${agentId}" --type "multi-test"
  3. npx claude-flow@alpha hooks post-edit --file "multi-test-${index}" --memory-key "agent/${agentId}/work"
  4. npx claude-flow@alpha hooks notify --message "Agent ${agentId} completed work" --level "success"
  5. npx claude-flow@alpha hooks post-task --task-id "multi-test-${agentId}" --analyze-performance true
  
  TASK: Complete your lifecycle as agent ${index + 1} of 3.
  COMPLETION: When all 5 steps are done.
  `);
});
```

## Validation Checks

### Check 1: Orphan Detection

After running tests, check for orphaned agents:

```bash
echo "🔍 ORPHAN DETECTION TEST"

# Get all registered agents
REGISTERED=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/registered" 2>/dev/null | wc -l)
echo "📊 Registered agents: $REGISTERED"

# Get all completed agents  
COMPLETED=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/completed" 2>/dev/null | wc -l)
echo "📊 Completed agents: $COMPLETED"

# Calculate orphans
ORPHANS=$((REGISTERED - COMPLETED))
echo "📊 Potential orphans: $ORPHANS"

if [ $ORPHANS -eq 0 ]; then
  echo "✅ SUCCESS: No orphaned agents detected"
else
  echo "❌ FAILURE: $ORPHANS agents may be orphaned"
  echo "🚨 This could cause API errors!"
fi
```

### Check 2: Memory State Validation

Verify agent states in memory:

```bash
echo "💾 MEMORY STATE VALIDATION"

# Check for agents that started but never completed
npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/started" > started_agents.txt
npx claude-flow@alpha hooks session-restore --pattern "agent/*/lifecycle/completed" > completed_agents.txt

# Find agents that started but didn't complete
INCOMPLETE=$(comm -23 started_agents.txt completed_agents.txt)

if [ -z "$INCOMPLETE" ]; then
  echo "✅ SUCCESS: All started agents completed properly"
else
  echo "❌ FAILURE: Some agents started but never completed:"
  echo "$INCOMPLETE"
fi

# Cleanup temp files
rm -f started_agents.txt completed_agents.txt
```

### Check 3: Resource Cleanup Validation

Verify no resources are leaked:

```bash
echo "🧹 RESOURCE CLEANUP VALIDATION"

# Check for lingering processes
CLAUDE_PROCESSES=$(ps aux | grep "claude-flow" | grep -v grep | wc -l)
echo "📊 Active claude-flow processes: $CLAUDE_PROCESSES"

# Check memory usage
MEMORY_USAGE=$(npx claude-flow@alpha hooks session-restore --pattern "agent/*" 2>/dev/null | wc -l)
echo "📊 Memory entries: $MEMORY_USAGE"

if [ $CLAUDE_PROCESSES -eq 0 ]; then
  echo "✅ SUCCESS: No lingering processes"
else
  echo "⚠️ WARNING: $CLAUDE_PROCESSES claude-flow processes still running"
fi
```

## Test Results Analysis

After running all tests, analyze results:

### Success Criteria
- ✅ All spawned agents complete their post-task hook
- ✅ No orphaned agents detected in memory
- ✅ No lingering processes or resource leaks
- ✅ Memory state shows proper lifecycle completion

### Failure Indicators  
- ❌ Agents that started but never completed
- ❌ Orphaned agents consuming memory
- ❌ API errors from resource exhaustion
- ❌ Inconsistent memory state

## Test Execution Plan

1. **Run single agent test** → Verify basic lifecycle completion
2. **Run multi-agent test** → Verify parallel completion
3. **Execute orphan detection** → Check for incomplete agents
4. **Validate memory state** → Confirm proper cleanup
5. **Monitor resource usage** → Ensure no leaks

This testing validates that the agent lifecycle management system prevents orphaned agents and API errors.