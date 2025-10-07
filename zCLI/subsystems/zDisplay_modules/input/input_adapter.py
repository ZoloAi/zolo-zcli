# zCLI/subsystems/zDisplay_modules/input/input_adapter.py
"""
Input adapter base class and factory for multi-mode input collection
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)


class InputMode:
    """Input mode constants."""
    TERMINAL = "Terminal"    # CLI mode (input() blocking)
    WEBSOCKET = "UI"         # GUI mode (async message-based)
    REST = "REST"            # REST API mode (preloaded data)


class InputAdapter:
    """
    Abstract base class for input adapters.
    
    Each adapter implements input collection for a specific mode:
    - Terminal: input() blocking calls
    - WebSocket: async message-based input
    - REST: preloaded data (no prompting)
    
    Key Methods:
    - collect_menu_choice(): Menu selection
    - collect_field_input(): Single field input
    - collect_form_data(): Complete form submission
    - collect_enum_choice(): Enum/multiple choice
    - collect_fk_value(): Foreign key picker
    - confirm_action(): Yes/No confirmation
    - pause(): Wait for user (press Enter)
    """
    
    def __init__(self, session):
        """
        Initialize input adapter.
        
        Args:
            session: zSession dict for context
        """
        self.session = session
        self.logger = logger
    
    # ═══════════════════════════════════════════════════════════
    # Abstract Methods (must be implemented by subclasses)
    # ═══════════════════════════════════════════════════════════
    
    def collect_menu_choice(self, options, prompt="Select an option by number"):
        """
        Collect menu selection from user.
        
        Args:
            options: List of menu options
            prompt: Prompt message
            
        Returns:
            Selected index (int) or None
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_menu_choice()")
    
    def collect_field_input(self, field_name, field_type="string", prompt=None):
        """
        Collect single field input from user.
        
        Args:
            field_name: Name of the field
            field_type: Type of the field (string, int, bool, etc.)
            prompt: Optional custom prompt
            
        Returns:
            User input (string) or None
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_field_input()")
    
    def collect_form_data(self, fields, model=None):
        """
        Collect complete form data from user.
        
        Args:
            fields: List of field names or field definitions
            model: Optional schema model for validation
            
        Returns:
            Dict with field values (zConv)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_form_data()")
    
    def collect_enum_choice(self, field_name, options, prompt=None):
        """
        Collect enum/multiple choice selection.
        
        Args:
            field_name: Name of the field
            options: List of valid options
            prompt: Optional custom prompt
            
        Returns:
            Selected option (string) or None
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_enum_choice()")
    
    def collect_fk_value(self, field_name, ref_table, ref_col, available_values):
        """
        Collect foreign key value from user.
        
        Args:
            field_name: Name of the FK field
            ref_table: Referenced table name
            ref_col: Referenced column name
            available_values: List of available FK values
            
        Returns:
            Selected FK value or None
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_fk_value()")
    
    def confirm_action(self, message, default=False):
        """
        Ask user for yes/no confirmation.
        
        Args:
            message: Confirmation message
            default: Default value if user just presses Enter
            
        Returns:
            Boolean (True/False)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement confirm_action()")
    
    def pause(self, message="Press Enter to continue..."):
        """
        Pause and wait for user.
        
        Args:
            message: Pause message
            
        Returns:
            None or action dict (e.g., {"action": "continue"})
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement pause()")
    
    def collect_retry_or_stop(self, message=None):
        """
        Ask user to retry or stop.
        
        Args:
            message: Optional custom message
            
        Returns:
            "retry" or "stop"
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_retry_or_stop()")


class InputFactory:
    """
    Factory for creating input adapters based on session mode.
    
    Supports:
    - Terminal: CLI input (blocking)
    - WebSocket: GUI input (async message-based)
    - REST: API input (preloaded data)
    """
    
    @staticmethod
    def create(session):
        """
        Create appropriate input adapter for session mode.
        
        Args:
            session: zSession dict (or None for Terminal default)
            
        Returns:
            InputAdapter instance
        """
        # Default to Terminal if no session
        if not session:
            logger.debug("[InputFactory] No session provided, defaulting to Terminal")
            from .input_terminal import TerminalInput
            return TerminalInput(session)
        
        mode = session.get("zMode", "Terminal")
        logger.debug("[InputFactory] Creating input adapter for mode: %s", mode)
        
        if mode == InputMode.TERMINAL or mode == "Terminal":
            from .input_terminal import TerminalInput
            return TerminalInput(session)
        
        elif mode == InputMode.WEBSOCKET or mode == "UI":
            from .input_websocket import WebSocketInput
            return WebSocketInput(session)
        
        elif mode == InputMode.REST or mode == "REST":
            from .input_rest import RESTInput
            return RESTInput(session)
        
        else:
            logger.warning("[InputFactory] Unknown mode '%s', defaulting to Terminal", mode)
            from .input_terminal import TerminalInput
            return TerminalInput(session)
