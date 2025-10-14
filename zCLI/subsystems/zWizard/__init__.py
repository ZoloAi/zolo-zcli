# zCLI/subsystems/zWizard/__init__.py
"""
zWizard - Core loop engine for vertical/horizontal walking.

Provides the fundamental iteration pattern used by both Wizard and Walker modes.
"""

from .zWizard import zWizard, handle_zWizard  # noqa: F401

__all__ = ['zWizard', 'handle_zWizard']

