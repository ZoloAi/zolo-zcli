#!/usr/bin/env python3
"""
Level 1: Primitives - block()
==============================

Goal:
    Send multiple lines at once while zDisplay handles the trailing newline.
    Great for small banners, status summaries, or preformatted text blocks.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_block.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate multi-line output with block()."""
    z = zCLI({"logger": "PROD"})

    print()
    print("=== Level 1C: block() - Multi-line output ===")
    print()

    block = """Deployment Summary
- Host: localhost
- Mode: Terminal
- Status: Ready to render"""

    z.display.block(block)

    print()
    print("block() keeps the formatting you supply and ends with a clean newline.")
    print("Note: write_block() still works as a backward-compatible alias.")
    print()


if __name__ == "__main__":
    run_demo()
