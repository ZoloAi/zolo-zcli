#!/usr/bin/env python3
"""Level 1: Initialize - Deployment Modes

Goal:
    Learn about the three deployment modes. This demo compares how each mode
    affects system behavior (banners, output, logging defaults).

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment.py
"""

from zCLI import zCLI

def run_demo():
    print("\n" + "="*60)
    print("  DEPLOYMENT MODES COMPARISON")
    print("="*60)

    # Three deployment modes available (uncomment to try each):
    # "Development" - Full output: banners + INFO logs (local dev)
    # "Testing"     - Clean logs only: no banners + INFO logs (staging/QA)
    # "Production"  - Minimal: no banners + ERROR logs (production)

    zSpark = {
        # "deployment": "Development",  # Full output
        # "deployment": "Testing",      # Clean logs
        "deployment": "Production",   # Minimal (active)
    }
    z = zCLI(zSpark)

    print("\n# Notice the difference:")
    print("  Did you see colorful banners above? (No = Production or Testing)")
    print("  This is deployment mode at work!")

    print("\n# Three deployment modes:")
    print("  Production  → No banners, minimal logging (silent)")
    print("  Testing     → No banners, detailed logging (clean)")
    print("  Development → Full banners, detailed logging (verbose)")

    print("\n# Try it yourself:")
    print("  1. Run this demo (currently in Production mode)")
    print("  2. Uncomment 'Testing' mode above and run again")
    print("  3. Uncomment 'Development' mode to see full banners")
    print("  4. Watch how the initialization output changes!")

    print("\n# Next:")
    print("  Level 2 will teach you how to use the logger in your code")
    print("  Level 3 will show you how to read configuration values")


if __name__ == "__main__":
    run_demo()
