#!/usr/bin/env python3
"""
Level 2: Foundation - text()
=============================

Goal:
    Use text() to display content with indentation.
    text() builds on line() but adds indent control.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/text.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate text display with indentation."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 2B: text() - Text with Indentation", color="GREEN", style="wave")
    z.display.line("")

    # No indentation (indent=0)
    z.display.text("Main content at level 0", indent=0)

    # Indentation levels (each level = 2 spaces)
    z.display.text("  Content at level 1", indent=1)
    z.display.text("    Content at level 2", indent=2)
    z.display.text("      Content at level 3", indent=3)

    z.display.line("")

    # Hierarchical structure
    z.display.text("Configuration:", indent=0)
    z.display.text("Database: PostgreSQL", indent=1)
    z.display.text("Host: localhost", indent=2)
    z.display.text("Port: 5432", indent=2)
    z.display.text("Cache: Redis", indent=1)
    z.display.text("Host: localhost", indent=2)
    z.display.text("Port: 6379", indent=2)

    z.display.line("")

    # With pause=True (pauses for Enter)
    z.display.text("This is a text with pause=True...", indent=0, pause=True)

    z.display.text("Continued after user acknowledgment", indent=0)

    z.display.line("")
    z.display.text("Key point: text() adds indent control to line().")
    z.display.text("           Each indent level = 2 spaces")
    z.display.text("           pause=True pauses for user input")
    z.display.text("           Note: break_after still works (backward compatible)")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

