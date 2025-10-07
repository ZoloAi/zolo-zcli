"""Logger module for zolo-zcli project."""

from .logger import Logger

# Create default logger instance
logger = Logger("zCLI")

def get_logger(name: str = "zCLI") -> Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (default: "zCLI")
        
    Returns:
        Logger: Logger instance
    """
    return Logger.get_logger(name)

def set_log_level(level: str):
    """
    Set the log level for all loggers.
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    Logger.set_global_level(level)

# Backward compatibility aliases
zCLILogger = Logger

__all__ = ["Logger", "zCLILogger", "get_logger", "set_log_level", "logger"]