# zCLI/subsystems/zWalker/__init__.py — Walker (UI Mode) Package
# ───────────────────────────────────────────────────────────────
"""
Walker Package - YAML-Driven UI/Menu Navigation

This package contains modules specific to Walker (UI) mode:
- zWalker.py: Main navigation controller
- zWalker_modules/: Empty (all navigation moved to core zNavigation)

Note: zDispatch and zNavigation (includes zMenu, zCrumbs, zLink) are now core subsystems 
in zCLI.subsystems for universal access. zLoader is also in zCLI.subsystems for shared usage.
"""

from .zWalker import zWalker
# zDispatch, zNavigation (includes zCrumbs, zLink, zMenu) are now imported from core subsystems

__all__ = [
    "zWalker",
]

