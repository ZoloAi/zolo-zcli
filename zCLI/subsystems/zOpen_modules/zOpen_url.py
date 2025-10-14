# zCLI/subsystems/zOpen/zOpen_url.py — URL Opening Operations
# ───────────────────────────────────────────────────────────────

import webbrowser
import subprocess


def zOpen_url(url, zSession, logger, display=None):
    """
    Handle URL opening using user's preferred browser.
    
    Uses machine.yaml preferences:
    - browser: User's preferred browser
    
    Args:
        url: URL to open
        zSession: Session with machine configuration
        logger: Logger instance
        display: Display instance (optional)
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.info("opening url: %s", url)
    
    # Get machine configuration
    zMachine = zSession.get("zMachine", {})
    browser = zMachine.get("browser")
    
    if logger and browser:
        logger.info("Using browser: %s", browser)
    
    # Try to open with user's preferred browser
    if browser and browser != "unknown":
        return zOpen_url_browser(url, browser, logger)
    
    # Fallback to system default browser
    return zOpen_url_browser(url, None, logger)


def zOpen_url_browser(url, browser, logger):
    """
    Open URL in specified or default browser.
    
    Args:
        url: URL to open
        browser: Preferred browser name (or None for system default)
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    try:
        if browser and browser not in ("unknown", "Safari", "Edge"):
            # Try to use specific browser if available
            import shutil
            if shutil.which(browser):
                subprocess.run([browser, url], check=False)
                if logger:
                    logger.info("Successfully opened URL in %s", browser)
                return "zBack"
        
        # Fallback to system default browser (webbrowser module)
        success = webbrowser.open(url)
        if success:
            if logger:
                logger.info("Successfully opened URL in system default browser")
            return "zBack"
        else:
            if logger:
                logger.warning("Browser failed to open URL")
            return "stop"
    
    except Exception as e:
        if logger:
            logger.warning("Browser error: %s", e)
        return "stop"


def zOpen_url_headless(url, capabilities, logger, display=None):
    """
    Handle URL opening on headless systems using available tools.
    
    Args:
        url: URL to open
        capabilities: Machine capabilities dict
        logger: Logger instance
        display: Display instance (optional)
        
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
                if display:
                    display.handle({
                        "event": "sysmsg",
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
    return zOpen_url_display(url, logger, display)


def zOpen_url_display(url, logger, display=None):
    """
    Display URL information when opening fails.
    
    Args:
        url: URL to display
        logger: Logger instance (optional)
        display: Display instance (optional)
        
    Returns:
        "zBack" always (graceful fallback)
    """
    if logger:
        logger.warning("Unable to open URL. Displaying information instead.")
    
    if display:
        display.handle({
            "event": "sysmsg",
            "label": "URL Information",
            "style": "~",
            "color": "INFO",
            "indent": 1,
        })
    print(f"URL: {url}")
    print("Unable to open in browser. Please copy and paste into your browser.")
    return "zBack"