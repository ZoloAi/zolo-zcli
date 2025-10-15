"""Menu interaction handler for zMenu."""

from logger import Logger

logger = Logger.get_logger(__name__)


class MenuInteraction:
    """Handles user interaction with menus for zMenu."""

    def __init__(self, menu):
        """Initialize menu interaction handler."""
        self.menu = menu
        self.zcli = menu.zcli
        self.logger = menu.logger

    def get_choice(self, menu_obj, display):
        """
        Get user choice from menu object.
        
        Args:
            menu_obj: Menu object with options
            display: Display adapter for input
            
        Returns:
            Selected option
        """
        options = menu_obj["options"]
        return self.get_choice_from_list(options, display)

    def get_choice_from_list(self, options, display):
        """
        Get user choice from list of options.
        
        Args:
            options: List of menu options
            display: Display adapter for input
            
        Returns:
            Selected option
        """
        # Streamlined input validation loop
        while True:
            choice = display.input({"event": "input"})
            self.logger.debug("User raw input: '%s'", choice)

            if not choice.isdigit():
                self.logger.debug("Input is not a valid digit.")
                display.handle({
                    "event": "text",
                    "text": "\nInvalid input — enter a number.",
                    "color": "ERROR"
                })
                continue

            index = int(choice)
            if index < 0 or index >= len(options):
                self.logger.debug("Input index %s is out of range.", index)
                display.handle({
                    "event": "text", 
                    "text": "\nChoice out of range.",
                    "color": "ERROR"
                })
                continue

            break  # Valid input

        selected = options[index]
        self.logger.debug("Selected: %s", selected)
        return selected

    def get_multiple_choices(self, options, display, prompt="Select options (comma-separated)"):
        """
        Get multiple choices from menu.
        
        Args:
            options: List of menu options
            display: Display adapter for input
            prompt: Prompt text
            
        Returns:
            List of selected options
        """
        display.handle({
            "event": "text",
            "text": prompt,
            "color": self.menu.mycolor
        })

        while True:
            choice = display.input({"event": "input"})
            self.logger.debug("User raw input: '%s'", choice)

            try:
                # Parse comma-separated choices
                indices = [int(x.strip()) for x in choice.split(",")]
                
                # Validate all indices
                invalid_indices = [i for i in indices if i < 0 or i >= len(options)]
                if invalid_indices:
                    display.handle({
                        "event": "text",
                        "text": f"\nInvalid indices: {invalid_indices}",
                        "color": "ERROR"
                    })
                    continue

                selected = [options[i] for i in indices]
                self.logger.debug("Selected multiple: %s", selected)
                return selected

            except ValueError:
                display.handle({
                    "event": "text",
                    "text": "\nInvalid input — enter comma-separated numbers.",
                    "color": "ERROR"
                })
                continue

    def get_choice_with_search(self, options, display, search_prompt="Search"):
        """
        Get choice with search functionality.
        
        Args:
            options: List of menu options
            display: Display adapter for input
            search_prompt: Search prompt text
            
        Returns:
            Selected option
        """
        filtered_options = options.copy()
        
        while True:
            # Show current filtered options
            if len(filtered_options) != len(options):
                display.handle({
                    "event": "text",
                    "text": f"\nFiltered to {len(filtered_options)} options:",
                    "color": self.menu.mycolor
                })
            
            for i, option in enumerate(filtered_options):
                display.handle({
                    "event": "text",
                    "text": f"  [{i}] {option}",
                    "color": self.menu.mycolor
                })

            # Get search or selection
            choice = display.input({"event": "input"})
            
            if choice.startswith("/"):
                # Search mode
                search_term = choice[1:].lower()
                filtered_options = [
                    opt for opt in options 
                    if search_term in str(opt).lower()
                ]
                
                if not filtered_options:
                    display.handle({
                        "event": "text",
                        "text": "No matches found.",
                        "color": "WARNING"
                    })
                    filtered_options = options.copy()
                
                continue
            
            # Selection mode
            if not choice.isdigit():
                display.handle({
                    "event": "text",
                    "text": "\nInvalid input — enter a number or /search",
                    "color": "ERROR"
                })
                continue

            index = int(choice)
            if index < 0 or index >= len(filtered_options):
                display.handle({
                    "event": "text",
                    "text": "\nChoice out of range.",
                    "color": "ERROR"
                })
                continue

            selected = filtered_options[index]
            self.logger.debug("Selected with search: %s", selected)
            return selected
