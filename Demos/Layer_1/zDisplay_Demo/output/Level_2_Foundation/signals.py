#!/usr/bin/env python3
"""
Level 2: Foundation - Signals
==============================

Goal:
    Use signals for color-coded feedback messages.
    success() = green, error() = red, warning() = yellow,
    info() = cyan, zMarker() = magenta separator.

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/signals.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate all five signal types."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 2C: Signals - Color-Coded Feedback", color="MAGENTA", style="wave")
    z.display.line("")

    # Success (green ✓)
    z.display.success("Operation completed successfully")

    # Error (red ✗)
    z.display.error("Connection failed")

    # Warning (yellow ⚠)
    z.display.warning("Deprecated feature in use")

    # Info (cyan ℹ)
    z.display.info("Processing 10 records...")

    z.display.line("")

    # With indentation
    z.display.success("Database connected", indent=0)
    z.display.info("Host: localhost", indent=1)
    z.display.info("Port: 5432", indent=1)

    z.display.line("")

    # zMarker - visual separator
    z.display.zMarker("Checkpoint 1")
    z.display.info("Stage 1 complete")
    z.display.zMarker("Checkpoint 2", color="CYAN")
    z.display.info("Stage 2 complete")

    z.display.line("")
    z.display.text("Key point: Signals provide semantic feedback.")
    z.display.text("           success = green, error = red, warning = yellow")
    z.display.text("           info = cyan, zMarker = workflow separator")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

