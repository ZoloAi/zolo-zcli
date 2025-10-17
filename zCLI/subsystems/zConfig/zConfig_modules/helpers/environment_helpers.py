# zCLI/subsystems/zConfig/zConfig_modules/helpers/environment_helpers.py
"""Helper functions for environment configuration."""

from zCLI import Path, Colors

def create_default_env_config(path, _env_data):
    """Create user environment config file on first run with given path and data."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        content = """
# zolo-zcli Environment Configuration
# This file was auto-generated on first run.
# You can edit this file to customize your environment-specific settings.

zEnv:
  # Environment Settings (customize these to your environment!)
  deployment: "Debug"  # Debug, Info, Production
  datacenter: "local"  # local, us-west-2, eu-central-1, etc.
  cluster: "single-node"  # single-node, multi-node, k8s-cluster
  node_id: "node-001"  # unique identifier for this node
  
  # Network Configuration
  network:
    host: "127.0.0.1"  # bind address
    port: 56891  # service port
    external_host: "localhost"  # external access hostname
    external_port: 56891  # external access port
  
  # WebSocket Configuration
  # WebSocket settings hierarchy: zSpark > system env (WEBSOCKET_*) > this file
  websocket:
    host: "127.0.0.1"  # WebSocket bind address (default: localhost for security)
    port: 56891  # WebSocket port
    require_auth: true  # require authentication for WebSocket connections
    allowed_origins: []  # list of allowed origins (empty = localhost only)
    max_connections: 100  # maximum concurrent WebSocket connections
    ping_interval: 20  # ping interval in seconds
    ping_timeout: 10  # ping timeout in seconds
  
  # Security Settings
  security:
    require_auth: true  # require authentication
    allow_anonymous: false  # allow anonymous access
    ssl_enabled: false  # enable SSL/TLS
    ssl_cert_path: ""  # path to SSL certificate
    ssl_key_path: ""  # path to SSL private key
  
  # Logging Configuration
  # Logger level hierarchy: zSpark > virtual env (ZOLO_LOGGER) > system env (ZOLO_LOGGER) > this file
  logging:
    level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: "detailed"  # simple, detailed, json
    file_enabled: true  # enable file logging
    file_path: "./logs/zolo-zcli.log"  # log file path
    max_file_size: "10MB"  # max log file size
    backup_count: 5  # number of backup files
  
  # Performance Settings
  performance:
    max_workers: 4  # max concurrent workers
    cache_size: 1000  # cache size limit
    cache_ttl: 3600  # cache time-to-live (seconds)
    timeout: 30  # default timeout (seconds)
  
  # Custom Fields (add your own as needed)
  # custom_field_1: "value"
  # custom_field_2: 42
  # custom_field_3: ["item1", "item2"]
"""

        Path(path).write_text(content, encoding="utf-8")
        print(f"{Colors.CONFIG}[EnvironmentConfig] Created environment config: {path}{Colors.RESET}")
        print(f"{Colors.CONFIG}[EnvironmentConfig] You can edit this file to customize environment settings{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.ERROR}[EnvironmentConfig] Failed to create environment config: {e}{Colors.RESET}")

