# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/BasicOutputs.py

"""BasicOutputs - fundamental output events built on zPrimitives."""


class BasicOutputs:
    """Basic output events: header, zDeclare, text."""

    def __init__(self, display_instance):
        """Initialize BasicOutputs with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors

    def header(self, label, color="RESET", indent=0, style="full"):
        """Section header with mode-aware output via primitives."""
        
        # Try GUI mode first - send clean event via primitive
        if self.zPrimitives.send_gui_event("header", {
            "label": label,
            "color": color,
            "indent": indent,
            "style": style
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - build formatted content and use write_line primitive
        # Constants from original _build_line function
        INDENT_WIDTH = 2  # 2 spaces per indent
        BASE_WIDTH = 60
        
        indent_str = "  " * indent
        total_width = BASE_WIDTH - (indent * INDENT_WIDTH)
        
        # Choose character based on style
        if style == "full":
            char = "═"
        elif style == "single":
            char = "─"
        elif style == "wave":
            char = "~"
        else:
            char = "─"
        
        # Build line with centered label (exact logic from _build_line)
        if label:
            label_len = len(label) + 2  # Add spaces around label
            space = total_width - label_len
            left = space // 2
            right = space - left
            
            # Apply color - resolve string to color code if needed
            if color and color != "RESET":
                # If color is a string (color name), resolve it
                if isinstance(color, str) and not color.startswith('\033'):
                    color_code = getattr(self.zColors, color, self.zColors.RESET)
                else:
                    color_code = color
                colored_label = f"{color_code} {label} {self.zColors.RESET}"
            else:
                colored_label = f" {label} "
            
            line = f"{char * left}{colored_label}{char * right}"
        else:
            line = char * total_width
        
        # Apply indentation and write using primitive
        content = f"{indent_str}{line}"
        self.zPrimitives.write_line(content)

    def text(self, content, indent=0, break_after=True, break_message=None):
        """Display text with optional indentation and break/pause.
        
        In Terminal mode:
        - Outputs the text
        - If break_after=True, pauses for user input (Press Enter)
        
        In GUI mode:
        - Sends clean text event with break flag as metadata
        - Frontend decides how to handle the break (no blocking here)
        """
        # Try GUI mode first - send clean event with break metadata
        if self.zPrimitives.send_gui_event("text", {
            "content": content,
            "indent": indent,
            "break": break_after,
            "break_message": break_message
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - output text and optionally pause
        # Apply indentation
        if indent > 0:
            indent_str = "  " * indent
            content = f"{indent_str}{content}"
        
        # Display text using primitive
        self.zPrimitives.write_line(content)
        
        # Auto-break if enabled (pause for user input)
        if break_after:
            # Build break message
            message = break_message or "Press Enter to continue..."
            if indent > 0:
                indent_str = "  " * indent
                message = f"{indent_str}{message}"
            
            # Display message and wait for Enter using primitives
            self.zPrimitives.write_line(message)
            self.zPrimitives.read_string("")  # Wait for Enter (discard result)

