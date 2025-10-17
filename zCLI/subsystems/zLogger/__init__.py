# zCLI/subsystems/zLogger/__init__.py

"""
zLogger Package - Logging Subsystem

This package contains the zLogger subsystem:
- zLogger.py: Main logging controller (zCLI-oriented)

Architecture:
- Uses zCLI instance for configuration and session access
- Reads logger.level from zConfig with enum validation
- Controls sysmsg visibility based on log level
- Provides logging interface consistent with zCLI patterns
"""

from .zLogger import zLogger

__all__ = ['zLogger']
