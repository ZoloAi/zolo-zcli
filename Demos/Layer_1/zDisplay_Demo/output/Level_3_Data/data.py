#!/usr/bin/env python3
"""
Level 3: Data - Structured Data Display
========================================

Goal:
    Display structured data with list(), outline(), and json_data().
    list() = bullet/number/letter lists
    outline() = hierarchical multi-level (1→a→i→•)
    json_data() = pretty-printed JSON with optional colors

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_3_Data/data.py
"""

from zCLI import zCLI


def run_demo():
    """Demonstrate structured data display methods."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 3: Data - Structured Data Display", color="YELLOW", style="wave")
    z.display.line("")

    # List - Bullet style
    z.display.text("Bullet List:")
    z.display.list(
        ["Fast execution", "Simple API", "Multi-mode rendering"],
        style="bullet"
    )

    z.display.line("")

    # List - Number style
    z.display.text("Numbered List:")
    z.display.list(
        ["Initialize zCLI", "Configure settings", "Deploy application"],
        style="number"
    )

    z.display.line("")

    # List - Letter style
    z.display.text("Letter List:")
    z.display.list(
        ["Option A", "Option B", "Option C"],
        style="letter"
    )

    z.display.line("")

    # Outline - Hierarchical multi-level
    z.display.text("Hierarchical Outline (1→a→i→•):")
    z.display.outline([
        {
            "content": "Backend Architecture",
            "children": [
                {
                    "content": "Python Runtime",
                    "children": [
                        "zCLI initialization",
                        "Event handling"
                    ]
                },
                "Data Processing Layer"
            ]
        },
        {
            "content": "Frontend Architecture",
            "children": ["Rendering Engine", "User Interaction"]
        }
    ])

    z.display.line("")

    # JSON Data - Without color
    z.display.text("JSON Data (plain):")
    config = {
        "version": "1.5.5",
        "mode": "Terminal",
        "features": ["ANSI colors", "Interactive input"],
        "ready": True
    }
    z.display.json_data(config, color=False)

    z.display.line("")

    # JSON Data - With color
    z.display.text("JSON Data (with syntax coloring):")
    z.display.json_data(config, color=True)

    z.display.line("")
    z.display.text("Key point: Structured data display.")
    z.display.text("           list() = bullet/number/letter")
    z.display.text("           outline() = hierarchical (1→a→i→•)")
    z.display.text("           json_data() = pretty-printed JSON")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

