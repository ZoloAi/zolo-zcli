# zCLI/subsystems/zDisplay_modules/input/input_terminal.py
"""
Terminal input adapter - Blocking input() calls (current implementation)
"""

from .input_adapter import InputAdapter
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class TerminalInput(InputAdapter):
    """
    Terminal input adapter for CLI mode.
    
    Uses blocking input() calls to collect user input from stdin.
    This is the current, fully-functional implementation.
    
    Key Characteristics:
    - Blocking (waits for user)
    - Synchronous
    - Validates input in loops
    - Prints prompts to stdout
    """
    
    def collect_menu_choice(self, options, prompt="Select an option by number"):
        """
        Collect menu selection from terminal.
        
        Args:
            options: List of menu options
            prompt: Prompt message
            
        Returns:
            Selected index (int) or None
        """
        while True:
            user_input = input(f"{prompt}: ").strip()
            logger.debug("User raw input: '%s'", user_input)
            
            if not user_input.isdigit():
                logger.debug("Input is not a valid digit.")
                print("\nInvalid input — enter a number.")
                continue
            
            index = int(user_input)
            if index < 0 or index >= len(options):
                logger.debug("Input index %s is out of range.", index)
                print("\nChoice out of range.")
                continue
            
            return index
    
    def collect_field_input(self, field_name, field_type="string", prompt=None):
        """
        Collect single field input from terminal.
        
        Args:
            field_name: Name of the field
            field_type: Type of the field (string, int, bool, etc.)
            prompt: Optional custom prompt
            
        Returns:
            User input (string) or None
        """
        if prompt is None:
            prompt = f"{field_name} ({field_type})"
        
        user_input = input(f"{prompt}: ").strip()
        logger.info("Field '%s' entered as: %s", field_name, user_input)
        return user_input
    
    def collect_form_data(self, fields, model=None):
        """
        Collect complete form data from terminal.
        
        This delegates to the existing render_zConv logic for now.
        In the future, this could be refactored to use the adapter methods.
        
        Args:
            fields: List of field names or field definitions
            model: Optional schema model for validation
            
        Returns:
            Dict with field values (zConv)
        """
        # For now, this is handled by render_zConv in display_forms.py
        # We'll refactor this in Phase 2
        logger.warning("[TerminalInput] collect_form_data() not yet implemented - use render_zConv()")
        return {}
    
    def collect_enum_choice(self, field_name, options, prompt=None):
        """
        Collect enum/multiple choice selection from terminal.
        
        Args:
            field_name: Name of the field
            options: List of valid options
            prompt: Optional custom prompt
            
        Returns:
            Selected option (string) or None
        """
        if prompt is None:
            print(f"\n* {field_name} (enum):")
        else:
            print(f"\n{prompt}")
        
        for idx, opt in enumerate(options):
            print(f"  {idx}: {opt}")
        
        while True:
            selected = input(f"Select {field_name} [0-{len(options)-1}]: ").strip()
            logger.info("User selected index: %s", selected)
            
            if selected.isdigit() and 0 <= int(selected) < len(options):
                chosen = options[int(selected)]
                logger.info("Field '%s' set to: %s", field_name, chosen)
                return chosen
            
            print("Invalid selection. Try again.")
            logger.warning("Invalid selection for field '%s': %s", field_name, selected)
    
    def collect_fk_value(self, field_name, ref_table, ref_col, available_values):
        """
        Collect foreign key value from terminal.
        
        Args:
            field_name: Name of the FK field
            ref_table: Referenced table name
            ref_col: Referenced column name
            available_values: List of available FK values
            
        Returns:
            Selected FK value or None
        """
        print(f"\n* {field_name} (FK → {ref_table}.{ref_col}):")
        for idx, val in enumerate(available_values):
            print(f"  {idx}: {val}")
        
        while True:
            selected = input(f"Select {field_name} [0-{len(available_values)-1}] or Enter to skip: ").strip()
            
            if selected == "":
                return None
            
            if selected.isdigit() and 0 <= int(selected) < len(available_values):
                picked = available_values[int(selected)]
                logger.info("FK field '%s' set to: %s", field_name, picked)
                return picked
            
            print("Invalid selection. Try again.")
    
    def confirm_action(self, message, default=False):
        """
        Ask user for yes/no confirmation in terminal.
        
        Args:
            message: Confirmation message
            default: Default value if user just presses Enter
            
        Returns:
            Boolean (True/False)
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{message} [{default_str}]: ").strip().lower()
        
        if response == "":
            return default
        
        return response in ("y", "yes")
    
    def pause(self, message="Press Enter to continue..."):
        """
        Pause and wait for user in terminal.
        
        Args:
            message: Pause message
            
        Returns:
            None
        """
        input(message)
        return None
    
    def collect_retry_or_stop(self, message=None):
        """
        Ask user to retry or stop in terminal.
        
        Args:
            message: Optional custom message
            
        Returns:
            "retry" or "stop"
        """
        if message:
            print(f"\n{message}")
        
        resp = input("\nPress Enter to retry or \nType 'stop' to cancel: ").strip().lower()
        return "stop" if resp == "stop" else "retry"
