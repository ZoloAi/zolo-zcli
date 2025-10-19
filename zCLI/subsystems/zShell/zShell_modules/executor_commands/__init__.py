# zCLI/subsystems/zShell/zShell_modules/executor_commands/__init__.py

# zCLI/subsystems/zShell_modules/executor_commands/__init__.py
# ───────────────────────────────────────────────────────────────
"""Executor Commands Registry - Modular command execution for zCLI."""

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
from .wizard_executor import execute_wizard
from .wizard_step_executor import execute_wizard_step
from .plugin_executor import execute_plugin
from .history_executor import execute_history
from .echo_executor import execute_echo
from .ls_executor import execute_ls
from .cd_executor import execute_cd, execute_pwd
from .alias_executor import execute_alias

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
    "execute_comm",
    "execute_wizard",
    "execute_wizard_step",
    "execute_plugin",
    "execute_history",
    "execute_echo",
    "execute_ls",
    "execute_cd",
    "execute_pwd",
    "execute_alias"
]
