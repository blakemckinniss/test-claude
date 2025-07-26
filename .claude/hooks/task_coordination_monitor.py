#!/usr/bin/env python3
"""
Task Coordination Monitor
Tracks Task agent execution and ensures full coordination workflow completion
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Set, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskCoordinationMonitor:
    """Monitors Task agent coordination workflow completion"""
    
    def __init__(self):
        self.hooks_dir = Path(__file__).parent
        self.cache_dir = self.hooks_dir / 'cache'
        self.task_dir = self.cache_dir / 'task_monitoring'
        self.task_dir.mkdir(parents=True, exist_ok=True)
        
        # Expected coordination workflow steps
        self.expected_coordination_hooks = {
            'pre-task': 'npx claude-flow@alpha hooks pre-task',
            'post-edit': 'npx claude-flow@alpha hooks post-edit', 
            'notification': 'npx claude-flow@alpha hooks notification',
            'post-task': 'npx claude-flow@alpha hooks post-task'
        }
    
    def start_task_monitoring(self, args: argparse.Namespace) -> None:
        """Start monitoring a new Task agent"""
        task_id = args.task_id or f"task_{int(time.time())}"
        
        logger.info(f"🔍 Starting Task coordination monitoring: {task_id}")
        
        # Create task monitoring record
        task_record = {
            'task_id': task_id,
            'description': getattr(args, 'description', ''),
            'prompt': getattr(args, 'prompt', ''),
            'start_time': time.time(),
            'expected_hooks': list(self.expected_coordination_hooks.keys()),
            'completed_hooks': [],
            'status': 'active',
            'coordination_score': 0.0
        }
        
        # Analyze prompt for coordination instructions
        prompt_text = task_record.get('prompt', '')
        has_coordination = self._analyze_coordination_instructions(prompt_text)
        
        if not has_coordination:
            logger.warning(f"⚠️ Task {task_id} missing coordination instructions!")
            task_record['warnings'] = ['Missing coordination hook instructions']
        
        # Save task record
        task_file = self.task_dir / f'{task_id}.json'
        with open(task_file, 'w') as f:
            json.dump(task_record, f, indent=2)
        
        logger.info(f"Task {task_id} monitoring initialized")
    
    def track_coordination_hook(self, args: argparse.Namespace) -> None:
        """Track execution of a coordination hook"""
        task_id = args.task_id
        hook_type = args.hook_type
        
        logger.info(f"📋 Tracking coordination hook: {hook_type} for task {task_id}")
        
        # Load task record
        task_file = self.task_dir / f'{task_id}.json'
        if not task_file.exists():
            logger.warning(f"Task record not found: {task_id}")
            return
        
        with open(task_file, 'r') as f:
            task_record = json.load(f)
        
        # Update coordination tracking
        if hook_type not in task_record.get('completed_hooks', []):
            task_record['completed_hooks'].append(hook_type)
            task_record['coordination_score'] = len(task_record['completed_hooks']) / len(task_record['expected_hooks'])
            
            logger.info(f"Hook {hook_type} completed. Score: {task_record['coordination_score']:.2f}")
        
        # Save updated record
        with open(task_file, 'w') as f:
            json.dump(task_record, f, indent=2)
    
    def validate_task_completion(self, args: argparse.Namespace) -> None:
        """Validate Task agent completed full coordination workflow"""
        task_id = args.task_id
        
        logger.info(f"✅ Validating Task completion: {task_id}")
        
        # Load task record
        task_file = self.task_dir / f'{task_id}.json'
        if not task_file.exists():
            logger.error(f"❌ Task record not found: {task_id}")
            self._report_missing_task(task_id)
            return
        
        with open(task_file, 'r') as f:
            task_record = json.load(f)
        
        # Check coordination completion
        completed_hooks = set(task_record.get('completed_hooks', []))
        expected_hooks = set(task_record.get('expected_hooks', []))
        missing_hooks = expected_hooks - completed_hooks
        
        coordination_score = task_record.get('coordination_score', 0.0)
        
        if coordination_score < 1.0:
            logger.error(f"❌ INCOMPLETE TASK COORDINATION: {task_id}")
            self._report_incomplete_coordination(task_id, missing_hooks, coordination_score)
        else:
            logger.info(f"✅ Task {task_id} completed full coordination workflow")
            self._report_successful_coordination(task_id)
        
        # Mark task as completed
        task_record['status'] = 'completed'
        task_record['end_time'] = time.time()
        task_record['duration'] = task_record['end_time'] - task_record['start_time']
        
        with open(task_file, 'w') as f:
            json.dump(task_record, f, indent=2)
    
    def _analyze_coordination_instructions(self, prompt: str) -> bool:
        """Check if prompt contains required coordination instructions"""
        coordination_keywords = [
            'npx claude-flow@alpha hooks pre-task',
            'npx claude-flow@alpha hooks post-edit',
            'npx claude-flow@alpha hooks notification', 
            'npx claude-flow@alpha hooks post-task'
        ]
        
        found_hooks = sum(1 for keyword in coordination_keywords if keyword in prompt)
        return found_hooks >= 3  # At least 3 out of 4 hooks should be mentioned
    
    def _report_incomplete_coordination(self, task_id: str, missing_hooks: Set[str], score: float) -> None:
        """Report incomplete Task coordination to Claude"""
        missing_list = '\n'.join(f"• {hook}" for hook in missing_hooks)
        
        error_message = f"""🚨 INCOMPLETE TASK COORDINATION DETECTED!

Task ID: {task_id}
Coordination Score: {score:.1%}
Missing coordination hooks:
{missing_list}

CRITICAL ISSUE: This Task agent did not execute the full coordination workflow!

Required coordination pattern:
1. START: npx claude-flow@alpha hooks pre-task --description '[task]'
2. DURING: npx claude-flow@alpha hooks post-edit --file '[file]' 
3. SHARE: npx claude-flow@alpha hooks notification --message '[decision]'
4. END: npx claude-flow@alpha hooks post-task --task-id '[task]'

IMMEDIATE ACTION REQUIRED:
• Terminate this incomplete Task agent
• Re-spawn with proper coordination instructions
• Ensure ALL Task agents include full coordination workflow
• Use swarm coordination patterns for complex tasks

This prevents broken agent coordination and ensures proper swarm execution!"""
        
        print(error_message, file=sys.stderr)
        sys.exit(2)  # Block execution and alert Claude
    
    def _report_successful_coordination(self, task_id: str) -> None:
        """Report successful Task coordination"""
        success_message = f"""✅ TASK COORDINATION COMPLETE

Task ID: {task_id}
Status: Full coordination workflow executed
Score: 100%

All required coordination hooks completed:
• ✅ pre-task (initialization)
• ✅ post-edit (progress tracking)  
• ✅ notification (decision sharing)
• ✅ post-task (completion)

Agent successfully coordinated with swarm! 🎯"""
        
        print(success_message)  # Success info for user
    
    def _report_missing_task(self, task_id: str) -> None:
        """Report missing task record"""
        error_message = f"""❌ TASK MONITORING FAILURE

Task ID: {task_id}
Issue: No coordination monitoring record found

This suggests the Task agent was spawned without proper monitoring setup!

REQUIRED: All Task agents must:
1. Be monitored from start to completion
2. Follow full coordination workflow
3. Execute all required coordination hooks
4. Report completion status

Re-spawn Task with proper coordination monitoring!"""
        
        print(error_message, file=sys.stderr)
        sys.exit(2)  # Block and alert Claude

def main():
    """Main entry point for Task coordination monitoring"""
    parser = argparse.ArgumentParser(description='Task Coordination Monitor')
    parser.add_argument('action', choices=['start', 'track', 'validate'])
    parser.add_argument('--task-id', help='Task identifier')
    parser.add_argument('--description', help='Task description')
    parser.add_argument('--prompt', help='Task prompt text')
    parser.add_argument('--hook-type', help='Coordination hook type')
    
    args = parser.parse_args()
    monitor = TaskCoordinationMonitor()
    
    if args.action == 'start':
        monitor.start_task_monitoring(args)
    elif args.action == 'track':
        monitor.track_coordination_hook(args)
    elif args.action == 'validate':
        monitor.validate_task_completion(args)
    else:
        logger.error(f"Unknown action: {args.action}")
        sys.exit(1)

if __name__ == '__main__':
    main()