# zCLI/subsystems/zDisplay/zDisplay_modules/events/__init__.py

"""Event packages - organized by category."""

from . import display_event_outputs
from . import display_event_inputs
from . import display_event_signals
from . import display_event_data
from . import display_event_advanced
from . import display_event_system
from . import display_event_auth
from . import display_event_widgets

__all__ = [
    'display_event_outputs',
    'display_event_inputs',
    'display_event_signals',
    'display_event_data',
    'display_event_advanced',
    'display_event_system',
    'display_event_auth',
    'display_event_widgets'
]
