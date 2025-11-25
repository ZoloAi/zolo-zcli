#!/usr/bin/env python3
"""
Level 3: User Input - Selection
================================

Goal:
    Learn selection() for user choices.
    - Single-select from list
    - Multi-select with checkboxes
    - Numbered and bullet styles
    - Default values

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/input_selection.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate selection input."""
    z = zCLI({"logger": "PROD"})
    
    # Initialize zVars for storing inputs
    if "zVars" not in z.session:
        z.session["zVars"] = {}
    
    print()
    print("=== Level 3: Selection Input ===")
    print()
    
    # ============================================
    # 1. Single Selection
    # ============================================
    z.display.header("Single Selection", color="CYAN", indent=0)
    z.display.text("Choose one option:")
    
    role = z.display.selection(
        "Select your role:",
        ["Developer", "Designer", "Manager", "Other"]
    )
    z.session["zVars"]["role"] = role
    z.display.success(f"Selected: {role}")
    z.display.text("")
    
    # ============================================
    # 2. Multi-Selection
    # ============================================
    z.display.header("Multi-Selection", color="GREEN", indent=0)
    z.display.text("Choose multiple skills (comma-separated or space-separated):")
    
    skills = z.display.selection(
        "Select your skills:",
        ["Python", "JavaScript", "React", "Django", "zCLI"],
        multi=True
    )
    z.session["zVars"]["skills"] = skills
    z.display.success(f"Selected: {', '.join(skills) if skills else 'None'}")
    z.display.text("")
    
    # ============================================
    # 3. Selection with Default
    # ============================================
    z.display.header("Selection with Default", color="YELLOW", indent=0)
    z.display.text("Press Enter to accept default:")
    
    theme = z.display.selection(
        "Choose theme:",
        ["Light", "Dark", "Auto"],
        default="Dark"
    )
    z.session["zVars"]["theme"] = theme
    z.display.success(f"Selected: {theme}")
    z.display.text("")
    
    # ============================================
    # 4. Multi-Selection with Defaults
    # ============================================
    z.display.header("Multi-Selection with Defaults", color="MAGENTA", indent=0)
    z.display.text("Pre-selected options (modify or accept):")
    
    notifications = z.display.selection(
        "Enable notifications for:",
        ["Email", "SMS", "Push", "Slack", "Teams"],
        multi=True,
        default=["Email", "Push"]
    )
    z.session["zVars"]["notifications"] = notifications
    z.display.success(f"Selected: {', '.join(notifications) if notifications else 'None'}")
    z.display.text("")
    
    # ============================================
    # 5. Bullet Style Selection
    # ============================================
    z.display.header("Bullet Style", color="BLUE", indent=0)
    z.display.text("Options displayed with bullets instead of numbers:")
    
    priority = z.display.selection(
        "Choose priority:",
        ["Low", "Medium", "High", "Critical"],
        style="bullet"
    )
    z.session["zVars"]["priority"] = priority
    z.display.success(f"Selected: {priority}")
    z.display.text("")
    
    # ============================================
    # Summary Display
    # ============================================
    z.display.header("Your Selections", color="CYAN", indent=0)
    z.display.text("All values stored in session['zVars']:")
    z.display.json_data(z.session["zVars"], indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ selection() - User choice input")
    z.display.text("✓ multi=True - Multiple selections")
    z.display.text("✓ default parameter - Pre-selected values")
    z.display.text("✓ style='bullet' or 'number' - Display format")
    z.display.text("✓ Store in session['zVars'] - Access throughout session")
    z.display.text("")
    
    print("Tip: selection() works identically in Terminal and GUI modes!")
    print()

if __name__ == "__main__":
    run_demo()

