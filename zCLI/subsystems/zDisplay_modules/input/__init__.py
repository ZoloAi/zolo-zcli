# zCLI/subsystems/zDisplay_modules/input/__init__.py
"""
Input adapters for multi-mode input collection.

Exports:
- InputMode: Mode constants (TERMINAL, WEBSOCKET, REST)
- InputAdapter: Abstract base class
- InputFactory: Factory for creating adapters
- TerminalInput: Terminal/CLI input (working)
- WebSocketInput: GUI input via zSocket (stub)
- RESTInput: REST API input (stub)
"""

from .input_adapter import InputMode, InputAdapter, InputFactory
from .input_terminal import TerminalInput
from .input_websocket import WebSocketInput
from .input_rest import RESTInput

__all__ = [
    "InputMode",
    "InputAdapter",
    "InputFactory",
    "TerminalInput",
    "WebSocketInput",
    "RESTInput",
]
