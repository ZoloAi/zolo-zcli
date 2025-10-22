# zCLI/subsystems/zWalker/__init__.py - Walker (UI Mode) Package
# --------------------------------------------------------------
"""
Walker Package - Modern YAML-Driven UI/Menu Navigation

This package contains the modern zWalker subsystem:
- zWalker.py: Main navigation controller (fully modernized)

Architecture:
- Uses core zCLI subsystems (zNavigation, zDispatch, zDisplay, etc.)
- No local subsystem instances - everything shared from core
- Unified navigation system via zNavigation
- Fully modernized - no legacy compatibility code

Note: All navigation components (zMenu, zCrumbs, zLink) are now part of 
core zNavigation subsystem for universal access across all subsystems.
"""

from .zWalker import zWalker
# zDispatch, zNavigation (includes zCrumbs, zLink, zMenu) are now imported from core subsystems

__all__ = [
    "zWalker",
]

