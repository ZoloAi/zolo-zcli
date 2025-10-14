# zCLI/subsystems/zDisplay_new_modules/events/walker/__init__.py
"""Walker-specific display events (menus, breadcrumbs)."""

from .menu import handle_menu
from .crumbs import handle_crumbs

__all__ = ["handle_menu", "handle_crumbs"]

