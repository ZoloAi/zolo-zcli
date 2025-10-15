# zCLI/subsystems/zConfig.py — Configuration Management Subsystem
# ───────────────────────────────────────────────────────────────
"""Cross-platform configuration management with hierarchical loading and secret support."""

import os
from logger import Logger
from .zConfig_modules import zConfigPaths, ConfigLoader
from .zConfig_modules.machine_config import MachineConfig

# Logger instance
logger = Logger.get_logger(__name__)


class zConfig:
    """Configuration management with hierarchical loading and cross-platform support."""

    def __init__(self, environment=None, zcli=None):
        """Initialize zConfig subsystem for specified environment."""
        # Initialize path resolver
        self.paths = zConfigPaths()

        # Load machine config FIRST (static, per-machine)
        self.machine = MachineConfig(self.paths)

        # Determine environment from machine config or env var
        if not environment:
            environment = (
                self.machine.get("deployment")  # From machine.yaml
                or os.getenv("ZOLO_ENV")        # From env var
                or "dev"                        # Default
            )

        self.environment = environment

        # Initialize config loader
        self.loader = ConfigLoader(self.environment)

        # Load application configuration
        self.config = self.loader.load(self.paths)

        # Load secrets (from env vars only!)
        self.secrets = self._load_secrets()

        # Store zCLI instance for display access
        self.zcli = zcli
        
        # Configuration color for system messages
        self.mycolor = "SCHEMA"  # Green bg (configuration/schema)

        # Print styled ready message (before zDisplay is available)
        self._print_ready()

        logger.info("[zConfig] Initialized for environment: %s (from %s)", 
                   self.environment,
                   "machine.yaml" if self.machine.get("deployment") else "ZOLO_ENV/default")
        logger.debug("[zConfig] Machine: %s on %s", 
                    self.machine.get("hostname"), 
                    self.machine.get("os"))
        logger.debug("[zConfig] Config sources: %s", self.loader.config_sources)

    # ═══════════════════════════════════════════════════════════
    # Configuration Access
    # ═══════════════════════════════════════════════════════════

    def get(self, path, default=None):
        """Get configuration value by dot-notation path."""
        keys = path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_section(self, section):
        """Get entire configuration section."""
        return self.config.get(section, {})

    def get_all(self):
        """Get complete configuration."""
        return self.config.copy()

    def get_machine(self, key=None, default=None):
        """Get machine configuration value."""
        if key is None:
            return self.machine.get_all()
        return self.machine.get(key, default)

    # ═══════════════════════════════════════════════════════════
    # Layer 0 Ready Message
    # ═══════════════════════════════════════════════════════════
    
    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        try:
            from ..zDisplay.zDisplay_modules.utils.colors import Colors
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
        except Exception:
            # Silently fail if Colors not available
            pass
    
    # ═══════════════════════════════════════════════════════════
    # Secret Management (Environment Variables Only)
    # ═══════════════════════════════════════════════════════════

    def _load_secrets(self):
        """Load secrets from environment variables ONLY."""
        return {
            # Database credentials
            "db_username": os.getenv("ZOLO_DB_USERNAME"),
            "db_password": os.getenv("ZOLO_DB_PASSWORD"),
            "db_host": os.getenv("ZOLO_DB_HOST"),

            # Security keys
            "jwt_secret": os.getenv("ZOLO_JWT_SECRET"),
            "api_master_key": os.getenv("ZOLO_API_MASTER_KEY"),
            "encryption_key": os.getenv("ZOLO_ENCRYPTION_KEY"),

            # SSL certificates
            "ssl_cert_path": os.getenv("ZOLO_SSL_CERT_PATH"),
            "ssl_key_path": os.getenv("ZOLO_SSL_KEY_PATH"),

            # External services
            "smtp_password": os.getenv("ZOLO_SMTP_PASSWORD"),
            "aws_access_key": os.getenv("ZOLO_AWS_ACCESS_KEY"),
            "aws_secret_key": os.getenv("ZOLO_AWS_SECRET_KEY"),
        }

    def get_secret(self, key, default=None):
        """Get secret value from environment variables."""
        value = self.secrets.get(key, default)

        if value is None:
            logger.warning("[zConfig] Secret '%s' not found in environment", key)

        return value

    def has_secret(self, key):
        """Check if secret is available."""
        return self.secrets.get(key) is not None

    # ═══════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════

    def get_environment(self):
        """Get current environment name."""
        return self.environment

    def get_paths_info(self):
        """Get path information for debugging."""
        return self.paths.get_info()

    def get_config_sources(self):
        """Get list of config sources that were loaded."""
        return self.loader.config_sources

    def ensure_user_config_dir(self):
        """Ensure user config directory exists."""
        return self.paths.ensure_user_config_dir()

    def print_info(self):
        """Print configuration information for debugging."""
        if not self.zcli:
            raise ValueError("zConfig.print_info() requires zCLI instance")

        self.zcli.display.handle({
            "event": "zConfig",
            "data": {
                "environment": self.environment,
                "machine": self.machine.get_all(),
                "sources": self.loader.config_sources,
                "paths": self.get_paths_info(),
                "secrets": {k: "✓" if v else "✗" for k, v in self.secrets.items()}
            }
        })

    # ═══════════════════════════════════════════════════════════
    # Configuration Persistence (formerly zExport)
    # ═══════════════════════════════════════════════════════════

    def persist_machine(self, key=None, value=None, show=False, reset=False):
        """
        Persist machine configuration changes to user's machine.yaml.
        
        Args:
            key: Machine config key (e.g., 'browser', 'ide')
            value: New value
            show: If True, show current values
            reset: If True, reset to auto-detected defaults
            
        Returns:
            bool: Success status
        """
        # Reset to defaults
        if reset:
            return self._reset_machine_config(key)
        
        # Show current values
        if show or (key is None and value is None):
            return self._show_machine_config()
        
        # Validate key
        if key not in self._get_valid_machine_keys():
            if self.zcli and self.zcli.display:
                self.zcli.display.handle({
                    "event": "error",
                    "message": f"Invalid machine config key: {key}",
                    "details": f"Valid keys: {', '.join(self._get_valid_machine_keys())}"
                })
            else:
                print(f"\n❌ Invalid machine config key: {key}")
                print(f"   Valid keys: {', '.join(self._get_valid_machine_keys())}\n")
            return False
        
        # Get current value
        current_value = self.machine.get(key)
        
        # Validate value (if applicable)
        validation_result = self._validate_machine_value(key, value)
        if not validation_result["valid"]:
            if self.zcli and self.zcli.display:
                self.zcli.display.handle({
                    "event": "error",
                    "message": validation_result['error']
                })
            else:
                print(f"\n❌ {validation_result['error']}\n")
            return False
        
        # Update runtime config
        self.machine.update(key, value)
        if self.zcli and hasattr(self.zcli, 'session'):
            self.zcli.session["zMachine"][key] = value
        
        # Persist to disk
        success = self.machine.save_user_config()
        
        if success:
            # Show success message
            user_config_path = self.paths.user_config_dir / "machine.yaml"
            if self.zcli and self.zcli.display:
                self.zcli.display.handle({
                    "event": "success",
                    "message": f"Updated machine config: {key}",
                    "details": f"{current_value} → {value}",
                    "file": str(user_config_path)
                })
            else:
                print(f"\n✅ Updated machine config: {key}")
                print(f"   {current_value} → {value}")
                print(f"   Saved to: {user_config_path}\n")
        else:
            if self.zcli and self.zcli.display:
                self.zcli.display.handle({
                    "event": "error",
                    "message": "Failed to save machine config"
                })
            else:
                print(f"\n❌ Failed to save machine config\n")
        
        return success

    def persist_config(self, key=None, value=None, show=False):
        """
        Persist application configuration changes to user's config.yaml.
        
        Args:
            key: Config key (e.g., 'logging.level', 'cache.max_size')
            value: New value
            show: If True, show current values
            
        Returns:
            bool: Success status
        """
        # Future implementation for config.yaml persistence
        if self.zcli and self.zcli.display:
            self.zcli.display.handle({
                "event": "warning",
                "message": "Config persistence not yet implemented. Coming in Phase 2!"
            })
        else:
            print("\n⚠️  Config persistence not yet implemented. Coming in Phase 2!")
        return False

    def _reset_machine_config(self, key=None):
        """
        Reset machine configuration to auto-detected defaults.
        
        Args:
            key: Specific key to reset, or None to reset all
            
        Returns:
            bool: Success status
        """
        from .zConfig_modules.machine_config import MachineConfig
        
        # Create a fresh MachineConfig to get auto-detected values
        fresh_config = MachineConfig(self.paths)
        auto_detected = fresh_config._auto_detect()
        
        user_config_path = self.paths.user_config_dir / "machine.yaml"
        
        if key:
            # Reset specific key
            if key not in self._get_valid_machine_keys():
                if self.zcli and self.zcli.display:
                    self.zcli.display.handle({
                        "event": "error",
                        "message": f"Invalid machine config key: {key}"
                    })
                else:
                    print(f"\n❌ Invalid machine config key: {key}\n")
                return False
            
            current_value = self.machine.get(key)
            default_value = auto_detected.get(key)
            
            # Update runtime and persist
            self.machine.update(key, default_value)
            if self.zcli and hasattr(self.zcli, 'session'):
                self.zcli.session["zMachine"][key] = default_value
            success = self.machine.save_user_config()
            
            if success:
                if self.zcli and self.zcli.display:
                    self.zcli.display.handle({
                        "event": "success",
                        "message": f"Reset machine config: {key}",
                        "details": f"{current_value} → {default_value} (auto-detected)",
                        "file": str(user_config_path)
                    })
                else:
                    print(f"\n✅ Reset machine config: {key}")
                    print(f"   {current_value} → {default_value} (auto-detected)")
                    print(f"   Saved to: {user_config_path}\n")
            else:
                if self.zcli and self.zcli.display:
                    self.zcli.display.handle({
                        "event": "error",
                        "message": "Failed to save machine config"
                    })
                else:
                    print(f"\n❌ Failed to save machine config\n")
            
            return success
        else:
            # Reset ALL keys - require explicit confirmation
            if self.zcli and self.zcli.display:
                self.zcli.display.handle({
                    "event": "warning",
                    "message": "Full reset requires explicit confirmation",
                    "details": "Use: config machine --reset [key] to reset specific key"
                })
            else:
                print("\n" + "="*70)
                print("⚠️  WARNING: Reset ALL machine config to defaults?")
                print("="*70)
                print("\nThis will:")
                print("  • Auto-detect all system settings")
                print("  • Reset all tool preferences to defaults")
                print("  • Overwrite your current machine.yaml")
                print(f"\nCurrent file: {user_config_path}")
                print("\n❌ Full reset requires explicit confirmation.")
                print("   Use: config machine --reset [key]  (to reset specific key)")
                print("   Example: config machine --reset browser\n")
            
            return False

    def _show_machine_config(self):
        """
        Display current machine configuration.
        
        Returns:
            bool: Success status
        """
        machine = self.machine.get_all()
        
        if self.zcli and self.zcli.display:
            self.zcli.display.handle({
                "event": "config_display",
                "title": "Machine Configuration",
                "data": machine,
                "file": str(self.paths.user_config_dir / "machine.yaml")
            })
        else:
            print("\n" + "="*70)
            print("Machine Configuration")
            print("="*70)
            
            # Group by category
            categories = {
                "Identity": ["os", "hostname", "architecture", "python_version"],
                "Deployment": ["deployment", "role"],
                "Tool Preferences": ["browser", "ide", "terminal", "shell"],
                "System Capabilities": ["cpu_cores", "memory_gb"],
            }
            
            for category, keys in categories.items():
                print(f"\n{category}:")
                for key in keys:
                    value = machine.get(key, "N/A")
                    print(f"  {key}: {value}")
            
            # Show file location
            user_config_path = self.paths.user_config_dir / "machine.yaml"
            print(f"\nConfig file: {user_config_path}")
            print("="*70 + "\n")
        
        return True

    def _get_valid_machine_keys(self):
        """
        Get list of valid machine config keys that users can modify.
        
        Returns:
            List of valid keys
        """
        return [
            # Identity (usually auto-detected, but can be overridden)
            "os", "hostname", "architecture", "python_version",
            # Deployment (user-editable)
            "deployment", "role",
            # Tool Preferences (user-editable)
            "browser", "ide", "terminal", "shell",
            # System Capabilities (usually auto-detected, but can be overridden)
            "cpu_cores", "memory_gb",
        ]

    def _validate_machine_value(self, key, value):
        """
        Validate machine config value.
        
        Args:
            key: Config key
            value: Value to validate
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str) keys
        """
        # Deployment validation
        if key == "deployment":
            valid_deployments = ["dev", "prod", "staging", "lfs"]
            if value not in valid_deployments:
                return {
                    "valid": False,
                    "error": f"Invalid deployment: {value}. Must be one of: {', '.join(valid_deployments)}"
                }
        
        # Role validation
        elif key == "role":
            valid_roles = ["development", "production", "testing", "staging"]
            if value not in valid_roles:
                return {
                    "valid": False,
                    "error": f"Invalid role: {value}. Must be one of: {', '.join(valid_roles)}"
                }
        
        # Numeric validation
        elif key in ["cpu_cores", "memory_gb"]:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return {"valid": False, "error": f"{key} must be positive"}
            except ValueError:
                return {"valid": False, "error": f"{key} must be a number"}
        
        # All validations passed
        return {"valid": True, "error": None}
