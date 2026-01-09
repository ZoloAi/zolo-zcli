#!/usr/bin/env python3
"""
Level 2: Foundation - header()
===============================

Goal:
    Use header() to create formatted section headers with styling.
    Headers provide visual structure to your output.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/header.py
"""

from zKernel import zKernel


def run_demo():
    """Demonstrate formatted section headers."""
    z = zKernel({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 2A: header() - Formatted Headers", color="CYAN", style="wave")
    z.display.line("")

    # Style: full (═══)
    z.display.header("System Initialization", color="CYAN", style="full")

    # Style: single (───)
    z.display.header("Loading Configuration", color="GREEN", style="single")

    # Style: wave (~~~)
    z.display.header("Processing Data", color="YELLOW", style="wave")

    # With indentation
    z.display.header("Main Section", color="MAGENTA", indent=0, style="full")
    z.display.header("Subsection", color="BLUE", indent=1, style="single")

    z.display.line("")
    z.display.text("Key point: header() creates visual structure.")
    z.display.text("           Three styles: full (═), single (─), wave (~)")
    z.display.text("           Colors: CYAN, GREEN, YELLOW, MAGENTA, BLUE, RED")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

