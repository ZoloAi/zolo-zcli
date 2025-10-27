# zCLI/utils/zTraceback.py
"""Centralized traceback utilities with enhanced error handling and interactive UI support."""

import traceback
import sys
import logging
from pathlib import Path
from typing import Optional, Any


class zTraceback:
    """Enhanced error handling with consistent traceback formatting."""

    def __init__(self, logger=None, zcli=None):
        """Initialize zTraceback with optional logger and zCLI instance."""
        self.logger = logger
        self.zcli = zcli

        # Exception context storage for interactive handling
        self.last_exception = None
        self.last_operation = None
        self.last_context = {}
        self.exception_history = []  # Stack of exceptions for navigation

    def format_exception(self, exc: Exception, include_locals: bool = False) -> str:
        """Format exception with enhanced details (include_locals for debug mode)."""
        if include_locals:
            # Enhanced format with local variables
            tb_lines = traceback.format_exception(
                type(exc), exc, exc.__traceback__
            )
            return ''.join(tb_lines)

        # Standard format
        return ''.join(traceback.format_exception_only(type(exc), exc))

    def get_traceback_info(self, exc: Exception) -> dict:
        """Extract structured traceback information (file, line, function, error details)."""
        tb = exc.__traceback__
        if not tb:
            return {
                'exception_type': type(exc).__name__,
                'exception_message': str(exc)
            }

        # Get the last frame (where error occurred)
        while tb.tb_next:
            tb = tb.tb_next

        frame = tb.tb_frame
        return {
            'file': frame.f_code.co_filename,
            'line': tb.tb_lineno,
            'function': frame.f_code.co_name,
            'exception_type': type(exc).__name__,
            'exception_message': str(exc)
        }

    def log_exception(self,
                     exc: Exception, 
                     message: str = "Exception occurred",
                     context: Optional[dict] = None,
                     include_locals: bool = False):
        """Log exception with enhanced context and add to history (Week 6.1.1)."""
        # Store exception for potential interactive handling
        self.last_exception = exc
        self.last_context = context or {}

        # Add to exception history (Week 6.1.1 - auto-registration support)
        self.exception_history.append({
            'exception': exc,
            'message': message,
            'context': context or {},
            'traceback': self.get_traceback_info(exc)
        })

        if not self.logger:
            # Fallback to print if no logger
            print(f"{message}: {exc}", file=sys.stderr)
            traceback.print_exc()
            return

        # Log the main error message with full traceback
        self.logger.error(message + ": %s", exc, exc_info=True)

        # Add structured context if provided
        if context:
            self.logger.debug("Error context: %s", context)

        # Add enhanced details in debug mode
        if include_locals and self.logger.isEnabledFor(logging.DEBUG):
            info = self.get_traceback_info(exc)
            self.logger.debug("Error location: %s:%s in %s()",
                            info.get('file', 'unknown'),
                            info.get('line', '?'),
                            info.get('function', 'unknown'))

    def interactive_handler(self, exc: Exception, 
                          operation: Optional[callable] = None,
                          context: Optional[dict] = None) -> Any:
        """Launch interactive traceback UI (Walker) for exception handling with retry support."""
        # Store exception details for UI access
        self.last_exception = exc
        self.last_operation = operation
        self.last_context = context or {}
        self.exception_history.append({
            'exception': exc,
            'operation': operation,
            'context': context
        })

        if not self.zcli:
            # Fallback: if no zcli instance, just log and return
            if self.logger:
                self.logger.error("Interactive traceback unavailable (no zcli instance)")
            print(f"Error: {exc}", file=sys.stderr)
            traceback.print_exc()
            return None

        # Launch Walker UI for interactive error handling
        try:
            # Import zCLI here to avoid circular dependency (zCLI.zCLI imports zTraceback)
            import zCLI

            # Get package directory to find UI file
            zcli_package_dir = Path(zCLI.__file__).parent

            # Create new zCLI instance for traceback UI
            traceback_cli = zCLI.zCLI({
                "zWorkspace": str(zcli_package_dir),
                "zVaFile": "@.UI.zUI.zcli_sys",
                "zBlock": "Traceback",
                "zVerbose": False
            })

            # Pass traceback handler to the new instance so UI can access exception
            traceback_cli.zTraceback.last_exception = exc
            traceback_cli.zTraceback.last_operation = operation
            traceback_cli.zTraceback.last_context = self.last_context

            return traceback_cli.walker.run()

        except Exception as ui_error:
            # Fallback if UI launch fails
            if self.logger:
                self.logger.error("Failed to launch interactive traceback UI: %s", ui_error)
            print(f"Original Error: {exc}", file=sys.stderr)
            traceback.print_exc()
            return None


# -----------------------------------------------------------------------
# Interactive Traceback Display Functions
# -----------------------------------------------------------------------

def display_formatted_traceback(zcli):
    """Display formatted traceback with hints, context, location (Week 6.1.1 enhanced)."""
    handler = zcli.zTraceback
    exc = handler.last_exception
    
    if not exc:
        zcli.display.warning("No exception to display")
        return None
    
    # Header
    zcli.display.zDeclare("Exception Details", color="ERROR", indent=0, style="full")
    
    # Exception type and message
    zcli.display.error(f"{type(exc).__name__}: {str(exc)}", indent=1)
    
    # NEW: Display actionable hint (if available from zCLIException)
    if hasattr(exc, 'hint') and exc.hint:
        zcli.display.zDeclare("Actionable Hint", color="SUCCESS", indent=1, style="single")
        # Split multi-line hints for better readability
        hint_lines = exc.hint.split('\n')
        for line in hint_lines:
            if line.strip():  # Skip empty lines
                zcli.display.text(line, indent=2)
    
    # NEW: Display exception-specific context (from zCLIException.context)
    if hasattr(exc, 'context') and exc.context:
        zcli.display.zDeclare("Exception Context", color="INFO", indent=1, style="single")
        for key, value in exc.context.items():
            zcli.display.text(f"{key}: {value}", indent=2)
    
    # Traceback info
    info = handler.get_traceback_info(exc)
    if info:
        zcli.display.zDeclare("Location", color="WARN", indent=1, style="single")
        zcli.display.text(f"File: {info.get('file', 'unknown')}", indent=2)
        zcli.display.text(f"Line: {info.get('line', '?')}", indent=2)
        zcli.display.text(f"Function: {info.get('function', 'unknown')}", indent=2)
    
    # Operation context (from log_exception call)
    if handler.last_context:
        zcli.display.zDeclare("Operation Context", color="INFO", indent=1, style="single")
        for key, value in handler.last_context.items():
            zcli.display.text(f"{key}: {value}", indent=2)
    
    # Full traceback
    zcli.display.zDeclare("Full Traceback", color="WARN", indent=1, style="single")
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    for line in tb_lines:
        zcli.display.text(line.rstrip(), indent=2)
    
    return None


def retry_last_operation(zcli):
    """Retry the last failed operation (auto-injected by zFunc)."""
    handler = zcli.zTraceback
    
    if not handler.last_operation:
        zcli.display.error("No operation to retry", indent=1)
        return None
    
    zcli.display.info("Retrying operation...", indent=1)
    try:
        result = handler.last_operation()
        zcli.display.success("[OK] Operation succeeded!", indent=1)
        return result
    except Exception as e:
        zcli.display.error(f"[ERROR] Operation failed again: {e}", indent=1)
        # Store new exception
        handler.last_exception = e
        return None


def show_exception_history(zcli):
    """Show history of exceptions (last 10 entries)."""
    handler = zcli.zTraceback
    history = handler.exception_history
    
    if not history:
        zcli.display.warning("No exception history", indent=1)
        return None
    
    zcli.display.zDeclare(f"Exception History ({len(history)} entries)", 
                         color="INFO", indent=0, style="full")
    
    for idx, entry in enumerate(reversed(history[-10:])):  # Show last 10
        exc = entry['exception']
        zcli.display.text(f"{idx + 1}. {type(exc).__name__}: {str(exc)}", indent=1)
    
    return None


class ExceptionContext:
    """Context manager for consistent exception handling with logging and optional retry."""
    
    def __init__(
        self,
        ztraceback: "zTraceback",
        operation: str,
        context: Optional[dict] = None,
        reraise: bool = False,
        default_return: Any = None
    ):
        """Initialize exception context (operation desc, context dict, reraise flag, default_return)."""
        self.ztraceback = ztraceback
        self.operation = operation
        self.context = context or {}
        self.reraise = reraise
        self.default_return = default_return
        self.exception = None
        self.result = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Store the exception for potential inspection
            self.exception = exc_val

            # Log the exception
            self.ztraceback.log_exception(
                exc_val,
                message=f"Error during {self.operation}",
                context=self.context
            )

            # Reraise if requested
            if self.reraise:
                return False

            # Set default return value
            self.result = self.default_return

            # Suppress exception (return True)
            return True

        return False
