#!/usr/bin/env python3
"""
Test script to validate hook compliance with separation of concerns
"""

import json
import subprocess
import sys
import tempfile
import os

def run_hook_test(hook_type, input_data, expected_behavior):
    """Run a hook and validate its behavior"""
    print(f"\n{'='*60}")
    print(f"Testing {hook_type} hook")
    print(f"{'='*60}")
    
    # Run the hook
    cmd = f"python /home/devcontainers/bench/test-game/.claude/hooks/main.py {hook_type}"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            timeout=30
        )
        
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("\n📋 OUTPUT:")
            print("-" * 40)
            print(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
            
        if result.stderr:
            print("\n⚠️ STDERR:")
            print(result.stderr[:500])
            
        # Validate behavior
        validation_results = []
        
        # Check for subprocess execution patterns
        if any(pattern in str(result.stderr) for pattern in ['subprocess.run', 'execute_command', 'Failed to run']):
            validation_results.append("❌ FAIL: Found subprocess execution attempt")
        else:
            validation_results.append("✅ PASS: No subprocess execution detected")
            
        # Check for instruction patterns
        if any(pattern in result.stdout for pattern in ['Tool:', 'Parameters:', 'Use the following', 'mcp__']):
            validation_results.append("✅ PASS: Returns instructions for MCP tools")
        else:
            validation_results.append("⚠️ WARN: No clear MCP tool instructions found")
            
        # Check for coordination patterns
        if hook_type == 'prompt' and 'swarm' in str(input_data).lower():
            if 'claude-flow@alpha hooks' in result.stdout:
                validation_results.append("✅ PASS: Includes coordination hook instructions")
            else:
                validation_results.append("⚠️ WARN: Missing coordination instructions")
                
        # Check exit code
        if result.returncode == 0:
            validation_results.append("✅ PASS: Successful exit code")
        else:
            validation_results.append(f"❌ FAIL: Non-zero exit code: {result.returncode}")
            
        print("\n🔍 VALIDATION RESULTS:")
        for vr in validation_results:
            print(f"  {vr}")
            
        return all('PASS' in vr or 'WARN' in vr for vr in validation_results)
        
    except subprocess.TimeoutExpired:
        print("❌ FAIL: Hook timed out")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error running hook: {e}")
        return False


def test_user_prompt_submit():
    """Test UserPromptSubmit hook with various prompts"""
    test_cases = [
        {
            'name': 'Simple task',
            'input': {
                'prompt': 'Fix the typo in README.md',
                'session_id': 'test-simple',
                'hook_event_name': 'UserPromptSubmit'
            },
            'expected': 'instructions'
        },
        {
            'name': 'Complex task requiring swarm',
            'input': {
                'prompt': 'Build a complete REST API with authentication, database, and comprehensive tests',
                'session_id': 'test-complex',
                'hook_event_name': 'UserPromptSubmit'
            },
            'expected': 'swarm_instructions'
        },
        {
            'name': 'Debugging task',
            'input': {
                'prompt': 'Debug why the login endpoint is returning 500 errors',
                'session_id': 'test-debug',
                'hook_event_name': 'UserPromptSubmit'
            },
            'expected': 'debug_instructions'
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"\n\n{'*'*80}")
        print(f"TEST CASE: {test['name']}")
        print(f"{'*'*80}")
        
        success = run_hook_test('prompt', test['input'], test['expected'])
        results.append((test['name'], success))
        
    return results


def test_pre_hooks():
    """Test PreToolUse hooks"""
    test_cases = [
        {
            'name': 'Pre-bash with claude-flow command',
            'hook': 'pre-bash',
            'input': {
                'tool_input': {
                    'command': 'npx claude-flow@alpha hooks pre-task --description "Starting work"'
                }
            }
        },
        {
            'name': 'Pre-task with agent spawn',
            'hook': 'pre-task',
            'input': {
                'tool_input': {
                    'prompt': 'You are a researcher agent. Analyze the codebase.',
                    'description': 'Research agent'
                }
            }
        },
        {
            'name': 'Pre-mcp with claude-flow tool',
            'hook': 'pre-mcp',
            'input': {
                'tool_input': {
                    '_tool_name': 'mcp__claude-flow__swarm_init'
                }
            }
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"\n\n{'*'*80}")
        print(f"TEST CASE: {test['name']}")
        print(f"{'*'*80}")
        
        success = run_hook_test(test['hook'], test['input'], 'monitoring')
        results.append((test['name'], success))
        
    return results


def check_file_patterns():
    """Check hook files for problematic patterns"""
    print("\n\n" + "="*80)
    print("🔍 CHECKING HOOK FILES FOR SUBPROCESS PATTERNS")
    print("="*80)
    
    patterns_to_check = [
        'subprocess.run',
        'subprocess.Popen',
        'os.system',
        'execute_command',
        'process_manager.execute_command'
    ]
    
    files_to_check = [
        '.claude/hooks/processors/user_prompt/workflows.py',
        '.claude/hooks/processors/user_prompt/mcp_tools.py',
        '.claude/hooks/main.py'
    ]
    
    found_issues = []
    
    for file_path in files_to_check:
        full_path = f"/home/devcontainers/bench/test-game/{file_path}"
        if os.path.exists(full_path):
            print(f"\nChecking {file_path}...")
            with open(full_path, 'r') as f:
                content = f.read()
                
            for pattern in patterns_to_check:
                if pattern in content:
                    # Check if it's in a comment or string
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern in line and not line.strip().startswith('#'):
                            # Additional check for instruction strings
                            if 'instruction' in line.lower() or 'Use the following' in line:
                                continue
                            found_issues.append(f"{file_path}:{i} - Found '{pattern}'")
                            
    if found_issues:
        print("\n❌ PROBLEMATIC PATTERNS FOUND:")
        for issue in found_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No subprocess execution patterns found in active code!")
        
    return len(found_issues) == 0


def main():
    """Run all compliance tests"""
    print("🚀 HOOK COMPLIANCE TEST SUITE")
    print("Testing separation of concerns: Claude Code executes, hooks provide instructions")
    
    all_results = []
    
    # Test UserPromptSubmit
    prompt_results = test_user_prompt_submit()
    all_results.extend(prompt_results)
    
    # Test Pre hooks
    pre_results = test_pre_hooks()
    all_results.extend(pre_results)
    
    # Check file patterns
    pattern_check = check_file_patterns()
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in all_results if success)
    total = len(all_results)
    
    print(f"\nHook Tests: {passed}/{total} passed")
    for name, success in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
        
    print(f"\nFile Pattern Check: {'✅ PASS' if pattern_check else '❌ FAIL'}")
    
    # Overall result
    all_passed = passed == total and pattern_check
    print(f"\n{'✅ ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED!'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())