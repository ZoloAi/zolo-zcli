# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/BasicData.py
"""BasicData - structured data display events (lists, JSON)."""

from zCLI import json, re


class BasicData:
    """Basic data display events for lists and JSON output."""

    def __init__(self, display_instance):
        """Initialize BasicData with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get reference to BasicOutputs for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization

    def list(self, items, style="bullet", indent=0):
        """Display list with bullets or numbers in Terminal/GUI modes."""
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("list", {
            "items": items,
            "style": style,
            "indent": indent
        }):
            return  # GUI event sent successfully

        # Terminal mode - format and display list
        # Use BasicOutputs.text() for consistent output (composition!)
        for i, item in enumerate(items, 1):
            if style == "number":
                prefix = f"{i}. "
            else:  # bullet
                prefix = "• "

            content = f"{prefix}{item}"
            # Compose: use BasicOutputs.text() instead of calling primitives directly
            if self.BasicOutputs:
                self.BasicOutputs.text(content, indent=indent, break_after=False)
            else:
                # Fallback if BasicOutputs not set (shouldn't happen)
                self.zPrimitives.write_line(f"{'  ' * indent}{content}")

    def json_data(self, data, indent_size=2, indent=0, color=False):
        """Display JSON with pretty formatting and optional syntax coloring."""
        # Try GUI mode first - send clean event with raw data
        if self.zPrimitives.send_gui_event("json", {
            "data": data,
            "indent_size": indent_size,
            "indent": indent
        }):
            return  # GUI event sent successfully

        # Terminal mode - serialize and format JSON
        if data is None:
            return

        # Serialize to JSON
        try:
            json_str = json.dumps(data, indent=indent_size, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            json_str = f"<Error serializing JSON: {e}>"

        # Apply base indentation to each line
        if indent > 0:
            indent_str = "  " * indent
            lines = json_str.split('\n')
            json_str = '\n'.join(f"{indent_str}{line}" for line in lines)

        # Apply syntax coloring if requested (terminal only)
        if color:
            json_str = self._colorize_json(json_str)

        # Compose: use BasicOutputs.text() instead of calling primitives directly
        if self.BasicOutputs:
            # Note: json_str already has indentation applied, so pass indent=0
            self.BasicOutputs.text(json_str, indent=0, break_after=False)
        else:
            # Fallback if BasicOutputs not set (shouldn't happen)
            self.zPrimitives.write_line(json_str)

    def _colorize_json(self, json_str):
        """Apply syntax coloring to JSON string with Cyan keys, Green strings, Yellow numbers, Magenta bools/null."""
        # Color keys (quoted strings followed by colon)
        json_str = re.sub(
            r'"([^"]+)"\s*:',
            f'{self.zColors.CYAN}"\\1"{self.zColors.RESET}:',
            json_str
        )

        # Color string values (quoted strings not followed by colon)
        json_str = re.sub(
            r':\s*"([^"]*)"',
            f': {self.zColors.GREEN}"\\1"{self.zColors.RESET}',
            json_str
        )

        # Color numbers
        json_str = re.sub(
            r'\b(\d+\.?\d*)\b',
            f'{self.zColors.YELLOW}\\1{self.zColors.RESET}',
            json_str
        )

        # Color booleans and null
        json_str = re.sub(
            r'\b(true|false|null)\b',
            f'{self.zColors.MAGENTA}\\1{self.zColors.RESET}',
            json_str
        )
        
        return json_str

