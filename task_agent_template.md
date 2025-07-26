# Task Agent Template with Full Coordination

## PHASE 2: Proper Task Agent Format Template

This template ensures all Task agents complete their full lifecycle without becoming orphaned.

## Complete Task Agent Template

When spawning agents using the Task tool, use this exact format:

```javascript
Task(`
You are the [Agent Type] agent in a coordinated swarm.

MANDATORY LIFECYCLE COORDINATION (PREVENTS API ERRORS):

1. INITIALIZE (REQUIRED FIRST STEP):
   Run: npx claude-flow@alpha hooks pre-task --description "Your specific task description" --auto-spawn-agents false
   
2. WORK PHASE (REQUIRED AFTER EACH OPERATION):
   After EVERY file operation, decision, or major step:
   Run: npx claude-flow@alpha hooks post-edit --file "[filepath or 'decision']" --memory-key "agent/[your-name]/[step-number]"
   
3. COORDINATE (REQUIRED FOR DECISIONS):
   When making important findings or decisions:
   Run: npx claude-flow@alpha hooks notification --message "Your decision or finding" --telemetry true
   
4. COMPLETE (REQUIRED FINAL STEP):
   When ALL work is finished:
   Run: npx claude-flow@alpha hooks post-task --task-id "[your-task-id]" --analyze-performance true

YOUR SPECIFIC TASK:
[Detailed task description goes here]

COMPLETION CRITERIA:
[Clear criteria for when the agent should run post-task hook]

REMEMBER: You MUST complete all 4 coordination steps or you will become an orphaned agent causing API errors!
`)
```

## Example: Proper Research Agent

```javascript
Task(`
You are the Research Agent in a coordinated swarm.

MANDATORY LIFECYCLE COORDINATION:

1. INITIALIZE:
   npx claude-flow@alpha hooks pre-task --description "Research API best practices for authentication" --auto-spawn-agents false
   
2. WORK PHASE:
   After each research step:
   npx claude-flow@alpha hooks post-edit --file "research-step-[N]" --memory-key "agent/researcher/step-[N]"
   
3. COORDINATE:
   npx claude-flow@alpha hooks notification --message "Found JWT best practices documentation" --telemetry true
   
4. COMPLETE:
   npx claude-flow@alpha hooks post-task --task-id "research-auth-patterns" --analyze-performance true

YOUR TASK: Research authentication patterns for REST APIs, focusing on JWT implementation and security best practices.

COMPLETION CRITERIA: When you have documented 3-5 authentication patterns with pros/cons analysis.

REMEMBER: Complete all coordination steps to prevent becoming orphaned!
`)
```

## Why This Template Prevents Orphaned Agents

1. **Clear Lifecycle**: Each agent knows exactly what steps to complete
2. **Mandatory Hooks**: No agent can skip coordination requirements
3. **Completion Criteria**: Agents know when they're finished
4. **Error Prevention**: Proper cleanup prevents API errors
5. **Trackable**: Swarm can monitor agent progress and completion

## Template Validation Checklist

Before spawning any Task agent, verify:
- ✅ Pre-task hook command included
- ✅ Post-edit hook pattern specified
- ✅ Notification hook usage defined
- ✅ Post-task hook requirement stated
- ✅ Clear completion criteria provided
- ✅ Agent knows when to terminate

## Common Mistakes That Create Orphaned Agents

❌ **Wrong**: Task("Do research on APIs")
- No coordination instructions
- No completion criteria
- No lifecycle management

✅ **Right**: Use the full template above with all 4 mandatory hooks

This template ensures every Task agent completes its full lifecycle properly.