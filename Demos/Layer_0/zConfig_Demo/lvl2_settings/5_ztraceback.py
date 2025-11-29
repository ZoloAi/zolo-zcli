#!/usr/bin/env python3
"""Level 2: zTraceback - Automatic Exception Handling

Enable automatic exception handling with zTraceback: True
No try/except needed - errors launch an interactive menu automatically!

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/5_ztraceback.py

What Happens:
    1. zTraceback: True installs sys.excepthook
    2. Error occurs in nested call stack (3 levels deep)
    3. Interactive menu launches AUTOMATICALLY
    4. No manual error handling code needed!

Call Stack (3 levels):
    run_demo() → handle_request() → process_data() → failing_operation()

Interactive Menu:
    - View Details: Error summary with location
    - Full Traceback: Complete nested call stack

Key Point:
    This is the SIMPLEST way to use zTraceback - just enable it
    and let it catch errors automatically. No try/except blocks!
"""

from zCLI import zCLI


def failing_operation():
    """Bottom layer - where the error originates."""
    return 10 / 0


def process_data(value):
    """Middle layer - processes data."""
    result = failing_operation()
    return result * value


def handle_request():
    """Top layer - entry point."""
    return process_data(5)


# Enable automatic traceback via zSpark
z = zCLI({
    "deployment": "Production",  # Keep console clean (auto-defaults to ERROR logging)
    "zTraceback": True,          # Enable automatic exception handling
})

print("\n# Session configuration:")
print(f"zTraceback : {z.session.get('zTraceback')}")
print(f"Deployment : {z.config.get_environment('deployment')}")
print(f"zLogger    : {z.session.get('zLogger')}")

print("\n# Triggering error (will be caught automatically)...")
print("# No try/except needed!\n")

# Just let the error happen - zTraceback will catch it!
result = handle_request()
print(f"Result: {result}")
