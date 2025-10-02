# zCLI/subsystems/__init__.py — Shared Subsystems Package
# ───────────────────────────────────────────────────────────────
"""
Shared Subsystems Package

This package contains subsystems used by both Shell and Walker modes:
- crud: Database operations (CRUD)
- zFunc: Function execution
- zDisplay: UI rendering and display
- zDialog: Interactive dialogs
- zWizard: Multi-step wizards
- zParser: YAML/config parsing
- zSchema: Schema validation
- zSession: Session management
- zSocket: WebSocket communication
- zOpen: File/URL opening
- zUtils: Utility functions
"""

# Import subsystem classes for convenient access
from .crud import ZCRUD, handle_zCRUD
from .zFunc import ZFunc, handle_zFunc
from .zDisplay import ZDisplay, handle_zDisplay
from .zDialog import ZDialog
from .zWizard import ZWizard
from .zParser import ZParser
from .zSchema import load_schema_ref
from .zSession import zSession, create_session
from .zSocket import ZSocket
from .zOpen import ZOpen
from .zUtils import ZUtils
from .zAuth import ZAuth, check_authentication
from .zMigrate import ZMigrate, auto_migrate_schema, detect_schema_changes

__all__ = [
    # CRUD
    "ZCRUD",
    "handle_zCRUD",
    
    # Core subsystems
    "ZFunc",
    "handle_zFunc",
    "ZDisplay",
    "handle_zDisplay",
    "ZDialog",
    "ZWizard",
    "ZParser",
    "load_schema_ref",
    "zSession",
    "create_session",
    "ZSocket",
    "ZOpen",
    "ZUtils",
    "ZAuth",
    "check_authentication",
    "ZMigrate",
    "auto_migrate_schema",
    "detect_schema_changes",
]

