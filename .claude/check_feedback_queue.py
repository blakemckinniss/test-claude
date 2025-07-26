#!/usr/bin/env python3
"""
Check and display current deferred feedback queue
"""

import sys
from pathlib import Path

# Add hooks directory to path
hooks_dir = Path(__file__).parent / 'hooks'
sys.path.insert(0, str(hooks_dir))

try:
    from deferred_feedback import deferred_feedback, has_queued_feedback, deliver_queued_feedback
    
    print("🔍 Deferred Feedback Queue Status")
    print("=" * 40)
    
    if has_queued_feedback():
        feedback = deliver_queued_feedback()
        print("📢 PENDING FEEDBACK FOUND:")
        print()
        print(feedback)
        print()
        print("✅ Feedback queue has been cleared after display")
    else:
        print("📭 No pending feedback in queue")
        
except ImportError as e:
    print(f"❌ Could not import deferred feedback system: {e}")
    print("Make sure deferred_feedback.py exists in .claude/hooks/")
except Exception as e:
    print(f"❌ Error checking feedback queue: {e}")