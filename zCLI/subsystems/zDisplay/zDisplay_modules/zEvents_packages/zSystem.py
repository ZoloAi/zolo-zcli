# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/zSystem.py

"""zSystem - zCLI system introspection and navigation displays.

These events display zCLI's internal state: session info, breadcrumbs, menus, forms.
All compose existing BasicOutputs events for maximum code reuse.
"""


class zSystem:
    """zCLI system events: zDeclare, zSession, zCrumbs, zMenu, zDialog."""

    def __init__(self, display_instance):
        """Initialize zSystem with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get references to other packages for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization
        self.Signals = None  # Will be set after zEvents initialization
        self.BasicInputs = None  # Will be set after zEvents initialization

    def zDeclare(self, label, color=None, indent=0, style=None):
        """System message/declaration - header with log level conditioning and auto-style.
        
        This is a composed event that uses header() internally with additional logic:
        - Checks log level to determine if message should be shown
        - Auto-selects style based on indent level if not specified
        - Uses subsystem color if available
        """
        # Check if system messages should be displayed based on logging level
        if not self._should_show_sysmsg():
            return
        
        # Use display's mycolor if no color specified
        if color is None:
            color = getattr(self.display, 'mycolor', 'RESET')
        
        # Auto-select style based on indent if not specified
        if style is None:
            if indent == 0:
                style = "full"
            elif indent == 1:
                style = "single"
            else:  # indent >= 2
                style = "wave"
        
        # Compose: use header event to do the actual rendering
        if self.BasicOutputs:
            self.BasicOutputs.header(label, color, indent, style)

    def zSession(self, session_data, break_after=True, break_message=None):
        """Display zCLI session information.
        
        Shows: zSession_ID, zMode, zMachine, zAuth, workspace info
        Composes: BasicOutputs.text(), Signals for colored fields
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("zSession", {
            "session": session_data,
            "break": break_after,
            "break_message": break_message
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - display session using composed events
        if not session_data:
            if self.BasicOutputs:
                self.BasicOutputs.text("No session available", break_after=False)
            return
        
        # Header
        self.zDeclare("View zSession", color="MAIN", indent=0)
        
        # Core session fields
        self._display_field("zSession_ID", session_data.get("zS_id"))
        self._display_field("zMode", session_data.get("zMode"))
        
        # zMachine section
        zMachine = session_data.get("zMachine", {})
        if zMachine:
            self._display_zmachine(zMachine)
        
        # Session fields
        if self.BasicOutputs:
            self.BasicOutputs.text("", break_after=False)
        for field in ["zWorkspace", "zVaFile_path", "zVaFilename", "zBlock"]:
            self._display_field(field, session_data.get(field))
        
        # zAuth section
        zAuth = session_data.get("zAuth", {})
        if zAuth:
            self._display_zauth(zAuth)
        
        # Optional break at the end
        if break_after and self.BasicOutputs:
            self.BasicOutputs.text("", break_after=False)
            self.BasicOutputs.text(break_message or "Press Enter to continue...", break_after=True)

    def zCrumbs(self, session_data):
        """Display breadcrumb navigation trail.
        
        Shows: Navigation path for each scope (e.g., "main > users > edit")
        Composes: BasicOutputs.text() for all output
        """
        # Try GUI mode first - send clean event
        z_crumbs = session_data.get("zCrumbs", {}) if session_data else {}
        
        if self.zPrimitives.send_gui_event("zCrumbs", {
            "crumbs": z_crumbs
        }):
            return  # GUI event sent successfully
        
        # Terminal mode - display breadcrumbs using composed events
        if not z_crumbs:
            return
        
        # Build formatted breadcrumb display
        crumbs_display = {}
        for scope, trail in z_crumbs.items():
            # Join trail with " > " separator
            path = " > ".join(trail) if trail else ""
            crumbs_display[scope] = path
        
        # Display breadcrumbs using BasicOutputs.text()
        if self.BasicOutputs:
            self.BasicOutputs.text("", break_after=False)
            self.BasicOutputs.text("zCrumbs:", break_after=False)
            for scope, path in crumbs_display.items():
                self.BasicOutputs.text(f"  {scope}[{path}]", break_after=False)

    def zMenu(self, menu_items, prompt="Select an option:", return_selection=False):
        """Display menu options and optionally collect selection.
        
        Shows: Numbered menu for Walker navigation
        Composes: BasicInputs.selection() for interactive menus
        
        Args:
            menu_items: List of (number, label) tuples
            prompt: Selection prompt
            return_selection: If True, collect and return user selection
        
        Returns:
            If return_selection=True: selected option label or None
            If return_selection=False: None (display only)
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("zMenu", {
            "menu": menu_items,
            "prompt": prompt,
            "return_selection": return_selection
        }):
            return None  # GUI event sent successfully
        
        # Terminal mode - compose BasicInputs.selection()
        if not menu_items:
            return None
        
        # Extract just the labels for selection
        options = [label for _, label in menu_items]
        
        # If interactive, use selection event
        if return_selection and self.BasicInputs:
            return self.BasicInputs.selection(
                prompt=prompt,
                options=options,
                multi=False,
                style="numbered"
            )
        else:
            # Display-only mode: just show the menu
            if self.BasicOutputs:
                self.BasicOutputs.text("", break_after=False)  # Blank line
                for number, option in menu_items:
                    self.BasicOutputs.text(f"  [{number}] {option}", break_after=False)
            return None

    def zDialog(self, context, zcli=None, walker=None):
        """Display form dialog and collect input.
        
        Shows: Interactive form with field collection
        Composes: BasicOutputs for display, zPrimitives for input
        
        Note: This is complex and may need more work for full migration
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("zDialog", {
            "context": context
        }):
            return {}  # GUI event sent successfully, return empty dict
        
        # Terminal mode - simplified form display
        fields = context.get("fields", [])
        
        # Display header using zDeclare
        self.zDeclare("Form Input", indent=0)
        
        zConv = {}
        
        # Simple field collection (full schema validation would need more work)
        for field in fields:
            if self.BasicOutputs:
                self.BasicOutputs.text(f"\n{field}:", break_after=False)
            # Use primitive for input
            value = self.zPrimitives.read_string(f"{field}: ")
            zConv[field] = value
        
        # Display footer
        self.zDeclare("Form Complete", indent=0)
        
        return zConv

    # Helper methods for zSession display
    def _display_field(self, label, value, indent=0, color="GREEN"):
        """Display a labeled field using composed events."""
        if not self.BasicOutputs:
            return
        
        color_code = getattr(self.zColors, color, self.zColors.RESET)
        content = f"{color_code}{label}:{self.zColors.RESET} {value}"
        self.BasicOutputs.text(content, indent=indent, break_after=False)

    def _display_section(self, title, indent=0, color="GREEN"):
        """Display a section title using composed events."""
        if not self.BasicOutputs:
            return
        
        color_code = getattr(self.zColors, color, self.zColors.RESET)
        content = f"{color_code}{title}:{self.zColors.RESET}"
        self.BasicOutputs.text(content, indent=indent, break_after=False)

    def _display_zmachine(self, zMachine):
        """Display zMachine section."""
        if not self.BasicOutputs:
            return
        
        self.BasicOutputs.text("", break_after=False)
        self._display_section("zMachine", color="GREEN")
        
        # Identity & Deployment
        for field in ["os", "hostname", "architecture", "python_version", "deployment", "role"]:
            if zMachine.get(field):
                self._display_field(f"  {field}", zMachine.get(field), color="YELLOW")
        
        # Tool Preferences
        if any([zMachine.get("browser"), zMachine.get("ide"), zMachine.get("shell")]):
            self.BasicOutputs.text("", break_after=False)
            self._display_section("  Tool Preferences", color="CYAN")
            for tool in ["browser", "ide", "shell"]:
                if zMachine.get(tool):
                    self._display_field(f"    {tool}", zMachine.get(tool), color="RESET")
        
        # System Capabilities
        if zMachine.get("cpu_cores") or zMachine.get("memory_gb"):
            self.BasicOutputs.text("", break_after=False)
            self._display_section("  System", color="CYAN")
            for field in ["cpu_cores", "memory_gb"]:
                if zMachine.get(field):
                    self._display_field(f"    {field}", zMachine.get(field), color="RESET")
        
        # zcli version
        if zMachine.get("zcli_version"):
            self.BasicOutputs.text("", break_after=False)
            self._display_field("  zcli_version", zMachine.get("zcli_version"), color="YELLOW")

    def _display_zauth(self, zAuth):
        """Display zAuth section."""
        if not self.BasicOutputs or not zAuth:
            return
        
        self.BasicOutputs.text("", break_after=False)
        self._display_section("zAuth", color="GREEN")
        
        for field in ["zAuth_id", "username", "role"]:
            if zAuth.get(field):
                self._display_field(f"  {field}", zAuth.get(field), color="YELLOW")

    def _should_show_sysmsg(self):
        """Check if system messages should be displayed based on logging level."""
        if not self.display or not hasattr(self.display, 'session'):
            return True
        
        session = self.display.session
        
        # Check if zCLI instance has logger with should_show_sysmsg method
        if hasattr(self.display, 'zcli'):
            zcli = self.display.zcli
            if zcli and hasattr(zcli, 'logger') and hasattr(zcli.logger, 'should_show_sysmsg'):
                return zcli.logger.should_show_sysmsg()
        
        # Fallback to legacy session debug flag
        debug = session.get("debug")
        if debug is not None:
            return debug
        
        # Fallback to deployment mode
        deployment = session.get("zMachine", {}).get("deployment", "dev")
        if deployment == "prod":
            return False
        
        return True

