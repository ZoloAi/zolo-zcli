# zCLI/subsystems/zDisplay_modules/events/basic/control.py
"""
Flow control event handlers - user interaction control.

Composed events for controlling program flow and user interaction.
"""

from ..primitives.raw import handle_line
from ..primitives.input import handle_read


def handle_break(obj, output_adapter, input_adapter):
    """
    Break - pause execution and wait for Enter.
    
    Simple flow interruption: displays message and waits for user to press Enter.
    
    Args:
        obj: Display object with:
            - message (str, optional): Message to display (default: "Press Enter to continue...")
            - indent (int, optional): Indentation level (default: 0)
        output_adapter: Output adapter for displaying message
        input_adapter: Input adapter for waiting
    """
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)
    
    # Apply indentation
    if indent > 0:
        indent_str = "  " * indent
        message = f"{indent_str}{message}"
    
    # Display message using line primitive
    handle_line({"content": message}, output_adapter)
    
    # Wait for Enter using read primitive (discard result)
    handle_read({"prompt": ""}, input_adapter)


def handle_pause(obj, output_adapter, input_adapter):
    """
    Pagination pause with next/previous page support.
    
    Displays a pause message with optional pagination controls.
    User can navigate pages or continue.
    
    Args:
        obj: Display object with:
            - message: Pause message (optional)
            - indent: Indentation level (optional)
            - pagination: Dict with current_page, total_pages (optional)
        output_adapter: Output adapter for message
        input_adapter: Input adapter for user choice
        
    Returns:
        dict: {"action": "next_page" | "prev_page" | "continue"}
        
    Example obj:
        {
            "event": "pause",
            "message": "Press Enter to continue...",
            "pagination": {
                "current_page": 2,
                "total_pages": 5
            }
        }
    """
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)
    pagination = obj.get("pagination", {})
    
    indent_str = "  " * indent
    
    # Display message
    output_adapter.write_line(f"{indent_str}* {message}")
    
    # Check if we have pagination
    if pagination:
        current_page = pagination.get("current_page", 1)
        total_pages = pagination.get("total_pages", 1)
        
        if total_pages > 1:
            # Show pagination info and options
            output_adapter.write_line(f"{indent_str}    Page {current_page} of {total_pages}")
            output_adapter.write_line(f"{indent_str}    [n] Next page | [p] Previous page | [Enter] Continue")
            
            # Get user input
            output_adapter.write_raw(f"{indent_str}>>> ")
            user_input = input_adapter.collect_field_input("choice", "string", "").strip().lower()
            
            # Handle navigation
            if user_input == 'n' and current_page < total_pages:
                return {"action": "next_page"}
            elif user_input == 'p' and current_page > 1:
                return {"action": "prev_page"}
    
    # Default: just wait for Enter
    input_adapter.pause()
    return {"action": "continue"}

