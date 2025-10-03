# zCLI/subsystems/zOpen/zOpen_url.py — URL Opening Operations
# ───────────────────────────────────────────────────────────────

import webbrowser
import subprocess
from zCLI.subsystems.zDisplay import handle_zDisplay


def zOpen_url(url, zSession, logger):
    """
    Handle URL opening with intelligent fallbacks based on machine capabilities.
    
    Args:
        url: URL to open
        zSession: Session with machine capabilities
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.info("opening url: %s", url)
    
    # Get machine capabilities from zSession
    zMachine = zSession.get("zMachine", {})
    capabilities = zMachine.get("capabilities", {})
    environment = zMachine.get("environment", "unknown")
    
    if logger:
        logger.debug("Machine capabilities: %s", capabilities)
        logger.debug("Environment: %s", environment)
    
    # Strategy 1: Try browser if available
    if capabilities.get("browser", False):
        return zOpen_url_browser(url, logger)
    
    # Strategy 2: Fallback to headless methods
    if environment == "headless" or not capabilities.get("browser", False):
        return zOpen_url_headless(url, capabilities, logger)
    
    # Strategy 3: Display URL info if all else fails
    return zOpen_url_display(url, logger)


def zOpen_url_browser(url, logger):
    """
    Open URL in browser.
    
    Args:
        url: URL to open
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    try:
        success = webbrowser.open(url)
        if success:
            if logger:
                logger.info("Successfully opened URL in browser")
            return "zBack"
        else:
            if logger:
                logger.warning("Browser failed to open URL")
            return "stop"
    except Exception as e:
        if logger:
            logger.warning("Browser error: %s", e)
        return "stop"


def zOpen_url_headless(url, capabilities, logger):
    """
    Handle URL opening on headless systems using available tools.
    
    Args:
        url: URL to open
        capabilities: Machine capabilities dict
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.info("Handling URL on headless system: %s", url)
    
    # Try curl to fetch and display content
    if capabilities.get("imports", False):  # imports means curl/wget available
        try:
            result = subprocess.run(['curl', '-s', '-L', url], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                if logger:
                    logger.info("Successfully fetched URL content via curl")
                handle_zDisplay({
                    "event": "header",
                    "label": "URL Content (via curl)",
                    "style": "~",
                    "color": "INFO",
                    "indent": 1,
                })
                
                # Display first 500 characters
                content = result.stdout
                if len(content) > 500:
                    print(content[:500] + "...")
                    print(f"\n[Content truncated - showing first 500 of {len(content)} characters]")
                else:
                    print(content)
                
                return "zBack"
            else:
                if logger:
                    logger.warning("curl failed with return code: %s", result.returncode)
        except Exception as e:
            if logger:
                logger.warning("curl error: %s", e)
    
    # Fallback: Just display URL
    return zOpen_url_display(url, logger)


def zOpen_url_display(url, logger):
    """
    Display URL information when opening fails.
    
    Args:
        url: URL to display
        logger: Logger instance (optional)
        
    Returns:
        "zBack" always (graceful fallback)
    """
    if logger:
        logger.warning("Unable to open URL. Displaying information instead.")
    
    handle_zDisplay({
        "event": "header",
        "label": "URL Information",
        "style": "~",
        "color": "INFO",
        "indent": 1,
    })
    print(f"URL: {url}")
    print("Unable to open in browser. Please copy and paste into your browser.")
    return "zBack"