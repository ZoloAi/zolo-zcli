# zCLI/subsystems/zConfig/zConfig_modules/config_websocket.py
"""WebSocket configuration management as part of zConfig."""

from zCLI import Colors, os, Any, Dict, List, Optional
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
ENV_VAR_TOKEN = "WEBSOCKET_TOKEN"
ENV_VAR_SSL_ENABLED = "WEBSOCKET_SSL_ENABLED"
ENV_VAR_SSL_CERT = "WEBSOCKET_SSL_CERT"
ENV_VAR_SSL_KEY = "WEBSOCKET_SSL_KEY"

# Config Keys
KEY_HOST = "host"
KEY_PORT = "port"
KEY_REQUIRE_AUTH = "require_auth"
KEY_ALLOWED_ORIGINS = "allowed_origins"
KEY_TOKEN = "token"
KEY_MAX_CONNECTIONS = "max_connections"
KEY_PING_INTERVAL = "ping_interval"
KEY_PING_TIMEOUT = "ping_timeout"
KEY_SSL_ENABLED = "ssl_enabled"
KEY_SSL_CERT = "ssl_cert"
KEY_SSL_KEY = "ssl_key"

# Default Values
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765  # Standard WebSocket development port (matches zComm primitives)
DEFAULT_REQUIRE_AUTH = False  # Security is opt-in, not opt-out (better UX for beginners)
DEFAULT_ALLOWED_ORIGINS: List[str] = []
DEFAULT_TOKEN = ""  # Empty by default - configure via .zEnv or env vars
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_PING_INTERVAL = 20
DEFAULT_PING_TIMEOUT = 10
DEFAULT_SSL_ENABLED = False  # SSL disabled by default for easier local development
DEFAULT_SSL_CERT = None
DEFAULT_SSL_KEY = None

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

        # 1. Check environment variables (Layer 3/4 - .zEnv or system env)
        env_host = os.getenv(ENV_VAR_HOST)
        env_port = os.getenv(ENV_VAR_PORT)
        env_auth = os.getenv(ENV_VAR_REQUIRE_AUTH)
        env_origins = os.getenv(ENV_VAR_ALLOWED_ORIGINS)
        env_token = os.getenv(ENV_VAR_TOKEN)
        env_ssl_enabled = os.getenv(ENV_VAR_SSL_ENABLED)
        env_ssl_cert = os.getenv(ENV_VAR_SSL_CERT)
        env_ssl_key = os.getenv(ENV_VAR_SSL_KEY)

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

        if env_token:
            websocket_config[KEY_TOKEN] = env_token
            print(f"{LOG_PREFIX} WebSocket token from env: {'*' * len(env_token)}")

        if env_ssl_enabled:
            websocket_config[KEY_SSL_ENABLED] = env_ssl_enabled.lower() in TRUTHY_VALUES
            print(f"{LOG_PREFIX} WebSocket SSL from env: {websocket_config[KEY_SSL_ENABLED]}")

        if env_ssl_cert:
            websocket_config[KEY_SSL_CERT] = env_ssl_cert
            print(f"{LOG_PREFIX} WebSocket SSL cert from env: {env_ssl_cert}")

        if env_ssl_key:
            websocket_config[KEY_SSL_KEY] = env_ssl_key
            print(f"{LOG_PREFIX} WebSocket SSL key from env: {env_ssl_key}")

        # 2. Check zSpark_obj for WebSocket settings (Layer 5 - highest priority, overrides env)
        if self.zcli.zspark_obj:
            zspark_ws = self.zcli.zspark_obj.get(CONFIG_SECTION_KEY, {})
            if zspark_ws:
                print(f"{LOG_PREFIX} WebSocket settings from zSpark: {list(zspark_ws.keys())}")
                websocket_config.update(zspark_ws)  # zSpark overrides everything else

        # 3. Apply defaults for any missing values
        self.config = {
            KEY_HOST: websocket_config.get(KEY_HOST, DEFAULT_HOST),
            KEY_PORT: websocket_config.get(KEY_PORT, DEFAULT_PORT),
            KEY_REQUIRE_AUTH: websocket_config.get(KEY_REQUIRE_AUTH, DEFAULT_REQUIRE_AUTH),
            KEY_ALLOWED_ORIGINS: websocket_config.get(KEY_ALLOWED_ORIGINS, DEFAULT_ALLOWED_ORIGINS),
            KEY_TOKEN: websocket_config.get(KEY_TOKEN, DEFAULT_TOKEN),
            KEY_MAX_CONNECTIONS: websocket_config.get(KEY_MAX_CONNECTIONS, DEFAULT_MAX_CONNECTIONS),
            KEY_PING_INTERVAL: websocket_config.get(KEY_PING_INTERVAL, DEFAULT_PING_INTERVAL),
            KEY_PING_TIMEOUT: websocket_config.get(KEY_PING_TIMEOUT, DEFAULT_PING_TIMEOUT),
            KEY_SSL_ENABLED: websocket_config.get(KEY_SSL_ENABLED, DEFAULT_SSL_ENABLED),
            KEY_SSL_CERT: websocket_config.get(KEY_SSL_CERT, DEFAULT_SSL_CERT),
            KEY_SSL_KEY: websocket_config.get(KEY_SSL_KEY, DEFAULT_SSL_KEY),
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
    def token(self) -> str:
        """Authentication token (from .zEnv or env vars)."""
        return self.config[KEY_TOKEN]

    @property
    def ssl_enabled(self) -> bool:
        """Whether SSL/TLS is enabled for WSS connections."""
        return self.config[KEY_SSL_ENABLED]

    @property
    def ssl_cert(self) -> Optional[str]:
        """Path to SSL certificate file."""
        return self.config[KEY_SSL_CERT]

    @property
    def ssl_key(self) -> Optional[str]:
        """Path to SSL private key file."""
        return self.config[KEY_SSL_KEY]

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
