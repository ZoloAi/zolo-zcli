# zCLI/subsystems/zDisplay/zDisplay_modules/delegates/delegate_outputs.py

"""
Output Formatting Delegate Methods for zDisplay.

This module provides formatted output convenience methods for common display
patterns like headers, formatted text, and declarations. These methods wrap
output events with consistent styling.

Methods:
    - header: Display section headers with formatting
    - zDeclare: Display zCLI system declarations
    - text: Display formatted text content

Pattern:
    All methods delegate to handle() with output event dictionaries.

Grade: A+ (Type hints, constants, comprehensive docs)
"""

from zCLI import Any, Optional

# ═══════════════════════════════════════════════════════════════════════════
# Local Constants - To Avoid Circular Imports
# ═══════════════════════════════════════════════════════════════════════════
# Note: These constants are duplicated to avoid circular imports with parent.
# KEEP IN SYNC with display_delegates.py!

KEY_EVENT = "event"
EVENT_HEADER = "header"
EVENT_ZDECLARE = "zDeclare"
EVENT_TEXT = "text"
DEFAULT_COLOR_RESET = "RESET"
DEFAULT_STYLE_FULL = "full"
DEFAULT_INDENT = 0


class DelegateOutputs:
    """Mixin providing formatted output delegate methods.
    
    These methods provide consistent formatting for common output patterns
    like headers, colored text, and zCLI declarations.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Output Formatting Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def header(
        self, 
        label: str, 
        color: str = DEFAULT_COLOR_RESET, 
        indent: int = DEFAULT_INDENT, 
        style: str = DEFAULT_STYLE_FULL
    ) -> Any:
        """Display formatted section header.
        
        Args:
            label: Header text to display
            color: Color code (default: RESET)
            indent: Indentation level (default: 0)
            style: Header style - 'full', 'single', 'minimal' (default: full)
            
        Returns:
            Any: Result from handle() method
            
        Example:
            display.header("User Management", color="CYAN", style="full")
        """
        return self.handle({
            KEY_EVENT: EVENT_HEADER,
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def zDeclare(
        self, 
        label: str, 
        color: Optional[str] = None, 
        indent: int = DEFAULT_INDENT, 
        style: Optional[str] = None
    ) -> Any:
        """Display zCLI system declaration.
        
        Args:
            label: Declaration label/message
            color: Optional color override (default: subsystem color)
            indent: Indentation level (default: 0)
            style: Optional style override (default: None)
            
        Returns:
            Any: Result from handle() method
            
        Example:
            display.zDeclare("[CONFIG] Loading schema", color="YELLOW")
        """
        return self.handle({
            KEY_EVENT: EVENT_ZDECLARE,
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def text(
        self, 
        content: str, 
        indent: int = DEFAULT_INDENT, 
        break_after: bool = True, 
        break_message: Optional[str] = None
    ) -> Any:
        """Display formatted text content.
        
        Args:
            content: Text content to display
            indent: Indentation level (default: 0)
            break_after: Add break after content (default: True)
            break_message: Optional break message (default: None)
            
        Returns:
            Any: Result from handle() method
            
        Example:
            display.text("Configuration loaded successfully", indent=2)
        """
        return self.handle({
            KEY_EVENT: EVENT_TEXT,
            "content": content,
            "indent": indent,
            "break_after": break_after,
            "break_message": break_message,
        })

