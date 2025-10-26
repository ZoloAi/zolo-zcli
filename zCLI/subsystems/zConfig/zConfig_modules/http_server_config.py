# zCLI/subsystems/zConfig/zConfig_modules/http_server_config.py

"""HTTP Server Configuration Module"""

from typing import Any, Dict


class HTTPServerConfig:
    """
    Configuration for zServer HTTP static file server
    
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
        Initialize HTTP server configuration
        
        Args:
            zspark_obj: zSpark configuration dictionary
            logger: Logger instance
        """
        self.logger = logger
        
        # Get HTTP server config from zSpark
        http_config = zspark_obj.get("http_server", {})
        
        # Set configuration with defaults
        self.host = http_config.get("host", "127.0.0.1")
        self.port = http_config.get("port", 8080)
        self.serve_path = http_config.get("serve_path", ".")
        self.enabled = http_config.get("enabled", False)
        
        # Log configuration
        if self.enabled:
            self.logger.info(f"[HTTPServerConfig] Enabled - {self.host}:{self.port}")
            self.logger.info(f"[HTTPServerConfig] Serve path: {self.serve_path}")
        else:
            self.logger.debug("[HTTPServerConfig] HTTP server disabled")
    
    def __repr__(self) -> str:
        return f"HTTPServerConfig(host={self.host}, port={self.port}, enabled={self.enabled})"

