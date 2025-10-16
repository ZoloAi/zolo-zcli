# zCLI/subsystems/zConfig_modules/config_loader.py
"""
Configuration loader with hierarchy support.

Loads config from multiple sources and merges them with priority.
"""

import os
import yaml
from pathlib import Path

# Note: No logger import to avoid circular dependency with zLogger subsystem


class ConfigLoader:
    """
    Configuration loader with hierarchical merging.
    
    Loads configuration from:
    1. Package defaults (config/zConfig.default.yaml)
    2. Environment-specific package config (config/zConfig.{env}.yaml)
    3. System config (OS-specific path)
    4. User config (OS-specific path)
    5. Project config (current directory)
    6. Environment variables (highest priority)
    
    Merges all sources with deep merge strategy.
    """
    
    def __init__(self, environment="dev"):
        """
        Initialize configuration loader.
        
        Args:
            environment: Environment name (dev, prod, staging, etc.)
        """
        self.environment = environment
        self.config = {}
        self.config_sources = []  # Track where config came from
    
    def load(self, paths_resolver):
        """
        Load configuration from all sources.
        
        Args:
            paths_resolver: zConfigPaths instance for path resolution
            
        Returns:
            Merged configuration dict
        """
        # 1. Load package defaults
        self._load_package_defaults()
        
        # 2. Load environment-specific package config
        self._load_package_environment_config()
        
        # 3. Load from file hierarchy
        for config_path, priority, source in paths_resolver.get_config_file_hierarchy():
            self._load_config_file(config_path, source)
        
        # 4. Apply environment variable overrides
        self._load_env_overrides()
        
        print(f"[ConfigLoader] Configuration loaded from {len(self.config_sources)} sources: {', '.join(self.config_sources)}")
        
        return self.config
    
    def _load_package_defaults(self):
        """Load package default configuration from user's Application Support directory."""
        try:
            # Look in user's Application Support directory first
            from .config_paths import zConfigPaths
            paths = zConfigPaths()
            user_configs_dir = paths.user_zconfigs_dir
            
            # Ensure zConfigs directory exists
            user_configs_dir.mkdir(parents=True, exist_ok=True)
            
            default_config = user_configs_dir / "zConfig.default.yaml"
            
            if default_config.exists():
                print(f"[ConfigLoader] Using existing user config: {default_config}")
                self._load_config_file(default_config, "user-defaults")
            else:
                # Try package defaults as fallback
                import zCLI
                package_root = Path(zCLI.__file__).parent.parent
                package_default_config = package_root / "config" / "zConfig.default.yaml"
                
                if package_default_config.exists():
                    print(f"[ConfigLoader] Creating user config from package defaults: {default_config}")
                    # Copy package defaults to user directory
                    import shutil
                    shutil.copy2(package_default_config, default_config)
                    self._load_config_file(default_config, "user-defaults")
                else:
                    print(f"[ConfigLoader] Package defaults not found: {package_default_config}")
                    # Use fallback hardcoded defaults
                    self.config = self._get_fallback_defaults()
                    self.config_sources.append("fallback-defaults")
        
        except Exception as e:
            print(f"[ConfigLoader] Failed to load package defaults: {e}")
            self.config = self._get_fallback_defaults()
            self.config_sources.append("fallback-defaults")
    
    def _load_package_environment_config(self):
        """Load environment-specific configuration from user's Application Support directory."""
        try:
            # Look in user's Application Support directory first
            from .config_paths import zConfigPaths
            paths = zConfigPaths()
            user_configs_dir = paths.user_zconfigs_dir
            
            # Ensure zConfigs directory exists
            user_configs_dir.mkdir(parents=True, exist_ok=True)
            
            env_config = user_configs_dir / f"zConfig.{self.environment}.yaml"
            
            if env_config.exists():
                self._load_config_file(env_config, f"user-{self.environment}")
            else:
                # Try package defaults as fallback
                import zCLI
                package_root = Path(zCLI.__file__).parent.parent
                package_env_config = package_root / "config" / f"zConfig.{self.environment}.yaml"
                
                if package_env_config.exists():
                    print(f"[ConfigLoader] Using package environment config, copying to user directory: {env_config}")
                    # Copy package environment config to user directory
                    import shutil
                    shutil.copy2(package_env_config, env_config)
                    self._load_config_file(env_config, f"user-{self.environment}")
                else:
                    print(f"[ConfigLoader] No config for environment: {self.environment}")
        
        except Exception as e:
            print(f"[ConfigLoader] Failed to load environment config: {e}")
    
    def _load_config_file(self, path, source):
        """
        Load and merge a YAML config file.
        
        Args:
            path: Path to config file
            source: Source description for logging
        """
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
                if data:
                    self._deep_merge(self.config, data)
                    self.config_sources.append(source)
                    print(f"[ConfigLoader] Loaded config from {source}: {path}")
                else:
                    print(f"[ConfigLoader] Config file is empty: {path}")
        
        except FileNotFoundError:
            print(f"[ConfigLoader] Config file not found: {path}")
        
        except yaml.YAMLError as e:
            print(f"[ConfigLoader] YAML parse error in {path}: {e}")
        
        except Exception as e:
            print(f"[ConfigLoader] Failed to load config from {path}: {e}")
    
    def _load_env_overrides(self):
        """
        Apply environment variable overrides.
        
        Environment variables have highest priority and override all config files.
        
        Supported env vars:
        - WEBSOCKET_HOST → zComm.network.host
        - WEBSOCKET_PORT → zComm.network.port
        - WEBSOCKET_REQUIRE_AUTH → zComm.security.require_auth
        - WEBSOCKET_MAX_CONNECTIONS → zComm.limits.max_connections
        - etc.
        """
        env_overrides = {}
        
        # zComm configuration (WebSocket & services)
        if os.getenv("WEBSOCKET_HOST"):
            self._set_nested(env_overrides, "zComm.network.host", os.getenv("WEBSOCKET_HOST"))
        
        if os.getenv("WEBSOCKET_PORT"):
            self._set_nested(env_overrides, "zComm.network.port", int(os.getenv("WEBSOCKET_PORT")))
        
        if os.getenv("WEBSOCKET_REQUIRE_AUTH"):
            value = os.getenv("WEBSOCKET_REQUIRE_AUTH").lower() in ("true", "1", "yes")
            self._set_nested(env_overrides, "zComm.security.require_auth", value)
        
        if os.getenv("WEBSOCKET_ALLOWED_ORIGINS"):
            origins = [o.strip() for o in os.getenv("WEBSOCKET_ALLOWED_ORIGINS").split(",") if o.strip()]
            self._set_nested(env_overrides, "zComm.security.allowed_origins", origins)
        
        if os.getenv("WEBSOCKET_AUTH_SCHEMA"):
            self._set_nested(env_overrides, "zComm.security.auth_schema", os.getenv("WEBSOCKET_AUTH_SCHEMA"))
        
        if os.getenv("WEBSOCKET_MAX_CONNECTIONS"):
            self._set_nested(env_overrides, "zComm.limits.max_connections", int(os.getenv("WEBSOCKET_MAX_CONNECTIONS")))
        
        if os.getenv("WEBSOCKET_RATE_LIMIT"):
            self._set_nested(env_overrides, "zComm.limits.rate_limit_per_minute", int(os.getenv("WEBSOCKET_RATE_LIMIT")))
        
        # zData configuration
        if os.getenv("ZOLO_DATA_BACKEND"):
            self._set_nested(env_overrides, "zData.backends.default", os.getenv("ZOLO_DATA_BACKEND"))
        
        # Apply overrides
        if env_overrides:
            self._deep_merge(self.config, env_overrides)
            self.config_sources.append("environment-variables")
            print("[ConfigLoader] Applied environment variable overrides")
    
    def _deep_merge(self, base, overlay):
        """
        Deep merge overlay into base dictionary.
        
        Recursively merges dictionaries, overlay values take precedence.
        
        Args:
            base: Base dictionary (modified in place)
            overlay: Overlay dictionary (values to merge in)
        """
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                self._deep_merge(base[key], value)
            else:
                # Override value
                base[key] = value
    
    def _set_nested(self, config, path, value):
        """
        Set nested config value using dot notation.
        
        Args:
            config: Config dict
            path: Dot-separated path (e.g., "zComm.network.host")
            value: Value to set
        """
        keys = path.split(".")
        current = config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set final value
        current[keys[-1]] = value
    
    def _get_fallback_defaults(self):
        """
        Hardcoded fallback defaults if config files can't be loaded.
        
        Returns:
            Minimal working configuration
        """
        return {
            "Meta": {
                "version": "1.0",
                "environment": self.environment
            },
            "zComm": {
                "network": {
                    "host": "127.0.0.1",
                    "port": 56891
                },
                "security": {
                    "require_auth": True,
                    "allowed_origins": [],
                    "auth_schema": "@.schemas.auth.zUsers",
                    "auth_token_field": "api_key"
                },
                "limits": {
                    "max_connections": 100,
                    "max_message_size": 102400,
                    "rate_limit_per_minute": 100
                },
                "timeouts": {
                    "auth_timeout": 10,
                    "ping_interval": 20,
                    "ping_timeout": 20
                }
            },
            "zData": {
                "backends": {
                    "default": "sqlite",
                    "sqlite": {"path": "./data.db"}
                }
            },
            "zLoader": {
                "cache": {
                    "max_size": 100,
                    "ttl": 3600
                }
            }
        }

