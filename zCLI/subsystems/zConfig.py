# zCLI/subsystems/zConfig.py — Configuration Management Subsystem
# ───────────────────────────────────────────────────────────────

"""
zConfig - Cross-platform Configuration Management

Purpose:
- Load configuration from hierarchical sources
- Support multiple environments (dev, prod, staging, etc.)
- Cross-platform path resolution (Linux, macOS, Windows)
- Environment variable overrides
- Secret management (via env vars only)

Key Responsibilities:
- Config file loading (YAML)
- Hierarchical merging
- Cross-platform paths
- Config validation
- Secret access (from env vars)

Philosophy: Everything is a zVaFile (including config!)
"""

import os
from logger import logger
from zCLI.subsystems.zConfig_modules import ZConfigPaths, ConfigLoader
from zCLI.subsystems.zConfig_modules.machine_config import MachineConfig


class ZConfig:
    """
    zConfig - Configuration Management Subsystem
    
    Loads and manages configuration from multiple sources with priority:
    1. Package defaults (embedded in package)
    2. Environment-specific config (dev/prod/staging)
    3. System config (OS-specific, requires admin)
    4. User config (OS-specific, per-user)
    5. Project config (current directory)
    6. Environment variables (highest priority)
    
    Cross-platform Support:
    - Linux: Uses /etc and XDG paths
    - macOS: Uses /Library and ~/Library paths  
    - Windows: Uses ProgramData and AppData paths
    
    Security:
    - Configuration files contain NO secrets
    - Secrets loaded from environment variables only
    - Config files can be committed to git safely
    """
    
    def __init__(self, environment=None):
        """
        Initialize zConfig subsystem.
        
        Args:
            environment: Environment name (dev, prod, staging, etc.)
                        If None, auto-detected from machine or ZOLO_ENV
        """
        # Initialize path resolver
        self.paths = ZConfigPaths()
        
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
        """
        Get configuration value by dot-notation path.
        
        Examples:
            config.get("zSocket.network.host")           → "127.0.0.1"
            config.get("zSocket.limits.max_connections") → 100
            config.get("nonexistent.path", "default")    → "default"
        
        Args:
            path: Dot-separated path to config value
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
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
        """
        Get entire configuration section.
        
        Examples:
            config.get_section("zSocket")  → {...}
            config.get_section("zData")    → {...}
        
        Args:
            section: Top-level section name
            
        Returns:
            Section dict or empty dict if not found
        """
        return self.config.get(section, {})
    
    def get_all(self):
        """
        Get complete configuration.
        
        Returns:
            Complete configuration dict
        """
        return self.config.copy()
    
    def get_machine(self, key=None, default=None):
        """
        Get machine configuration value.
        
        Examples:
            config.get_machine("hostname")      → "lfs-prod-01"
            config.get_machine("text_editor")   → "vim"
            config.get_machine()                → {...} (all machine config)
        
        Args:
            key: Machine config key (or None for all)
            default: Default value if key not found
            
        Returns:
            Machine config value or default
        """
        if key is None:
            return self.machine.get_all()
        return self.machine.get(key, default)
    
    # ═══════════════════════════════════════════════════════════
    # Secret Management (Environment Variables Only)
    # ═══════════════════════════════════════════════════════════
    
    def _load_secrets(self):
        """
        Load secrets from environment variables ONLY.
        
        Never loads secrets from config files!
        
        Returns:
            Dict with secret values (or None if not set)
        """
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
        """
        Get secret value from environment variables.
        
        Secrets are NEVER stored in config files!
        
        Examples:
            config.get_secret("db_password")
            config.get_secret("jwt_secret")
        
        Args:
            key: Secret key name
            default: Default value if not set
            
        Returns:
            Secret value or default
        """
        value = self.secrets.get(key, default)
        
        if value is None:
            logger.warning("[zConfig] Secret '%s' not found in environment", key)
        
        return value
    
    def has_secret(self, key):
        """
        Check if secret is available.
        
        Args:
            key: Secret key name
            
        Returns:
            Boolean indicating if secret is set
        """
        return self.secrets.get(key) is not None
    
    # ═══════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════
    
    def get_environment(self):
        """
        Get current environment name.
        
        Returns:
            Environment name (dev, prod, staging, etc.)
        """
        return self.environment
    
    def get_paths_info(self):
        """
        Get path information for debugging.
        
        Returns:
            Dict with all config paths
        """
        return self.paths.get_info()
    
    def get_config_sources(self):
        """
        Get list of config sources that were loaded.
        
        Returns:
            List of source names
        """
        return self.loader.config_sources
    
    def ensure_user_config_dir(self):
        """
        Ensure user config directory exists.
        
        Creates the directory if it doesn't exist.
        
        Returns:
            Path to user config directory
        """
        return self.paths.ensure_user_config_dir()
    
    def print_info(self):
        """Print configuration information for debugging."""
        print("\n" + "=" * 70)
        print("zConfig - Configuration Information")
        print("=" * 70)
        print(f"Environment: {self.environment}")
        print()
        
        print("Machine Information:")
        machine_info = self.machine.get_all()
        for key, value in machine_info.items():
            print(f"  {key}: {value}")
        print()
        
        print("Config Sources (in load order):")
        for source in self.loader.config_sources:
            print(f"  ✓ {source}")
        print()
        
        print("Config Paths:")
        paths_info = self.get_paths_info()
        for key, value in paths_info.items():
            print(f"  {key}: {value}")
        print()
        
        print("Secrets Available:")
        for key in self.secrets:
            status = "✓" if self.secrets[key] else "✗"
            print(f"  {status} {key}")
        print("=" * 70)


# ─────────────────────────────────────────────────────────────
# Backward Compatibility
# ─────────────────────────────────────────────────────────────

_DEFAULT_CONFIG = None


def get_config(environment=None):
    """
    Get global config instance (singleton pattern).
    
    Args:
        environment: Environment name (optional)
        
    Returns:
        ZConfig instance
    """
    global _DEFAULT_CONFIG
    
    if _DEFAULT_CONFIG is None:
        _DEFAULT_CONFIG = ZConfig(environment)
    
    return _DEFAULT_CONFIG

