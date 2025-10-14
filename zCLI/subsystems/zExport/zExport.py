# zCLI/subsystems/zExport.py
"""
zExport - Configuration Export Subsystem

Provides user-facing commands to persist configuration changes to disk.
Solves the problem of users being unable to update config files from within zolo-zcli.

Use Cases:
1. Update machine preferences (browser, IDE)
2. Fix misconfigured settings that prevent zOpen from working
3. Change deployment environment (dev → prod)
4. Persist runtime changes without manual YAML editing

Example Usage:
    --export machine browser Chrome
    --export machine ide cursor
    --export machine deployment prod
    --export machine --reset browser
"""

import yaml
from pathlib import Path
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class ZExport:
    """
    Configuration export handler.
    
    Provides commands to update and persist configuration files:
    - machine.yaml (user preferences, tool settings)
    - config.yaml (application settings) [future]
    """
    
    def __init__(self, zcli):
        """
        Initialize zExport.
        
        Args:
            zcli: zCLI instance
        """
        self.zcli = zcli
        self.config = zcli.config
        self.session = zcli.session
        self.display = zcli.display
        
        logger.info("zExport initialized")
    
    def handle(self, target, key=None, value=None, show=False, reset=False):
        """
        Handle export command.
        
        Args:
            target: Export target ('machine', 'config')
            key: Configuration key to update
            value: New value for the key
            show: If True, show current values without updating
            reset: If True, reset to auto-detected defaults
            
        Returns:
            bool: Success status
        """
        if target == "machine":
            return self.export_machine(key, value, show, reset)
        elif target == "config":
            return self.export_config(key, value, show)
        else:
            print(f"\n❌ Unknown export target: {target}\n")
            return False
    
    def export_machine(self, key=None, value=None, show=False, reset=False):
        """
        Export machine configuration to user's machine.yaml.
        
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
            print(f"\n❌ Invalid machine config key: {key}")
            print(f"   Valid keys: {', '.join(self._get_valid_machine_keys())}\n")
            return False
        
        # Get current value
        current_value = self.config.get_machine().get(key)
        
        # Validate value (if applicable)
        validation_result = self._validate_machine_value(key, value)
        if not validation_result["valid"]:
            print(f"\n❌ {validation_result['error']}\n")
            return False
        
        # Update runtime config
        self.config.machine.update(key, value)
        self.session["zMachine"][key] = value
        
        # Persist to disk
        success = self.config.machine.save_user_config()
        
        if success:
            # Show success message
            user_config_path = self.config.paths.user_config_dir / "machine.yaml"
            print(f"\n✅ Updated machine config: {key}")
            print(f"   {current_value} → {value}")
            print(f"   Saved to: {user_config_path}\n")
        else:
            print(f"\n❌ Failed to save machine config\n")
        
        return success
    
    def export_config(self, key=None, value=None, show=False):
        """
        Export application configuration to user's config.yaml.
        
        Args:
            key: Config key (e.g., 'logging.level', 'cache.max_size')
            value: New value
            show: If True, show current values
            
        Returns:
            bool: Success status
        """
        # Future implementation for config.yaml export
        self.display.handle({
            "event": "zPrint",
            "color": "YELLOW",
            "label": "Config export not yet implemented. Coming in Phase 2!",
        })
        return False
    
    def _reset_machine_config(self, key=None):
        """
        Reset machine configuration to auto-detected defaults.
        
        Args:
            key: Specific key to reset, or None to reset all
            
        Returns:
            bool: Success status
        """
        from zCLI.subsystems.zConfig_modules.machine_config import MachineConfig
        
        # Create a fresh MachineConfig to get auto-detected values
        fresh_config = MachineConfig(self.config.paths)
        auto_detected = fresh_config._auto_detect()
        
        user_config_path = self.config.paths.user_config_dir / "machine.yaml"
        
        if key:
            # Reset specific key
            if key not in self._get_valid_machine_keys():
                print(f"\n❌ Invalid machine config key: {key}\n")
                return False
            
            current_value = self.config.get_machine().get(key)
            default_value = auto_detected.get(key)
            
            # Update runtime and persist
            self.config.machine.update(key, default_value)
            self.session["zMachine"][key] = default_value
            success = self.config.machine.save_user_config()
            
            if success:
                print(f"\n✅ Reset machine config: {key}")
                print(f"   {current_value} → {default_value} (auto-detected)")
                print(f"   Saved to: {user_config_path}\n")
            else:
                print(f"\n❌ Failed to save machine config\n")
            
            return success
        else:
            # Reset ALL keys - regenerate entire file
            print("\n" + "="*70)
            print("⚠️  WARNING: Reset ALL machine config to defaults?")
            print("="*70)
            print("\nThis will:")
            print("  • Auto-detect all system settings")
            print("  • Reset all tool preferences to defaults")
            print("  • Overwrite your current machine.yaml")
            print(f"\nCurrent file: {user_config_path}")
            
            # In non-interactive mode, require explicit confirmation
            # For now, we'll just show what would be reset
            print("\n❌ Full reset requires explicit confirmation.")
            print("   Use: export machine --reset [key]  (to reset specific key)")
            print("   Example: export machine --reset browser\n")
            
            return False
    
    def _show_machine_config(self):
        """
        Display current machine configuration.
        
        Returns:
            bool: Success status
        """
        machine = self.config.get_machine()
        
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
        user_config_path = self.config.paths.user_config_dir / "machine.yaml"
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
