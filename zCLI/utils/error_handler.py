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
    
    def __init__(self, logger=None):
        """Initialize ErrorHandler with optional logger.
        
        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger
    
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

