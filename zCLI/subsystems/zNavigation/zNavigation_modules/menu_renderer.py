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
            display.handle({
                "event": "sysmsg",
                "label": title,
                "style": "full",
                "color": self.menu.mycolor,
                "indent": 0
            })

        # Create menu pairs for display
        menu_pairs = list(enumerate(options))
        
        # Show breadcrumbs if available (for walker context)
        try:
            display.handle({"event": "zCrumbs"})
        except Exception:
            # Ignore if zCrumbs not available
            pass

        # Render menu
        display.handle({
            "event": "zMenu",
            "menu": menu_pairs
        })

        self.logger.debug("Rendered menu with %d options", len(options))

    def render_simple(self, options, display, prompt="Select option"):
        """
        Render simple menu without complex formatting.
        
        Args:
            options: List of options to display
            display: Display adapter to use
            prompt: Prompt text
        """
        display.handle({
            "event": "sysmsg",
            "label": prompt,
            "style": "single",
            "color": self.menu.mycolor,
            "indent": 0
        })

        # Simple numbered list
        for i, option in enumerate(options):
            display.handle({
                "event": "text",
                "text": f"  [{i}] {option}",
                "color": self.menu.mycolor
            })

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
        display.handle({
            "event": "text",
            "text": option_text,
            "color": self.menu.mycolor
        })

        self.logger.debug("Rendered compact menu with %d options", len(options))
