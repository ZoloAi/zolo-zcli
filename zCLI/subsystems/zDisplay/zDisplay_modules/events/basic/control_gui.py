# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/control_gui.py

"""GUI-specific flow control event handlers (async, non-blocking)."""

import time


def handle_break_gui(obj, output_adapter, logger):
    """Break for GUI - send JSON event, don't block."""
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)
    
    if logger:
        logger.debug("[GUI] handle_break: message='%s'", message)
    
    # Apply indentation
    if indent > 0:
        indent_str = "  " * indent
        message = f"{indent_str}{message}"
    
    # Send break event to GUI (non-blocking)
    if hasattr(output_adapter, 'send_event'):
        output_adapter.send_event("break", {
            "message": message,
            "indent": indent,
            "timestamp": time.time()
        })
    else:
        # Fallback to line output for Terminal mode
        output_adapter.write_line(message)
    
    # Return immediately - GUI will handle continuation
    return {"status": "sent", "event": "break"}


def handle_pause_gui(obj, output_adapter, logger):
    """Pagination pause for GUI - send JSON event with pagination info."""
    message = obj.get("message", "Press Enter to continue...")
    indent = obj.get("indent", 0)
    pagination = obj.get("pagination", {})
    
    if logger:
        logger.debug("[GUI] handle_pause: pagination=%s", bool(pagination))
    
    # Send pause event to GUI with pagination data
    if hasattr(output_adapter, 'send_event'):
        output_adapter.send_event("pause", {
            "message": message,
            "indent": indent,
            "pagination": pagination,
            "timestamp": time.time()
        })
    else:
        # Fallback to line output for Terminal mode
        indent_str = "  " * indent
        output_adapter.write_line(f"{indent_str}* {message}")
    
    # Return immediately - GUI will handle pagination
    return {"status": "sent", "event": "pause", "pagination": pagination}


def handle_loading_gui(obj, output_adapter, logger):
    """Loading state for GUI - show spinner/progress indicator."""
    message = obj.get("message", "Loading...")
    loading_type = obj.get("type", "spinner")  # spinner, progress, dots
    
    if logger:
        logger.debug("[GUI] handle_loading: message='%s', type='%s'", message, loading_type)
    
    if hasattr(output_adapter, 'send_event'):
        output_adapter.send_event("loading", {
            "message": message,
            "type": loading_type,
            "timestamp": time.time()
        })
    else:
        # Fallback to simple text for Terminal
        output_adapter.write_line(f"⏳ {message}")
    
    return {"status": "sent", "event": "loading"}


def handle_await_gui(obj, output_adapter, logger):
    """Async wait state for GUI - show waiting indicator."""
    message = obj.get("message", "Waiting...")
    operation = obj.get("operation", "")
    
    if logger:
        logger.debug("[GUI] handle_await: message='%s'", message)
    
    if hasattr(output_adapter, 'send_event'):
        output_adapter.send_event("await", {
            "message": message,
            "operation": operation,
            "timestamp": time.time()
        })
    else:
        # Fallback to simple text for Terminal
        output_adapter.write_line(f"⏸ {message}")
    
    return {"status": "sent", "event": "await"}


def handle_idle_gui(obj, output_adapter, logger):
    """Idle state for GUI - clear loading/waiting states."""
    if logger:
        logger.debug("[GUI] handle_idle")
    
    if hasattr(output_adapter, 'send_event'):
        output_adapter.send_event("idle", {
            "timestamp": time.time()
        })
    
    return {"status": "sent", "event": "idle"}

