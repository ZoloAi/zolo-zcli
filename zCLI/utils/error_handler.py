# zCLI/utils/error_handler.py
"""Centralized error handling and traceback utilities for zCLI.

This module provides enhanced error handling with consistent traceback formatting
across all zCLI subsystems. The ErrorHandler is automatically initialized in the
zCLI core and available via zcli.error_handler.

Usage Examples:
    
    # Basic usage - log exception with traceback
    try:
        risky_operation()
    except Exception as e:
        self.zcli.error_handler.log_exception(
            e, 
            message="Error during operation",
            context={'action': 'insert', 'table': 'users'}
        )
    
    # Using ExceptionContext for cleaner code
    from zCLI.utils import ExceptionContext
    
    with ExceptionContext(
        self.zcli.error_handler,
        operation="database insert",
        context={'table': 'users'},
        default_return="error"
    ):
        result = perform_database_insert()
    
    # Get structured traceback information
    try:
        operation()
    except Exception as e:
        info = self.zcli.error_handler.get_traceback_info(e)
        # Returns: {'file': '...', 'line': 42, 'function': 'operation', 
        #           'exception_type': 'ValueError', 'exception_message': '...'}

Note: The standard pattern logger.error(..., exc_info=True) is also fully 
supported and includes traceback automatically.
"""

import traceback
import sys
import logging
from typing import Optional, Any


class ErrorHandler:
    """Enhanced error handling with consistent traceback formatting."""
    
    def __init__(self, logger=None, zcli=None):
        """Initialize ErrorHandler with optional logger.
        
        Args:
            logger: Logger instance for error reporting
            zcli: Reference to parent zCLI instance for interactive features
        """
        self.logger = logger
        self.zcli = zcli
        
        # Exception context storage for interactive handling
        self.last_exception = None
        self.last_operation = None
        self.last_context = {}
        self.exception_history = []  # Stack of exceptions for navigation
    
    def format_exception(self, exc: Exception, include_locals: bool = False) -> str:
        """Format exception with enhanced details.
        
        Args:
            exc: The exception to format
            include_locals: Include local variables in traceback (for debug mode)
        
        Returns:
            Formatted exception string
        """
        if include_locals:
            # Enhanced format with local variables
            tb_lines = traceback.format_exception(
                type(exc), exc, exc.__traceback__
            )
            return ''.join(tb_lines)
        else:
            # Standard format
            return ''.join(traceback.format_exception_only(type(exc), exc))
    
    def get_traceback_info(self, exc: Exception) -> dict:
        """Extract structured traceback information.
        
        Args:
            exc: The exception to analyze
        
        Returns:
            Dictionary with file, line, function, and error details
        """
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
        """Log exception with enhanced context.
        
        Args:
            exc: The exception to log
            message: Custom message prefix
            context: Additional context dictionary
            include_locals: Include local variables (debug mode only)
        """
        # Store exception for potential interactive handling
        self.last_exception = exc
        self.last_context = context or {}
        
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
        """Launch interactive traceback UI for exception handling.
        
        Args:
            exc: The exception to handle
            operation: Optional callable to retry the operation
            context: Additional context about the exception
        
        Returns:
            Result from UI interaction (retry result, user choice, etc.)
        """
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
            # Create new zCLI instance for traceback UI
            # We need to get the package directory to find the UI file
            from pathlib import Path
            import zCLI as zcli_module
            zcli_package_dir = Path(zcli_module.__file__).parent
            
            traceback_cli = type(self.zcli)({
                "zWorkspace": str(zcli_package_dir),
                "zVaFile": "@.UI.zUI.zcli_sys",
                "zBlock": "Traceback",
                "zVerbose": False
            })
            
            # Pass error handler to the new instance so UI can access exception
            traceback_cli.error_handler.last_exception = exc
            traceback_cli.error_handler.last_operation = operation
            traceback_cli.error_handler.last_context = self.last_context
            
            return traceback_cli.walker.run()
            
        except Exception as ui_error:
            # Fallback if UI launch fails
            if self.logger:
                self.logger.error("Failed to launch interactive traceback UI: %s", ui_error)
            print(f"Original Error: {exc}", file=sys.stderr)
            traceback.print_exc()
            return None


# ═══════════════════════════════════════════════════════════════════
# Interactive Traceback Display Functions
# ═══════════════════════════════════════════════════════════════════

def display_formatted_traceback(zcli):
    """Display formatted traceback using zDisplay.
    
    Args:
        zcli: zCLI instance (auto-injected by zFunc)
    """
    handler = zcli.error_handler
    exc = handler.last_exception
    
    if not exc:
        zcli.display.warning("No exception to display")
        return
    
    # Header
    zcli.display.zDeclare("Exception Details", color="ERROR", indent=0, style="full")
    
    # Exception type and message
    zcli.display.error(f"{type(exc).__name__}: {str(exc)}", indent=1)
    
    # Traceback info
    info = handler.get_traceback_info(exc)
    if info:
        zcli.display.zDeclare("Location", color="WARN", indent=1, style="single")
        zcli.display.text(f"File: {info.get('file', 'unknown')}", indent=2)
        zcli.display.text(f"Line: {info.get('line', '?')}", indent=2)
        zcli.display.text(f"Function: {info.get('function', 'unknown')}", indent=2)
    
    # Context
    if handler.last_context:
        zcli.display.zDeclare("Context", color="INFO", indent=1, style="single")
        for key, value in handler.last_context.items():
            zcli.display.text(f"{key}: {value}", indent=2)
    
    # Full traceback
    zcli.display.zDeclare("Full Traceback", color="WARN", indent=1, style="single")
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    for line in tb_lines:
        zcli.display.text(line.rstrip(), indent=2)


def retry_last_operation(zcli):
    """Retry the last failed operation.
    
    Args:
        zcli: zCLI instance (auto-injected by zFunc)
    """
    handler = zcli.error_handler
    
    if not handler.last_operation:
        zcli.display.error("No operation to retry", indent=1)
        return
    
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
    """Show history of exceptions.
    
    Args:
        zcli: zCLI instance (auto-injected by zFunc)
    """
    handler = zcli.error_handler
    history = handler.exception_history
    
    if not history:
        zcli.display.warning("No exception history", indent=1)
        return
    
    zcli.display.zDeclare(f"Exception History ({len(history)} entries)", 
                         color="INFO", indent=0, style="full")
    
    for idx, entry in enumerate(reversed(history[-10:])):  # Show last 10
        exc = entry['exception']
        zcli.display.text(f"{idx + 1}. {type(exc).__name__}: {str(exc)}", indent=1)


class ExceptionContext:
    """Context manager for consistent exception handling.
    
    Usage:
        with ExceptionContext(error_handler, "database operation", 
                             context={'table': 'users'}, 
                             default_return="error"):
            result = perform_risky_operation()
    """
    
    def __init__(self, error_handler: ErrorHandler, 
                 operation: str,
                 context: Optional[dict] = None,
                 reraise: bool = False,
                 default_return: Any = None):
        """Initialize exception context.
        
        Args:
            error_handler: ErrorHandler instance
            operation: Description of the operation being performed
            context: Additional context for error logging
            reraise: Whether to reraise the exception after logging
            default_return: Value to return if exception is caught
        """
        self.error_handler = error_handler
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
            self.error_handler.log_exception(
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

