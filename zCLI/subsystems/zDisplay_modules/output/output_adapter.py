# zCLI/subsystems/zDisplay_modules/output/output_adapter.py
"""
Output adapter base class and factory for multi-mode rendering
"""

from logger import Logger


class OutputMode:
    """Output mode constants."""
    TERMINAL = "Terminal"    # CLI mode (print to stdout)
    WEBSOCKET = "UI"         # GUI mode (broadcast via zSocket)
    REST = "REST"            # REST API mode (accumulate data)


class OutputAdapter:
    """
    Abstract base class for output adapters.
    
    Each adapter implements rendering for a specific output mode:
    - Terminal: print() to stdout
    - WebSocket: broadcast() via zSocket
    - REST: accumulate data for JSON response
    """
    
    def __init__(self, session):
        """
        Initialize output adapter.
        
        Args:
            session: zSession dict for context
        """
        self.session = session
        self.logger = Logger.get_logger()
    
    # ═══════════════════════════════════════════════════════════
    # Abstract Methods (must be implemented by subclasses)
    # ═══════════════════════════════════════════════════════════
    
    def render_header(self, obj):
        """Render section header."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_header()")
    
    def render_menu(self, obj):
        """Render menu options."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_menu()")
    
    def render_table(self, obj):
        """Render data table."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_table()")
    
    def render_form(self, obj):
        """Render interactive form."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_form()")
    
    def render_pause(self, obj):
        """Handle pause/pagination."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_pause()")
    
    def render_json(self, obj):
        """Render JSON data."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_json()")
    
    def render_session(self, obj):
        """Render session information."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_session()")
    
    def render_marker(self, obj):
        """Render flow marker."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_marker()")
    
    def render_crumbs(self, obj):
        """Render breadcrumb trail."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement render_crumbs()")


class OutputFactory:
    """
    Factory for creating output adapters based on session mode.
    
    Supports:
    - Terminal: CLI output (print to stdout)
    - WebSocket: GUI output (broadcast via zSocket)
    - REST: API output (accumulate data)
    """
    
    @staticmethod
    def create(session):
        """
        Create appropriate output adapter for session mode.
        
        Args:
            session: zSession dict (or None for Terminal default)
            
        Returns:
            OutputAdapter instance
        """
        # Default to Terminal if no session
        if not session:
            logger.debug("[OutputFactory] No session provided, defaulting to Terminal")
            from .output_terminal import TerminalOutput
            return TerminalOutput(session)
        
        mode = session.get("zMode", "Terminal")
        logger.debug("[OutputFactory] Creating output adapter for mode: %s", mode)
        
        if mode == OutputMode.TERMINAL or mode == "Terminal":
            from .output_terminal import TerminalOutput
            return TerminalOutput(session)
        
        elif mode == OutputMode.WEBSOCKET or mode == "UI":
            from .output_websocket import WebSocketOutput
            return WebSocketOutput(session)
        
        elif mode == OutputMode.REST or mode == "REST":
            from .output_rest import RESTOutput
            return RESTOutput(session)
        
        else:
            logger.warning("[OutputFactory] Unknown mode '%s', defaulting to Terminal", mode)
            from .output_terminal import TerminalOutput
            return TerminalOutput(session)
