#!/usr/bin/env python3
"""
Test script to validate post-edit hook safety fixes
This ensures hooks don't break Claude API tool execution sequences
"""

def test_function():
    """Test function to trigger post-edit hook"""
    print("Testing hook safety - this should not cause API errors")
    return "success"

if __name__ == "__main__":
    result = test_function()
    print(f"Test result: {result}")