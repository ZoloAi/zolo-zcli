# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents.py

"""zEvents class - organized event packages for complex display operations."""

from .zEvents_packages import BasicOutputs, BasicInputs, Signals, BasicData, AdvancedData, zSystem, zAuthEvents

class zEvents:
    """Event orchestrator - organizes events into logical packages.
    
    Packages:
    - BasicOutputs: header, text
    - BasicInputs: selection (unified single/multi-select)
    - Signals: error, warning, success, info, zMarker
    - BasicData: list, json
    - AdvancedData: zTable (with pagination)
    - zSystem: zDeclare, zSession, zCrumbs, zMenu, zDialog
    - zAuth: login_prompt, login_success, login_failure, logout_success, status_display
    """

    def __init__(self, display_instance):
        """Initialize zEvents with packaged event categories."""
        self.display = display_instance
        
        # Initialize event packages
        self.BasicOutputs = BasicOutputs(display_instance)
        self.BasicInputs = BasicInputs(display_instance)
        self.Signals = Signals(display_instance)
        self.BasicData = BasicData(display_instance)
        self.AdvancedData = AdvancedData(display_instance)
        self.zSystem = zSystem(display_instance)
        self.zAuth = zAuthEvents(display_instance)
        
        # Set up composition references (packages can use each other)
        self.BasicInputs.BasicOutputs = self.BasicOutputs
        self.Signals.BasicOutputs = self.BasicOutputs
        self.BasicData.BasicOutputs = self.BasicOutputs
        self.AdvancedData.BasicOutputs = self.BasicOutputs
        self.AdvancedData.Signals = self.Signals
        self.zSystem.BasicOutputs = self.BasicOutputs
        self.zSystem.Signals = self.Signals
        self.zSystem.BasicInputs = self.BasicInputs
        self.zAuth.BasicOutputs = self.BasicOutputs
        self.zAuth.Signals = self.Signals
    
    # Convenience delegates to BasicOutputs for backward compatibility
    def header(self, label, color="RESET", indent=0, style="full"):
        """Delegate to BasicOutputs.header."""
        return self.BasicOutputs.header(label, color, indent, style)
    
    def text(self, content, indent=0, break_after=True, break_message=None):
        """Delegate to BasicOutputs.text."""
        return self.BasicOutputs.text(content, indent, break_after, break_message)
    
    # Convenience delegates to BasicInputs
    def selection(self, prompt, options, multi=False, default=None, style="numbered"):
        """Delegate to BasicInputs.selection."""
        return self.BasicInputs.selection(prompt, options, multi, default, style)
    
    # Convenience delegates to Signals
    def error(self, content, indent=0):
        """Delegate to Signals.error."""
        return self.Signals.error(content, indent)
    
    def warning(self, content, indent=0):
        """Delegate to Signals.warning."""
        return self.Signals.warning(content, indent)
    
    def success(self, content, indent=0):
        """Delegate to Signals.success."""
        return self.Signals.success(content, indent)
    
    def info(self, content, indent=0):
        """Delegate to Signals.info."""
        return self.Signals.info(content, indent)
    
    def zMarker(self, label="Marker", color="MAGENTA", indent=0):
        """Delegate to Signals.zMarker."""
        return self.Signals.zMarker(label, color, indent)
    
    # Convenience delegates to BasicData
    def list(self, items, style="bullet", indent=0):
        """Delegate to BasicData.list."""
        return self.BasicData.list(items, style, indent)
    
    def json_data(self, data, indent_size=2, indent=0, color=False):
        """Delegate to BasicData.json_data."""
        return self.BasicData.json_data(data, indent_size, indent, color)
    
    # Convenience delegates to AdvancedData
    def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
        """Delegate to AdvancedData.zTable."""
        return self.AdvancedData.zTable(title, columns, rows, limit, offset, show_header)
    
    # Convenience delegates to zSystem
    def zDeclare(self, label, color=None, indent=0, style=None):
        """Delegate to zSystem.zDeclare."""
        return self.zSystem.zDeclare(label, color, indent, style)
    
    def zSession(self, session_data, break_after=True, break_message=None):
        """Delegate to zSystem.zSession."""
        return self.zSystem.zSession(session_data, break_after, break_message)
    
    def zCrumbs(self, session_data):
        """Delegate to zSystem.zCrumbs."""
        return self.zSystem.zCrumbs(session_data)
    
    def zMenu(self, menu_items, prompt="Select an option:", return_selection=False):
        """Delegate to zSystem.zMenu."""
        return self.zSystem.zMenu(menu_items, prompt, return_selection)
    
    def zDialog(self, context, zcli=None, walker=None):
        """Delegate to zSystem.zDialog."""
        return self.zSystem.zDialog(context, zcli, walker)


