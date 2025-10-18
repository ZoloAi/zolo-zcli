# zCLI/subsystems/zDisplay/zDisplay_modules/events/primitives/__init__.py

"""
Primitive event handlers - atomic I/O operations (cannot be decomposed).

These are the most basic building blocks that all other events use.
"""

from .raw import handle_raw, handle_line, handle_block
from .input import handle_read, handle_read_password
from .input_terminal import (
    handle_prompt_terminal,
    handle_input_terminal,
    handle_confirm_terminal,
    handle_password_terminal,
    handle_field_terminal,
    handle_multiline_terminal,
)
from .input_gui import (
    handle_prompt_gui,
    handle_input_gui,
    handle_confirm_gui,
    handle_password_gui,
    handle_field_gui,
    handle_multiline_gui,
)

__all__ = [
    'handle_raw',
    'handle_line',
    'handle_block',
    'handle_read',
    'handle_read_password',
    'handle_prompt_terminal',
    'handle_input_terminal',
    'handle_confirm_terminal',
    'handle_password_terminal',
    'handle_field_terminal',
    'handle_multiline_terminal',
    'handle_prompt_gui',
    'handle_input_gui',
    'handle_confirm_gui',
    'handle_password_gui',
    'handle_field_gui',
    'handle_multiline_gui',
]
