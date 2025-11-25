#!/usr/bin/env python3
"""
Level 1: Basic Outputs - header() and text()
==============================================

Goal:
    Learn the foundation of zDisplay output.
    - header() for formatted section titles
    - text() for content with indentation
    - Line breaks and spacing control

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_1_Outputs_Signals/outputs_simple.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate basic header and text output."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 1: Basic Outputs ===")
    print()
    
    # ============================================
    # 1. Simple Headers
    # ============================================
    z.display.header("Simple Header", color="CYAN", indent=0)
    z.display.text("Headers create visual separation between sections.")
    z.display.text("")
    
    # ============================================
    # 2. Text with Indentation
    # ============================================
    z.display.header("Text with Indentation", color="GREEN", indent=0)
    z.display.text("Text at indent level 0 (no indentation)")
    z.display.text("Text at indent level 1", indent=1)
    z.display.text("Text at indent level 2", indent=2)
    z.display.text("Text at indent level 3", indent=3)
    z.display.text("")
    
    # ============================================
    # 3. Line Breaks
    # ============================================
    z.display.header("Line Break Control", color="YELLOW", indent=0)
    z.display.text("This line has a break after it (default)", break_after=True)
    z.display.text("This line has NO break after", break_after=False)
    z.display.text("So this appears right after!", break_after=False)
    z.display.text("")  # Add spacing
    
    # ============================================
    # 4. Nested Headers
    # ============================================
    z.display.header("Parent Section", color="MAGENTA", indent=0)
    z.display.text("Content under parent section")
    z.display.header("Child Section", color="BLUE", indent=1)
    z.display.text("Content under child section", indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ header() - Create section titles with colors")
    z.display.text("✓ text() - Display content with indentation")
    z.display.text("✓ indent parameter - Control nesting levels (0-3+)")
    z.display.text("✓ break_after - Control line spacing")
    z.display.text("")
    
    print("Tip: These basics power ALL other display events!")
    print()

if __name__ == "__main__":
    run_demo()

