#!/usr/bin/env python3
"""
Level 1: Primitives - raw()
============================

Goal:
    See how raw() prints text immediately with no newline.
    Perfect for inline updates, progress indicators, or building
    output piece by piece on the same line.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_raw.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate raw output without automatic newlines."""
    z = zCLI({"logger": "PROD"})

    print()
    print("=== Level 1A: raw() - No newline added ===")
    print()

    # All on one line - raw() never adds newlines
    z.display.raw("First")
    z.display.raw(" + ")
    z.display.raw("Second")
    z.display.raw(" + ")
    z.display.raw("Third")
    z.display.raw("\n")  # You control when to break

    print()

    # Use case: Building status messages
    z.display.raw("Status: ")
    z.display.raw("✓ Connected")
    z.display.raw("\n")

    print()
    print("Key point: raw() gives you full control.")
    print("           YOU decide when to add the newline.")
    print()


if __name__ == "__main__":
    run_demo()
