import os
import webbrowser
from urllib.parse import urlparse

from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession


class ZOpen:
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle(self, zHorizontal):
        handle_zDisplay({
            "event": "header",
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

        parsed = urlparse(raw_path)
        if parsed.scheme in ("http", "https") or raw_path.startswith("www."):
            url = raw_path if parsed.scheme else f"https://{raw_path}"
            self.logger.info("opening url: %s", url)
            webbrowser.open(url)
            return "zBack"

        if raw_path.startswith("@") or raw_path.startswith("~"):
            path = self._resolve_zPath(raw_path)
        else:
            path = os.path.abspath(os.path.expanduser(raw_path))

        self.logger.debug("resolved path: %s", path)

        if not path.endswith(".html"):
            self.logger.warning("zOpen only supports .html files: %s", path)
            return "stop"

        if not os.path.exists(path):
            self.logger.error("file not found: %s", path)
            return "stop"

        url = f"file://{path}"
        self.logger.info("opening url: %s", url)
        webbrowser.open(url)
        return "zBack"

    def _resolve_zPath(self, zPath: str) -> str:
        """Translate a zPath to an absolute filesystem path.

        Supports workspace-relative paths prefixed with ``@`` and absolute
        paths prefixed with ``~``. Any other value is treated as a normal
        filesystem path and returned as-is.
        """
        zPath = zPath.lstrip(".")
        parts = zPath.split(".")

        if parts[0] == "@":
            base = self.zSession.get("zWorkspace") or ""
            parts = parts[1:]
        elif parts[0] == "~":
            base = os.path.sep
            parts = parts[1:]
        else:
            base = ""

        if len(parts) < 2:
            self.logger.error("invalid zPath: %s", zPath)
            return ""

        *dirs, filename, ext = parts
        file_name = f"{filename}.{ext}"
        return os.path.abspath(os.path.join(base, *dirs, file_name))


def handle_zOpen(zHorizontal, walker=None):
    """Backward-compatible wrapper for existing function-based API."""
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZOpen(walker).handle(zHorizontal)
