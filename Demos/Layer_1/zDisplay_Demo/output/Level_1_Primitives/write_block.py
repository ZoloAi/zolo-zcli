#!/usr/bin/env python3
"""
Level 1: Primitives - write_block()
==================================

Goal:
    Send multiple lines at once while zDisplay handles the trailing newline.
    Great for small banners, status summaries, or preformatted text blocks.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_block.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate multi-line output with write_block()."""
    z = zCLI({"logger": "PROD"})

    print()
    print("=== Level 1C: write_block() - Multi-line output ===")
    print()

    block = """Deployment Summary
- Host: localhost
- Mode: Terminal
- Status: Ready to render"""

    z.display.write_block(block)

    print("write_block() keeps the formatting you supply and ends with a clean newline.")
    print()


if __name__ == "__main__":
    run_demo()
