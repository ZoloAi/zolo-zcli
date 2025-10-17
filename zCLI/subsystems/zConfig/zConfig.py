# zCLI/subsystems/zConfig/zConfig.py
"""Cross-platform configuration management with hierarchical loading and secret support."""

from zCLI import Colors
from .zConfig_modules import (
    zConfigPaths,
    MachineConfig,
    EnvironmentConfig,
    ConfigPersistence,
    SessionConfig,
    LoggerConfig,
)

class zConfig:
    """Configuration management with hierarchical loading and cross-platform support."""

    def __init__(self, zcli=None, zSpark_obj=None):
        """Initialize zConfig subsystem."""
        # Store zCLI instance for display access
        self.zcli = zcli

        # Store zSpark instance if provided
        self.zSpark = zSpark_obj

        # Initialize path resolver
        self.sys_paths = zConfigPaths()

        # Load machine config FIRST (static, per-machine)
        self.machine = MachineConfig(self.sys_paths)

        # Load environment config SECOND (deployment, runtime settings)
        self.environment = EnvironmentConfig(self.sys_paths)

        # Initialize session THIRD (uses machine and environment config for session creation)
        # Pass self so SessionConfig can call back to create_logger()
        self.session = SessionConfig(self.machine, self.environment, zcli, zSpark_obj, zconfig=self)

        # Print styled ready message (before zDisplay is available)
        self.mycolor = "CONFIG"
        self._print_ready()

    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        color_code = getattr(Colors, self.mycolor, Colors.RESET)
        label = "zConfig Ready"
        BASE_WIDTH = 60
        char = "═"
        label_len = len(label) + 2
        space = BASE_WIDTH - label_len
        left = space // 2
        right = space - left
        colored_label = f"{color_code} {label} {Colors.RESET}"
        line = f"{char * left}{colored_label}{char * right}"
        print(line)

    @staticmethod
    def print_config_ready(label, color="CONFIG"):
        """Print styled 'Ready' message for any config subsystem."""
        color_code = getattr(Colors, color, Colors.RESET)
        BASE_WIDTH = 60
        char = "═"
        label_len = len(label) + 2
        space = BASE_WIDTH - label_len
        left = space // 2
        right = space - left
        colored_label = f"{color_code} {label} {Colors.RESET}"
        line = f"{char * left}{colored_label}{char * right}"
        print(line)

    # ═══════════════════════════════════════════════════════════
    # Configuration Access Methods
    # ═══════════════════════════════════════════════════════════

    def get_machine(self, key=None, default=None):
        """Get machine config value by key (or all values if key=None)."""
        if key is None:
            return self.machine.get_all()
        return self.machine.get(key, default)

    def get_environment(self, key=None, default=None):
        """Get environment config value by key (or all values if key=None)."""
        if key is None:
            return self.environment.get_all()
        return self.environment.get(key, default)

    def create_logger(self, session_data):
        """Create logger instance with session data."""
        return LoggerConfig(self.environment, self.zcli, session_data)

    @property
    def persistence(self):
        """Lazy-load persistence subsystem when needed for saving changes."""
        if not hasattr(self, '_persistence'):
            self._persistence = ConfigPersistence(self.machine, self.environment, self.sys_paths, self.zcli)  # pylint: disable=attribute-defined-outside-init
        return self._persistence
