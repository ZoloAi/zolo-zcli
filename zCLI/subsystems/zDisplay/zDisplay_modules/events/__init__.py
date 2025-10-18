# zCLI/subsystems/zDisplay/zDisplay_modules/events/__init__.py

"""
Event handlers organized by complexity level (LSF - Least Significant First).
"""

from . import primitives, basic, composed, walker, forms, tables

# Import all handlers from primitives
from .primitives import (
    handle_raw,
    handle_line,
    handle_block,
    handle_read,
    handle_read_password,
    handle_prompt_terminal,
    handle_input_terminal,
    handle_confirm_terminal,
    handle_password_terminal,
    handle_field_terminal,
    handle_multiline_terminal,
    handle_prompt_gui,
    handle_input_gui,
    handle_confirm_gui,
    handle_password_gui,
    handle_field_gui,
    handle_multiline_gui,
)

# Import all handlers from basic
from .basic import (
    handle_text,
    handle_header,
    handle_sysmsg,
    handle_error,
    handle_warning,
    handle_success,
    handle_info,
    handle_marker,
    handle_list,
    handle_json,
    handle_break,
    handle_pause,
    handle_break_gui,
    handle_pause_gui,
    handle_loading_gui,
    handle_await_gui,
    handle_idle_gui,
    handle_radio_terminal,
    handle_checkbox_terminal,
    handle_dropdown_terminal,
    handle_autocomplete_terminal,
    handle_range_terminal,
    handle_radio_gui,
    handle_checkbox_gui,
    handle_dropdown_gui,
    handle_autocomplete_gui,
    handle_range_gui,
)

# Import handlers from other modules
from .composed import handle_session
from .walker import handle_menu, handle_crumbs
from .forms import handle_dialog
from .tables import handle_data_table, handle_schema_table

__all__ = [
    'primitives',
    'basic', 
    'composed',
    'walker',
    'forms',
    'tables',
    # Primitive handlers
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
    # Basic handlers
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
    # Composed handlers
    'handle_session',
    # Walker handlers
    'handle_menu',
    'handle_crumbs',
    # Form handlers
    'handle_dialog',
    # Table handlers
    'handle_data_table',
    'handle_schema_table',
]
