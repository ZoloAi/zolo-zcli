# zCLI/subsystems/zDisplay/zDisplay_modules/output/output_adapter.py

"""Base output adapter and factory for mode-specific rendering."""

from zCLI.subsystems.zDisplay.zDisplay_modules.utils import Colors

class OutputAdapter:
    """Base class for output adapters (Terminal, WebSocket)."""

    def __init__(self, session=None, logger=None):
        """Initialize with optional session context and logger."""
        self.session = session or {}
        self.logger = logger
        self.colors = Colors

    # Primitive operations (subclasses must implement)
    def write_raw(self, content):
        """Write raw content with no formatting."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement write_raw()")

    def write_line(self, content):
        """Write single line with newline."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement write_line()")

    def write_block(self, content):
        """Write multi-line block."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement write_block()")

class OutputFactory:
    """Factory for creating output adapters based on session mode."""

    @staticmethod
    def create(session=None, logger=None):
        """Create output adapter for session mode (defaults to Terminal)."""
        from .output_terminal import TerminalOutput

        if not session:
            if logger:
                logger.debug("[OutputFactory] No session, defaulting to Terminal")
            return TerminalOutput(session, logger)

        mode = session.get("zMode", "Terminal")
        if logger:
            logger.debug("[OutputFactory] Creating adapter for mode: %s", mode)

        if mode == "Terminal":
            return TerminalOutput(session, logger)
        if mode in ("UI", "WebSocket"):
            if logger:
                logger.warning("[OutputFactory] WebSocket not implemented, using Terminal")
            return TerminalOutput(session, logger)
        if logger:
            logger.warning("[OutputFactory] Unknown mode '%s', using Terminal", mode)
        return TerminalOutput(session, logger)
