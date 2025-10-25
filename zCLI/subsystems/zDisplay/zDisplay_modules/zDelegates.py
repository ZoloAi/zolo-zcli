# zCLI/subsystems/zDisplay/zDisplay_modules/zDelegates.py

"""Convenience delegate methods for zDisplay.

These are thin wrappers that call display.handle() for backward compatibility.
All methods route through the unified handle() method with event dictionaries.

New code should use display.handle() directly with event dicts.
These delegates exist for convenience and backward compatibility only.
"""


class zDisplayDelegates:
    """Mixin class providing convenience delegate methods for zDisplay.
    
    All methods are thin wrappers that call self.handle() with appropriate
    event dictionaries. This keeps the main zDisplay class clean while
    maintaining backward compatibility with existing code.
    
    Note: This is a mixin class. The handle() method is provided by the
    subclass (zDisplay). Linter warnings about missing 'handle' member
    are expected and can be ignored.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Primitive Output Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def write_raw(self, content):
        """Write raw content without processing. Wrapper for handle()."""
        return self.handle({"event": "write_raw", "content": content})

    def write_line(self, content):
        """Write content with newline. Wrapper for handle()."""
        return self.handle({"event": "write_line", "content": content})

    def write_block(self, content):
        """Write content as a block. Wrapper for handle()."""
        return self.handle({"event": "write_block", "content": content})

    # ═══════════════════════════════════════════════════════════════════════════
    # Primitive Input Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def read_string(self, prompt=""):
        """Read string input from user. Wrapper for handle()."""
        return self.handle({"event": "read_string", "prompt": prompt})

    def read_password(self, prompt=""):
        """Read password input (masked). Wrapper for handle()."""
        return self.handle({"event": "read_password", "prompt": prompt})

    def read_primitive(self, obj):
        """Read string primitive with obj parameter. Wrapper for handle()."""
        prompt = obj.get("prompt", "")
        return self.handle({"event": "read_string", "prompt": prompt})

    def read_password_primitive(self, obj):
        """Read password primitive with obj parameter. Wrapper for handle()."""
        prompt = obj.get("prompt", "")
        return self.handle({"event": "read_password", "prompt": prompt})

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Output Event Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def header(self, label, color="RESET", indent=0, style="full"):
        """Display formatted header. Wrapper for handle()."""
        return self.handle({
            "event": "header",
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def zDeclare(self, label, color=None, indent=0, style=None):
        """Display system declaration. Wrapper for handle()."""
        return self.handle({
            "event": "zDeclare",
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def text(self, content, indent=0, break_after=True, break_message=None):
        """Display text content. Wrapper for handle()."""
        return self.handle({
            "event": "text",
            "content": content,
            "indent": indent,
            "break_after": break_after,
            "break_message": break_message,
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # Signal Event Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def error(self, content, indent=0):
        """Display error message. Wrapper for handle()."""
        return self.handle({
            "event": "error",
            "content": content,
            "indent": indent,
        })

    def warning(self, content, indent=0):
        """Display warning message. Wrapper for handle()."""
        return self.handle({
            "event": "warning",
            "content": content,
            "indent": indent,
        })

    def success(self, content, indent=0):
        """Display success message. Wrapper for handle()."""
        return self.handle({
            "event": "success",
            "content": content,
            "indent": indent,
        })

    def info(self, content, indent=0):
        """Display info message. Wrapper for handle()."""
        return self.handle({
            "event": "info",
            "content": content,
            "indent": indent,
        })

    def zMarker(self, label="Marker", color="MAGENTA", indent=0):
        """Display marker. Wrapper for handle()."""
        return self.handle({
            "event": "zMarker",
            "label": label,
            "color": color,
            "indent": indent,
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # Data Event Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def list(self, items, style="bullet", indent=0):
        """Display list of items. Wrapper for handle()."""
        return self.handle({
            "event": "list",
            "items": items,
            "style": style,
            "indent": indent,
        })

    def json_data(self, data, indent_size=2, indent=0, color=False):
        """Display JSON data. Wrapper for handle()."""
        return self.handle({
            "event": "json_data",
            "data": data,
            "indent_size": indent_size,
            "indent": indent,
            "color": color,
        })

    def json(self, data, indent_size=2, indent=0, color=False):
        """Alias for json_data. Wrapper for handle()."""
        return self.handle({
            "event": "json",
            "data": data,
            "indent_size": indent_size,
            "indent": indent,
            "color": color,
        })

    def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
        """Display table with pagination. Wrapper for handle()."""
        return self.handle({
            "event": "zTable",
            "title": title,
            "columns": columns,
            "rows": rows,
            "limit": limit,
            "offset": offset,
            "show_header": show_header,
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # System Event Delegates
    # ═══════════════════════════════════════════════════════════════════════════

    def zSession(self, session_data, break_after=True, break_message=None):
        """Display session information. Wrapper for handle()."""
        return self.handle({
            "event": "zSession",
            "session_data": session_data,
            "break_after": break_after,
            "break_message": break_message,
        })

    def zCrumbs(self, session_data):
        """Display breadcrumb navigation. Wrapper for handle()."""
        return self.handle({
            "event": "zCrumbs",
            "session_data": session_data,
        })

    def zMenu(self, menu_items, prompt="Select an option:", return_selection=False):
        """Display menu for selection. Wrapper for handle()."""
        return self.handle({
            "event": "zMenu",
            "menu_items": menu_items,
            "prompt": prompt,
            "return_selection": return_selection,
        })

    def selection(self, prompt, options, multi=False, default=None, style="numbered"):
        """Display selection interface. Wrapper for handle()."""
        return self.handle({
            "event": "selection",
            "prompt": prompt,
            "options": options,
            "multi": multi,
            "default": default,
            "style": style,
        })

    def zDialog(self, context, zcli=None, walker=None):
        """Display dialog form. Wrapper for handle()."""
        return self.handle({
            "event": "zDialog",
            "context": context,
            "zcli": zcli,
            "walker": walker,
        })

