#!/usr/bin/env python3
"""
Level 1: Signal Events - Color-Coded Feedback
==============================================

Goal:
    Learn zDisplay's signal system for user feedback.
    - success() - Green checkmark for positive outcomes
    - error() - Red X for failures
    - warning() - Yellow warning for cautions
    - info() - Blue info icon for general messages

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_1_Outputs_Signals/signals_basic.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate the four signal types."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 1: Signal Events ===")
    print()
    
    # ============================================
    # 1. Success Signals
    # ============================================
    z.display.header("Success Signals", color="GREEN", indent=0)
    z.display.text("Used for positive outcomes and confirmations:")
    z.display.success("Operation completed successfully!")
    z.display.success("File saved to disk", indent=1)
    z.display.success("Database connection established", indent=1)
    z.display.text("")
    
    # ============================================
    # 2. Error Signals
    # ============================================
    z.display.header("Error Signals", color="RED", indent=0)
    z.display.text("Used for failures and critical issues:")
    z.display.error("Something went wrong!")
    z.display.error("File not found: config.yaml", indent=1)
    z.display.error("Database connection failed", indent=1)
    z.display.text("")
    
    # ============================================
    # 3. Warning Signals
    # ============================================
    z.display.header("Warning Signals", color="YELLOW", indent=0)
    z.display.text("Used for cautions and potential issues:")
    z.display.warning("Be careful here!")
    z.display.warning("Disk space running low", indent=1)
    z.display.warning("Deprecated API in use", indent=1)
    z.display.text("")
    
    # ============================================
    # 4. Info Signals
    # ============================================
    z.display.header("Info Signals", color="BLUE", indent=0)
    z.display.text("Used for general information and status updates:")
    z.display.info("Just letting you know...")
    z.display.info("Processing 1,234 records", indent=1)
    z.display.info("Cache warmed up", indent=1)
    z.display.text("")
    
    # ============================================
    # 5. Combined Example
    # ============================================
    z.display.header("Real-World Example: File Upload", color="CYAN", indent=0)
    z.display.info("Starting file upload process...")
    z.display.info("Validating file format", indent=1)
    z.display.success("Format valid: PDF", indent=2)
    z.display.info("Checking file size", indent=1)
    z.display.warning("File is large (12MB) - may take time", indent=2)
    z.display.info("Uploading to server", indent=1)
    z.display.success("Upload complete!", indent=2)
    z.display.success("File uploaded successfully: report.pdf")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ success() - Positive outcomes (green ✓)")
    z.display.text("✓ error() - Failures and errors (red ✗)")
    z.display.text("✓ warning() - Cautions and warnings (yellow ⚠)")
    z.display.text("✓ info() - General information (blue ℹ)")
    z.display.text("✓ All signals support indentation for nested feedback")
    z.display.text("")
    
    print("Tip: Signals provide automatic color-coding and icons!")
    print()

if __name__ == "__main__":
    run_demo()

