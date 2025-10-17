# zCLI/subsystems/zConfig/zConfig.py
"""Cross-platform configuration management with hierarchical loading and secret support."""

from .zConfig_modules import (
    zConfigPaths,
    MachineConfig,
    EnvironmentConfig,
    ConfigPersistence,
    SessionConfig,
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
        self.session = SessionConfig(self.machine, self.environment, zcli, zSpark_obj)

        print(f"[zConfig] Machine: {self.machine.get('hostname')} on {self.machine.get('os')}")
        #print(f"[zConfig] Config sources: {self.loader.config_sources}")

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

    @property
    def persistence(self):
        """Lazy-load persistence subsystem when needed for saving changes."""
        if not hasattr(self, '_persistence'):
            self._persistence = ConfigPersistence(self.machine, self.environment, self.sys_paths, self.zcli)
        return self._persistence
