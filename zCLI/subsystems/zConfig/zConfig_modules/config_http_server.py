# zCLI/subsystems/zConfig/zConfig_modules/config_http_server.py
"""HTTP Server Configuration Module"""

from zCLI import Any, Dict, Optional, os
from zCLI.utils import print_ready_message

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[HttpServerConfig]"
SUBSYSTEM_NAME = "HttpServerConfig"
READY_MESSAGE = "zServer Ready"

# Config Section (v1.5.7: Renamed from 'http_server' to match subsystem name)
CONFIG_SECTION_KEY = "zServer"  # Supports both http.server (Dev) and WSGI/Gunicorn (Prod)

# Config Keys
KEY_HOST = "host"
KEY_PORT = "port"
KEY_SERVE_PATH = "serve_path"
KEY_ROUTES_FILE = "routes_file"
KEY_ENABLED = "enabled"
KEY_ZSHELL = "zShell"  # v1.5.8: Drop into zShell REPL (default: False = silent blocking)

# Default Values
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
DEFAULT_SERVE_PATH = "."
DEFAULT_ROUTES_FILE = None
DEFAULT_ENABLED = False
DEFAULT_ZSHELL = False  # v1.5.8: Default to silent blocking (standard server behavior)
DEFAULT_SSL_ENABLED = False  # v1.5.10: SSL disabled by default for local development
DEFAULT_SSL_CERT = None
DEFAULT_SSL_KEY = None

# Environment Variables
ENV_VAR_HTTP_SSL_ENABLED = "HTTP_SSL_ENABLED"
ENV_VAR_HTTP_SSL_CERT = "HTTP_SSL_CERT"
ENV_VAR_HTTP_SSL_KEY = "HTTP_SSL_KEY"

# Truthy values for boolean environment variables
TRUTHY_VALUES = {'true', '1', 'yes', 'on'}


class HttpServerConfig:
    """
    Configuration for zServer (HTTP + WSGI/Gunicorn deployment).
    
    Manages zServer settings from zSpark configuration with sensible defaults.
    Supports both Development (http.server) and Production (Gunicorn/WSGI) modes.
    
    Configuration Key: 'zServer' (backward compatible with 'http_server')
    
    Attributes:
        host: Server host address
        port: Server port
        serve_path: Directory to serve files from
        routes_file: Optional routes configuration file (auto-detected if not specified)
        enabled: Whether zServer is enabled (if True, server ALWAYS waits)
        zShell: Whether to drop into zShell REPL (False = silent blocking)
    """
    
    # Type hints for instance attributes
    logger: Any
    host: str
    port: int
    serve_path: str
    routes_file: Optional[str]
    enabled: bool
    zShell: bool  # v1.5.8: Drop into zShell REPL (default: False)
    ssl_enabled: bool  # v1.5.10: HTTPS support
    ssl_cert: Optional[str]  # v1.5.10: SSL certificate path
    ssl_key: Optional[str]  # v1.5.10: SSL key path
    
    def __init__(self, zspark_obj: Dict[str, Any], logger: Any) -> None:
        """
        Initialize zServer configuration.
        
        Args:
            zspark_obj: zSpark configuration dictionary (looks for 'zServer' key)
            logger: Logger instance for configuration logging
        """
        self.logger = logger
        
        # Get zServer config from zSpark (v1.5.7: Supports 'zServer' key, backward compatible with 'http_server')
        http_config = zspark_obj.get(CONFIG_SECTION_KEY, {})
        
        # Backward compatibility: Check for old 'http_server' key if 'zServer' not found
        if not http_config and "http_server" in zspark_obj:
            http_config = zspark_obj.get("http_server", {})
            self.logger.framework.debug("[HttpServerConfig] Using deprecated 'http_server' key (use 'zServer' instead)")
        
        # Set configuration with defaults
        self.host = http_config.get(KEY_HOST, DEFAULT_HOST)
        self.port = http_config.get(KEY_PORT, DEFAULT_PORT)
        self.serve_path = http_config.get(KEY_SERVE_PATH, DEFAULT_SERVE_PATH)
        self.routes_file = http_config.get(KEY_ROUTES_FILE, DEFAULT_ROUTES_FILE)
        self.enabled = http_config.get(KEY_ENABLED, DEFAULT_ENABLED)
        self.zShell = http_config.get(KEY_ZSHELL, DEFAULT_ZSHELL)  # v1.5.8: Interactive mode
        
        # SSL Configuration (v1.5.10: HTTPS support with deployment-aware defaults)
        # Environment variables from .zEnv (base or deployment-specific)
        env_ssl_enabled = os.getenv(ENV_VAR_HTTP_SSL_ENABLED)
        env_ssl_cert = os.getenv(ENV_VAR_HTTP_SSL_CERT)
        env_ssl_key = os.getenv(ENV_VAR_HTTP_SSL_KEY)
        
        # Check deployment mode from zSpark (determines auto-SSL behavior)
        deployment = None
        for key in ["deployment", "Deployment", "DEPLOYMENT"]:
            if key in zspark_obj:
                deployment = str(zspark_obj[key])
                break
        
        # If not in zSpark, check env (from .zEnv)
        if not deployment:
            deployment = os.getenv('DEPLOYMENT', 'Development')
        
        is_production = deployment.lower() == 'production'
        
        # Deployment-aware SSL defaults (v1.5.10):
        # - Explicit env var (HTTP_SSL_ENABLED) → highest priority
        # - Production + certs present → auto-enable HTTPS
        # - Development or no certs → disable HTTPS
        if env_ssl_enabled is not None:
            # Explicit env var takes precedence
            self.ssl_enabled = env_ssl_enabled.lower() in TRUTHY_VALUES
        elif is_production and env_ssl_cert and env_ssl_key:
            # Production + certs present = auto-enable SSL
            self.ssl_enabled = True
            self.logger.framework.debug(
                f"{LOG_PREFIX} Production mode: SSL auto-enabled (certs detected)"
            )
        else:
            # Development or no certs = disable SSL
            self.ssl_enabled = DEFAULT_SSL_ENABLED
        
        self.ssl_cert = env_ssl_cert if env_ssl_cert else DEFAULT_SSL_CERT
        self.ssl_key = env_ssl_key if env_ssl_key else DEFAULT_SSL_KEY
        
        if self.ssl_enabled:
            self.logger.framework.debug(f"{LOG_PREFIX} SSL enabled: {self.ssl_enabled}")
            if self.ssl_cert:
                self.logger.framework.debug(f"{LOG_PREFIX} SSL cert: {self.ssl_cert}")
            if self.ssl_key:
                self.logger.framework.debug(f"{LOG_PREFIX} SSL key: {self.ssl_key}")
        
        # Log configuration
        if self.enabled:
            self.logger.info(f"{LOG_PREFIX} Enabled - {self.host}:{self.port}")
            self.logger.info(f"{LOG_PREFIX} Serve path: {self.serve_path}")
            if self.routes_file:
                self.logger.info(f"{LOG_PREFIX} Routes file: {self.routes_file}")
        else:
            self.logger.framework.debug(f"{LOG_PREFIX} HTTP server disabled")
        
        # Check production mode for banner suppression (zSpark Layer 5)
        is_production = False
        if zspark_obj and isinstance(zspark_obj, dict):
            for key in ["deployment", "Deployment", "DEPLOYMENT"]:
                if key in zspark_obj:
                    is_production = str(zspark_obj[key]).lower() == "production"
                    break
        
        # Print ready message (deployment-aware)
        # Also check for Testing mode (use zspark_obj to check early, before full init)
        is_testing = False
        if zspark_obj and isinstance(zspark_obj, dict):
            deployment = str(zspark_obj.get('deployment', '')).lower()
            is_testing = deployment in ['testing', 'info']
        print_ready_message(READY_MESSAGE, color="CONFIG", is_production=is_production, is_testing=is_testing)
    
    def __repr__(self) -> str:
        """Return string representation of HttpServerConfig instance."""
        return f"HttpServerConfig(host={self.host}, port={self.port}, enabled={self.enabled})"

