# zCLI/subsystems/zConfig/zConfig_modules/config_validator.py

"""
Configuration Validator - Fail Fast on Invalid Config
======================================================

Validates zSpark_obj configuration before initializing subsystems.
If anything is wrong, fails immediately with clear error messages.

Week 1.1 - Layer 0: Foundation
"""

from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigValidationError(Exception):
    """Raised when zSpark_obj configuration is invalid"""
    pass


class ConfigValidator:
    """
    Validates zSpark_obj configuration dictionary.
    
    Validates:
    - zWorkspace: Path exists and is directory
    - zMode: Must be "Terminal" or "zBifrost"
    - websocket: Port, host, require_auth types
    - http_server: Port, host, serve_path, enabled types
    - Port conflicts: websocket and http_server can't use same port
    
    Usage:
        validator = ConfigValidator(zspark_obj, logger)
        validator.validate()  # Raises ConfigValidationError if invalid
    """
    
    VALID_MODES = ["Terminal", "zBifrost"]
    
    def __init__(self, zspark_obj: Dict[str, Any], logger=None):
        """
        Initialize validator.
        
        Args:
            zspark_obj: Configuration dictionary to validate
            logger: Optional logger instance (if None, validation happens before logger exists)
        """
        self.config = zspark_obj or {}
        self.logger = logger
        self.errors: List[str] = []
    
    def validate(self) -> None:
        """
        Run all validations.
        
        Raises:
            ConfigValidationError: If any validation fails
        """
        # Run all validation checks
        self._validate_workspace()
        self._validate_mode()
        self._validate_websocket()
        self._validate_http_server()
        self._validate_port_conflicts()
        self._validate_plugins()
        
        # If any errors, raise with all messages
        if self.errors:
            error_msg = "\n❌ Invalid zSpark configuration:\n\n"
            for i, error in enumerate(self.errors, 1):
                error_msg += f"  {i}. {error}\n"
            error_msg += "\n💡 Fix the above issues and try again.\n"
            raise ConfigValidationError(error_msg)
    
    def _validate_workspace(self) -> None:
        """Validate zWorkspace path"""
        workspace = self.config.get("zWorkspace")
        
        # Optional, but if provided must be valid
        if workspace is None:
            return
        
        # Must be string
        if not isinstance(workspace, str):
            self.errors.append(
                f"zWorkspace: Must be string, got {type(workspace).__name__}"
            )
            return
        
        # Path must exist
        path = Path(workspace).expanduser()
        if not path.exists():
            self.errors.append(
                f"zWorkspace: Path '{workspace}' does not exist"
            )
            return
        
        # Must be directory
        if not path.is_dir():
            self.errors.append(
                f"zWorkspace: '{workspace}' is not a directory"
            )
    
    def _validate_mode(self) -> None:
        """Validate zMode"""
        mode = self.config.get("zMode")
        
        if mode is None:
            return  # Optional, defaults to "Terminal"
        
        # Must be string
        if not isinstance(mode, str):
            self.errors.append(
                f"zMode: Must be string, got {type(mode).__name__}"
            )
            return
        
        # Must be valid mode
        if mode not in self.VALID_MODES:
            self.errors.append(
                f"zMode: Must be one of {self.VALID_MODES}, got '{mode}' "
                f"(case-sensitive)"
            )
    
    def _validate_websocket(self) -> None:
        """Validate websocket configuration"""
        ws_config = self.config.get("websocket")
        
        if ws_config is None:
            return  # Optional
        
        # Must be dict
        if not isinstance(ws_config, dict):
            self.errors.append(
                f"websocket: Must be dict, got {type(ws_config).__name__}"
            )
            return
        
        # Validate port
        self._validate_port(ws_config, "websocket")
        
        # Validate host
        host = ws_config.get("host")
        if host is not None and not isinstance(host, str):
            self.errors.append(
                f"websocket.host: Must be string, got {type(host).__name__}"
            )
        
        # Validate require_auth
        auth = ws_config.get("require_auth")
        if auth is not None and not isinstance(auth, bool):
            self.errors.append(
                f"websocket.require_auth: Must be boolean, got {type(auth).__name__}"
            )
        
        # Validate allowed_origins
        origins = ws_config.get("allowed_origins")
        if origins is not None:
            if not isinstance(origins, list):
                self.errors.append(
                    f"websocket.allowed_origins: Must be list, got {type(origins).__name__}"
                )
            elif not all(isinstance(o, str) for o in origins):
                self.errors.append(
                    "websocket.allowed_origins: All items must be strings"
                )
    
    def _validate_http_server(self) -> None:
        """Validate http_server configuration"""
        http_config = self.config.get("http_server")
        
        if http_config is None:
            return  # Optional
        
        # Must be dict
        if not isinstance(http_config, dict):
            self.errors.append(
                f"http_server: Must be dict, got {type(http_config).__name__}"
            )
            return
        
        # Validate port
        self._validate_port(http_config, "http_server")
        
        # Validate host
        host = http_config.get("host")
        if host is not None and not isinstance(host, str):
            self.errors.append(
                f"http_server.host: Must be string, got {type(host).__name__}"
            )
        
        # Validate serve_path
        serve_path = http_config.get("serve_path")
        if serve_path is not None:
            if not isinstance(serve_path, str):
                self.errors.append(
                    f"http_server.serve_path: Must be string, got {type(serve_path).__name__}"
                )
            else:
                path = Path(serve_path).expanduser()
                if not path.exists():
                    self.errors.append(
                        f"http_server.serve_path: Path '{serve_path}' does not exist"
                    )
        
        # Validate enabled
        enabled = http_config.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            self.errors.append(
                f"http_server.enabled: Must be boolean, got {type(enabled).__name__}"
            )
    
    def _validate_port(self, config: Dict[str, Any], prefix: str) -> None:
        """
        Validate port number in a config dict.
        
        Args:
            config: Dict containing 'port' key
            prefix: Config section name (e.g., "websocket", "http_server")
        """
        port = config.get("port")
        
        if port is None:
            return  # Optional, has defaults
        
        # Must be integer
        if not isinstance(port, int):
            self.errors.append(
                f"{prefix}.port: Must be integer, got {type(port).__name__} "
                f"(hint: use {port} not '{port}')"
            )
            return
        
        # Must be in valid range
        if not (1 <= port <= 65535):
            self.errors.append(
                f"{prefix}.port: Must be 1-65535, got {port}"
            )
    
    def _validate_port_conflicts(self) -> None:
        """Ensure websocket and http_server don't use same port"""
        ws_config = self.config.get("websocket", {})
        http_config = self.config.get("http_server", {})
        
        # Skip if either is not a dict (already reported error)
        if not isinstance(ws_config, dict) or not isinstance(http_config, dict):
            return
        
        ws_port = ws_config.get("port")
        http_port = http_config.get("port")
        
        # Skip if either is None or invalid type (already reported error)
        if ws_port is None or http_port is None:
            return
        if not isinstance(ws_port, int) or not isinstance(http_port, int):
            return
        
        # Check for conflict
        if ws_port == http_port:
            self.errors.append(
                f"Port conflict: websocket and http_server both configured to use "
                f"port {ws_port}. They must use different ports."
            )
    
    def _validate_plugins(self) -> None:
        """Validate plugins configuration"""
        plugins = self.config.get("plugins")
        
        if plugins is None:
            return  # Optional
        
        # Can be string or list
        if isinstance(plugins, str):
            return  # Single plugin path is OK
        
        if isinstance(plugins, list):
            # All items must be strings
            if not all(isinstance(p, str) for p in plugins):
                self.errors.append(
                    "plugins: All items must be strings (file paths or module names)"
                )
        else:
            self.errors.append(
                f"plugins: Must be string or list, got {type(plugins).__name__}"
            )

