# zCLI/subsystems/zDisplay_new_modules/events/primitives/__init__.py
"""
Primitive event handlers - atomic I/O operations (cannot be decomposed).

These are the most basic building blocks that all other events use.
"""

from .raw import handle_raw, handle_line, handle_block
from .input import handle_read, handle_read_password

__all__ = [
    'handle_raw',
    'handle_line',
    'handle_block',
    'handle_read',
    'handle_read_password',
]

