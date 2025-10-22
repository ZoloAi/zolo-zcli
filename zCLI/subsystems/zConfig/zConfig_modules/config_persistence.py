# zCLI/subsystems/zConfig/zConfig_modules/config_persistence.py
"""Configuration persistence for saving/loading zCLI config changes."""

from zCLI import Colors

class ConfigPersistence:
    """Manages configuration persistence to files - handles only editable zCLI config parts."""

    def __init__(self, machine_config, environment_config, paths, zcli=None):
        """Initialize config persistence with dependencies."""
        self.machine = machine_config
        self.environment = environment_config
        self.paths = paths
        self.zcli = zcli
    
    # ═══════════════════════════════════════════════════════════
    # Machine Config Persistence (User Preferences Only)
    # ═══════════════════════════════════════════════════════════
    
    def persist_machine(self, key=None, value=None, show=False, reset=False):
        """
        Persist machine configuration changes to user's zConfig.machine.yaml.
        
        Only handles USER-EDITABLE preferences, not auto-detected characteristics.
        
        Args:
            key: Machine config key (e.g., 'browser', 'ide', 'terminal')
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
            return self.show_machine_config()
        
        # Validate key is user-editable
        if key not in self._get_editable_machine_keys():
            self._handle_error(
                f"Invalid machine config key: {key}",
                f"Editable keys: {', '.join(self._get_editable_machine_keys())}"
            )
            return False
        
        # Get current value
        current_value = self.machine.get(key)
        
        # Validate value (if applicable)
        validation_result = self._validate_machine_value(key, value)
        if not validation_result["valid"]:
            self._handle_error(validation_result['error'])
            return False
        
        # Update runtime config
        self.machine.update(key, value)
        if self.zcli and hasattr(self.zcli, 'session'):
            self.zcli.session["zMachine"][key] = value
        
        # Persist to disk
        success = self.machine.save_user_config()
        
        if success:
            # Show success message
            user_config_path = self.paths.user_zconfigs_dir / "zConfig.machine.yaml"
            self._handle_success(
                f"Updated machine config: {key}",
                f"{current_value} → {value}",
                str(user_config_path)
            )
        else:
            self._handle_error("Failed to save machine config")
        
        return success

    # ═══════════════════════════════════════════════════════════
    # Environment Config Persistence (zCLI Environment Settings)
    # ═══════════════════════════════════════════════════════════
    
    def persist_environment(self, key=None, value=None, show=False, reset=False):
        """
        Persist environment configuration changes to user's zConfig.env.yaml.
        
        Handles zCLI-specific environment settings (deployment, logging, etc.).
        Does NOT handle system environment variables or virtual environments.
        
        Args:
            key: Environment config key (e.g., 'deployment', 'logging.level')
            value: New value
            show: If True, show current values
            reset: If True, reset to defaults
            
        Returns:
            bool: Success status
        """
        # Reset to defaults
        if reset:
            return self._reset_environment_config(key)
        
        # Show current values
        if show or (key is None and value is None):
            return self.show_environment_config()
        
        # Validate key is user-editable
        if key not in self._get_editable_environment_keys():
            self._handle_error(
                f"Invalid environment config key: {key}",
                f"Editable keys: {', '.join(self._get_editable_environment_keys())}"
            )
            return False
        
        # Get current value
        current_value = self.environment.get(key)
        
        # Validate value (if applicable)
        validation_result = self._validate_environment_value(key, value)
        if not validation_result["valid"]:
            self._handle_error(validation_result['error'])
            return False
        
        # Update runtime config
        self.environment.env[key] = value
        
        # Persist to disk
        success = self.environment.save_user_config()
        
        if success:
            # Show success message
            user_config_path = self.paths.user_zconfigs_dir / "zConfig.env.yaml"
            self._handle_success(
                f"Updated environment config: {key}",
                f"{current_value} → {value}",
                str(user_config_path)
            )
        else:
            self._handle_error("Failed to save environment config")
        
        return success

    # ═══════════════════════════════════════════════════════════
    # Machine Config Helpers
    # ═══════════════════════════════════════════════════════════
    
    def _reset_machine_config(self, key=None):
        """
        Reset machine configuration to auto-detected defaults.
        
        Args:
            key: Specific key to reset, or None to reset all
            
        Returns:
            bool: Success status
        """
        from .helpers import auto_detect_machine
        
        # Get fresh auto-detected values
        auto_detected = auto_detect_machine()
        
        user_config_path = self.paths.user_zconfigs_dir / "zConfig.machine.yaml"
        
        if key:
            # Reset specific key
            if key not in self._get_editable_machine_keys():
                self._handle_error(f"Invalid machine config key: {key}")
                return False
            
            current_value = self.machine.get(key)
            default_value = auto_detected.get(key)
            
            # Update runtime and persist
            self.machine.update(key, default_value)
            if self.zcli and hasattr(self.zcli, 'session'):
                self.zcli.session["zMachine"][key] = default_value
            success = self.machine.save_user_config()
            
            if success:
                self._handle_success(
                    f"Reset machine config: {key}",
                    f"{current_value} → {default_value} (auto-detected)",
                    str(user_config_path)
                )
            else:
                self._handle_error("Failed to save machine config")
            
            return success
        else:
            # Reset ALL keys - require explicit confirmation
            self._handle_error(
                "Full reset requires explicit confirmation",
                "Use: config machine --reset [key] to reset specific key"
            )
            return False

    def show_machine_config(self):
        """Display current machine configuration."""
        machine = self.machine.get_all()
        
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}{'='*70}{Colors.RESET}")
        print(f"{Colors.CONFIG}Machine Configuration{Colors.RESET}")
        print(f"{Colors.CONFIG}{'='*70}{Colors.RESET}")
        
        # Group by category
        categories = {
            "Identity (Auto-detected)": ["os", "hostname", "architecture", "python_version", "processor"],
            "User Preferences (Editable)": ["browser", "ide", "terminal", "shell"],
            "System Info (Auto-detected)": ["cpu_cores", "memory_gb", "os_version", "os_name"],
        }
        
        for category, keys in categories.items():
            print(f"\n{Colors.CONFIG}{category}:{Colors.RESET}")
            for key in keys:
                value = machine.get(key, "N/A")
                editable = key in self._get_editable_machine_keys()
                marker = "[EDIT] " if editable else "[LOCK] "
                print(f"  {marker}{key}: {value}")
        
        # Show file location
        user_config_path = self.paths.user_zconfigs_dir / "zConfig.machine.yaml"
        print(f"\n{Colors.CONFIG}Config file: {user_config_path}{Colors.RESET}")
        print(f"{Colors.CONFIG}{'='*70}{Colors.RESET}\n")
        
        return True

    def _get_editable_machine_keys(self):
        """
        Get list of user-editable machine config keys.
        
        Only includes preferences that users can reasonably override.
        Excludes auto-detected characteristics like OS, hostname, etc.
        """
        return [
            # User tool preferences (can be overridden)
            "browser", "ide", "terminal", "shell",
            # System capabilities (can be overridden for testing/edge cases)
            "cpu_cores", "memory_gb",
        ]

    def _validate_machine_value(self, key, value):
        """Validate machine config value."""
        # Numeric validation
        if key in ["cpu_cores", "memory_gb"]:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return {"valid": False, "error": f"{key} must be positive"}
            except ValueError:
                return {"valid": False, "error": f"{key} must be a number"}
        
        # All validations passed
        return {"valid": True, "error": None}

    # ═══════════════════════════════════════════════════════════
    # Environment Config Helpers
    # ═══════════════════════════════════════════════════════════
    
    def _reset_environment_config(self, key=None):  # pylint: disable=unused-argument
        """Reset environment configuration to defaults."""
        # TODO: Implement environment config reset
        self._handle_error("Environment config reset not yet implemented")
        return False

    def show_environment_config(self):
        """Display current environment configuration."""
        env = self.environment.get_all()
        
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}{'='*70}{Colors.RESET}")
        print(f"{Colors.CONFIG}Environment Configuration{Colors.RESET}")
        print(f"{Colors.CONFIG}{'='*70}{Colors.RESET}")
        
        # Show environment settings
        print(f"\n{Colors.CONFIG}zCLI Environment Settings:{Colors.RESET}")
        for key, value in env.items():
            print(f"  [EDIT] {key}: {value}")
        
        # Show file location
        user_config_path = self.paths.user_zconfigs_dir / "zConfig.env.yaml"
        print(f"\n{Colors.CONFIG}Config file: {user_config_path}{Colors.RESET}")
        print(f"{Colors.CONFIG}{'='*70}{Colors.RESET}\n")
        
        return True

    def _get_editable_environment_keys(self):
        """Get list of user-editable environment config keys."""
        return [
            # Basic environment settings
            "deployment", "role", "datacenter", "cluster", "node_id",
            # Network settings
            "network.host", "network.port", "network.external_host", "network.external_port",
            # Security settings
            "security.require_auth", "security.allow_anonymous", "security.ssl_enabled",
            # Logging settings
            "logging.level", "logging.format", "logging.file_enabled", "logging.file_path",
            # Performance settings
            "performance.max_workers", "performance.cache_size", "performance.cache_ttl", "performance.timeout",
        ]

    def _validate_environment_value(self, key, value):
        """Validate environment config value."""
        # Deployment validation
        if key == "deployment":
            valid_deployments = ["Debug", "Info", "Production"]
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
        
        # Logging level validation
        elif key == "logging.level":
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if value.upper() not in valid_levels:
                return {
                    "valid": False,
                    "error": f"Invalid log level: {value}. Must be one of: {', '.join(valid_levels)}"
                }
        
        # Numeric validation for performance settings
        elif key in ["performance.max_workers", "performance.cache_size", "performance.cache_ttl", "performance.timeout"]:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return {"valid": False, "error": f"{key} must be positive"}
            except ValueError:
                return {"valid": False, "error": f"{key} must be a number"}
        
        # All validations passed
        return {"valid": True, "error": None}
    
    # ═══════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════
    
    def _handle_error(self, message, details=None):
        """Handle error messages."""
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.ERROR}[ERROR] {message}{Colors.RESET}")
        if details:
            print(f"   {details}")
        print()
    
    def _handle_success(self, message, details=None, file_path=None):
        """Handle success messages."""
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}[OK] {message}{Colors.RESET}")
        if details:
            print(f"   {details}")
        if file_path:
            print(f"   Saved to: {file_path}")
        print()