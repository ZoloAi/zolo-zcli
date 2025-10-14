# zCLI/subsystems/zOpen.py — Core zOpen Handler
# ───────────────────────────────────────────────────────────────
"""Core zOpen handler for file and URL opening operations."""

from urllib.parse import urlparse
from logger import Logger

# Import zOpen modules from registry
from .zOpen_modules.zOpen_url import zOpen_url
from .zOpen_modules.zOpen_file import zOpen_file
from .zOpen_modules.zOpen_path import zOpen_zPath

# Logger instance
logger = Logger.get_logger(__name__)


class zOpen:
    """Core zOpen class for file and URL opening operations."""
    
    def __init__(self, zcli):
        """Initialize zOpen with zCLI instance."""
        if zcli is None:
            raise ValueError("zOpen requires a zCLI instance")
        
        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")
        
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.zparser = zcli.zparser
        self.zfunc = zcli.zfunc
        self.dialog = zcli.dialog
        self.mycolor = "ZOPEN"
        
        self.display.handle({
            "event": "sysmsg",
            "label": "zOpen Ready",
            "color": self.mycolor,
            "indent": 0
        })

    def handle(self, zHorizontal):
        """Handle zOpen operations with optional hooks."""
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
            result = zOpen_url(url, self.session, self.logger, display=self.display, zcli=self.zcli)
        
        elif raw_path.startswith("@") or raw_path.startswith("~"):
            # zPath handling
            result = zOpen_zPath(raw_path, self.session, self.logger, display=self.display, zcli=self.zcli)
        
        else:
            # Local file handling
            import os
            path = os.path.abspath(os.path.expanduser(raw_path))
            result = zOpen_file(path, self.session, self.logger, display=self.display, zcli=self.zcli)
        
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


def handle_zOpen(zHorizontal, walker=None, zcli=None):
    """Backward-compatible function for zOpen operations."""
    # Modern: use zcli directly if provided
    if zcli:
        return zOpen(zcli).handle(zHorizontal)
    
    # Legacy: extract zcli from walker
    if walker and hasattr(walker, 'zcli'):
        return zOpen(walker.zcli).handle(zHorizontal)
    
    raise ValueError("handle_zOpen requires either zcli or walker with zcli attribute")


# Export main components
__all__ = ["zOpen", "handle_zOpen"]