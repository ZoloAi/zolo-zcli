# zCLI/subsystems/zShell/shell_modules/commands/__init__.py

"""Command Executors Registry - Modular command execution for zCLI."""

# Import command executors
from .shell_cmd_data import execute_data
from .shell_cmd_func import execute_func
from .shell_cmd_session import execute_session
from .shell_cmd_walker import execute_walker
from .shell_cmd_open import execute_open
from .shell_cmd_auth import execute_auth
from .shell_cmd_load import execute_load
from .shell_cmd_export import execute_export
from .shell_cmd_utils import execute_utils
from .shell_cmd_config import execute_config
from .shell_cmd_comm import execute_comm
from .shell_cmd_wizard import execute_wizard
from .shell_cmd_wizard_step import execute_wizard_step
from .shell_cmd_plugin import execute_plugin
from .shell_cmd_ls import execute_ls
from .shell_cmd_cd import execute_cd, execute_pwd
from .shell_cmd_shortcut import execute_shortcut
from .shell_cmd_where import execute_where
from .shell_cmd_help import execute_help

__all__ = [
    "execute_data",
    "execute_func", 
    "execute_session",
    "execute_walker",
    "execute_open",
    "execute_auth",
    "execute_load",
    "execute_export",
    "execute_utils",
    "execute_config",
    "execute_comm",
    "execute_wizard",
    "execute_wizard_step",
    "execute_plugin",
    "execute_ls",
    "execute_cd",
    "execute_pwd",
    "execute_shortcut",
    "execute_where",
    "execute_help"
]
