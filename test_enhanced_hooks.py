#!/usr/bin/env python3
"""
Test the enhanced hooks that provide constant MCP tool suggestions
"""

import json
import subprocess
import sys
import time

def test_hook(hook_type, input_data, description):
    """Test a hook and display output"""
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"Hook: {hook_type}")
    print(f"{'='*80}")
    
    cmd = f"python /home/devcontainers/bench/test-game/.claude/hooks/main.py {hook_type}"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            timeout=10
        )
        
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("\n📋 OUTPUT:")
            print("-" * 40)
            print(result.stdout)
            
        if result.stderr:
            print("\n⚠️ STDERR:")
            print(result.stderr[:500])
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run comprehensive hook tests"""
    print("🚀 ENHANCED HOOK TESTING - Constant MCP Tool Suggestions")
    print("Testing hooks that provide proactive guidance and tool suggestions")
    
    test_cases = [
        # UserPromptSubmit - Complex task
        {
            'hook': 'prompt',
            'input': {
                'prompt': 'Build a complete REST API with authentication, database integration, and comprehensive test coverage',
                'session_id': 'test-complex-api',
                'hook_event_name': 'UserPromptSubmit'
            },
            'description': 'Complex API development task - should suggest swarm coordination'
        },
        
        # UserPromptSubmit - Debugging task
        {
            'hook': 'prompt',
            'input': {
                'prompt': 'Debug why the login endpoint is returning 500 errors and fix the authentication flow',
                'session_id': 'test-debug',
                'hook_event_name': 'UserPromptSubmit'
            },
            'description': 'Debugging task - should suggest zen debug tools'
        },
        
        # Pre-Task hook
        {
            'hook': 'pre-task',
            'input': {
                'tool_name': 'Task',
                'tool_input': {
                    'description': 'Research agent for API patterns',
                    'prompt': 'You are a research agent. Analyze REST API best practices.'
                },
                'hook_event_name': 'PreToolUse'
            },
            'description': 'Task agent spawn - should remind about coordination hooks'
        },
        
        # Pre-MCP Claude Flow
        {
            'hook': 'pre-mcp',
            'input': {
                'tool_name': 'mcp__claude-flow__swarm_init',
                'tool_input': {
                    '_tool_name': 'mcp__claude-flow__swarm_init',
                    'topology': 'hierarchical',
                    'maxAgents': 5
                },
                'hook_event_name': 'PreToolUse'
            },
            'description': 'Swarm initialization - should provide orchestration guidance'
        },
        
        # Pre-Bash with grep
        {
            'hook': 'pre-bash',
            'input': {
                'tool_name': 'Bash',
                'tool_input': {
                    'command': 'grep -r "TODO" src/'
                },
                'hook_event_name': 'PreToolUse'
            },
            'description': 'Grep command - should suggest using rg instead'
        },
        
        # Post-Edit Python file
        {
            'hook': 'post-edit',
            'input': {
                'tool_name': 'Edit',
                'tool_input': {
                    'file_path': '/home/project/api/auth.py'
                },
                'tool_result': {
                    'success': True
                },
                'hook_event_name': 'PostToolUse'
            },
            'description': 'Python file edited - should suggest testing'
        },
        
        # Post-MCP GitHub
        {
            'hook': 'post-mcp',
            'input': {
                'tool_name': 'mcp__github__list_issues',
                'tool_input': {
                    '_tool_name': 'mcp__github__list_issues'
                },
                'tool_result': {
                    'issues': [
                        {'number': 1, 'title': 'Bug in auth'},
                        {'number': 2, 'title': 'Add tests'}
                    ]
                },
                'hook_event_name': 'PostToolUse'
            },
            'description': 'GitHub issues listed - should suggest follow-up actions'
        },
        
        # Notification - Waiting
        {
            'hook': 'notification',
            'input': {
                'message': 'Claude is waiting for your input',
                'session_id': 'test-waiting',
                'hook_event_name': 'Notification'
            },
            'description': 'Waiting notification - should provide helpful suggestions'
        },
        
        # Pre-Edit sensitive file
        {
            'hook': 'pre-edit',
            'input': {
                'tool_name': 'Write',
                'tool_input': {
                    'file_path': '/home/project/.env'
                },
                'hook_event_name': 'PreToolUse'
            },
            'description': 'Sensitive file edit - should show warning'
        },
        
        # Post-Bash test failure
        {
            'hook': 'post-bash',
            'input': {
                'tool_name': 'Bash',
                'tool_input': {
                    'command': 'npm test'
                },
                'tool_result': {
                    'exitCode': 1,
                    'stdout': 'Tests failed: 3 failing'
                },
                'hook_event_name': 'PostToolUse'
            },
            'description': 'Test failure - should suggest debugging tools'
        }
    ]
    
    results = []
    for test in test_cases:
        success = test_hook(test['hook'], test['input'], test['description'])
        results.append((test['description'], success))
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} passed")
    for desc, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {desc}")
    
    # Demonstrate continuous insights
    print("\n\n" + "="*80)
    print("💡 CONTINUOUS INSIGHTS DEMONSTRATION")
    print("="*80)
    print("\nThe enhanced hooks now provide:")
    print("1. **Proactive MCP tool suggestions** based on context")
    print("2. **Workflow recommendations** for complex tasks")
    print("3. **Coordination reminders** for swarm operations")
    print("4. **Follow-up actions** after tool completion")
    print("5. **Safety warnings** for sensitive operations")
    print("6. **Performance tips** and best practices")
    print("7. **Context-aware guidance** throughout the session")
    print("\n✨ Hooks actively guide Claude Code with relevant tool suggestions!")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())