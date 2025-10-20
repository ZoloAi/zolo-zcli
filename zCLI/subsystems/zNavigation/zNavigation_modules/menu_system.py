# zCLI/subsystems/zNavigation/zNavigation_modules/menu_system.py

"""Menu system for zNavigation."""

from .menu_builder import MenuBuilder
from .menu_renderer import MenuRenderer
from .menu_interaction import MenuInteraction


class MenuSystem:
    """Unified menu system for zNavigation."""

    def __init__(self, navigation):
        """Initialize menu system."""
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger

        # Initialize menu components
        self.builder = MenuBuilder(self)
        self.renderer = MenuRenderer(self)
        self.interaction = MenuInteraction(self)

    def create(self, options, title=None, allow_back=True, walker=None):
        """
        Create and display a menu, return user choice.
        
        Args:
            options: List of menu options or dict with options
            title: Optional menu title
            allow_back: Whether to add "Back" option
            walker: Optional walker instance for context
            
        Returns:
            Selected option or "zBack" if back chosen
        """
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display
        
        display.zDeclare("zNavigation Menu Create", color=self.navigation.mycolor, indent=1, style="full")

        # Build menu object
        menu_obj = self.builder.build(options, title, allow_back)
        
        # Render menu
        self.renderer.render(menu_obj, display)
        
        # Get user interaction
        choice = self.interaction.get_choice(menu_obj, display)
        
        return choice

    def select(self, options, prompt="Select option", walker=None):
        """
        Simple selection menu without complex navigation.
        
        Args:
            options: List of options to select from
            prompt: Prompt text to display
            walker: Optional walker instance for context
            
        Returns:
            Selected option
        """
        display = walker.display if walker else self.zcli.display
        
        display.zDeclare("zNavigation Menu Select", color=self.navigation.mycolor, indent=1, style="single")

        # Build simple menu
        menu_obj = self.builder.build(options, prompt, allow_back=False)
        
        # Render menu
        self.renderer.render(menu_obj, display)
        
        # Get user choice
        choice = self.interaction.get_choice(menu_obj, display)
        
        return choice

    def handle(self, zMenu_obj, walker=None):
        """
        Handle legacy zMenu object format (for backward compatibility).
        
        Args:
            zMenu_obj: Legacy menu object with zBlock, zKey, zHorizontal, is_anchor
            walker: Walker instance (required for legacy format)
            
        Returns:
            Menu result
        """
        if not walker:
            raise ValueError("Legacy zNavigation.handle requires walker instance")
        
        display = walker.display
        
        display.zDeclare("Handle zNavigation Menu", color=self.navigation.mycolor, indent=1, style="full")

        self.logger.debug(
            "\nzMENU Object:"
            "\n. zBlock      : %s"
            "\n. zKey        : %s"
            "\n. zHorizontal : %s"
            "\n. is_anchor   : %s",
            zMenu_obj.get("zBlock"),
            zMenu_obj.get("zKey"),
            zMenu_obj.get("zHorizontal"),
            zMenu_obj.get("is_anchor")
        )

        # Handle anchor mode logic
        options = zMenu_obj["zHorizontal"]
        if not zMenu_obj["is_anchor"]:
            self.logger.debug("Anchor mode active — injecting zBack into menu.")
            options = options + ["zBack"]

        self.logger.debug("zMenu options:\n%s", options)

        # Create menu pairs for display
        menu_pairs = list(enumerate(options))
        display.zCrumbs(self.zcli.session)
        display.zMenu(menu_pairs)

        # Get user choice
        choice = self.interaction.get_choice_from_list(options, display)
        
        # Modern approach: just return the choice
        # The walker's execute_loop will look up the key and dispatch it
        display.zDeclare("zNavigation Menu return", color=self.navigation.mycolor, indent=1, style="~")
        self.logger.debug("Menu selected: %s", choice)
        return choice
