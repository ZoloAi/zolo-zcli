# zCLI/subsystems/zData/zData_modules/shared/backends/__init__.py

"""Backend adapters for zData with factory and auto-registration."""

from .base_adapter import BaseDataAdapter
from .adapter_factory import AdapterFactory
from . import adapter_registry  # Import to trigger auto-registration

__all__ = ["BaseDataAdapter", "AdapterFactory"]
