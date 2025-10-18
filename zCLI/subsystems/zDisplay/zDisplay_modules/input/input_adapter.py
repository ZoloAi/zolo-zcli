# zCLI/subsystems/zDisplay/zDisplay_modules/input/input_adapter.py

"""Base input adapter for mode-specific input collection."""

class InputAdapter:
    """Base class for input adapters (Terminal, WebSocket)."""
    
    def __init__(self, session=None, logger=None):
        """Initialize with optional session context and logger."""
        self.session = session or {}
        self.logger = logger
    
    # Primitive operations (subclasses must implement)
    def read_string(self, prompt=""):
        """Read string from input (blocks until Enter)."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement read_string()")
    
    def read_password(self, prompt=""):
        """Read masked string from input."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement read_password()")


class InputFactory:
    """Factory for creating input adapters based on session mode."""
    
    @staticmethod
    def create(session=None, logger=None):
        """Create input adapter for session mode (defaults to Terminal)."""
        from .input_terminal import TerminalInput
        from .input_websocket import WebSocketInput
        
        if not session:
            if logger:
                logger.debug("[InputFactory] No session, defaulting to Terminal")
            return TerminalInput(session, logger)
        
        mode = session.get("zMode", "Terminal")
        if logger:
            logger.debug("[InputFactory] Creating adapter for mode: %s", mode)
        
        if mode == "Terminal":
            return TerminalInput(session, logger)
        if mode in ("UI", "WebSocket"):
            if logger:
                logger.info("[InputFactory] Creating WebSocket adapter for mode: %s", mode)
            return WebSocketInput(session, logger)
        if logger:
            logger.warning("[InputFactory] Unknown mode '%s', using Terminal", mode)
        return TerminalInput(session, logger)

