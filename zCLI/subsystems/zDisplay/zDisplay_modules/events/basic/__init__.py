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
from .control_gui import (
    handle_break_gui,
    handle_pause_gui,
    handle_loading_gui,
    handle_await_gui,
    handle_idle_gui,
)
from .selection_terminal import (
    handle_radio_terminal,
    handle_checkbox_terminal,
    handle_dropdown_terminal,
    handle_autocomplete_terminal,
    handle_range_terminal,
)
from .selection_gui import (
    handle_radio_gui,
    handle_checkbox_gui,
    handle_dropdown_gui,
    handle_autocomplete_gui,
    handle_range_gui,
)

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
    'handle_break_gui',
    'handle_pause_gui',
    'handle_loading_gui',
    'handle_await_gui',
    'handle_idle_gui',
    'handle_radio_terminal',
    'handle_checkbox_terminal',
    'handle_dropdown_terminal',
    'handle_autocomplete_terminal',
    'handle_range_terminal',
    'handle_radio_gui',
    'handle_checkbox_gui',
    'handle_dropdown_gui',
    'handle_autocomplete_gui',
    'handle_range_gui',
]
