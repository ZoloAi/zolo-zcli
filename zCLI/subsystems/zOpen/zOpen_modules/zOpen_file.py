# zCLI/subsystems/zOpen/zOpen_file.py — Local File Opening Operations
# ───────────────────────────────────────────────────────────────

import os
import webbrowser


def zOpen_file(path, zSession, logger, display=None, zcli=None):
    """Handle local file opening based on file type."""
    if logger:
        logger.debug("resolved path: %s", path)
    
    # Enhanced display: Show file info as JSON
    if display and os.path.exists(path):
        file_info = {
            "path": path,
            "exists": True,
            "size": f"{os.path.getsize(path)} bytes",
            "type": os.path.splitext(path)[1]
        }
        display.handle({
            "event": "json",
            "data": file_info,
            "color": True,
            "indent": 1
        })
    
    # Check if file exists
    if not os.path.exists(path):
        if logger:
            logger.error("file not found: %s", path)
        
        # zDialog fallback: Offer to create file or cancel
        if zcli and zcli.dialog:
            if logger:
                logger.info("Prompting user for action on missing file")
            
            try:
                result = zcli.dialog.handle({
                    "zDialog": {
                        "model": None,
                        "fields": [{
                            "name": "action",
                            "type": "enum",
                            "options": ["Create file", "Cancel"]
                        }]
                    }
                })
                
                if result.get("action") == "Create file":
                    # Create empty file
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write("")
                    if logger:
                        logger.info("Created file: %s", path)
                    if display:
                        display.handle({
                            "event": "success",
                            "label": f"Created {path}",
                            "color": "GREEN",
                            "indent": 1
                        })
                    # Continue with opening the newly created file
                else:
                    return "stop"
            except Exception as e:
                if logger:
                    logger.warning("Dialog fallback failed: %s", e)
                return "stop"
        else:
            return "stop"
    
    # Route to appropriate handler based on file extension
    _, ext = os.path.splitext(path.lower())
    
    if ext in ['.html', '.htm']:
        return zOpen_html(path, logger, display)
    elif ext in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
        return zOpen_text(path, zSession, logger, display, zcli)
    else:
        if logger:
            logger.warning("Unsupported file type: %s", ext)
        if display:
            display.handle({
                "event": "error",
                "label": f"Unsupported file type: {ext}",
                "color": "RED",
                "indent": 1
            })
        return "stop"


def zOpen_html(path, logger, display=None):
    """Open HTML files in browser."""
    url = f"file://{path}"
    if logger:
        logger.info("opening html file: %s", url)
    
    try:
        success = webbrowser.open(url)
        if success:
            if logger:
                logger.info("Successfully opened HTML file in browser")
            if display:
                display.handle({
                    "event": "success",
                    "label": f"Opened {os.path.basename(path)} in browser",
                    "color": "GREEN",
                    "indent": 1
                })
            return "zBack"
        else:
            if logger:
                logger.warning("Browser failed to open HTML file")
            if display:
                display.handle({
                    "event": "error",
                    "label": "Browser failed to open HTML file",
                    "color": "RED",
                    "indent": 1
                })
            return "stop"
    except Exception as e:
        if logger:
            logger.warning("Browser error: %s", e)
        if display:
            display.handle({
                "event": "error",
                "label": f"Browser error: {str(e)}",
                "color": "RED",
                "indent": 1
            })
        return "stop"


def zOpen_text(path, zSession, logger, display=None, zcli=None):
    """Open text files using user's preferred IDE."""
    if logger:
        logger.info("opening text file: %s", path)
    
    # Get machine configuration
    zMachine = zSession.get("zMachine", {})
    
    # Use IDE for all text files
    editor = zMachine.get("ide", "nano")
    
    if logger:
        logger.info("Using IDE: %s", editor)
    
    # zDialog: Optionally ask for IDE if multiple available
    available_editors = ["cursor", "code", "nano", "vim"]
    if zcli and zcli.dialog and editor == "unknown":
        try:
            result = zcli.dialog.handle({
                "zDialog": {
                    "model": None,
                    "fields": [{
                        "name": "ide",
                        "type": "enum",
                        "options": available_editors
                    }]
                }
            })
            editor = result.get("ide", "nano")
        except Exception as e:
            if logger:
                logger.warning("IDE selection dialog failed: %s", e)
    
    # Try to open with IDE
    try:
        import subprocess
        
        if os.name == 'nt':  # Windows
            try:
                os.startfile(path)  # type: ignore
            except AttributeError:
                subprocess.run([editor, path], check=False)
        else:  # Unix/Linux/macOS
            subprocess.run([editor, path], check=False)
        
        if logger:
            logger.info("Successfully opened file with %s", editor)
        if display:
            display.handle({
                "event": "success",
                "label": f"Opened {os.path.basename(path)} in {editor}",
                "color": "GREEN",
                "indent": 1
            })
        return "zBack"
    
    except Exception as e:
        if logger:
            logger.warning("Failed to open with IDE %s: %s", editor, e)
        if display:
            display.handle({
                "event": "error",
                "label": f"Failed to open with {editor}: {str(e)}",
                "color": "RED",
                "indent": 1
            })
        
        # Fallback: Display file content
        return zOpen_text_display(path, logger, display)


def zOpen_text_display(path, logger, display=None):
    """Display text file content when IDE opening fails."""
    if logger:
        logger.info("Displaying text file content")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if display:
            display.handle({
                "event": "sysmsg",
                "label": f"File Content: {os.path.basename(path)}",
                "style": "~",
                "color": "INFO",
                "indent": 1,
            })
        
        # Display first 1000 characters
        if len(content) > 1000:
            print(content[:1000] + "...")
            print(f"\n[Content truncated - showing first 1000 of {len(content)} characters]")
        else:
            print(content)
        
        return "zBack"
        
    except Exception as e:
        if logger:
            logger.error("Failed to read file: %s", e)
        return "stop"
