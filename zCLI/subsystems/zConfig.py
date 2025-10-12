# zCLI/subsystems/zConfig.py — Configuration Management Subsystem
# ───────────────────────────────────────────────────────────────
"""Cross-platform configuration management with hierarchical loading and secret support."""

import os
from logger import Logger
from zCLI.subsystems.zConfig_modules import zConfigPaths, ConfigLoader
from zCLI.subsystems.zConfig_modules.machine_config import MachineConfig

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
