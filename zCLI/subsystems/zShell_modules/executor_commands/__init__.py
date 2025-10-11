# zCLI/subsystems/zShell_modules/executor_commands/__init__.py
# ───────────────────────────────────────────────────────────────
"""
Executor Commands Registry - Modular command execution for zCLI.

This package contains specialized command executors that were extracted
from the monolithic zShell_executor.py for better organization.
"""

# Import command executors
from .data_executor import execute_data
from .func_executor import execute_func
from .session_executor import execute_session
from .walker_executor import execute_walker
from .open_executor import execute_open
from .test_executor import execute_test
from .auth_executor import execute_auth
from .load_executor import execute_load
from .export_executor import execute_export
from .utils_executor import execute_utils
from .config_executor import execute_config
from .comm_executor import execute_comm

__all__ = [
    "execute_data",
    "execute_func", 
    "execute_session",
    "execute_walker",
    "execute_open",
    "execute_test",
    "execute_auth",
    "execute_load",
    "execute_export",
    "execute_utils",
    "execute_config",
    "execute_comm"
]
