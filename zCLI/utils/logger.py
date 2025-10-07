"""Self-contained logging utilities for the zCLI package."""

from __future__ import annotations

import logging
import sys
from typing import Optional, TextIO


class LogColors:
    """ANSI colors specifically for system logs."""

    LOG_PREFIX = "\033[38;5;248m"  # Medium gray for log metadata (readable on dark bg)
    DEBUG = "\033[38;5;250m"  # Light gray for debug
    INFO = "\033[38;5;39m"  # Bright blue for info
    WARNING = "\033[38;5;214m"  # Orange for warnings
    ERROR = "\033[38;5;196m"  # Bright red for errors
    CRITICAL = "\033[38;5;201m"  # Magenta for critical
    RESET = "\033[0m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors and metadata markers to log messages."""

    LEVEL_COLORS = {
        "DEBUG": LogColors.DEBUG,
        "INFO": LogColors.INFO,
        "WARNING": LogColors.WARNING,
        "ERROR": LogColors.ERROR,
        "CRITICAL": LogColors.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - see class docstring
        level_color = self.LEVEL_COLORS.get(record.levelname, LogColors.INFO)
        timestamp = self.formatTime(record, self.datefmt)
        metadata = f"{LogColors.LOG_PREFIX}[{timestamp}]{LogColors.RESET}"
        level = f"{level_color}{LogColors.BOLD}[{record.levelname}]{LogColors.RESET}"
        location = f"{LogColors.LOG_PREFIX}{record.name}:{record.lineno}{LogColors.RESET}"
        message = f"{level_color}{record.getMessage()}{LogColors.RESET}"
        marker = f"{LogColors.LOG_PREFIX}●{LogColors.RESET}"
        return f"{marker} {metadata} {level} {location} | {message}"


_DEFAULT_LOGGER_NAME = "zCLI"
_CONFIGURED = False


def _configure_root_handler(stream: TextIO | None = None) -> logging.Handler:
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(ColoredFormatter(datefmt="%H:%M:%S"))
    return handler


def init_logging(
    *,
    level: int = logging.INFO,
    stream: TextIO | None = None,
    logger_name: str = _DEFAULT_LOGGER_NAME,
) -> logging.Logger:
    """Initialise the base logger used by the application."""

    global _CONFIGURED, _DEFAULT_LOGGER_NAME

    base_logger = logging.getLogger(logger_name)
    if not _CONFIGURED:
        handler = _configure_root_handler(stream)
        base_logger.addHandler(handler)
        base_logger.propagate = False
        _CONFIGURED = True

    base_logger.setLevel(level)
    _DEFAULT_LOGGER_NAME = logger_name
    return base_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger, initialising the logging subsystem on first use."""

    if not _CONFIGURED:
        init_logging()

    target_name = name or _DEFAULT_LOGGER_NAME
    logger = logging.getLogger(target_name)
    if target_name != _DEFAULT_LOGGER_NAME:
        logger.setLevel(logging.NOTSET)
    return logger


def set_log_level(level: str) -> None:
    """Set the log level for the base logger."""

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    selected = level_map.get(level.upper())
    base_logger = get_logger(_DEFAULT_LOGGER_NAME)
    if selected is not None:
        base_logger.setLevel(selected)
    else:
        base_logger.warning("Invalid log level: %s. Using INFO.", level)
        base_logger.setLevel(logging.INFO)
