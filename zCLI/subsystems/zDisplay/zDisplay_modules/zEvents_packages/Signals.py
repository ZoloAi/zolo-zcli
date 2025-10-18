# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/Signals.py

"""Signals - colored feedback messages for user notifications."""


class Signals:
    """Signal events for feedback: error, warning, success, info, zMarker.
    
    Composes BasicOutputs.text() for output - follows the reuse pattern!
    """

    def __init__(self, display_instance):
        """Initialize Signals with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get reference to BasicOutputs for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization

    def error(self, content, indent=0):
        """Error message with red color.
        
        Terminal: Red colored text
        GUI: Clean event with 'error' type for custom styling
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("error", {
            "content": content,
            "indent": indent
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - apply red color and compose with BasicOutputs.text()
        colored = f"{self.zColors.RED}{content}{self.zColors.RESET}"
        if self.BasicOutputs:
            self.BasicOutputs.text(colored, indent=indent, break_after=False)
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            self.zPrimitives.write_line(f"{'  ' * indent}{colored}")

    def warning(self, content, indent=0):
        """Warning message with yellow color.
        
        Terminal: Yellow colored text
        GUI: Clean event with 'warning' type for custom styling
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("warning", {
            "content": content,
            "indent": indent
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - apply yellow color and compose with BasicOutputs.text()
        colored = f"{self.zColors.YELLOW}{content}{self.zColors.RESET}"
        if self.BasicOutputs:
            self.BasicOutputs.text(colored, indent=indent, break_after=False)
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            self.zPrimitives.write_line(f"{'  ' * indent}{colored}")

    def success(self, content, indent=0):
        """Success message with green color.
        
        Terminal: Green colored text
        GUI: Clean event with 'success' type for custom styling
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("success", {
            "content": content,
            "indent": indent
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - apply green color and compose with BasicOutputs.text()
        colored = f"{self.zColors.GREEN}{content}{self.zColors.RESET}"
        if self.BasicOutputs:
            self.BasicOutputs.text(colored, indent=indent, break_after=False)
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            self.zPrimitives.write_line(f"{'  ' * indent}{colored}")

    def info(self, content, indent=0):
        """Info message with cyan color.
        
        Terminal: Cyan colored text
        GUI: Clean event with 'info' type for custom styling
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("info", {
            "content": content,
            "indent": indent
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - apply cyan color and compose with BasicOutputs.text()
        colored = f"{self.zColors.CYAN}{content}{self.zColors.RESET}"
        if self.BasicOutputs:
            self.BasicOutputs.text(colored, indent=indent, break_after=False)
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            self.zPrimitives.write_line(f"{'  ' * indent}{colored}")

    def zMarker(self, label="Marker", color="MAGENTA", indent=0):
        """Flow marker - visual separator for workflow stages.
        
        Terminal: Displays separator lines with colored label
        GUI: Clean event with marker data for custom rendering
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("zMarker", {
            "label": label,
            "color": color,
            "indent": indent
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - create visual marker with separator lines
        # Get color from Colors class
        color_code = getattr(self.zColors, color.upper(), self.zColors.MAGENTA)
        
        # Create marker line and colored label
        marker_line = "=" * 60
        colored_label = f"{color_code}{label}{self.zColors.RESET}"
        
        # Compose: use BasicOutputs.text() for all lines
        if self.BasicOutputs:
            self.BasicOutputs.text("", indent=indent, break_after=False)  # Blank line
            self.BasicOutputs.text(marker_line, indent=indent, break_after=False)
            self.BasicOutputs.text(colored_label, indent=indent, break_after=False)
            self.BasicOutputs.text(marker_line, indent=indent, break_after=False)
            self.BasicOutputs.text("", indent=indent, break_after=False)  # Blank line
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            indent_str = "  " * indent
            self.zPrimitives.write_line("")
            self.zPrimitives.write_line(f"{indent_str}{marker_line}")
            self.zPrimitives.write_line(f"{indent_str}{colored_label}")
            self.zPrimitives.write_line(f"{indent_str}{marker_line}")
            self.zPrimitives.write_line("")

