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
        required_fields = ["zSpace", "zVaFile", "zVaFolder", "zBlock"]
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
        # Preserve current zMode (Terminal or zBifrost) - user controls the mode
        current_mode = zcli.session.get("zMode", "Terminal")
        
        # Construct full zPath from zVaFolder + zVaFile (NO <zBlock> suffix)
        zva_folder = zcli.session.get("zVaFolder", "@")
        zva_file = zcli.session["zVaFile"]
        zblock = zcli.session.get("zBlock", "Root")
        
        # Build full zPath for loader: zVaFolder.zVaFile (NO <zBlock>)
        full_zpath = f"{zva_folder}.{zva_file}"
        
        zcli.zspark_obj.update({
            "zSpace": zcli.session["zSpace"],
            "zVaFile": full_zpath,  # Full zPath to file (e.g., "@.zCLI.UI.zUI.zcli_sys")
            "zVaFolder": zva_folder,
            "zBlock": zblock,  # Separate - used after file is loaded
            "zMode": current_mode  # Respect current mode (Terminal or zBifrost)
        })
        
        # Import and launch Walker
        try:
            from zCLI.subsystems.zWalker.zWalker import zWalker
            zcli.logger.info("Creating zWalker instance from zCLI...")
            walker = zWalker(zcli)
            
            zcli.logger.info("Starting Walker in %s mode...", current_mode)
            result = walker.run()
            
            # After Walker exits normally, restore original mode
            zcli.logger.info("Walker exited normally")
            zcli.session["zMode"] = current_mode
            
            return {"success": "Walker session completed", "result": result}
            
        except SystemExit as e:
            # Walker called sys.exit() - this is normal for "stop" or completion
            zcli.logger.info("Walker exited via sys.exit(%s)", e.code)
            zcli.session["zMode"] = current_mode
            
            # Determine if it was a normal exit or error
            if e.code == 0 or e.code is None:
                return {"success": "Walker exited normally"}
            else:
                return {"note": f"Walker exited with code {e.code}"}
            
        except Exception as e:
            zcli.logger.error("Failed to launch Walker: %s", e, exc_info=True)
            zcli.session["zMode"] = current_mode  # Restore original mode on error
            return {"error": f"Walker launch failed: {str(e)}"}
    
    else:
        return {"error": f"Unknown walker command: {action}. Use: walker run"}
