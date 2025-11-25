#!/usr/bin/env python3
"""
Level 2: Hierarchical Outlines
===============================

Goal:
    Learn outline() for multi-level hierarchical content.
    - Word-style numbering (1 → a → i → bullet)
    - Nested children with automatic styling
    - Complex document structures

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_outline.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate hierarchical outline formatting."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 2: Hierarchical Outlines ===")
    print()
    
    # ============================================
    # 1. Simple Outline
    # ============================================
    z.display.header("Simple Outline", color="CYAN", indent=0)
    z.display.text("Two-level hierarchy:")
    
    simple_outline = [
        {
            "content": "Frontend Development",
            "children": [
                "HTML structure",
                "CSS styling",
                "JavaScript logic"
            ]
        },
        {
            "content": "Backend Development",
            "children": [
                "Python/zCLI framework",
                "Database integration",
                "API endpoints"
            ]
        }
    ]
    z.display.outline(simple_outline, indent=1)
    z.display.text("")
    
    # ============================================
    # 2. Multi-Level Outline
    # ============================================
    z.display.header("Multi-Level Outline", color="GREEN", indent=0)
    z.display.text("Full Word-style numbering (1 → a → i → •):")
    
    complex_outline = [
        {
            "content": "Backend Architecture",
            "children": [
                {
                    "content": "Python Runtime Environment",
                    "children": [
                        "zCLI framework initialization",
                        "zDisplay subsystem loading",
                        "Event handler registration"
                    ]
                },
                {
                    "content": "Data Processing Layer",
                    "children": [
                        "Input validation",
                        "Business logic execution"
                    ]
                }
            ]
        },
        {
            "content": "Frontend Architecture",
            "children": [
                {
                    "content": "Rendering Engine",
                    "children": [
                        "ANSI escape sequences",
                        "Unicode character support"
                    ]
                },
                {
                    "content": "User Interaction",
                    "children": [
                        "Keyboard input handling",
                        "Interactive navigation commands"
                    ]
                }
            ]
        }
    ]
    z.display.outline(complex_outline, indent=1)
    z.display.text("")
    
    # ============================================
    # 3. Project Structure Example
    # ============================================
    z.display.header("Real-World Example: Project Structure", color="YELLOW", indent=0)
    
    project_outline = [
        {
            "content": "Source Code",
            "children": [
                {
                    "content": "Subsystems",
                    "children": [
                        "zConfig - Configuration management",
                        "zDisplay - Rendering engine",
                        "zComm - Communication layer"
                    ]
                },
                {
                    "content": "Utilities",
                    "children": [
                        "Validation helpers",
                        "Color utilities",
                        "Exception handlers"
                    ]
                }
            ]
        },
        {
            "content": "Documentation",
            "children": [
                "User guides",
                "API reference",
                "Examples"
            ]
        },
        {
            "content": "Tests",
            "children": [
                {
                    "content": "Unit Tests",
                    "children": [
                        "zConfig tests",
                        "zDisplay tests",
                        "zComm tests"
                    ]
                },
                "Integration tests",
                "End-to-end tests"
            ]
        }
    ]
    z.display.outline(project_outline, indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ outline() - Multi-level hierarchical content")
    z.display.text("✓ Automatic Word-style numbering (1, a, i, •)")
    z.display.text("✓ Nested children with 'content' and 'children' keys")
    z.display.text("✓ Perfect for documentation and structure display")
    z.display.text("")
    
    print("Tip: Outlines are ideal for representing complex hierarchies!")
    print()

if __name__ == "__main__":
    run_demo()

