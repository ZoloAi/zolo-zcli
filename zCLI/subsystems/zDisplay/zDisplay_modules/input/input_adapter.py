# zCLI/subsystems/zDisplay_modules/input/input_adapter.py
"""Base input adapter for mode-specific input collection."""

from logger import Logger

logger = Logger.get_logger(__name__)


class InputAdapter:
    """Base class for input adapters (Terminal, WebSocket)."""
    
    def __init__(self, session=None):
        """Initialize with optional session context."""
        self.session = session or {}
        self.logger = Logger.get_logger()
    
    # Primitive operations (subclasses must implement)
    def read_string(self, prompt=""):
        """
        Read string from input (blocks until Enter).
        
        Most atomic input operation - reads until newline.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            String entered by user
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement read_string()")
    
    def read_password(self, prompt=""):
        """
        Read masked string from input.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            String entered by user (input was masked)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement read_password()")


class InputFactory:
    """Factory for creating input adapters based on session mode."""
    
    @staticmethod
    def create(session=None):
        """Create input adapter for session mode (defaults to Terminal)."""
        from .input_terminal import TerminalInput
        
        if not session:
            logger.debug("[InputFactory] No session, defaulting to Terminal")
            return TerminalInput(session)
        
        mode = session.get("zMode", "Terminal")
        logger.debug("[InputFactory] Creating adapter for mode: %s", mode)
        
        if mode == "Terminal":
            return TerminalInput(session)
        if mode in ("UI", "WebSocket"):
            logger.warning("[InputFactory] WebSocket not implemented, using Terminal")
            return TerminalInput(session)
        logger.warning("[InputFactory] Unknown mode '%s', using Terminal", mode)
        return TerminalInput(session)

