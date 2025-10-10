"""
Backend adapters package for zData subsystem (shared infrastructure).

Provides adapter factory and auto-registration of built-in adapters.
"""

from .base_adapter import BaseDataAdapter
from .adapter_factory import AdapterFactory
from . import adapter_registry  # Import to trigger auto-registration

__all__ = ["BaseDataAdapter", "AdapterFactory"]
