#!/usr/bin/env python3
"""
Level 3: User Input - Buttons
==============================

Goal:
    Learn button() for action confirmation.
    - Explicit y/n confirmation required
    - No default values (prevents accidents)
    - Color-coded by action type
    - Returns True (yes) or False (no)

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/input_button.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate button input."""
    z = zCLI({"logger": "PROD"})
    
    # Initialize zVars for storing actions
    if "zVars" not in z.session:
        z.session["zVars"] = {}
    
    print()
    print("=== Level 3: Button Actions ===")
    print()
    
    # ============================================
    # 1. Success Button (Primary Action)
    # ============================================
    z.display.header("Success Button", color="GREEN", indent=0)
    z.display.text("Confirm positive actions:")
    
    if z.display.button("Save Profile", action="save_profile", color="success"):
        z.session["zVars"]["profile_saved"] = True
        z.display.success("✅ Profile saved successfully!")
    else:
        z.session["zVars"]["profile_saved"] = False
        z.display.info("Profile not saved.")
    z.display.text("")
    
    # ============================================
    # 2. Danger Button (Destructive Action)
    # ============================================
    z.display.header("Danger Button", color="RED", indent=0)
    z.display.text("Confirm destructive actions with explicit warning:")
    
    if z.display.button("Delete Account", action="delete_account", color="danger"):
        z.session["zVars"]["account_deleted"] = True
        z.display.warning("⚠️ Account marked for deletion!")
    else:
        z.session["zVars"]["account_deleted"] = False
        z.display.info("Account deletion cancelled.")
    z.display.text("")
    
    # ============================================
    # 3. Warning Button (Caution Required)
    # ============================================
    z.display.header("Warning Button", color="YELLOW", indent=0)
    z.display.text("Actions that need caution:")
    
    if z.display.button("Reset Settings", action="reset_settings", color="warning"):
        z.session["zVars"]["settings_reset"] = True
        z.display.warning("Settings reset to defaults")
    else:
        z.session["zVars"]["settings_reset"] = False
        z.display.info("Settings unchanged.")
    z.display.text("")
    
    # ============================================
    # 4. Info Button (Informational Action)
    # ============================================
    z.display.header("Info Button", color="BLUE", indent=0)
    z.display.text("Standard informational actions:")
    
    if z.display.button("Export Data", action="export_data", color="info"):
        z.session["zVars"]["data_exported"] = True
        z.display.success("Data exported to export.json")
    else:
        z.session["zVars"]["data_exported"] = False
        z.display.info("Export cancelled.")
    z.display.text("")
    
    # ============================================
    # 5. Primary Button (Default Color)
    # ============================================
    z.display.header("Primary Button", color="CYAN", indent=0)
    z.display.text("Standard primary actions:")
    
    if z.display.button("Submit Form", action="submit_form", color="primary"):
        z.session["zVars"]["form_submitted"] = True
        z.display.success("Form submitted successfully!")
    else:
        z.session["zVars"]["form_submitted"] = False
        z.display.info("Form submission cancelled.")
    z.display.text("")
    
    # ============================================
    # 6. Workflow Example
    # ============================================
    z.display.header("Real-World Workflow", color="MAGENTA", indent=0)
    z.display.text("Multi-step process with confirmations:")
    
    # Step 1: Prepare
    if z.display.button("Prepare Backup", color="info"):
        z.display.info("Files prepared for backup", indent=1)
        
        # Step 2: Confirm
        if z.display.button("Start Backup", color="success"):
            z.display.success("Backup started", indent=1)
            z.session["zVars"]["backup_completed"] = True
        else:
            z.display.warning("Backup cancelled after preparation", indent=1)
            z.session["zVars"]["backup_completed"] = False
    else:
        z.display.info("Backup not prepared")
        z.session["zVars"]["backup_completed"] = False
    
    z.display.text("")
    
    # ============================================
    # Action Summary
    # ============================================
    z.display.header("Action Summary", color="CYAN", indent=0)
    z.display.text("All actions stored in session['zVars']:")
    z.display.json_data(z.session["zVars"], indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ button() - Action confirmation with y/n")
    z.display.text("✓ NO defaults - Explicit confirmation required")
    z.display.text("✓ color parameter - success, danger, warning, info, primary")
    z.display.text("✓ Returns boolean - True (confirmed), False (cancelled)")
    z.display.text("✓ action parameter - Optional identifier for tracking")
    z.display.text("")
    
    print("Tip: Buttons prevent accidental actions by requiring explicit confirmation!")
    print()

if __name__ == "__main__":
    run_demo()

