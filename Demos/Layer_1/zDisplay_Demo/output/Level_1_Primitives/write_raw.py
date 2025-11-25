#!/usr/bin/env python3
"""
Level 1: Primitives - write_raw()
=================================

Goal:
    See how write_raw() prints text immediately with no newline.
    Perfect for inline updates ("Loading..."), progress ticks, or
    combining manual spacing with higher-level display events.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_raw.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate raw output without automatic newlines."""
    z = zCLI({"logger": "PROD"})

    print()
    print("=== Level 1A: write_raw() - No newline added ===")
    print()

    z.display.write_raw("Downloading")
    z.display.write_raw("...")
    z.display.write_raw(" still working")
    z.display.write_raw(" (all on one line)")

    # Finish the line so the terminal prompt returns cleanly
    z.display.write_raw("\n")

    print("Tip: write_raw() is great for inline status without forcing a newline.")
    print()


if __name__ == "__main__":
    run_demo()
