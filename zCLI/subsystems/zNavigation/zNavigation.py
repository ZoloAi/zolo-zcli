"""zNavigation - Unified Navigation System Subsystem for zCLI."""

from logger import Logger
from .zNavigation_modules.menu_system import MenuSystem
from .zNavigation_modules.breadcrumbs import Breadcrumbs
from .zNavigation_modules.navigation import Navigation
from .zNavigation_modules.linking import Linking

# Logger instance
logger = Logger.get_logger(__name__)


class zNavigation:
    """Unified navigation system subsystem for zCLI."""

    def __init__(self, zcli):
        """Initialize zNavigation subsystem."""
        if zcli is None:
            raise ValueError("zNavigation requires a zCLI instance")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "MENU"  # Keep MENU color for backward compatibility

        # Initialize navigation modules
        self.menu = MenuSystem(self)
        self.breadcrumbs = Breadcrumbs(self)
        self.navigation = Navigation(self)
        self.linking = Linking(self)

        # Print styled ready message using zDisplay (available in Layer 1)
        self.zcli.display.handle({
            "event": "sysmsg",
            "label": "zNavigation Ready",
            "color": self.mycolor,
            "indent": 0
        })

        self.logger.info("[zNavigation] Unified navigation system ready")

    # Menu System Methods
    def create(self, options, title=None, allow_back=True, walker=None):
        """Create and display a menu, return user choice."""
        return self.menu.create(options, title, allow_back, walker)

    def select(self, options, prompt="Select option", walker=None):
        """Simple selection menu without complex navigation."""
        return self.menu.select(options, prompt, walker)

    def handle(self, zMenu_obj, walker=None):
        """Handle legacy zMenu object format (for backward compatibility)."""
        return self.menu.handle(zMenu_obj, walker)

    # Breadcrumbs Methods
    def handle_zCrumbs(self, zBlock, zKey, walker=None):
        """Handle breadcrumb trail management."""
        return self.breadcrumbs.handle_zCrumbs(zBlock, zKey, walker)

    def handle_zBack(self, show_banner=True, walker=None):
        """Handle back navigation."""
        return self.breadcrumbs.handle_zBack(show_banner, walker)

    # Navigation Methods
    def navigate_to(self, target, context=None):
        """Navigate to a specific target."""
        return self.navigation.navigate_to(target, context)

    def get_current_location(self):
        """Get current navigation location."""
        return self.navigation.get_current_location()

    def get_navigation_history(self):
        """Get navigation history."""
        return self.navigation.get_navigation_history()

    # Linking Methods
    def handle_zLink(self, zHorizontal, walker=None):
        """Handle inter-file linking."""
        return self.linking.handle_zLink(zHorizontal, walker)

    def create_link(self, source, target, metadata=None):
        """Create a navigation link."""
        return self.linking.create_link(source, target, metadata)


# Standalone handler functions for backward compatibility
def handle_zMenu(zMenu_obj, zcli=None, walker=None):
    """Standalone menu handler function."""
    if walker:
        zcli_instance = walker.zcli
    elif zcli:
        zcli_instance = zcli
    else:
        raise ValueError("handle_zMenu requires either zcli or walker parameter")
    
    return zcli_instance.navigation.handle(zMenu_obj, walker=walker)


def handle_zLink(zHorizontal, walker=None):
    """Standalone link handler function."""
    if not walker:
        raise ValueError("handle_zLink requires walker parameter")
    
    return walker.zcli.navigation.handle_zLink(zHorizontal, walker)


def handle_zCrumbs(zBlock, zKey, walker=None):
    """Standalone breadcrumbs handler function."""
    if not walker:
        raise ValueError("handle_zCrumbs requires walker parameter")
    
    return walker.zcli.navigation.handle_zCrumbs(zBlock, zKey, walker)
