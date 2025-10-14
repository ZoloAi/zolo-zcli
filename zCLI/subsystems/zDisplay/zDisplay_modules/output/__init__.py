# zCLI/subsystems/zDisplay_modules/output/__init__.py
"""
Output adapters for zDisplay - mode-specific rendering implementations.
"""

from .output_adapter import OutputAdapter, OutputFactory

__all__ = ['OutputAdapter', 'OutputFactory']

