# zCLI/subsystems/zWalker/__init__.py — Walker (UI Mode) Package
# ───────────────────────────────────────────────────────────────
"""
Walker Package - YAML-Driven UI/Menu Navigation

This package contains modules specific to Walker (UI) mode:
- zWalker.py: Main navigation controller
- zWalker_modules/: Component modules
  - zDispatch: Event/action dispatching
  - zMenu: Menu rendering and navigation
  - zLink: Inter-file linking
  - zCrumbs: Breadcrumb navigation tracking

Note: zLoader is in zCLI.subsystems for shared usage.
"""

from .zWalker import zWalker
from .zWalker_modules.zDispatch import ZDispatch
from .zWalker_modules.zMenu import ZMenu
from .zWalker_modules.zLink import ZLink
from .zWalker_modules.zCrumbs import zCrumbs

__all__ = [
    "zWalker",
    "ZDispatch",
    "ZMenu",
    "ZLink",
    "zCrumbs",
]

