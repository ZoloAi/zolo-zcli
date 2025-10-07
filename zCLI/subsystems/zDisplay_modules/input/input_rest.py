# zCLI/subsystems/zDisplay_modules/input/input_rest.py
"""
REST API input adapter - Preloaded data (STUB)

TODO: Implement when REST API wrapper is created
"""

from .input_adapter import InputAdapter
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class RESTInput(InputAdapter):
    """
    REST API input adapter.
    
    In REST mode, all input data is provided upfront in the API request.
    No interactive prompting occurs - the adapter returns preloaded data.
    
    Key Differences from Terminal/WebSocket:
    - No prompting (data is preloaded)
    - No waiting for user input
    - Returns data from request payload
    - Validation happens before/after, not during input
    
    Use Case:
    - External API integrations
    - Programmatic access to zolo-zcli
    - Headless automation
    - Batch operations
    
    Example REST Request:
    ```
    POST /api/users
    {
        "username": "john_doe",
        "email": "john@example.com",
        "role": "admin"
    }
    ```
    
    The input adapter returns this preloaded data instead of prompting.
    
    STATUS: STUB - Ready for implementation when REST API is needed
    """
    
    def __init__(self, session):
        super().__init__(session)
        self.preloaded_data = session.get("zRequestData", {}) if session else {}
    
    def _get_preloaded_value(self, key, default=None):
        """
        Get preloaded value from request data.
        
        Args:
            key: Data key
            default: Default value if not found
            
        Returns:
            Preloaded value or default
        """
        value = self.preloaded_data.get(key, default)
        self.logger.debug("[RESTInput] Retrieved preloaded value for '%s': %s", key, value)
        return value
    
    # ═══════════════════════════════════════════════════════════
    # Input Collection Methods (Return preloaded data)
    # ═══════════════════════════════════════════════════════════
    
    def collect_menu_choice(self, options, prompt="Select an option by number"):
        """
        Return preloaded menu choice.
        
        REST API should include menu choice in request:
        {"menu_choice": 0}
        
        Args:
            options: List of menu options (ignored in REST)
            prompt: Prompt message (ignored in REST)
            
        Returns:
            Preloaded choice index or 0 (default)
        """
        self.logger.debug("[RESTInput] collect_menu_choice - returning preloaded value")
        choice = self._get_preloaded_value("menu_choice", 0)
        
        # Validate choice is in range
        if not isinstance(choice, int) or choice < 0 or choice >= len(options):
            self.logger.warning("[RESTInput] Invalid menu choice %s, defaulting to 0", choice)
            return 0
        
        return choice
    
    def collect_field_input(self, field_name, field_type="string", prompt=None):
        """
        Return preloaded field value.
        
        REST API should include field values in request:
        {"username": "john_doe", "email": "john@example.com"}
        
        Args:
            field_name: Name of the field
            field_type: Type of the field (for validation)
            prompt: Prompt message (ignored in REST)
            
        Returns:
            Preloaded field value or empty string
        """
        self.logger.debug("[RESTInput] collect_field_input - field: %s", field_name)
        value = self._get_preloaded_value(field_name, "")
        
        # TODO: Type validation based on field_type
        # For now, just return as string
        return str(value) if value is not None else ""
    
    def collect_form_data(self, fields, model=None):
        """
        Return preloaded form data.
        
        REST API should include all form fields in request:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "role": "admin"
        }
        
        Args:
            fields: List of field names
            model: Optional schema model (for validation)
            
        Returns:
            Dict with preloaded field values
        """
        self.logger.debug("[RESTInput] collect_form_data - fields: %s", fields)
        
        # Extract only requested fields from preloaded data
        form_data = {}
        for field in fields:
            if isinstance(field, str):
                field_name = field
            elif isinstance(field, dict):
                field_name = field.get("name", "")
            else:
                continue
            
            value = self._get_preloaded_value(field_name)
            if value is not None:
                form_data[field_name] = value
        
        self.logger.info("[RESTInput] Returning form data: %s", form_data)
        return form_data
    
    def collect_enum_choice(self, field_name, options, prompt=None):
        """
        Return preloaded enum value.
        
        REST API should include enum value in request:
        {"role": "admin"}
        
        Args:
            field_name: Name of the field
            options: List of valid options
            prompt: Prompt message (ignored in REST)
            
        Returns:
            Preloaded enum value or first option
        """
        self.logger.debug("[RESTInput] collect_enum_choice - field: %s", field_name)
        value = self._get_preloaded_value(field_name)
        
        # Validate value is in options
        if value not in options:
            self.logger.warning("[RESTInput] Invalid enum value '%s' for field '%s', using first option", 
                              value, field_name)
            return options[0] if options else None
        
        return value
    
    def collect_fk_value(self, field_name, ref_table, ref_col, available_values):
        """
        Return preloaded FK value.
        
        REST API should include FK value in request:
        {"user_id": 123}
        
        Args:
            field_name: Name of the FK field
            ref_table: Referenced table name (ignored in REST)
            ref_col: Referenced column name (ignored in REST)
            available_values: List of available FK values
            
        Returns:
            Preloaded FK value or None
        """
        self.logger.debug("[RESTInput] collect_fk_value - field: %s", field_name)
        value = self._get_preloaded_value(field_name)
        
        # Validate value is in available values
        if value is not None and value not in available_values:
            self.logger.warning("[RESTInput] Invalid FK value '%s' for field '%s'", value, field_name)
            return None
        
        return value
    
    def confirm_action(self, message, default=False):
        """
        Return preloaded confirmation.
        
        REST API should include confirmation in request:
        {"confirm": true}
        
        Args:
            message: Confirmation message (ignored in REST)
            default: Default value if not provided
            
        Returns:
            Boolean confirmation
        """
        self.logger.debug("[RESTInput] confirm_action - message: %s", message)
        confirmed = self._get_preloaded_value("confirm", default)
        return bool(confirmed)
    
    def pause(self, message="Press Enter to continue..."):
        """
        No pause in REST mode - return immediately.
        
        Args:
            message: Pause message (ignored in REST)
            
        Returns:
            Action dict
        """
        self.logger.debug("[RESTInput] pause() called (no-op in REST mode)")
        return {"action": "continue"}
    
    def collect_retry_or_stop(self, message=None):
        """
        Return preloaded retry/stop choice.
        
        REST API should include retry choice in request:
        {"retry": true}
        
        Args:
            message: Message (ignored in REST)
            
        Returns:
            "retry" or "stop"
        """
        self.logger.debug("[RESTInput] collect_retry_or_stop")
        should_retry = self._get_preloaded_value("retry", False)
        return "retry" if should_retry else "stop"
