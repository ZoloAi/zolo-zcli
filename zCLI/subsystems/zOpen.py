# zCLI/subsystems/zOpen.py — Core zOpen Handler
# ───────────────────────────────────────────────────────────────
"""Core zOpen handler for file and URL opening operations."""

from urllib.parse import urlparse
from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession

# Import zOpen modules from registry
from .zOpen_modules.zOpen_url import zOpen_url
from .zOpen_modules.zOpen_file import zOpen_file
from .zOpen_modules.zOpen_path import zOpen_zPath


class ZOpen:
    """
    Core zOpen class that handles file and URL opening operations.
    
    Provides intelligent opening based on:
    - File types (URL, HTML, text, zPath)
    - Machine capabilities (browser, curl, etc.)
    - Environment (GUI vs headless)
    """
    
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

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
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZOpen(walker).handle(zHorizontal)


# Export main components
__all__ = ["ZOpen", "handle_zOpen"]