# zCLI/subsystems/zData/__init__.py
# ----------------------------------------------------------------
# zData subsystem - Unified data management across multiple backends.
# ----------------------------------------------------------------

from .zData import ZData, handle_zData, load_schema_ref

__all__ = ["ZData", "handle_zData", "load_schema_ref"]
