# zCLI/subsystems/zOpen/zOpen_file.py — Local File Opening Operations
# ───────────────────────────────────────────────────────────────

import os
import webbrowser
from zCLI.subsystems.zDisplay import handle_zDisplay


def zOpen_file(path, zSession, logger):
    """
    Handle local file opening based on file type.
    
    Args:
        path: Absolute file path
        zSession: Session with machine capabilities
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.debug("resolved path: %s", path)
    
    # Check if file exists
    if not os.path.exists(path):
        if logger:
            logger.error("file not found: %s", path)
        return "stop"
    
    # Route to appropriate handler based on file extension
    _, ext = os.path.splitext(path.lower())
    
    if ext in ['.html', '.htm']:
        return zOpen_html(path, logger)
    elif ext in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
        return zOpen_text(path, zSession, logger)
    else:
        if logger:
            logger.warning("Unsupported file type: %s", ext)
        return "stop"


def zOpen_html(path, logger):
    """
    Open HTML files in browser.
    
    Args:
        path: HTML file path
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    url = f"file://{path}"
    if logger:
        logger.info("opening html file: %s", url)
    
    try:
        success = webbrowser.open(url)
        if success:
            if logger:
                logger.info("Successfully opened HTML file in browser")
            return "zBack"
        else:
            if logger:
                logger.warning("Browser failed to open HTML file")
            return "stop"
    except Exception as e:
        if logger:
            logger.warning("Browser error: %s", e)
        return "stop"


def zOpen_text(path, zSession, logger):
    """
    Open text files using available text editor/viewer.
    
    Args:
        path: Text file path
        zSession: Session with machine capabilities
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.info("opening text file: %s", path)
    
    # Get machine capabilities
    zMachine = zSession.get("zMachine", {})
    capabilities = zMachine.get("capabilities", {})
    
    # Try to open with default text editor if available
    if capabilities.get("default_text_editor", False):
        try:
            import subprocess
            # Try to open with system default text editor
            if os.name == 'nt':  # Windows
                try:
                    os.startfile(path)  # type: ignore
                except AttributeError:
                    # Fallback for systems without startfile
                    subprocess.run(['notepad', path], check=True)
            elif os.name == 'posix':  # Unix/Linux/macOS
                subprocess.run(['open', path], check=True)  # macOS
                # Note: Linux would use xdg-open, but we'll handle that in capabilities
            if logger:
                logger.info("Successfully opened text file with default editor")
            return "zBack"
        except Exception as e:
            if logger:
                logger.warning("Failed to open with default editor: %s", e)
    
    # Fallback: Display file content
    return zOpen_text_display(path, logger)


def zOpen_text_display(path, logger):
    """
    Display text file content when editor opening fails.
    
    Args:
        path: Text file path
        logger: Logger instance
        
    Returns:
        "zBack" always (graceful fallback)
    """
    if logger:
        logger.info("Displaying text file content")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        handle_zDisplay({
            "event": "header",
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