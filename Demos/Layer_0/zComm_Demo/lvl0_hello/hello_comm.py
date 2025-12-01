#!/usr/bin/env python3
"""
Level 0: Hello zComm - Your First Communication Demo
====================================================

After mastering zConfig's 5-layer hierarchy, you now have everything you need
to start using zComm - zCLI's communication layer for HTTP, services, and networking.

Goal:
    Build on your zConfig knowledge to explore zComm's capabilities.
    - Use the same zSpark pattern you learned in zConfig
    - Check if a network port is available
    - See how zComm auto-initializes alongside zConfig

Key Discovery:
    zComm requires zero additional setup - it's ready the moment you call zCLI().
    Just like zConfig, zComm is a Layer 0 subsystem that "just works."

Run:
    python Demos/Layer_0/zComm_Demo/lvl0_hello/hello_comm.py
"""

from zCLI import zCLI

def run_demo():
    """
    Initialize zCLI and demonstrate basic zComm functionality.
    
    Notice: We're using the same zSpark pattern from zConfig demos.
    """
    zSpark = {
        "deployment": "Production",
        "title": "hello-comm",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zCLI(zSpark)

    print()
    print("="*60)
    print("  HELLO ZCOMM - YOUR FIRST COMMUNICATION DEMO")
    print("="*60)

    # Check if common web port is available
    # This uses z.comm (Layer 0 subsystem)
    port = 8080
    is_available = z.comm.check_port(port)

    print()
    print(f"Port {port}: {'✓ available' if is_available else '✗ in use'}")
    print()
    print("# What you discovered:")
    print("  ✓ zComm auto-initializes with zCLI (Layer 0)")
    print("  ✓ Same zSpark pattern as zConfig demos")
    print("  ✓ Network utilities ready instantly")
    print("  ✓ Zero configuration required")
    print()
    print("# Next Steps:")
    print("  → Level 1: HTTP client, service detection")
    print("  → Level 2: Error handling, multiple services")
    print("  → Level 3: Service lifecycle management")
    print()

if __name__ == "__main__":
    run_demo()

