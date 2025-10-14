# zCLI/subsystems/zOpen/zOpen_url.py — URL Opening Operations
# ───────────────────────────────────────────────────────────────

import webbrowser
import subprocess


def zOpen_url(url, zSession, logger, display=None, zcli=None):
    """Handle URL opening using user's preferred browser."""
    if logger:
        logger.info("opening url: %s", url)
    
    # Enhanced display: Show URL info as JSON
    if display:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        url_info = {
            "url": url,
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path
        }
        display.handle({
            "event": "json",
            "data": url_info,
            "color": True,
            "indent": 1
        })
    
    # Get machine configuration
    zMachine = zSession.get("zMachine", {})
    browser = zMachine.get("browser")
    
    if logger and browser:
        logger.info("Using browser: %s", browser)
    
    # Try to open with user's preferred browser
    if browser and browser != "unknown":
        return zOpen_url_browser(url, browser, logger, display)
    
    # Fallback to system default browser
    return zOpen_url_browser(url, None, logger, display)


def zOpen_url_browser(url, browser, logger, display=None):
    """Open URL in specified or default browser."""
    try:
        if browser and browser not in ("unknown", "Safari", "Edge"):
            # Try to use specific browser if available
            import shutil
            if shutil.which(browser):
                subprocess.run([browser, url], check=False)
                if logger:
                    logger.info("Successfully opened URL in %s", browser)
                if display:
                    display.handle({
                        "event": "success",
                        "label": f"Opened URL in {browser}",
                        "color": "GREEN",
                        "indent": 1
                    })
                return "zBack"
        
        # Fallback to system default browser (webbrowser module)
        success = webbrowser.open(url)
        if success:
            if logger:
                logger.info("Successfully opened URL in system default browser")
            if display:
                display.handle({
                    "event": "success",
                    "label": "Opened URL in default browser",
                    "color": "GREEN",
                    "indent": 1
                })
            return "zBack"
        else:
            if logger:
                logger.warning("Browser failed to open URL")
            if display:
                display.handle({
                    "event": "error",
                    "label": "Browser failed to open URL",
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