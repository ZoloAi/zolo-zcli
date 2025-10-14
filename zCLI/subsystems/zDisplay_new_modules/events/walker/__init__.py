# zCLI/subsystems/zDisplay_new_modules/events/walker/__init__.py
"""Walker-specific display events (menus, breadcrumbs)."""

from zCLI.subsystems.zDisplay_new_modules.events.walker.menu import handle_menu
from zCLI.subsystems.zDisplay_new_modules.events.walker.crumbs import handle_crumbs

__all__ = ["handle_menu", "handle_crumbs"]

