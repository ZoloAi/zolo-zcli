# zCLI/subsystems/zDisplay_modules/events/composed/__init__.py
"""
Composed event handlers - complex display operations.

These handlers compose multiple basic and primitive operations.
"""

from .session import handle_session

__all__ = [
    'handle_session',
]

