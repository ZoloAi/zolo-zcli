#!/usr/bin/env python3
"""
Level 1: Primitives - line()
=============================

Goal:
    Use line() to write single lines that always end with a newline.
    Perfect for log-style output where each entry should start on its own line.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_line.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate line() adding newlines for you."""
    z = zCLI({"logger": "PROD"})

    print()
    print("=== Level 1B: line() - Automatic newline ===")
    print()

    z.display.line("1) Each call becomes its own line")
    z.display.line("2) No need to append \\n manually")
    z.display.line("3) Works the same in Terminal or zBifrost")

    print()
    print("Notice how the terminal spacing stays clean without manual newline management.")
    print("Note: write_line() still works as a backward-compatible alias.")
    print()


if __name__ == "__main__":
    run_demo()
