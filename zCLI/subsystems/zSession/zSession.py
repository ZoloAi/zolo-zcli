# zCLI/subsystems/zSession.py — Session Management Subsystem
# ───────────────────────────────────────────────────────────────
"""
Session management subsystem for zCLI.
Provides session lifecycle and authentication.
    Dependencies: zCLI, zDisplay
"""

import requests
import secrets
from logger import Logger

logger = Logger.get_logger(__name__)


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
        """
        Generate a random session ID with given prefix.
        
        Args:
            prefix: ID prefix (default: "zS")
            
        Returns:
            String like "zS_a1b2c3d4"
        """
        random_hex = secrets.token_hex(4)  # 8 character hex string
        return f"{prefix}_{random_hex}"

    def create_session(self, machine_config=None):
        """
        Create isolated session instance for zCLI.
        
        Args:
            machine_config: Machine configuration dict (from zConfig)
        Returns:
            dict: New session with default values
        """
        return {
            "zS_id": None,
            "zWorkspace": None,
            "zVaFile_path": None,
            "zVaFilename": None,
            "zBlock": None,
            "zMode": None,
            "zMachine": machine_config or {},  # Machine-level config (static per machine)
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            },
            "zCrumbs": {},
            "zCache": {
                "system_cache": {},   # UI and config files (auto-cached, LRU)
                "pinned_cache": {},   # Aliases (user-loaded, never evicts)
                "schema_cache": {},   # Active connections (wizard-only, in-memory)
            },
            "wizard_mode": {
                "active": False,      # Is wizard canvas mode active?
                "lines": [],          # Multi-line buffer (YAML or commands)
                "format": None,       # Detected on run: "yaml", "commands", or "hybrid"
                "transaction": False  # Transaction flag for execution
            },
        }

    def login(self, data, url=None):
        """
        Authenticate and update session with user credentials.
        
        Args:
            data: Login credentials dict
            url: Authentication endpoint (defaults to local server)
            
        Returns:
            dict: Authentication result or None on failure
        """
        session = self.zcli.session
        
        # Display authentication message using new display system
        self.zcli.display.handle({
            "event": "sysmsg",
            "label": "send_to_server",
            "color": self.mycolor,
            "indent": 0
        })
        
        if not url:
            url = "http://127.0.0.1:5000/zAuth"
            self.logger.debug("[Web] No URL provided — defaulting to %s", url)
        
        # Include current session mode so server can distinguish CLI vs Web
        data.setdefault("mode", session.get("zMode"))
        
        self.logger.info("[>>] Sending request to %s", url)
        self.logger.debug("└── Payload: %s", data)
        
        try:
            response = requests.post(url, json=data, timeout=10)
            
            self.logger.info("[<<] Response received [status=%s]", response.status_code)
            self.logger.debug("└── Body: %s", response.text)
            
            result = response.json()
            
            if result.get("status") == "success" and "user" in result:
                user = result["user"]
                session["zAuth"].update({
                    "username": user.get("username"),
                    "role": user.get("role"),
                    "id": user.get("id", None),
                    "API_Key": user.get("api_key", None)
                })
                
                self.logger.info("[*] Authenticated user: %s (role=%s)", 
                               user.get("username"), user.get("role"))
                self.logger.debug(
                    "└── Updated zSession['zAuth']: id=%s, API_Key=%s",
                    user.get("id", None),
                    user.get("api_key", None)
                )
                
                return result
            
            self.logger.warning("[FAIL] Login failed or missing user data in response: %s", result)
            return None
        
        except Exception as e:
            self.logger.error("[ERROR] Exception during request to %s: %s", url, e)
            return None
