#!/usr/bin/env python3
"""
Level 1: Primitives - read_string()
====================================

Goal:
    See how read_string() collects user text input.
    The most basic input primitive - prompt and capture.

Run:
    python Demos/Layer_1/zDisplay_Demo/input/Level_1_Primitives/read_string.py
"""

import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zKernel import zKernel


def run_demo():
    """Demonstrate basic string input collection."""
    z = zKernel({"logger": "PROD"})

    z.display.line("")
    z.display.line("=== Level 1D: read_string() - Collect text input ===")
    z.display.line("")

    # Simple prompt
    name = z.display.read_string("What's your name? ")
    z.display.line(f"Hello, {name}!")

    z.display.line("")

    # Use case: Configuration input
    z.display.line("--- Quick configuration ---")
    host = z.display.read_string("Database host [localhost]: ")
    if not host:
        host = "localhost"
    port = z.display.read_string("Database port [5432]: ")
    if not port:
        port = "5432"
    
    z.display.line("")
    z.display.line(f"✓ Configuration: {host}:{port}")

    z.display.line("")
    z.display.line("Key point: read_string() pauses and waits for user input.")
    z.display.line("           Returns the text they type (without the newline).")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

