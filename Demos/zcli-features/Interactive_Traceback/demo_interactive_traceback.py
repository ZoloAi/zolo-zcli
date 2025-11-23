#!/usr/bin/env python3
"""Demo script to actually see the interactive traceback UI in action."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from zCLI import zCLI


def failing_operation():
    """A function that will fail."""
    print("  [RUNNING] Attempting to divide by zero...")
    return 10 / 0


def main():
    print("\n" + "="*70)
    print("Interactive Traceback Demo - zCLI v1.5.3")
    print("="*70)
    print("\nThis will trigger a ZeroDivisionError and launch the interactive UI.")
    print("You'll see a menu with options to:")
    print("  1. View Details")
    print("  2. Full Traceback")
    print("  3. Exception History")
    print("  4. Exit")
    print()
    
    # Initialize zCLI
    print("\nInitializing zCLI...")
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    print("[OK] zCLI initialized\n")
    
    # Trigger an exception and launch interactive UI
    print("="*70)
    print("Triggering Exception...")
    print("="*70)
    
    try:
        failing_operation()
    except Exception as e:
        print(f"\n[CAUGHT] {type(e).__name__}: {e}")
        print("\n[LAUNCHING] Interactive Traceback UI...\n")
        
        # Launch the interactive traceback UI
        result = zcli.zTraceback.interactive_handler(
            e,
            context={
                'demo': 'interactive_traceback',
                'test_value': 10,
                'operation': 'division by zero'
            }
        )
        
        print("\n" + "="*70)
        print(f"[RESULT] UI interaction complete. Returned: {result}")
        print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Demo interrupted by user")
        sys.exit(0)

