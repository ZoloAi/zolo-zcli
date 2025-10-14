# zCLI/subsystems/zDisplay_new_modules/input/input_terminal.py
"""Terminal input adapter - stdin input collection."""

import getpass
from .input_adapter import InputAdapter


class TerminalInput(InputAdapter):
    """Terminal input via input() from stdin."""
    
    def read_string(self, prompt=""):
        """
        Read string from stdin (blocks until Enter).
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            String entered by user (stripped of leading/trailing whitespace)
        """
        if prompt:
            return input(prompt).strip()
        return input().strip()
    
    def read_password(self, prompt=""):
        """
        Read masked password from stdin.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            String entered by user (input was masked)
        """
        if prompt:
            return getpass.getpass(prompt).strip()
        return getpass.getpass().strip()

