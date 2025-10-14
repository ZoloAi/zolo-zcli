# zCLI/subsystems/zDisplay_modules/events/primitives/input.py
"""
Input primitive handlers - atomic input operations.

These are the most basic input operations that cannot be decomposed further:
- read: Read string from input (blocks until Enter)
- read_password: Read masked string (for passwords)
"""

from logger import Logger

logger = Logger.get_logger(__name__)


def handle_read(obj, input_adapter):
    """
    Read string primitive - most atomic input operation.
    
    Blocks until user presses Enter, returns string.
    
    Args:
        obj: Display object with:
            - prompt (str, optional): Prompt to display before reading
            
    Returns:
        String entered by user
    """
    prompt = obj.get("prompt", "")
    return input_adapter.read_string(prompt)


def handle_read_password(obj, input_adapter):
    """
    Read password primitive - masked input.
    
    Args:
        obj: Display object with:
            - prompt (str, optional): Prompt to display before reading
            
    Returns:
        String entered by user (input was masked)
    """
    prompt = obj.get("prompt", "")
    return input_adapter.read_password(prompt)

