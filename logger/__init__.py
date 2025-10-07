"""Logger module for zolo-zcli project."""

from .logger import zCLILogger

# Create default logger instance
logger = zCLILogger("zCLI")

def get_logger(name=None):
    """Get a logger instance."""
    if name:
        return zCLILogger(name)
    return logger

def set_log_level(level: str):
    """Set the log level for the default logger."""
    import logging
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    if level.upper() in level_map:
        logger.logger.setLevel(level_map[level.upper()])
    else:
        logger.warning(f"Invalid log level: {level}. Using INFO.")
        logger.logger.setLevel(logging.INFO)

__all__ = ["zCLILogger", "get_logger", "set_log_level", "logger"]
