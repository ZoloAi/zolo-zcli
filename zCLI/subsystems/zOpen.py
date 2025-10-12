# zCLI/subsystems/zOpen.py — Core zOpen Handler
# ───────────────────────────────────────────────────────────────
"""Core zOpen handler for file and URL opening operations."""

from urllib.parse import urlparse
from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay
# Global session import removed - use instance-based sessions

# Import zOpen modules from registry
from .zOpen_modules.zOpen_url import zOpen_url
from .zOpen_modules.zOpen_file import zOpen_file
from .zOpen_modules.zOpen_path import zOpen_zPath

# Logger instance
logger = Logger.get_logger(__name__)


class ZOpen:
    """
    Core zOpen class that handles file and URL opening operations.
    
    Provides intelligent opening based on:
    - File types (URL, HTML, text, zPath)
    - Machine capabilities (browser, curl, etc.)
    - Environment (GUI vs headless)
    """
    
    def __init__(self, zcli_or_walker=None):
        # Accept either zcli instance (shell mode) or walker (UI mode)
        if hasattr(zcli_or_walker, 'session'):
            # Modern zCLI instance
            self.zcli = zcli_or_walker
            self.walker = None
            self.zSession = zcli_or_walker.session
            self.logger = zcli_or_walker.logger
        elif hasattr(zcli_or_walker, 'zSession'):
            # Legacy walker instance
            self.walker = zcli_or_walker
            self.zcli = None
            self.zSession = zcli_or_walker.zSession
            self.logger = getattr(zcli_or_walker, "logger", logger)
        else:
            # No valid instance
            raise ValueError("ZOpen requires a zCLI instance or walker with session")

    def handle(self, zHorizontal):
        """
        Main entry point for zOpen operations.
        
        Args:
            zHorizontal: zOpen expression like "zOpen(https://example.com)"
            
        Returns:
            "zBack" on success, "stop" on failure
        """
        handle_zDisplay({
            "event": "sysmsg",
            "label": "Handle zOpen",
            "style": "full",
            "color": "ZOPEN",
            "indent": 1,
        })
        handle_zDisplay({
            "event": "zCrumbs"
        })

        self.logger.debug("incoming zOpen request: %s", zHorizontal)

        # Extract path from expression like zOpen(path)
        raw_path = zHorizontal[len("zOpen("):-1].strip().strip('"').strip("'")
        self.logger.debug("parsed path: %s", raw_path)

        # Determine file type and route to appropriate handler
        parsed = urlparse(raw_path)
        
        if parsed.scheme in ("http", "https") or raw_path.startswith("www."):
            # URL handling
            url = raw_path if parsed.scheme else f"https://{raw_path}"
            return zOpen_url(url, self.zSession, self.logger)
        
        elif raw_path.startswith("@") or raw_path.startswith("~"):
            # zPath handling
            return zOpen_zPath(raw_path, self.zSession, self.logger)
        
        else:
            # Local file handling
            import os
            path = os.path.abspath(os.path.expanduser(raw_path))
            return zOpen_file(path, self.zSession, self.logger)


def handle_zOpen(zHorizontal, walker=None):
    """Standalone function for zOpen operations."""
    if walker is None:
        raise ValueError("handle_zOpen requires a walker parameter")
    return ZOpen(walker).handle(zHorizontal)


# Export main components
__all__ = ["ZOpen", "handle_zOpen"]