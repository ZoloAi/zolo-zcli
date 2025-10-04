# zCLI/subsystems/zOpen_modules/__init__.py — zOpen Registry Package
# ───────────────────────────────────────────────────────────────
"""
zOpen Registry Package

This package serves as a registry for zOpen specialized modules:
- zOpen_url.py: URL opening with browser/curl fallbacks
- zOpen_file.py: Local file opening operations
- zOpen_path.py: zPath resolution and opening

Note: The main ZOpen class and handle_zOpen function are now in zOpen.py
"""

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