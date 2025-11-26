#!/usr/bin/env python3
"""
Level 2: Foundation - selection()
==================================

Goal:
    See how selection() lets users choose from a list.
    Single choice or multiple choices, with optional defaults.

Run:
    python Demos/Layer_1/zDisplay_Demo/input/Level_2_Foundation/selection.py
"""

import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zCLI import zCLI


def run_demo():
    """Demonstrate selection input."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.line("=== Level 2B: selection() - Choose from list ===")
    z.display.line("")

    # Single selection
    z.display.line("1. Single choice:")
    role = z.display.selection(
        "Select your role:",
        ["Developer", "Designer", "Manager"]
    )
    z.display.success(f"Selected: {role}")

    z.display.line("")

    # Multi-selection
    z.display.line("2. Multiple choices:")
    skills = z.display.selection(
        "Select your skills:",
        ["Python", "JavaScript", "React", "Django"],
        multi=True
    )
    z.display.success(f"Selected: {', '.join(skills) if skills else 'None'}")

    z.display.line("")

    # Selection with default
    z.display.line("3. With default (press Enter to accept):")
    theme = z.display.selection(
        "Choose theme:",
        ["Light", "Dark", "Auto"],
        default="Dark"
    )
    z.display.success(f"Selected: {theme}")

    z.display.line("")
    z.display.line("Key point: selection() displays numbered options.")
    z.display.line("           User types number(s) to select.")
    z.display.line("           multi=True allows multiple selections.")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

