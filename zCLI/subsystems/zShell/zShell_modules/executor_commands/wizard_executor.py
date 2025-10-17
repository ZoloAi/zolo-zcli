# zCLI/subsystems/zShell/zShell_modules/executor_commands/wizard_executor.py

"""Wizard command execution for zCLI."""

def execute_wizard(zcli, parsed):
    """Execute wizard commands for canvas mode."""
    options = parsed.get("options", {})
    
    # Check for --start flag
    if options.get("start"):
        # Enter wizard canvas mode
        zcli.session["wizard_mode"]["active"] = True
        zcli.session["wizard_mode"]["lines"] = []
        zcli.session["wizard_mode"]["format"] = None
        
        zcli.logger.info("Entered wizard canvas mode")
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║              Wizard Canvas Mode - Active               ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print("\nBuild your workflow by typing YAML structure or shell commands.")
        print("Each Enter adds a new line to the buffer.")
        print("\nCommands:")
        print("  wizard --show    Show buffer")
        print("  wizard --clear   Clear buffer")
        print("  wizard --run     Execute buffer")
        print("  wizard --stop    Exit canvas mode")
        print()
        
        return {"status": "wizard_started"}
    
    else:
        # Other wizard commands (--stop, --run, --show, --clear) are handled
        # by the executor's wizard control methods, not here
        return {"error": "Wizard command should be handled by executor methods"}

