# zCLI/subsystems/zConfig/zConfig.py
"""Cross-platform configuration management with hierarchical loading and secret support."""

from zCLI.utils import print_ready_message, validate_zcli_instance
from .zConfig_modules import (
    zConfigPaths,
    MachineConfig,
    EnvironmentConfig,
    ConfigPersistence,
    SessionConfig,
    LoggerConfig,
    WebSocketConfig,
)

class zConfig:
    """Configuration management with hierarchical loading and cross-platform support."""

    def __init__(self, zcli, zSpark_obj=None):
        """Initialize zConfig subsystem."""

        # Validate zCLI instance, pre zSession creation
        validate_zcli_instance(zcli, "zConfig", require_session=False)
        self.zcli = zcli
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

        # Initialize WebSocket configuration (uses environment config and session)
        self.websocket = WebSocketConfig(self.environment, zcli, self.session.create_session())

        # Print styled ready message (before zDisplay is available)
        print_ready_message("zConfig Ready", color="CONFIG")

    @staticmethod
    def print_config_ready(label, color="CONFIG"):
        """Print styled 'Ready' message for any config subsystem.
        
        Deprecated: Use print_ready_message from zCLI.utils instead.
        Kept for backward compatibility.
        """
        print_ready_message(label, color=color)

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
