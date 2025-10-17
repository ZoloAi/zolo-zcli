# zCLI/subsystems/zSession/zSession.py

"""
Session management subsystem for zCLI.
"""

import os
import secrets

class zSession:
    """Session management subsystem."""

    def __init__(self, zcli):
        """Initialize zSession subsystem with zCLI instance."""
        self.zcli = zcli
        self.logger = zcli.logger

        # Session color for system messages (stored as string, resolved by zDisplay)
        self.mycolor = "MAIN"

        # Print styled ready message (before zDisplay is available)
        self._print_ready()

    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        try:
            from ..zDisplay.zDisplay_modules.utils.colors import Colors
            color_code = getattr(Colors, self.mycolor, Colors.RESET)
            label = "zSession Ready"
            BASE_WIDTH = 60
            char = "═"
            label_len = len(label) + 2
            space = BASE_WIDTH - label_len
            left = space // 2
            right = space - left
            colored_label = f"{color_code} {label} {Colors.RESET}"
            line = f"{char * left}{colored_label}{char * right}"
            print(line)
        except Exception:
            # Silently fail if Colors not available
            pass

    def generate_id(self, prefix: str = "zS") -> str:
        """Generate random session ID with prefix (default: 'zS') -> 'zS_a1b2c3d4'."""
        random_hex = secrets.token_hex(4)  # 8 character hex string
        return f"{prefix}_{random_hex}"

    def create_session(self, machine_config=None):
        """Create isolated session instance for zCLI with optional machine config."""
        return {
            "zS_id": None,
            "zWorkspace": os.getcwd(),
            "zVaFile_path": None,
            "zVaFilename": None,
            "zBlock": None,
            "zMode": None,
            "zLogger_level":  None,
            "zMachine": machine_config or {},
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            },
            "zCrumbs": {},
            "zCache": {
                "system_cache": {},
                "pinned_cache": {},
                "schema_cache": {},
            },
            "wizard_mode": {
                "active": False,
                "lines": [],
                "format": None,
                "transaction": False
            },
            "zCLI": self.zcli,
        }

