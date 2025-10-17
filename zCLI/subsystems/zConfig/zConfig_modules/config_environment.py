# zCLI/subsystems/zConfig/zConfig_modules/config_environment.py
"""Environment-level configuration management for deployment and runtime settings."""

from zCLI import os, sys, yaml, Colors
from .helpers import create_default_env_config, load_config_with_override

class EnvironmentConfig:
    """Manages environment-specific settings and deployment configuration."""

    def __init__(self, paths):
        """Initialize environment configuration with paths for resolution."""
        self.paths = paths

        # Detect environment types
        self._detect_environments()

        # Get minimal defaults first
        self.env = self._get_defaults()

        # Load and override from config file (check exists, create if missing)
        load_config_with_override(
            self.paths,
            "zEnv",
            create_default_env_config,
            self.env,
            "EnvironmentConfig"
        )

        print(f"{Colors.CONFIG}[EnvironmentConfig] Ready{Colors.RESET}")

    def _detect_environments(self):
        """Detect virtual environment and system environment."""
        # Detect if running in virtual environment
        self.in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        # Store environment info
        self.venv_path = sys.prefix if self.in_venv else None
        self.system_env = dict(os.environ)

        # Print detection results
        if self.in_venv:
            print(f"{Colors.CONFIG}[EnvironmentConfig] Virtual environment detected: {self.venv_path}{Colors.RESET}")
        else:
            print(f"{Colors.CONFIG}[EnvironmentConfig] Running in system environment{Colors.RESET}")

    def _get_defaults(self):
        """Get minimal hardcoded default environment values (first run fallback)."""
        print(f"{Colors.CONFIG}[EnvironmentConfig] Loading environment defaults...{Colors.RESET}")

        env = {
            # Minimal defaults - comprehensive config is in zConfig.zEnvironment.yaml
            "deployment": os.getenv("ZOLO_DEPLOYMENT") or os.getenv("ZOLO_ENV") or "Debug",
            "role": "development",
        }

        print(
            f"{Colors.CONFIG}[EnvironmentConfig] Environment: "
            f"{env['deployment']} ({env['role']}){Colors.RESET}"
        )

        return env

    def get(self, key, default=None):
        """Get environment config value by key, returning default if not found."""
        return self.env.get(key, default)

    def get_all(self):
        """Get all environment configuration values."""
        return self.env.copy()

    def get_env_var(self, key, default=None):
        """Get environment variable with fallback to default."""
        return self.system_env.get(key, default)

    def is_in_venv(self):
        """Check if running in virtual environment."""
        return self.in_venv

    def get_venv_path(self):
        """Get virtual environment path if running in venv."""
        return self.venv_path

    def save_user_config(self):
        """Save current environment config to user's env.yaml."""
        try:
            path = self.paths.user_zconfigs_dir / "zConfig.env.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)

            content = {"zEnv": self.env}

            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)

            print(f"[EnvironmentConfig] Saved environment config to: {path}")
            return True

        except Exception as e:
            print(f"[EnvironmentConfig] Failed to save environment config: {e}")
            return False
