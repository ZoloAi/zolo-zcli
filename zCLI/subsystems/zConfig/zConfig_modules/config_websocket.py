# zCLI/subsystems/zConfig/zConfig_modules/config_websocket.py
"""WebSocket configuration management as part of zConfig."""

from zCLI import Colors, os, Any, Dict, List
from zCLI.utils import print_ready_message, validate_zcli_instance

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[WebSocketConfig]"
SUBSYSTEM_NAME = "WebSocketConfig"
READY_MESSAGE = "WebSocketConfig Ready"

# Config Section
CONFIG_SECTION_KEY = "websocket"

# Environment Variables
ENV_VAR_HOST = "WEBSOCKET_HOST"
ENV_VAR_PORT = "WEBSOCKET_PORT"
ENV_VAR_REQUIRE_AUTH = "WEBSOCKET_REQUIRE_AUTH"
ENV_VAR_ALLOWED_ORIGINS = "WEBSOCKET_ALLOWED_ORIGINS"

# Config Keys
KEY_HOST = "host"
KEY_PORT = "port"
KEY_REQUIRE_AUTH = "require_auth"
KEY_ALLOWED_ORIGINS = "allowed_origins"
KEY_MAX_CONNECTIONS = "max_connections"
KEY_PING_INTERVAL = "ping_interval"
KEY_PING_TIMEOUT = "ping_timeout"

# Default Values
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 56891
DEFAULT_REQUIRE_AUTH = True
DEFAULT_ALLOWED_ORIGINS: List[str] = []
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_PING_INTERVAL = 20
DEFAULT_PING_TIMEOUT = 10

# String Parsing
TRUTHY_VALUES = ("true", "1", "yes")
ORIGINS_DELIMITER = ","

class WebSocketConfig:
    """Manages WebSocket configuration with hierarchical loading."""

    # Type hints for instance attributes
    environment: Any  # EnvironmentConfig
    zcli: Any  # zCLI instance
    config: Dict[str, Any]

    def __init__(self, environment_config: Any, zcli: Any) -> None:
        """
        Initialize WebSocket config with environment config and zcli instance.
        
        Args:
            environment_config: EnvironmentConfig instance with environment settings
            zcli: Main zCLI instance for accessing zSpark and other subsystems
        """
        # Validate required parameters
        validate_zcli_instance(zcli, SUBSYSTEM_NAME, require_session=False)

        self.environment = environment_config
        self.zcli = zcli

        # Get WebSocket configuration from environment (which uses hierarchy)
        self._load_websocket_config()

        # Print ready message (deployment-aware)
        # Use environment.is_production() directly since we have the environment object
        print_ready_message(READY_MESSAGE, color="CONFIG", is_production=self.environment.is_production(), is_testing=self.environment.is_testing())

    def _load_websocket_config(self) -> None:
        """Load WebSocket configuration following hierarchy: zSpark > env > config file > defaults."""

        # Get base config from environment
        websocket_config: Dict[str, Any] = self.environment.get(CONFIG_SECTION_KEY, {})

        # 1. Check zSpark_obj for WebSocket settings (highest priority)
        if self.zcli.zspark_obj:
            zspark_ws = self.zcli.zspark_obj.get(CONFIG_SECTION_KEY, {})
            if zspark_ws:
                print(f"{LOG_PREFIX} WebSocket settings from zSpark: {list(zspark_ws.keys())}")
                websocket_config.update(zspark_ws)

        # 2. Check environment variables (second priority)
        env_host = os.getenv(ENV_VAR_HOST)
        env_port = os.getenv(ENV_VAR_PORT)
        env_auth = os.getenv(ENV_VAR_REQUIRE_AUTH)
        env_origins = os.getenv(ENV_VAR_ALLOWED_ORIGINS)

        if env_host:
            websocket_config[KEY_HOST] = env_host
            print(f"{LOG_PREFIX} WebSocket host from env: {env_host}")

        if env_port:
            try:
                websocket_config[KEY_PORT] = int(env_port)
                print(f"{LOG_PREFIX} WebSocket port from env: {env_port}")
            except ValueError:
                print(f"{Colors.WARNING}{LOG_PREFIX} Invalid {ENV_VAR_PORT}: {env_port}{Colors.RESET}")

        if env_auth:
            websocket_config[KEY_REQUIRE_AUTH] = env_auth.lower() in TRUTHY_VALUES
            print(f"{LOG_PREFIX} WebSocket auth from env: {websocket_config[KEY_REQUIRE_AUTH]}")

        if env_origins:
            origins_list = [origin.strip() for origin in env_origins.split(ORIGINS_DELIMITER) if origin.strip()]
            websocket_config[KEY_ALLOWED_ORIGINS] = origins_list
            print(f"{LOG_PREFIX} WebSocket origins from env: {origins_list}")

        # 3. Apply defaults for any missing values
        self.config = {
            KEY_HOST: websocket_config.get(KEY_HOST, DEFAULT_HOST),
            KEY_PORT: websocket_config.get(KEY_PORT, DEFAULT_PORT),
            KEY_REQUIRE_AUTH: websocket_config.get(KEY_REQUIRE_AUTH, DEFAULT_REQUIRE_AUTH),
            KEY_ALLOWED_ORIGINS: websocket_config.get(KEY_ALLOWED_ORIGINS, DEFAULT_ALLOWED_ORIGINS),
            KEY_MAX_CONNECTIONS: websocket_config.get(KEY_MAX_CONNECTIONS, DEFAULT_MAX_CONNECTIONS),
            KEY_PING_INTERVAL: websocket_config.get(KEY_PING_INTERVAL, DEFAULT_PING_INTERVAL),
            KEY_PING_TIMEOUT: websocket_config.get(KEY_PING_TIMEOUT, DEFAULT_PING_TIMEOUT),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get WebSocket config value by key."""
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get complete WebSocket configuration."""
        return self.config.copy()

    def update(self, key: str, value: Any) -> None:
        """Update WebSocket config value (runtime only)."""
        self.config[key] = value

    # ═══════════════════════════════════════════════════════════
    # Convenience Properties
    # ═══════════════════════════════════════════════════════════

    @property
    def host(self) -> str:
        """WebSocket bind address."""
        return self.config[KEY_HOST]

    @property
    def port(self) -> int:
        """WebSocket port."""
        return self.config[KEY_PORT]

    @property
    def require_auth(self) -> bool:
        """Whether authentication is required."""
        return self.config[KEY_REQUIRE_AUTH]

    @property
    def allowed_origins(self) -> List[str]:
        """List of allowed origins."""
        return self.config[KEY_ALLOWED_ORIGINS]

    @property
    def max_connections(self) -> int:
        """Maximum concurrent connections."""
        return self.config[KEY_MAX_CONNECTIONS]

    @property
    def ping_interval(self) -> int:
        """Ping interval in seconds."""
        return self.config[KEY_PING_INTERVAL]

    @property
    def ping_timeout(self) -> int:
        """Ping timeout in seconds."""
        return self.config[KEY_PING_TIMEOUT]
