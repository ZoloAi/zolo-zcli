# zCLI/subsystems/zShell/zShell_modules/executor_commands/walker_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/walker_executor.py
# --------------------------------------------------------------
"""Walker command execution for zCLI."""

def execute_walker(zcli, parsed):
    """Execute walker commands like 'walker run'."""
    action = parsed["action"]
    
    if action == "run":
        # Launch Walker using session's zVaF configuration
        zcli.logger.info("Launching Walker from session configuration...")
        
        # Validate required session fields
        required_fields = ["zWorkspace", "zVaFilename", "zVaFile_path", "zBlock"]
        missing = []
        
        for field in required_fields:
            if not zcli.session.get(field):
                missing.append(field)
        
        if missing:
            return {
                "error": f"Missing required session fields: {', '.join(missing)}",
                "note": "Use 'session set <field> <value>' to configure Walker"
            }
        
        # Build zSpark configuration from session
        zcli.zspark_obj.update({
            "zWorkspace": zcli.session["zWorkspace"],
            "zVaFilename": zcli.session["zVaFilename"],
            "zVaFile_path": zcli.session.get("zVaFile_path", "@"),
            "zBlock": zcli.session.get("zBlock", "Root"),
            "zMode": "zBifrost"  # Walker always runs in zBifrost mode
        })
        
        # Set session mode to zBifrost for Walker
        zcli.session["zMode"] = "zBifrost"
        
        # Import and launch Walker
        try:
            from zCLI.subsystems.zWalker.zWalker import zWalker
            zcli.logger.info("Creating zWalker instance from zCLI...")
            walker = zWalker(zcli)
            
            zcli.logger.info("Starting Walker UI mode...")
            result = walker.run()
            
            # After Walker exits normally, return to Terminal mode
            zcli.logger.info("Walker exited normally, returning to Terminal mode...")
            zcli.session["zMode"] = "Terminal"
            
            return {"success": "Walker session completed", "result": result}
            
        except SystemExit as e:
            # Walker called sys.exit() - this is normal for "stop" or completion
            zcli.logger.info("Walker exited via sys.exit(%s), returning to Terminal mode...", e.code)
            zcli.session["zMode"] = "Terminal"
            
            # Determine if it was a normal exit or error
            if e.code == 0 or e.code is None:
                return {"success": "Walker exited normally"}
            else:
                return {"note": f"Walker exited with code {e.code}"}
            
        except Exception as e:
            zcli.logger.error("Failed to launch Walker: %s", e, exc_info=True)
            zcli.session["zMode"] = "Terminal"
            return {"error": f"Walker launch failed: {str(e)}"}
    
    else:
        return {"error": f"Unknown walker command: {action}. Use: walker run"}
