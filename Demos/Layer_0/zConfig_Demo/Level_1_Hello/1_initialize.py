#!/usr/bin/env python3
"""Level 0: Hello zConfig
A minimal demo to initialize zCLI and understand what happens."""

from zCLI import zCLI

def run_demo():
    """Initialize zCLI - that's it!"""
    z = zCLI()

    print()
    print("✓ zCLI initialized - 18 subsystems ready")
    print()

if __name__ == "__main__":
    run_demo()
