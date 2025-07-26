#!/usr/bin/env python3
"""
Test file to trigger post-edit hook with Claude-visible feedback
"""

def calculate_sum(a, b):
    """Calculate the sum of two numbers"""
    return a + b

def main():
    print("Testing enhanced hook visibility")
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()