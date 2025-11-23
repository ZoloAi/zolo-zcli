# zCLI/subsystems/zConfig/zConfig_modules/config_environment.py
"""Environment-level configuration management for deployment and runtime settings."""

from zCLI import os, sys, yaml, Any, Dict, Optional
from zCLI.utils import print_ready_message
from .helpers import create_default_env_config, load_config_with_override
from .config_paths import zConfigPaths

# Module constants
LOG_PREFIX = "[EnvironmentConfig]"
READY_MESSAGE = "EnvironmentConfig Ready"
YAML_KEY = "zEnv"
SUBSYSTEM_NAME = "EnvironmentConfig"

# Environment variable names
ENV_VAR_DEPLOYMENT = "ZOLO_DEPLOYMENT"
ENV_VAR_DEPLOYMENT_ALT = "ZOLO_ENV"

# Config keys
KEY_DEPLOYMENT = "deployment"
KEY_ROLE = "role"

# Default values
DEFAULT_DEPLOYMENT = "Debug"
DEFAULT_ROLE = "development"

class EnvironmentConfig:
    """Manages environment-specific settings and deployment configuration."""

    # Type hints for instance attributes
    paths: zConfigPaths
    env: Dict[str, Any]
    in_venv: bool
    venv_path: Optional[str]
    system_env: Dict[str, str]

    def __init__(self, paths: zConfigPaths) -> None:
        """Initialize environment configuration with paths for resolution."""
        self.paths = paths

        # Detect environment types
        self._detect_environments()

        # Get minimal defaults first
        self.env = self._get_defaults()

        # Load and override from config file (check exists, create if missing)
        load_config_with_override(
            self.paths,
            YAML_KEY,
            create_default_env_config,
            self.env,
            self.paths.ZENVIRONMENT_FILENAME,
            SUBSYSTEM_NAME,
            log_level=paths._log_level
        )

        print_ready_message(READY_MESSAGE, color="CONFIG", log_level=paths._log_level)

    def _detect_environments(self) -> None:
        """Detect virtual environment and system environment."""
        from zCLI.utils import print_if_not_prod
        
        # Load dotenv file (if available) before capturing environment snapshot
        dotenv_path = self.paths.load_dotenv()
        if dotenv_path:
            print_if_not_prod(f"{LOG_PREFIX} Dotenv loaded from: {dotenv_path}", self.paths._log_level)

        # Detect if running in virtual environment
        self.in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        # Store environment info
        self.venv_path = sys.prefix if self.in_venv else None
        self.system_env = dict(os.environ)

        # Print detection results
        if self.in_venv:
            print_if_not_prod(f"{LOG_PREFIX} Virtual environment detected: {self.venv_path}", self.paths._log_level)
        else:
            print_if_not_prod(f"{LOG_PREFIX} Running in system environment", self.paths._log_level)

    def _get_defaults(self) -> Dict[str, Any]:
        """Get minimal hardcoded default environment values (first run fallback)."""
        from zCLI.utils import print_if_not_prod
        
        print_if_not_prod(f"{LOG_PREFIX} Loading environment defaults...", self.paths._log_level)

        env = {
            # Minimal defaults - comprehensive config is in zConfig.environment.yaml
            KEY_DEPLOYMENT: os.getenv(ENV_VAR_DEPLOYMENT) or os.getenv(ENV_VAR_DEPLOYMENT_ALT) or DEFAULT_DEPLOYMENT,
            KEY_ROLE: DEFAULT_ROLE,
        }

        print_if_not_prod(f"{LOG_PREFIX} Environment: {env[KEY_DEPLOYMENT]} ({env[KEY_ROLE]})", self.paths._log_level)

        return env

    def get(self, key: str, default: Any = None) -> Any:
        """Get environment config value by key, returning default if not found."""
        return self.env.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all environment configuration values."""
        return self.env.copy()

    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with fallback to default."""
        return self.system_env.get(key, default)

    def is_in_venv(self) -> bool:
        """Check if running in virtual environment."""
        return self.in_venv

    def get_venv_path(self) -> Optional[str]:
        """Get virtual environment path if running in venv."""
        return self.venv_path

    def save_user_config(self) -> bool:
        """Save current environment config to user's zConfig.environment.yaml."""
        try:
            path = self.paths.user_zconfigs_dir / self.paths.ZENVIRONMENT_FILENAME
            path.parent.mkdir(parents=True, exist_ok=True)

            content = {YAML_KEY: self.env}

            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)

            print(f"{LOG_PREFIX} Saved environment config to: {path}")
            return True

        except Exception as e:
            print(f"{LOG_PREFIX} Failed to save environment config: {e}")
            return False
