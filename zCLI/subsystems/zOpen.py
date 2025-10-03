# zCLI/subsystems/zOpen.py — Legacy zOpen Interface
# ───────────────────────────────────────────────────────────────
"""
Legacy zOpen interface for backward compatibility.

This file provides backward compatibility for existing zOpen usage.
New code should import directly from zCLI.subsystems.zOpen package.
"""

from .zOpen.zOpen_handler import ZOpen, handle_zOpen

# Export for backward compatibility
__all__ = ["ZOpen", "handle_zOpen"]