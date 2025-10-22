# zCLI/subsystems/zConfig/zConfig_modules/config_machine.py
"""Machine-level configuration management for system identity and preferences."""

from zCLI import yaml
from .helpers import auto_detect_machine, create_user_machine_config, load_config_with_override

class MachineConfig:
    """Manages machine settings including system details, tool preferences, and hardware info."""

    def __init__(self, paths):
        """Initialize machine configuration with paths for resolution."""
        self.paths = paths

        # Auto-detect machine defaults
        self.machine = auto_detect_machine()

        # Load and override from config file (check exists, create if missing)
        load_config_with_override(
            self.paths,
            "zMachine",
            create_user_machine_config,
            self.machine,
            "MachineConfig"
        )

        # Print ready message
        from ..zConfig import zConfig
        zConfig.print_config_ready("MachineConfig Ready")

    def get(self, key, default=None):
        """Get machine config value by key, returning default if not found."""
        return self.machine.get(key, default)

    def get_all(self):
        """Get complete machine configuration."""
        return self.machine.copy()

    def update(self, key, value):
        """Update machine config value (runtime only)."""
        self.machine[key] = value

    def save_user_config(self):
        """Save current machine config to user's machine.yaml."""
        try:
            path = self.paths.user_config_dir / "machine.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)

            content = {"zMachine": self.machine}

            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)

            print(f"[MachineConfig] Saved machine config to: {path}")
            return True

        except Exception as e:
            print(f"[MachineConfig] Failed to save machine config: {e}")
            return False
