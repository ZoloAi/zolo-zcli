# zCLI/subsystems/zDisplay_modules/display_input.py
"""
Input handling for zDisplay - User input collection
"""

from zCLI.utils.logger import logger


def handle_input(zInput_Obj, walker=None):
    """
    Handle various input events.
    
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
    event = zInput_Obj["event"]

    if event == "break":
        input("Press Enter to continue...")
        return None
    
    if event == "while":
        resp = input("\nPress Enter to retry or \nType 'stop' to cancel: ").strip().lower()
        return "stop" if resp == "stop" else "retry"
    
    if event == "input":
        user_input = input("Select an option by number: ").strip()
        print("\n")
        return user_input
    
    if event == "field":
        field = zInput_Obj.get("field", "value")
        input_type = zInput_Obj.get("input_type", "string")
        user_input = input(f"{field} ({input_type}): ").strip()
        return user_input

    return None
