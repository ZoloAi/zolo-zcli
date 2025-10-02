# zCLI/__init__.py — Main zCLI Module
# ───────────────────────────────────────────────────────────────

# Import the new zCLI Core
from .zCore.zCLI import zCLI as zCLI_Core
from .walker.zWalker import zWalker

# Legacy zCLI class for backward compatibility
class zCLI(zCLI_Core):
    """Legacy zCLI class that extends the new zCLI Core for backward compatibility."""
    
    def __init__(self, zSpark_obj):
        super().__init__(zSpark_obj)

# Export both the new core and legacy interfaces
__all__ = ["zCLI", "zCLI_Core", "zWalker"]
