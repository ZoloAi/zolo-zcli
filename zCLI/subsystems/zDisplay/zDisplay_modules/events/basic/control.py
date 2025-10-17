# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/control.py

"""Flow control event handlers for user interaction."""

from ..primitives.raw import handle_line
from ..primitives.input import handle_read


def handle_break(obj, output_adapter, input_adapter, logger):
    """Break - pause execution and wait for Enter."""
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)

    # Apply indentation
    if indent > 0:
        indent_str = "  " * indent
        message = f"{indent_str}{message}"

    # Display message using line primitive
    handle_line({"content": message}, output_adapter, logger)

    # Wait for Enter using read primitive (discard result)
    handle_read({"prompt": ""}, input_adapter, logger)

def handle_pause(obj, output_adapter, input_adapter, logger):
    """Pagination pause with next/previous page support."""
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)
    pagination = obj.get("pagination", {})

    logger.debug("handle_pause: pagination=%s", bool(pagination))

    indent_str = "  " * indent

    # Display message
    output_adapter.write_line(f"{indent_str}* {message}")

    # Check if we have pagination
    if pagination:
        current_page = pagination.get("current_page", 1)
        total_pages = pagination.get("total_pages", 1)

        if total_pages > 1:
            logger.debug("Showing pagination: page %d of %d", current_page, total_pages)
            # Show pagination info and options
            output_adapter.write_line(f"{indent_str}    Page {current_page} of {total_pages}")
            output_adapter.write_line(f"{indent_str}    [n] Next page | [p] Previous page | [Enter] Continue")

            # Get user input
            output_adapter.write_raw(f"{indent_str}>>> ")
            user_input = input_adapter.collect_field_input("choice", "string", "").strip().lower()

            # Handle navigation
            if user_input == 'n' and current_page < total_pages:
                logger.debug("User selected: next page")
                return {"action": "next_page"}
            elif user_input == 'p' and current_page > 1:
                logger.debug("User selected: previous page")
                return {"action": "prev_page"}

    # Default: just wait for Enter
    logger.debug("Pausing for user input")
    input_adapter.pause()
    return {"action": "continue"}
