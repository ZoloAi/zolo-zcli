# zCLI/subsystems/zConfig/zConfig_modules/config_websocket.py
"""WebSocket configuration management as part of zConfig."""

from zCLI import Colors, os

class WebSocketConfig:
    """Manages WebSocket configuration with hierarchical loading."""

    def __init__(self, environment_config, zcli, session_data):
        """Initialize WebSocket config with environment config, zcli instance, and session data."""
        # Validate required parameters
        if zcli is None:
            raise ValueError("zcli parameter is required and cannot be None")
        if session_data is None:
            raise ValueError("session_data parameter is required and cannot be None")

        self.environment = environment_config
        self.zcli = zcli
        self.session_data = session_data
        self.mycolor = "WEBSOCKET"

        # Get WebSocket configuration from environment (which uses hierarchy)
        self._load_websocket_config()

        # Print ready message
        from ..zConfig import zConfig
        zConfig.print_config_ready("WebSocketConfig Ready")

    def _load_websocket_config(self):
        """Load WebSocket configuration following hierarchy: zSpark > env > config file > defaults."""
        
        # Get base config from environment
        websocket_config = self.environment.get("websocket", {})
        
        # 1. Check zSpark_obj for WebSocket settings (highest priority)
        if self.zcli.zspark_obj:
            zspark_ws = self.zcli.zspark_obj.get("websocket", {})
            if zspark_ws:
                print(f"[WebSocketConfig] WebSocket settings from zSpark: {list(zspark_ws.keys())}")
                websocket_config.update(zspark_ws)
        
        # 2. Check environment variables (second priority)
        env_host = os.getenv("WEBSOCKET_HOST")
        env_port = os.getenv("WEBSOCKET_PORT")
        env_auth = os.getenv("WEBSOCKET_REQUIRE_AUTH")
        env_origins = os.getenv("WEBSOCKET_ALLOWED_ORIGINS")
        
        if env_host:
            websocket_config["host"] = env_host
            print(f"[WebSocketConfig] WebSocket host from env: {env_host}")
        
        if env_port:
            try:
                websocket_config["port"] = int(env_port)
                print(f"[WebSocketConfig] WebSocket port from env: {env_port}")
            except ValueError:
                print(f"{Colors.WARNING}[WebSocketConfig] Invalid WEBSOCKET_PORT: {env_port}{Colors.RESET}")
        
        if env_auth:
            websocket_config["require_auth"] = env_auth.lower() in ("true", "1", "yes")
            print(f"[WebSocketConfig] WebSocket auth from env: {websocket_config['require_auth']}")
        
        if env_origins:
            origins_list = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
            websocket_config["allowed_origins"] = origins_list
            print(f"[WebSocketConfig] WebSocket origins from env: {origins_list}")
        
        # 3. Apply defaults for any missing values
        self.config = {
            "host": websocket_config.get("host", "127.0.0.1"),
            "port": websocket_config.get("port", 56891),
            "require_auth": websocket_config.get("require_auth", True),
            "allowed_origins": websocket_config.get("allowed_origins", []),
            "max_connections": websocket_config.get("max_connections", 100),
            "ping_interval": websocket_config.get("ping_interval", 20),
            "ping_timeout": websocket_config.get("ping_timeout", 10),
        }

    def get(self, key, default=None):
        """Get WebSocket config value by key."""
        return self.config.get(key, default)

    def get_all(self):
        """Get complete WebSocket configuration."""
        return self.config.copy()

    def update(self, key, value):
        """Update WebSocket config value (runtime only)."""
        self.config[key] = value

    # ═══════════════════════════════════════════════════════════
    # Convenience Properties
    # ═══════════════════════════════════════════════════════════

    @property
    def host(self):
        """WebSocket bind address."""
        return self.config["host"]

    @property
    def port(self):
        """WebSocket port."""
        return self.config["port"]

    @property
    def require_auth(self):
        """Whether authentication is required."""
        return self.config["require_auth"]

    @property
    def allowed_origins(self):
        """List of allowed origins."""
        return self.config["allowed_origins"]

    @property
    def max_connections(self):
        """Maximum concurrent connections."""
        return self.config["max_connections"]

    @property
    def ping_interval(self):
        """Ping interval in seconds."""
        return self.config["ping_interval"]

    @property
    def ping_timeout(self):
        """Ping timeout in seconds."""
        return self.config["ping_timeout"]
