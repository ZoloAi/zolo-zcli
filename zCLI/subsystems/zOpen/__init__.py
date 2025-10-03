# zCLI/subsystems/zOpen/__init__.py — zOpen Package Exports
# ───────────────────────────────────────────────────────────────
"""
zOpen Operations Package

This package provides file and URL opening operations for zCLI:
- URL: Open HTTP/HTTPS URLs with intelligent fallbacks
- File: Open local files (HTML, text, etc.)
- zPath: Resolve and open zPath references

Architecture:
- zOpen_handler.py: Core infrastructure (ZOpen class, session management)
- zOpen_url.py: URL opening with browser/curl fallbacks
- zOpen_file.py: Local file opening
- zOpen_path.py: zPath resolution and opening
"""

from .zOpen_handler import (
    ZOpen,
    handle_zOpen
)

from .zOpen_url import (
    zOpen_url,
    zOpen_url_browser,
    zOpen_url_headless
)

from .zOpen_file import (
    zOpen_file,
    zOpen_html,
    zOpen_text
)

from .zOpen_path import (
    zOpen_zPath,
    resolve_zPath
)

__all__ = [
    # Main class and handler
    "ZOpen",
    "handle_zOpen",
    
    # URL operations
    "zOpen_url",
    "zOpen_url_browser", 
    "zOpen_url_headless",
    
    # File operations
    "zOpen_file",
    "zOpen_html",
    "zOpen_text",
    
    # Path operations
    "zOpen_zPath",
    "resolve_zPath",
]