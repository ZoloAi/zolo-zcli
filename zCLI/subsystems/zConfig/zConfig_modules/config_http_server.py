# zCLI/subsystems/zConfig/zConfig_modules/config_http_server.py
"""HTTP Server Configuration Module"""

from zCLI import Any, Dict
from zCLI.utils import print_ready_message

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[HttpServerConfig]"
SUBSYSTEM_NAME = "HttpServerConfig"
READY_MESSAGE = "HttpServerConfig Ready"

# Config Section
CONFIG_SECTION_KEY = "http_server"

# Config Keys
KEY_HOST = "host"
KEY_PORT = "port"
KEY_SERVE_PATH = "serve_path"
KEY_ENABLED = "enabled"

# Default Values
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
DEFAULT_SERVE_PATH = "."
DEFAULT_ENABLED = False


class HttpServerConfig:
    """
    Configuration for zServer HTTP static file server.
    
    Manages HTTP server settings from zSpark configuration with sensible defaults.
    
    Attributes:
        host: Server host address
        port: Server port
        serve_path: Directory to serve files from
        enabled: Whether HTTP server is enabled
    """
    
    # Type hints for instance attributes
    logger: Any
    host: str
    port: int
    serve_path: str
    enabled: bool
    
    def __init__(self, zspark_obj: Dict[str, Any], logger: Any) -> None:
        """
        Initialize HTTP server configuration.
        
        Args:
            zspark_obj: zSpark configuration dictionary
            logger: Logger instance for configuration logging
        """
        self.logger = logger
        
        # Get HTTP server config from zSpark
        http_config = zspark_obj.get(CONFIG_SECTION_KEY, {})
        
        # Set configuration with defaults
        self.host = http_config.get(KEY_HOST, DEFAULT_HOST)
        self.port = http_config.get(KEY_PORT, DEFAULT_PORT)
        self.serve_path = http_config.get(KEY_SERVE_PATH, DEFAULT_SERVE_PATH)
        self.enabled = http_config.get(KEY_ENABLED, DEFAULT_ENABLED)
        
        # Log configuration
        if self.enabled:
            self.logger.info(f"{LOG_PREFIX} Enabled - {self.host}:{self.port}")
            self.logger.info(f"{LOG_PREFIX} Serve path: {self.serve_path}")
        else:
            self.logger.debug(f"{LOG_PREFIX} HTTP server disabled")
        
        # Print ready message
        print_ready_message(READY_MESSAGE, color="CONFIG")
    
    def __repr__(self) -> str:
        """Return string representation of HttpServerConfig instance."""
        return f"HttpServerConfig(host={self.host}, port={self.port}, enabled={self.enabled})"

