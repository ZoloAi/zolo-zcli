# zCLI/subsystems/zNavigation/zNavigation_modules/menu_renderer.py

"""Menu renderer for zMenu."""

class MenuRenderer:
    """Handles menu display and rendering for zMenu."""

    def __init__(self, menu):
        """Initialize menu renderer."""
        self.menu = menu
        self.zcli = menu.zcli
        self.logger = menu.logger

    def render(self, menu_obj, display):
        """
        Render menu to display.
        
        Args:
            menu_obj: Menu object to render
            display: Display adapter to use
        """
        options = menu_obj["options"]
        title = menu_obj.get("title")
        allow_back = menu_obj.get("allow_back", True)

        # Show title if provided
        if title:
            display.zDeclare(title, color=self.menu.mycolor, indent=0, style="full")

        # Create menu pairs for display
        menu_pairs = list(enumerate(options))
        
        # Show breadcrumbs if available (for walker context)
        try:
            display.zCrumbs(self.zcli.session)
        except Exception:
            # Ignore if zCrumbs not available
            pass

        # Render menu using modern zDisplay method
        display.zMenu(menu_pairs)

        self.logger.debug("Rendered menu with %d options", len(options))

    def render_simple(self, options, display, prompt="Select option"):
        """
        Render simple menu without complex formatting.
        
        Args:
            options: List of options to display
            display: Display adapter to use
            prompt: Prompt text
        """
        display.zDeclare(prompt, color=self.menu.mycolor, indent=0, style="single")

        # Simple numbered list
        for i, option in enumerate(options):
            display.text(f"  [{i}] {option}")

        self.logger.debug("Rendered simple menu with %d options", len(options))

    def render_compact(self, options, display):
        """
        Render compact menu for space-constrained displays.
        
        Args:
            options: List of options to display
            display: Display adapter to use
        """
        # Show options in a compact format
        option_text = " | ".join(f"{i}:{opt}" for i, opt in enumerate(options))
        display.text(option_text)

        self.logger.debug("Rendered compact menu with %d options", len(options))
