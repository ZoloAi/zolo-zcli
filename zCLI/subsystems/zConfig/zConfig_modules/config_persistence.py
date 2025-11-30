# zCLI/subsystems/zConfig/zConfig_modules/config_persistence.py
"""Configuration persistence for saving/loading zCLI config changes."""

from zCLI import Colors, Any, Dict, List, Optional
from .config_session import SESSION_KEY_ZMACHINE

# ═══════════════════════════════════════════════════════════════════
# Module Constants - Week 6.2.10
# ═══════════════════════════════════════════════════════════════════

# Display Markers
MARKER_EDITABLE = "[EDIT] "
MARKER_LOCKED = "[LOCK] "

# Category Names
CATEGORY_IDENTITY = "Identity (Auto-detected)"
CATEGORY_USER_PREFS = "User Preferences (Editable)"
CATEGORY_SYSTEM_INFO = "System Info (Auto-detected)"

# Valid Configuration Values
VALID_DEPLOYMENTS = ["Development", "Testing", "Production"]
DEPRECATED_DEPLOYMENTS = ["Debug", "Info"]  # Mapped to Development/Testing
VALID_ROLES = ["development", "production", "testing", "staging"]
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Machine Config Keys (Editable)
EDITABLE_MACHINE_KEYS = [
    "browser", "ide", "terminal", "shell",  # User tool preferences
    "cpu_cores_limit", "memory_gb_limit",   # Resource allocation limits (optional)
]

# Machine Config Keys (By Category)
MACHINE_KEYS_IDENTITY = ["os", "hostname", "architecture", "python_version", "processor"]
MACHINE_KEYS_USER_PREFS = ["browser", "ide", "terminal", "shell"]
MACHINE_KEYS_SYSTEM_INFO = ["cpu_cores", "memory_gb", "os_version", "os_name"]

# Environment Config Keys (Editable)
EDITABLE_ENVIRONMENT_KEYS = [
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

# Error Messages
ERROR_INVALID_KEY = "Invalid {config_type} config key: {key}"
ERROR_EDITABLE_KEYS = "Editable keys: {keys}"
ERROR_FAILED_TO_SAVE = "Failed to save {config_type} config"
ERROR_MUST_BE_POSITIVE = "{key} must be positive"
ERROR_MUST_BE_NUMBER = "{key} must be a number"
ERROR_INVALID_DEPLOYMENT = "Invalid deployment: {value}. Must be one of: {valid_values}"
ERROR_INVALID_ROLE = "Invalid role: {value}. Must be one of: {valid_values}"
ERROR_INVALID_LOG_LEVEL = "Invalid log level: {value}. Must be one of: {valid_values}"
ERROR_RESET_REQUIRES_CONFIRMATION = "Full reset requires explicit confirmation"
ERROR_RESET_USE_KEY = "Use: config machine --reset [key] to reset specific key"
ERROR_RESET_NOT_IMPLEMENTED = "{config_type} config reset not yet implemented"

# Success Messages
SUCCESS_UPDATED = "Updated {config_type} config: {key}"
SUCCESS_RESET = "Reset {config_type} config: {key}"
SUCCESS_CHANGE_DETAIL = "{old_value} → {new_value}"
SUCCESS_RESET_DETAIL = "{old_value} → {new_value} (auto-detected)"
SUCCESS_SAVED_TO = "Saved to: {file_path}"

# Display Headers
HEADER_SEPARATOR = "=" * 70
HEADER_MACHINE_CONFIG = "Machine Configuration"
HEADER_ENVIRONMENT_CONFIG = "Environment Configuration"
HEADER_ZC_ENV_SETTINGS = "zCLI Environment Settings:"
HEADER_CONFIG_FILE = "Config file: {file_path}"


# ═══════════════════════════════════════════════════════════════════
# ConfigPersistence Class
# ═══════════════════════════════════════════════════════════════════

class ConfigPersistence:
    """Manages configuration persistence to files - handles only editable zCLI config parts."""

    def __init__(self, machine_config: Any, environment_config: Any, paths: Any, zcli: Optional[Any] = None) -> None:
        """Initialize config persistence with dependencies."""
        self.machine = machine_config
        self.environment = environment_config
        self.paths = paths
        self.zcli = zcli
    
    # ═══════════════════════════════════════════════════════════
    # Machine Config Persistence (User Preferences Only)
    # ═══════════════════════════════════════════════════════════
    
    def persist_machine(self, key: Optional[str] = None, value: Optional[Any] = None, 
                       show: bool = False, reset: bool = False) -> bool:
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
        if key not in EDITABLE_MACHINE_KEYS:
            self._handle_error(
                ERROR_INVALID_KEY.format(config_type="machine", key=key),
                ERROR_EDITABLE_KEYS.format(keys=', '.join(EDITABLE_MACHINE_KEYS))
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
        self._update_session_machine(key, value)
        
        # Persist to disk
        success = self.machine.save_user_config()
        
        if success:
            # Show success message
            user_config_path = self.paths.user_zconfigs_dir / self.paths.ZMACHINE_USER_FILENAME
            self._handle_success(
                SUCCESS_UPDATED.format(config_type="machine", key=key),
                SUCCESS_CHANGE_DETAIL.format(old_value=current_value, new_value=value),
                str(user_config_path)
            )
        else:
            self._handle_error(ERROR_FAILED_TO_SAVE.format(config_type="machine"))
        
        return success

    # ═══════════════════════════════════════════════════════════
    # Environment Config Persistence (zCLI Environment Settings)
    # ═══════════════════════════════════════════════════════════
    
    def persist_environment(self, key: Optional[str] = None, value: Optional[Any] = None, 
                           show: bool = False, reset: bool = False) -> bool:
        """
        Persist environment configuration changes to user's zConfig.environment.yaml.
        
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
        if key not in EDITABLE_ENVIRONMENT_KEYS:
            self._handle_error(
                ERROR_INVALID_KEY.format(config_type="environment", key=key),
                ERROR_EDITABLE_KEYS.format(keys=', '.join(EDITABLE_ENVIRONMENT_KEYS))
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
            user_config_path = self.paths.user_zconfigs_dir / self.paths.ZENVIRONMENT_FILENAME
            self._handle_success(
                SUCCESS_UPDATED.format(config_type="environment", key=key),
                SUCCESS_CHANGE_DETAIL.format(old_value=current_value, new_value=value),
                str(user_config_path)
            )
        else:
            self._handle_error(ERROR_FAILED_TO_SAVE.format(config_type="environment"))
        
        return success

    # ═══════════════════════════════════════════════════════════
    # Machine Config Helpers
    # ═══════════════════════════════════════════════════════════
    
    def _reset_machine_config(self, key: Optional[str] = None) -> bool:
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
        
        user_config_path = self.paths.user_zconfigs_dir / self.paths.ZMACHINE_USER_FILENAME
        
        if key:
            # Reset specific key
            if key not in EDITABLE_MACHINE_KEYS:
                self._handle_error(ERROR_INVALID_KEY.format(config_type="machine", key=key))
                return False
            
            current_value = self.machine.get(key)
            default_value = auto_detected.get(key)
            
            # Update runtime and persist
            self.machine.update(key, default_value)
            self._update_session_machine(key, default_value)
            success = self.machine.save_user_config()
            
            if success:
                self._handle_success(
                    SUCCESS_RESET.format(config_type="machine", key=key),
                    SUCCESS_RESET_DETAIL.format(old_value=current_value, new_value=default_value),
                    str(user_config_path)
                )
            else:
                self._handle_error(ERROR_FAILED_TO_SAVE.format(config_type="machine"))
            
            return success
        else:
            # Reset ALL keys - require explicit confirmation
            self._handle_error(
                ERROR_RESET_REQUIRES_CONFIRMATION,
                ERROR_RESET_USE_KEY
            )
            return False

    def show_machine_config(self) -> bool:
        """Display current machine configuration."""
        machine = self.machine.get_all()
        
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_MACHINE_CONFIG}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}")
        
        # Group by category
        categories = {
            CATEGORY_IDENTITY: MACHINE_KEYS_IDENTITY,
            CATEGORY_USER_PREFS: MACHINE_KEYS_USER_PREFS,
            CATEGORY_SYSTEM_INFO: MACHINE_KEYS_SYSTEM_INFO,
        }
        
        for category, keys in categories.items():
            print(f"\n{Colors.CONFIG}{category}:{Colors.RESET}")
            for key in keys:
                value = machine.get(key, "N/A")
                editable = key in EDITABLE_MACHINE_KEYS
                marker = MARKER_EDITABLE if editable else MARKER_LOCKED
                print(f"  {marker}{key}: {value}")
        
        # Show file location
        user_config_path = self.paths.user_zconfigs_dir / self.paths.ZMACHINE_USER_FILENAME
        print(f"\n{Colors.CONFIG}{HEADER_CONFIG_FILE.format(file_path=user_config_path)}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}\n")
        
        return True

    def _get_editable_machine_keys(self) -> List[str]:
        """
        Get list of user-editable machine config keys.
        
        Only includes preferences that users can reasonably override.
        Excludes auto-detected characteristics like OS, hostname, etc.
        
        Returns:
            List of editable key names
        """
        return EDITABLE_MACHINE_KEYS

    def _validate_machine_value(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Validate machine config value.
        
        Args:
            key: Config key being validated
            value: Value to validate
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str or None) keys
        """
        # Numeric validation
        if key in ["cpu_cores", "memory_gb"]:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return {"valid": False, "error": ERROR_MUST_BE_POSITIVE.format(key=key)}
            except ValueError:
                return {"valid": False, "error": ERROR_MUST_BE_NUMBER.format(key=key)}
        
        # All validations passed
        return {"valid": True, "error": None}

    # ═══════════════════════════════════════════════════════════
    # Environment Config Helpers
    # ═══════════════════════════════════════════════════════════
    
    def _reset_environment_config(self, key: Optional[str] = None) -> bool:  # pylint: disable=unused-argument
        """
        Reset environment configuration to defaults.
        
        Args:
            key: Specific key to reset, or None to reset all
            
        Returns:
            bool: Success status
        """
        # TODO: Implement environment config reset
        self._handle_error(ERROR_RESET_NOT_IMPLEMENTED.format(config_type="Environment"))
        return False

    def show_environment_config(self) -> bool:
        """Display current environment configuration."""
        env = self.environment.get_all()
        
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_ENVIRONMENT_CONFIG}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}")
        
        # Show environment settings
        print(f"\n{Colors.CONFIG}{HEADER_ZC_ENV_SETTINGS}{Colors.RESET}")
        for key, value in env.items():
            print(f"  {MARKER_EDITABLE}{key}: {value}")
        
        # Show file location
        user_config_path = self.paths.user_zconfigs_dir / self.paths.ZENVIRONMENT_FILENAME
        print(f"\n{Colors.CONFIG}{HEADER_CONFIG_FILE.format(file_path=user_config_path)}{Colors.RESET}")
        print(f"{Colors.CONFIG}{HEADER_SEPARATOR}{Colors.RESET}\n")
        
        return True

    def _get_editable_environment_keys(self) -> List[str]:
        """
        Get list of user-editable environment config keys.
        
        Returns:
            List of editable key names
        """
        return EDITABLE_ENVIRONMENT_KEYS

    def _validate_environment_value(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Validate environment config value.
        
        Args:
            key: Config key being validated
            value: Value to validate
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str or None) keys
        """
        # Deployment validation
        if key == "deployment":
            if value not in VALID_DEPLOYMENTS:
                return {
                    "valid": False,
                    "error": ERROR_INVALID_DEPLOYMENT.format(
                        value=value,
                        valid_values=', '.join(VALID_DEPLOYMENTS)
                    )
                }
        
        # Role validation
        elif key == "role":
            if value not in VALID_ROLES:
                return {
                    "valid": False,
                    "error": ERROR_INVALID_ROLE.format(
                        value=value,
                        valid_values=', '.join(VALID_ROLES)
                    )
                }
        
        # Logging level validation
        elif key == "logging.level":
            if value.upper() not in VALID_LOG_LEVELS:
                return {
                    "valid": False,
                    "error": ERROR_INVALID_LOG_LEVEL.format(
                        value=value,
                        valid_values=', '.join(VALID_LOG_LEVELS)
                    )
                }
        
        # Numeric validation for performance settings
        elif key in ["performance.max_workers", "performance.cache_size", "performance.cache_ttl", "performance.timeout"]:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return {"valid": False, "error": ERROR_MUST_BE_POSITIVE.format(key=key)}
            except ValueError:
                return {"valid": False, "error": ERROR_MUST_BE_NUMBER.format(key=key)}
        
        # All validations passed
        return {"valid": True, "error": None}
    
    # ═══════════════════════════════════════════════════════════
    # Session Update Helper - Week 6.2.10
    # ═══════════════════════════════════════════════════════════
    
    def _update_session_machine(self, key: str, value: Any) -> None:
        """
        Update machine config in session dict if available.
        
        Args:
            key: Machine config key
            value: New value
        """
        if self.zcli and hasattr(self.zcli, 'session'):
            self.zcli.session[SESSION_KEY_ZMACHINE][key] = value
    
    # ═══════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════
    
    def _handle_error(self, message: str, details: Optional[str] = None) -> None:
        """
        Handle error messages.
        
        Args:
            message: Error message
            details: Optional details
        """
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.ERROR}[ERROR] {message}{Colors.RESET}")
        if details:
            print(f"   {details}")
        print()
    
    def _handle_success(self, message: str, details: Optional[str] = None, file_path: Optional[str] = None) -> None:
        """
        Handle success messages.
        
        Args:
            message: Success message
            details: Optional change details
            file_path: Optional file path where changes were saved
        """
        # Layer 0: Always use print (zDisplay not available yet)
        print(f"\n{Colors.CONFIG}[OK] {message}{Colors.RESET}")
        if details:
            print(f"   {details}")
        if file_path:
            print(f"   {SUCCESS_SAVED_TO.format(file_path=file_path)}")
        print()
