#!/usr/bin/env python3
"""
Level 4: System Display Events
===============================

Goal:
    Learn system-level display events.
    - zDeclare() - System announcements and declarations
    - zSession() - Display session state
    - zConfig() - Display configuration info

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_4_System/system_declare.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate system display events."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 4: System Display Events ===")
    print()
    
    # ============================================
    # 1. zDeclare - System Announcements
    # ============================================
    z.display.header("zDeclare()", color="CYAN", indent=0)
    z.display.text("System-level announcements and declarations:")
    
    z.display.zDeclare("System Initialization")
    z.display.zDeclare("Loading Configuration", indent=1)
    z.display.zDeclare("Connecting to Services", indent=1)
    z.display.zDeclare("Ready for Operations")
    z.display.text("")
    
    # ============================================
    # 2. zDeclare with Colors
    # ============================================
    z.display.header("zDeclare() with Colors", color="GREEN", indent=0)
    z.display.text("Colored declarations for different states:")
    
    z.display.zDeclare("Starting Services", color="GREEN")
    z.display.zDeclare("Caution: Limited Resources", color="YELLOW")
    z.display.zDeclare("Critical: Manual Intervention Required", color="RED")
    z.display.zDeclare("Information: Cache Warming", color="BLUE")
    z.display.text("")
    
    # ============================================
    # 3. zSession - Display Session State
    # ============================================
    z.display.header("zSession()", color="YELLOW", indent=0)
    z.display.text("Display current session information:")
    
    # Add some demo session variables
    if "zVars" not in z.session:
        z.session["zVars"] = {}
    z.session["zVars"]["demo_mode"] = True
    z.session["zVars"]["user_role"] = "developer"
    
    z.display.zSession(z.session)
    z.display.text("")
    
    # ============================================
    # 4. zConfig - Display Configuration
    # ============================================
    z.display.header("zConfig()", color="MAGENTA", indent=0)
    z.display.text("Display machine and environment configuration:")
    
    config_data = {
        "machine": {
            "os": z.config.get_machine("os"),
            "hostname": z.config.get_machine("hostname"),
            "python_version": z.config.get_machine("python_version")
        },
        "environment": {
            "deployment": z.session.get("deployment", "Debug"),
            "workspace": str(z.config.sys_paths.workspace_dir),
            "mode": z.session.get("zMode", "Terminal")
        }
    }
    
    z.display.zConfig(config_data)
    z.display.text("")
    
    # ============================================
    # 5. Real-World Example: Startup Sequence
    # ============================================
    z.display.header("Real-World Example: Application Startup", color="BLUE", indent=0)
    
    z.display.zDeclare("Application Starting", color="CYAN")
    z.display.text("")
    
    z.display.zDeclare("Phase 1: Configuration", color="GREEN")
    z.display.info("Loading environment variables", indent=1)
    z.display.info("Validating paths", indent=1)
    z.display.success("Configuration complete", indent=1)
    z.display.text("")
    
    z.display.zDeclare("Phase 2: Services", color="GREEN")
    z.display.info("Connecting to database", indent=1)
    z.display.info("Initializing cache", indent=1)
    z.display.success("Services ready", indent=1)
    z.display.text("")
    
    z.display.zDeclare("Phase 3: Runtime", color="GREEN")
    z.display.text("Session state:", indent=1)
    z.display.zSession(z.session, break_after=False)
    z.display.text("")
    
    z.display.text("Configuration:", indent=1)
    z.display.zConfig(config_data, break_after=False)
    z.display.text("")
    
    z.display.zDeclare("Application Ready", color="GREEN")
    z.display.success("All systems operational!")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ zDeclare() - System announcements and declarations")
    z.display.text("✓ Color parameter - GREEN, YELLOW, RED, BLUE for states")
    z.display.text("✓ zSession() - Display current session state")
    z.display.text("✓ zConfig() - Display machine/environment config")
    z.display.text("✓ Perfect for startup sequences and system status")
    z.display.text("")
    
    print("Tip: System events provide professional status reporting!")
    print()

if __name__ == "__main__":
    run_demo()

