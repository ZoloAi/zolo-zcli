#!/usr/bin/env python3
# zCLI/utils/test_plugin.py

"""
zCLI Test Plugin - Demonstrates plugin capabilities.

This plugin provides simple functions for testing plugin invocation
in schemas, workflows, and UI files.

Functions:
    hello_world(name): Returns a greeting string
    random_number(min_val, max_val): Returns a random integer
    get_plugin_info(): Returns plugin metadata
"""

import random


def hello_world(name="World"):
    """
    Return a greeting string.
    
    Args:
        name (str): Name to greet (default: "World")
        
    Returns:
        str: Greeting message
        
    Example:
        >>> hello_world("Alice")
        "Hello, Alice!"
    """
    return f"Hello, {name}!"


def random_number(min_val=0, max_val=100):
    """
    Generate a random integer between min_val and max_val (inclusive).
    
    Args:
        min_val (int): Minimum value (default: 0)
        max_val (int): Maximum value (default: 100)
        
    Returns:
        int: Random integer
        
    Example:
        >>> random_number(1, 10)
        7  # (random)
    """
    return random.randint(min_val, max_val)


def get_plugin_info():
    """
    Get plugin metadata.
    
    Returns:
        dict: Plugin information
    """
    return {
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Simple plugin for zCLI testing and demonstrations",
        "functions": ["hello_world", "random_number", "get_plugin_info"]
    }


def run_self_test():
    """
    Run plugin self-test.
    
    Returns:
        dict: Test results with status and details
    """
    try:
        # Test hello_world
        greeting1 = hello_world()
        greeting2 = hello_world("zCLI")
        
        # Test random_number
        num1 = random_number()
        num2 = random_number(1, 10)
        
        # Test get_plugin_info
        info = get_plugin_info()
        
        # Validate results
        assert greeting1 == "Hello, World!"
        assert greeting2 == "Hello, zCLI!"
        assert 0 <= num1 <= 100
        assert 1 <= num2 <= 10
        assert info["name"] == "Test Plugin"
        
        return {
            "status": "success",
            "tests_passed": 5,
            "results": {
                "hello_default": greeting1,
                "hello_custom": greeting2,
                "random_default": num1,
                "random_custom": num2,
                "plugin_info": info
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "tests_passed": 0
        }


if __name__ == "__main__":
    print("[TEST] zCLI Test Plugin - Self Test")
    print("=" * 50)
    
    result = run_self_test()
    
    if result["status"] == "success":
        print("[OK] Plugin self-test PASSED")
        print(f"[STATS] Tests passed: {result['tests_passed']}")
        print(f"[INFO] Default greeting: {result['results']['hello_default']}")
        print(f"[TARGET] Custom greeting: {result['results']['hello_custom']}")
        print(f"[RANDOM] Random (0-100): {result['results']['random_default']}")
        print(f"[RANDOM] Random (1-10): {result['results']['random_custom']}")
        print(f"[INFO] Plugin: {result['results']['plugin_info']['name']} v{result['results']['plugin_info']['version']}")
    else:
        print("[FAIL] Plugin self-test FAILED")
        print(f"[ERROR] Error: {result['error']}")
        exit(1)
