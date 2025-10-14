# zCLI/subsystems/zOpen.py — Core zOpen Handler
# ───────────────────────────────────────────────────────────────
"""Core zOpen handler for file and URL opening operations."""

from urllib.parse import urlparse
from logger import Logger
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
            self.display = zcli_or_walker.display
            self.zparser = zcli_or_walker.zparser
            self.zfunc = zcli_or_walker.zfunc
            self.dialog = zcli_or_walker.dialog
        elif hasattr(zcli_or_walker, 'zSession'):
            # Legacy walker instance
            self.walker = zcli_or_walker
            self.zcli = getattr(zcli_or_walker, 'zcli', None)
            self.zSession = zcli_or_walker.zSession
            self.logger = getattr(zcli_or_walker, "logger", logger)
            self.display = getattr(zcli_or_walker, "display", None)
            # Try to get subsystems from walker's zcli
            self.zparser = getattr(self.zcli, 'zparser', None) if self.zcli else None
            self.zfunc = getattr(self.zcli, 'zfunc', None) if self.zcli else None
            self.dialog = getattr(self.zcli, 'dialog', None) if self.zcli else None
        else:
            # No valid instance
            raise ValueError("ZOpen requires a zCLI instance or walker with session")

    def handle(self, zHorizontal):
        """
        Main entry point for zOpen operations.
        
        Supports two formats:
        1. String: "zOpen(path)"
        2. Dict: {"zOpen": {"path": "...", "onSuccess": "zFunc(...)", "onFail": "..."}}
        
        Args:
            zHorizontal: zOpen expression (string or dict)
            
        Returns:
            Result from handler or hook execution
        """
        if self.display:
            self.display.handle({
                "event": "sysmsg",
                "label": "Handle zOpen",
                "style": "full",
                "color": "ZOPEN",
                "indent": 1,
            })
            self.display.handle({
                "event": "zCrumbs"
            })

        self.logger.debug("incoming zOpen request: %s", zHorizontal)

        # Parse input - support both string and dict formats
        if isinstance(zHorizontal, dict):
            # Dict format: {"zOpen": {"path": "...", "onSuccess": "...", "onFail": "..."}}
            zOpen_obj = zHorizontal.get("zOpen", {})
            raw_path = zOpen_obj.get("path", "")
            on_success = zOpen_obj.get("onSuccess")
            on_fail = zOpen_obj.get("onFail")
        else:
            # String format: "zOpen(path)"
            raw_path = zHorizontal[len("zOpen("):-1].strip().strip('"').strip("'")
            on_success = None
            on_fail = None
        
        self.logger.debug("parsed path: %s", raw_path)

        # Determine file type and route to appropriate handler
        parsed = urlparse(raw_path)
        
        if parsed.scheme in ("http", "https") or raw_path.startswith("www."):
            # URL handling
            url = raw_path if parsed.scheme else f"https://{raw_path}"
            result = zOpen_url(url, self.zSession, self.logger, display=self.display, zcli=self.zcli)
        
        elif raw_path.startswith("@") or raw_path.startswith("~"):
            # zPath handling
            result = zOpen_zPath(raw_path, self.zSession, self.logger, display=self.display, zcli=self.zcli)
        
        else:
            # Local file handling
            import os
            path = os.path.abspath(os.path.expanduser(raw_path))
            result = zOpen_file(path, self.zSession, self.logger, display=self.display, zcli=self.zcli)
        
        # Execute hooks based on result
        if result == "zBack" and on_success and self.zfunc:
            self.logger.info("Executing onSuccess hook: %s", on_success)
            if self.display:
                self.display.handle({
                    "event": "sysmsg",
                    "label": "→ onSuccess",
                    "style": "single",
                    "color": "ZOPEN",
                    "indent": 2,
                })
            return self.zfunc.handle(on_success)
        
        elif result == "stop" and on_fail and self.zfunc:
            self.logger.info("Executing onFail hook: %s", on_fail)
            if self.display:
                self.display.handle({
                    "event": "sysmsg",
                    "label": "→ onFail",
                    "style": "single",
                    "color": "ZOPEN",
                    "indent": 2,
                })
            return self.zfunc.handle(on_fail)
        
        return result


def handle_zOpen(zHorizontal, walker=None):
    """Standalone function for zOpen operations."""
    if walker is None:
        raise ValueError("handle_zOpen requires a walker parameter")
    return ZOpen(walker).handle(zHorizontal)


# Export main components
__all__ = ["ZOpen", "handle_zOpen"]