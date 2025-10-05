# zCLI/subsystems/zDisplay_modules/output/__init__.py
"""
Output adapters for multi-mode rendering.

Exports:
- OutputMode: Mode constants (TERMINAL, WEBSOCKET, REST)
- OutputAdapter: Abstract base class
- OutputFactory: Factory for creating adapters
- TerminalOutput: Terminal/CLI output (working)
- WebSocketOutput: GUI output via zSocket (stub)
- RESTOutput: REST API output (stub)
"""

from .output_adapter import OutputMode, OutputAdapter, OutputFactory
from .output_terminal import TerminalOutput
from .output_websocket import WebSocketOutput
from .output_rest import RESTOutput

__all__ = [
    "OutputMode",
    "OutputAdapter",
    "OutputFactory",
    "TerminalOutput",
    "WebSocketOutput",
    "RESTOutput",
]
