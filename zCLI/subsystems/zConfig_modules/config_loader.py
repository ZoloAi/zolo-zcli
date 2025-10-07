# zCLI/subsystems/zConfig_modules/config_loader.py
"""
Configuration loader with hierarchy support.

Loads config from multiple sources and merges them with priority.
"""

import os
import yaml
from pathlib import Path
from logger import logger


class ConfigLoader:
    """
    Configuration loader with hierarchical merging.
    
    Loads configuration from:
    1. Package defaults (config/config.default.yaml)
    2. Environment-specific package config (config/config.{env}.yaml)
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
            paths_resolver: ZConfigPaths instance for path resolution
            
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
        
        logger.info("[ConfigLoader] Configuration loaded from %d sources: %s",
                   len(self.config_sources), ", ".join(self.config_sources))
        
        return self.config
    
    def _load_package_defaults(self):
        """Load package default configuration."""
        try:
            # Get package config directory
            import zCLI
            package_root = Path(zCLI.__file__).parent.parent
            default_config = package_root / "config" / "config.default.yaml"
            
            if default_config.exists():
                self._load_config_file(default_config, "package-defaults")
            else:
                logger.warning("[ConfigLoader] Package defaults not found: %s", default_config)
                # Use fallback hardcoded defaults
                self.config = self._get_fallback_defaults()
                self.config_sources.append("fallback-defaults")
        
        except Exception as e:
            logger.error("[ConfigLoader] Failed to load package defaults: %s", e)
            self.config = self._get_fallback_defaults()
            self.config_sources.append("fallback-defaults")
    
    def _load_package_environment_config(self):
        """Load environment-specific package configuration."""
        try:
            # Get package config directory
            import zCLI
            package_root = Path(zCLI.__file__).parent.parent
            env_config = package_root / "config" / f"config.{self.environment}.yaml"
            
            if env_config.exists():
                self._load_config_file(env_config, f"package-{self.environment}")
            else:
                logger.debug("[ConfigLoader] No package config for environment: %s", self.environment)
        
        except Exception as e:
            logger.warning("[ConfigLoader] Failed to load environment config: %s", e)
    
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
                    logger.info("[ConfigLoader] Loaded config from %s: %s", source, path)
                else:
                    logger.warning("[ConfigLoader] Config file is empty: %s", path)
        
        except FileNotFoundError:
            logger.debug("[ConfigLoader] Config file not found: %s", path)
        
        except yaml.YAMLError as e:
            logger.error("[ConfigLoader] YAML parse error in %s: %s", path, e)
        
        except Exception as e:
            logger.error("[ConfigLoader] Failed to load config from %s: %s", path, e)
    
    def _load_env_overrides(self):
        """
        Apply environment variable overrides.
        
        Environment variables have highest priority and override all config files.
        
        Supported env vars:
        - WEBSOCKET_HOST → zSocket.network.host
        - WEBSOCKET_PORT → zSocket.network.port
        - WEBSOCKET_REQUIRE_AUTH → zSocket.security.require_auth
        - WEBSOCKET_MAX_CONNECTIONS → zSocket.limits.max_connections
        - etc.
        """
        env_overrides = {}
        
        # zSocket configuration
        if os.getenv("WEBSOCKET_HOST"):
            self._set_nested(env_overrides, "zSocket.network.host", os.getenv("WEBSOCKET_HOST"))
        
        if os.getenv("WEBSOCKET_PORT"):
            self._set_nested(env_overrides, "zSocket.network.port", int(os.getenv("WEBSOCKET_PORT")))
        
        if os.getenv("WEBSOCKET_REQUIRE_AUTH"):
            value = os.getenv("WEBSOCKET_REQUIRE_AUTH").lower() in ("true", "1", "yes")
            self._set_nested(env_overrides, "zSocket.security.require_auth", value)
        
        if os.getenv("WEBSOCKET_ALLOWED_ORIGINS"):
            origins = [o.strip() for o in os.getenv("WEBSOCKET_ALLOWED_ORIGINS").split(",") if o.strip()]
            self._set_nested(env_overrides, "zSocket.security.allowed_origins", origins)
        
        if os.getenv("WEBSOCKET_AUTH_SCHEMA"):
            self._set_nested(env_overrides, "zSocket.security.auth_schema", os.getenv("WEBSOCKET_AUTH_SCHEMA"))
        
        if os.getenv("WEBSOCKET_MAX_CONNECTIONS"):
            self._set_nested(env_overrides, "zSocket.limits.max_connections", int(os.getenv("WEBSOCKET_MAX_CONNECTIONS")))
        
        if os.getenv("WEBSOCKET_RATE_LIMIT"):
            self._set_nested(env_overrides, "zSocket.limits.rate_limit_per_minute", int(os.getenv("WEBSOCKET_RATE_LIMIT")))
        
        # zData configuration
        if os.getenv("ZOLO_DATA_BACKEND"):
            self._set_nested(env_overrides, "zData.backends.default", os.getenv("ZOLO_DATA_BACKEND"))
        
        # Apply overrides
        if env_overrides:
            self._deep_merge(self.config, env_overrides)
            self.config_sources.append("environment-variables")
            logger.debug("[ConfigLoader] Applied environment variable overrides")
    
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
            path: Dot-separated path (e.g., "zSocket.network.host")
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
            "zSocket": {
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

