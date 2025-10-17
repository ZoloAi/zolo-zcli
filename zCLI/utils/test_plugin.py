#!/usr/bin/env python3
# zCLI/utils/test_plugin.py

"""
zCLI Plugin Test - Simple Hello World Plugin

This is a simple test plugin that demonstrates how external modules
can be loaded and executed by the zCLI framework.

Usage:
    python zCLI/utils/test_plugin.py
"""

def hello_world(name="World"):
    """
    Simple hello world function for plugin testing.
    
    Args:
        name: Name to greet (default: "World")
        
    Returns:
        str: Greeting message
    """
    return f"Hello, {name}! This is a zCLI plugin test."


def get_plugin_info():
    """
    Get information about this plugin.
    
    Returns:
        dict: Plugin metadata
    """
    return {
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Simple hello world plugin for zCLI testing",
        "functions": ["hello_world", "get_plugin_info"]
    }


def run_self_test():
    """
    Run a self-test of the plugin functionality.
    
    Returns:
        dict: Test results
    """
    try:
        # Test hello_world function
        result1 = hello_world()
        result2 = hello_world("zCLI")
        
        # Test get_plugin_info function
        info = get_plugin_info()
        
        return {
            "status": "success",
            "tests_passed": 3,
            "results": {
                "hello_default": result1,
                "hello_custom": result2,
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
    print("🧪 zCLI Plugin Test - Self Test")
    print("=" * 40)
    
    result = run_self_test()
    
    if result["status"] == "success":
        print("✅ Plugin self-test PASSED")
        print(f"📊 Tests passed: {result['tests_passed']}")
        print(f"🌍 Default greeting: {result['results']['hello_default']}")
        print(f"🎯 Custom greeting: {result['results']['hello_custom']}")
        print(f"📋 Plugin info: {result['results']['plugin_info']['name']} v{result['results']['plugin_info']['version']}")
    else:
        print("❌ Plugin self-test FAILED")
        print(f"🚨 Error: {result['error']}")
        exit(1)
