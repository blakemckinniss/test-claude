#!/usr/bin/env python3
"""
Test file for deferred feedback system
This should trigger a post-edit hook that queues feedback for later delivery
"""

def test_deferred_feedback():
    """Test function that should generate deferred feedback"""
    print("Testing deferred feedback system")
    print("This edit should queue feedback about Python validation")
    return "feedback_test_complete"

if __name__ == "__main__":
    result = test_deferred_feedback()
    print(f"Result: {result}")