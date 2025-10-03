# zCLI/walker/__init__.py — Walker (UI Mode) Package
# ───────────────────────────────────────────────────────────────
"""
Walker Package - YAML-Driven UI/Menu Navigation

This package contains modules specific to Walker (UI) mode:
- zWalker: Main navigation controller
- zDispatch: Event/action dispatching
- zMenu: Menu rendering and navigation
- zLink: Inter-file linking
- zCrumbs: Breadcrumb navigation tracking

Note: zLoader has been moved to zCLI.subsystems for shared usage.
"""

from .zWalker import zWalker
from .zDispatch import ZDispatch
from .zMenu import ZMenu
from .zLink import ZLink
from .zCrumbs import zCrumbs

__all__ = [
    "zWalker",
    "ZDispatch",
    "ZMenu",
    "ZLink",
    "zCrumbs",
]

