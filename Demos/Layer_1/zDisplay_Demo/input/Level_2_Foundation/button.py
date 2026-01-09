#!/usr/bin/env python3
"""
Level 2: Foundation - button()
===============================

Goal:
    See how button() confirms user actions with yes/no.
    Requires explicit confirmation - no accidental destructive actions.

Run:
    python Demos/Layer_1/zDisplay_Demo/input/Level_2_Foundation/button.py
"""

import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zKernel import zKernel


def run_demo():
    """Demonstrate button confirmation input."""
    z = zKernel({"logger": "PROD"})

    z.display.line("")
    z.display.line("=== Level 2A: button() - Action confirmation ===")
    z.display.line("")

    # Basic confirmation
    z.display.line("1. Safe action (green):")
    if z.display.button("Save Profile", color="success"):
        z.display.success("✅ Profile saved!")
    else:
        z.display.info("Profile not saved")

    z.display.line("")

    # Destructive action
    z.display.line("2. Dangerous action (red):")
    if z.display.button("Delete Account", color="danger"):
        z.display.warning("⚠️ Account marked for deletion!")
    else:
        z.display.info("Account deletion cancelled")

    z.display.line("")

    # Workflow example
    z.display.line("3. Multi-step workflow:")
    if z.display.button("Start Backup", color="info"):
        z.display.info("Preparing backup...", indent=1)
        if z.display.button("Confirm Backup", color="success"):
            z.display.success("✓ Backup completed!", indent=1)
        else:
            z.display.warning("Backup cancelled", indent=1)
    else:
        z.display.info("Backup not started")

    z.display.line("")
    z.display.line("Key point: button() requires explicit y/n confirmation.")
    z.display.line("           Color-coded by action type (success, danger, info).")
    z.display.line("           Returns True (yes) or False (no).")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

