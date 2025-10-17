# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/__init__.py

# zCLI/subsystems/zDisplay_modules/events/basic/__init__.py
"""
Basic event handlers - simple formatted output built on primitives.

These handlers compose primitive operations (raw, line, block).
"""

from .text import handle_text, handle_header
from .sysmsg import handle_sysmsg
from .signals import handle_error, handle_warning, handle_success, handle_info, handle_marker
from .data import handle_list, handle_json
from .control import handle_break, handle_pause

__all__ = [
    'handle_text',
    'handle_header',
    'handle_sysmsg',
    'handle_error',
    'handle_warning',
    'handle_success',
    'handle_info',
    'handle_marker',
    'handle_list',
    'handle_json',
    'handle_break',
    'handle_pause',
]
