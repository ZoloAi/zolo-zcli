#!/usr/bin/env python3
"""
Level 1: Primitives - read_password()
======================================

Goal:
    See how read_password() collects secure password input.
    Just like read_string(), but masks the input with asterisks (***).

Run:
    python Demos/Layer_1/zDisplay_Demo/input/Level_1_Primitives/read_password.py
"""

import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zCLI import zCLI


def run_demo():
    """Demonstrate masked password input collection."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.line("=== Level 1E: read_password() - Masked input ===")
    z.display.line("")

    # Simple password prompt
    z.display.line("Try typing a password (you won't see it):")
    password = z.display.read_password("Password: ")
    z.display.line(f"✓ Password captured ({len(password)} characters)")

    z.display.line("")

    # Use case: Authentication flow
    z.display.line("--- Login simulation ---")
    username = z.display.read_string("Username: ")
    password = z.display.read_password("Password: ")
    
    z.display.line("")
    if username and password:
        z.display.line(f"✓ Credentials collected for: {username}")
        z.display.line(f"  Password length: {len(password)} characters")
    else:
        z.display.line("✗ Username and password are required")

    z.display.line("")
    z.display.line("Key point: read_password() masks input for security.")
    z.display.line("           The user's typing is hidden from view.")
    z.display.line("           Perfect for passwords, API keys, tokens.")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

