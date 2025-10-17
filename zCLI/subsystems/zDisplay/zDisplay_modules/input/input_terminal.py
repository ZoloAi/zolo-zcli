# zCLI/subsystems/zDisplay/zDisplay_modules/input/input_terminal.py

"""Terminal input adapter - stdin input collection."""

import getpass
from .input_adapter import InputAdapter


class TerminalInput(InputAdapter):
    """Terminal input via input() from stdin."""

    def read_string(self, prompt=""):
        """Read string from stdin (blocks until Enter)."""
        if prompt:
            return input(prompt).strip()
        return input().strip()

    def read_password(self, prompt=""):
        """Read masked password from stdin."""
        if prompt:
            return getpass.getpass(prompt).strip()
        return getpass.getpass().strip()
