# zCLI/subsystems/zDisplay_modules/display_input.py
"""
Input handling for zDisplay - User input collection (now uses InputFactory)
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from .input import InputFactory


def handle_input(zInput_Obj, walker=None):
    """
    Handle various input events using appropriate InputAdapter.
    
    Now uses InputFactory to select the correct input adapter based on mode:
    - Terminal: Blocking input() calls
    - WebSocket: Async message-based input
    - REST: Preloaded data
    
    Supported events:
    - break: Pause for user (press Enter)
    - while: Retry or stop prompt
    - input: Menu selection
    - field: Form field input
    
    Args:
        zInput_Obj: Input configuration dict
        walker: Optional walker instance
        
    Returns:
        User input or None
    """
    # Get session from walker
    session = None
    if walker:
        session = getattr(walker, "session", None) or getattr(walker, "zSession", None)
    
    # Create appropriate input adapter
    input_adapter = InputFactory.create(session)
    
    event = zInput_Obj.get("event")

    if event == "break":
        return input_adapter.pause()
    
    if event == "while":
        return input_adapter.collect_retry_or_stop()
    
    if event == "input":
        # Menu selection - return raw input for backward compatibility
        # The calling code (zMenu) will validate the input
        # For Terminal: returns user input string
        # For WebSocket/REST: returns choice index as string
        options = zInput_Obj.get("options", [])
        if options:
            choice_idx = input_adapter.collect_menu_choice(options)
            return str(choice_idx)
        else:
            # Fallback: collect as field
            return input_adapter.collect_field_input("choice", "int", "Select an option by number")
    
    if event == "field":
        field = zInput_Obj.get("field", "value")
        input_type = zInput_Obj.get("input_type", "string")
        return input_adapter.collect_field_input(field, input_type)

    logger.warning("[handle_input] Unknown event: %s", event)
    return None
