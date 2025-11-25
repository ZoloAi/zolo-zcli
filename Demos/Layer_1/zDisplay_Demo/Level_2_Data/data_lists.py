#!/usr/bin/env python3
"""
Level 2: Lists - Bullets and Numbers
=====================================

Goal:
    Learn list() for presenting items with formatting.
    - Bullet style (• markers)
    - Number style (1, 2, 3...)
    - Letter style (a, b, c...)
    - Indentation support

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_lists.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate list formatting styles."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 2: Lists ===")
    print()
    
    # ============================================
    # 1. Bulleted Lists
    # ============================================
    z.display.header("Bulleted Lists", color="CYAN", indent=0)
    z.display.text("Best for unordered items and features:")
    
    features = [
        "Fast - Zero-config initialization",
        "Simple - Declarative API",
        "Multi-mode - Terminal and GUI",
        "Tested - 1,073+ tests passing",
        "Elegant - Swiper-style patterns"
    ]
    z.display.list(features, style="bullet", indent=1)
    z.display.text("")
    
    # ============================================
    # 2. Numbered Lists
    # ============================================
    z.display.header("Numbered Lists", color="GREEN", indent=0)
    z.display.text("Best for sequential steps and priorities:")
    
    steps = [
        "Initialize zCLI with zMode='zBifrost'",
        "Define display logic with z.display events",
        "Register WebSocket event handler",
        "Start server with z.walker.run()",
        "Open HTML client in browser"
    ]
    z.display.list(steps, style="number", indent=1)
    z.display.text("")
    
    # ============================================
    # 3. Letter Lists
    # ============================================
    z.display.header("Letter Lists", color="YELLOW", indent=0)
    z.display.text("Best for options and alternatives:")
    
    options = [
        "Continue with default settings",
        "Customize configuration",
        "Import from existing project",
        "Start from scratch"
    ]
    z.display.list(options, style="letter", indent=1)
    z.display.text("")
    
    # ============================================
    # 4. Nested Lists with Indentation
    # ============================================
    z.display.header("Nested Lists", color="MAGENTA", indent=0)
    z.display.text("Combine with indentation for hierarchy:")
    
    z.display.text("zCLI Layers:", indent=0)
    z.display.list([
        "Layer 0: Foundation (zConfig, zComm, zDisplay)",
        "Layer 1: Core Services (zAuth, zDispatch, zParser)",
        "Layer 2: Business Logic (zFunc, zDialog, zData)",
        "Layer 3: Orchestration (zShell, zWalker, zServer)"
    ], style="number", indent=1)
    z.display.text("")
    
    # ============================================
    # 5. Real-World Example
    # ============================================
    z.display.header("Real-World Example: Installation Checklist", color="BLUE", indent=0)
    
    z.display.text("Prerequisites:", indent=0)
    prereqs = [
        "Python 3.8 or higher",
        "pip package manager",
        "Git for cloning repository"
    ]
    z.display.list(prereqs, style="bullet", indent=1)
    z.display.text("")
    
    z.display.text("Installation Steps:", indent=0)
    install_steps = [
        "Clone the repository",
        "Install dependencies",
        "Run test suite",
        "Verify installation"
    ]
    z.display.list(install_steps, style="number", indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ list() with style='bullet' - Unordered items")
    z.display.text("✓ list() with style='number' - Sequential steps")
    z.display.text("✓ list() with style='letter' - Options/alternatives")
    z.display.text("✓ Indentation - Create visual hierarchy")
    z.display.text("")
    
    print("Tip: Lists are perfect for presenting features and steps!")
    print()

if __name__ == "__main__":
    run_demo()

