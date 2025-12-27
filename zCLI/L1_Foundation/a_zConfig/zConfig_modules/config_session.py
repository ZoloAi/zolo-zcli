# zCLI/subsystems/zConfig/zConfig_modules/config_session.py
"""
Session Configuration and Management for zCLI.

Manages runtime session creation with three-tier authentication architecture:

1. zSession Auth (Layer 1): Internal zCLI/Zolo users
   - session["zAuth"]["zSession"] contains zCLI user credentials
   - Used for zCLI features, premium plugins, Zolo cloud services
   - Authenticated via zcli.auth.login()

2. Application Auth (Layer 2): External application users
   - session["zAuth"]["applications"] is a dict of app-specific credentials
   - Multiple apps can be authenticated simultaneously (multi-app support!)
   - Used for applications BUILT on zCLI (e.g., eCommerce stores, SaaS apps)
   - Authenticated via zcli.auth.authenticate_app_user(app_name, token, config)
   - Configurable user model (developer defines schema)
   - session["zAuth"]["active_app"] tracks which app is currently focused

3. Dual-Auth (Layer 3): Both contexts active simultaneously
   - session["zAuth"]["active_context"] = "dual"
   - session["zAuth"]["dual_mode"] = True
   - Example: Store owner using zCLI analytics on their store

Session Structure:
    session["session_hash"] = "a1b2c3d4"  # v1.6.0: Cache invalidation token (regenerates on login/logout)
    session["zAuth"] = {
        "zSession": {
            "authenticated": False,
            "id": None,
            "username": None,
            "role": None,
            "api_key": None
        },
        "applications": {  # Multi-app support: dict of app authentications
            "ecommerce_store": {
                "authenticated": True,
                "id": 456,
                "username": "customer_bob",
                "role": "customer",
                "api_key": "store_token_xyz"
            },
            "analytics_dashboard": {
                "authenticated": True,
                "id": 789,
                "username": "analyst_alice",
                "role": "analyst",
                "api_key": "analytics_token_abc"
            }
        },
        "active_app": None,  # Which app is currently focused?
        "active_context": None,  # "zSession", "application", or "dual"
        "dual_mode": False
    }
"""

from zCLI import secrets, Any, Dict, Optional
from zCLI.utils import print_ready_message, validate_zcli_instance
from .helpers.machine_detectors import _safe_getcwd

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[SessionConfig]"
READY_MESSAGE = "zSession Ready"
SUBSYSTEM_NAME = "SessionConfig"

# Colors
COLOR_MAIN = "MAIN"
COLOR_CONFIG = "CONFIG"

# Session ID generation
DEFAULT_SESSION_PREFIX = "zS"
TOKEN_HEX_LENGTH = 4

# Default values
DEFAULT_ZTRACEBACK = False  # Opt-in: Set zTraceback: True in zSpark to enable automatic exception handling
DEFAULT_LOG_LEVEL = "INFO"

# zMode values
ZMODE_TERMINAL = "Terminal"
ZMODE_ZBIFROST = "zBifrost"
VALID_ZMODES = (ZMODE_TERMINAL, ZMODE_ZBIFROST)

# Action routing
ACTION_PLACEHOLDER = "#"  # No-op action for development/testing (placeholder for UI development)

# Environment variables
ENV_VAR_LOGGER = "ZOLO_LOGGER"
ENV_VAR_PATH = "PATH"

# Config keys
CONFIG_KEY_LOGGING = "logging"
CONFIG_KEY_LEVEL = "level"

# ═══════════════════════════════════════════════════════════
# Session Dict Keys (for external consumption)
# ═══════════════════════════════════════════════════════════

SESSION_KEY_ZS_ID = "zS_id"
SESSION_KEY_TITLE = "title"
SESSION_KEY_ZSPACE = "zSpace"
SESSION_KEY_ZVAFOLDER = "zVaFolder"
SESSION_KEY_ZVAFILE = "zVaFile"
SESSION_KEY_ZBLOCK = "zBlock"
SESSION_KEY_ZMODE = "zMode"
SESSION_KEY_ZLOGGER = "zLogger"
SESSION_KEY_LOGGER_PATH = "logger_path"
SESSION_KEY_ZTRACEBACK = "zTraceback"
SESSION_KEY_ZMACHINE = "zMachine"
SESSION_KEY_ZAUTH = "zAuth"
SESSION_KEY_ZCRUMBS = "zCrumbs"
SESSION_KEY_ZCACHE = "zCache"
SESSION_KEY_WIZARD_MODE = "wizard_mode"
SESSION_KEY_ZSPARK = "zSpark"
SESSION_KEY_VIRTUAL_ENV = "virtual_env"
SESSION_KEY_SYSTEM_ENV = "system_env"
SESSION_KEY_LOGGER_INSTANCE = "logger_instance"
SESSION_KEY_ZVARS = "zVars"
SESSION_KEY_ZSHORTCUTS = "zShortcuts"
SESSION_KEY_BROWSER = "browser"
SESSION_KEY_IDE = "ide"
SESSION_KEY_SESSION_HASH = "session_hash"  # v1.6.0: For frontend cache invalidation

# zSpark dict keys
ZSPARK_KEY_TITLE = "title"
ZSPARK_KEY_ZSPACE = "zSpace"
ZSPARK_KEY_ZVAFOLDER = "zVaFolder"
ZSPARK_KEY_ZVAFILE = "zVaFile"
ZSPARK_KEY_ZBLOCK = "zBlock"
ZSPARK_KEY_ZTRACEBACK = "zTraceback"
ZSPARK_KEY_ZMODE = "zMode"
ZSPARK_KEY_LOGGER = "logger"
ZSPARK_KEY_LOGGER_PATH = "logger_path"

# zAuth nested keys (Three-Tier Architecture)
# Top-level context keys
ZAUTH_KEY_ZSESSION = "zSession"
ZAUTH_KEY_APPLICATIONS = "applications"  # Plural for multi-app support!
ZAUTH_KEY_ACTIVE_APP = "active_app"      # Tracks which app is focused
ZAUTH_KEY_ACTIVE_CONTEXT = "active_context"
ZAUTH_KEY_DUAL_MODE = "dual_mode"

# User info keys (used in both zSession and application contexts)
ZAUTH_KEY_AUTHENTICATED = "authenticated"
ZAUTH_KEY_ID = "id"
ZAUTH_KEY_USERNAME = "username"
ZAUTH_KEY_ROLE = "role"
ZAUTH_KEY_API_KEY = "api_key"  # Changed from "API_Key" for consistency

# Context values
CONTEXT_ZSESSION = "zSession"
CONTEXT_APPLICATION = "application"
CONTEXT_DUAL = "dual"

# zCache nested keys
ZCACHE_KEY_SYSTEM = "system_cache"
ZCACHE_KEY_PINNED = "pinned_cache"
ZCACHE_KEY_SCHEMA = "schema_cache"
ZCACHE_KEY_PLUGIN = "plugin_cache"

# wizard_mode nested keys
WIZARD_KEY_ACTIVE = "active"
WIZARD_KEY_LINES = "lines"
WIZARD_KEY_FORMAT = "format"
WIZARD_KEY_TRANSACTION = "transaction"


# ═══════════════════════════════════════════════════════════
# SessionConfig Class
# ═══════════════════════════════════════════════════════════

class SessionConfig:
    """
    Manages runtime session creation and configuration for zCLI.
    
    Creates isolated session instances with machine config, environment settings,
    logger initialization, and zSpark integration for programmatic use.
    """

    def __init__(
        self,
        machine_config: Any,
        environment_config: Any,
        zcli: Any,
        zSpark_obj: Optional[Dict[str, Any]] = None,
        zconfig: Optional[Any] = None
    ) -> None:
        """
        Initialize SessionConfig with machine/environment configs and zCLI instance.
        
        Args:
            machine_config: MachineConfig instance for hardware/OS details
            environment_config: EnvironmentConfig instance for deployment settings
            zcli: zCLI instance (required for validation)
            zSpark_obj: Optional dict for programmatic configuration override
            zconfig: zConfig instance (required for logger creation)
        
        Raises:
            ValueError: If zconfig is None (required for logger initialization)
        """
        validate_zcli_instance(zcli, SUBSYSTEM_NAME, require_session=False)
        if zconfig is None:
            raise ValueError(f"{SUBSYSTEM_NAME} requires a zConfig instance")

        self.machine = machine_config
        self.environment = environment_config
        self.zcli = zcli
        self.zSpark = zSpark_obj
        self.zconfig = zconfig
        self.mycolor = COLOR_MAIN

        # Extract log level for log-aware printing
        from zCLI.utils import get_log_level_from_zspark
        self._log_level = get_log_level_from_zspark(zSpark_obj)

        # Print ready message (deployment-aware)
        print_ready_message(READY_MESSAGE, color=COLOR_CONFIG, is_production=self.environment.is_production(), is_testing=self.environment.is_testing())

    def generate_id(self, prefix: str = DEFAULT_SESSION_PREFIX) -> str:
        """Generate random session ID with prefix (default: 'zS') -> 'zS_a1b2c3d4'."""
        random_hex = secrets.token_hex(TOKEN_HEX_LENGTH)
        return f"{prefix}_{random_hex}"
    
    def _generate_session_hash(self) -> str:
        """
        Generate session hash for frontend cache invalidation (v1.6.0).
        
        This hash changes on every session creation and should be regenerated
        on auth state changes (login/logout) to invalidate frontend caches.
        
        Returns:
            8-character hex hash (e.g., 'a1b2c3d4')
        """
        return secrets.token_hex(4)  # 4 bytes = 8 hex chars
    
    @staticmethod
    def regenerate_session_hash(session: Dict[str, Any]) -> str:
        """
        Regenerate session_hash in existing session (called on login/logout).
        
        This is called by zAuth when authentication state changes to invalidate
        frontend caches. Frontend should detect hash change and clear stale caches.
        
        Args:
            session: zCLI session dict
        
        Returns:
            New session hash (8-character hex)
        
        Usage:
            # In zAuth after login/logout
            new_hash = SessionConfig.regenerate_session_hash(zcli.session)
        """
        new_hash = secrets.token_hex(4)
        session[SESSION_KEY_SESSION_HASH] = new_hash
        return new_hash

    def _get_zSpark_value(self, key: str, default: Any = None) -> Any:
        """
        Safely get value from zSpark dict with type checking.
        
        Args:
            key: The key to retrieve from zSpark dict
            default: Default value if key not found or zSpark is None
        
        Returns:
            Value from zSpark[key] if exists, otherwise default
        """
        if self.zSpark is not None and isinstance(self.zSpark, dict):
            return self.zSpark.get(key, default)
        return default

    def _detect_session_title(self) -> str:
        """
        Detect session title for log file naming.
        
        Priority:
            1. zSpark["title"] - explicit user override
            2. Script filename (sys.argv[0]) - automatic detection
            3. "zcli-interactive" - fallback for REPL/edge cases
        
        Returns:
            Session title string suitable for log filename
        """
        import sys
        from pathlib import Path
        
        # Check for explicit title in zSpark
        explicit_title = self._get_zSpark_value(ZSPARK_KEY_TITLE)
        if explicit_title:
            return str(explicit_title)
        
        # Detect from script filename
        try:
            script_path = sys.argv[0]
            if script_path:
                # Handle different execution modes
                if script_path == "-c":
                    # python -c "code"
                    return "zcli-interactive"
                elif script_path == "-m":
                    # python -m module
                    # Try to get module name from argv[1]
                    if len(sys.argv) > 1:
                        return Path(sys.argv[1]).stem
                    return "zcli-module"
                elif script_path in ("", "-"):
                    # Interactive or stdin
                    return "zcli-interactive"
                else:
                    # Normal script execution
                    return Path(script_path).stem
        except (IndexError, AttributeError):
            pass
        
        # Fallback
        return "zcli-interactive"

    def create_session(self, machine_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create isolated session instance for zCLI with optional machine config.
        
        Builds complete session dict with machine config, environment detection,
        zSpark overrides, and logger initialization. Session dict is the foundation
        for all runtime state in zCLI.
        
        Args:
            machine_config: Optional machine config dict (uses self.machine if None)
        
        Returns:
            Dict containing complete session configuration with all runtime state
        """
        # Use provided machine config or get from machine config instance
        if machine_config is None:
            machine_config = self.machine.get_all()

        # Environment detection priority: zSpark > virtual environment > system environment
        zSpark_value = self.zSpark
        virtual_env = self.environment.get_venv_path() if self.environment.is_in_venv() else None
        system_env = self.environment.get_env_var(ENV_VAR_PATH)

        # Determine zSpace: zSpark > getcwd (safe version handles deleted directories)
        zSpace = self._get_zSpark_value(ZSPARK_KEY_ZSPACE) or _safe_getcwd()

        # Determine zTraceback: zSpark > default (True)
        zTraceback = self._get_zSpark_value(ZSPARK_KEY_ZTRACEBACK, DEFAULT_ZTRACEBACK)

        # Determine session title for log file naming
        session_title = self._detect_session_title()
        
        # Determine logger path for custom log file location
        logger_path = self._detect_logger_path()

        # Create session dict with constants for all keys
        session = {
            SESSION_KEY_ZS_ID: self.generate_id(),
            SESSION_KEY_TITLE: session_title,
            SESSION_KEY_ZSPACE: zSpace,
            SESSION_KEY_ZVAFOLDER: self._get_zSpark_value("zVaFolder"),
            SESSION_KEY_ZVAFILE: self._get_zSpark_value("zVaFile"),
            SESSION_KEY_ZBLOCK: self._get_zSpark_value("zBlock"),
            SESSION_KEY_ZMODE: self.detect_zMode(),
            SESSION_KEY_ZLOGGER: self._detect_logger_level(),
            SESSION_KEY_LOGGER_PATH: logger_path,
            SESSION_KEY_ZTRACEBACK: zTraceback,
            SESSION_KEY_ZMACHINE: machine_config,
            SESSION_KEY_BROWSER: self._get_zSpark_value("browser"),  # Optional override
            SESSION_KEY_IDE: self._get_zSpark_value("ide"),          # Optional override
            SESSION_KEY_SESSION_HASH: self._generate_session_hash(),  # v1.6.0: Cache invalidation token
            SESSION_KEY_ZAUTH: {
                # Three-tier authentication structure with multi-app support
                ZAUTH_KEY_ZSESSION: {
                    ZAUTH_KEY_AUTHENTICATED: False,
                    ZAUTH_KEY_ID: None,
                    ZAUTH_KEY_USERNAME: None,
                    ZAUTH_KEY_ROLE: None,
                    ZAUTH_KEY_API_KEY: None
                },
                ZAUTH_KEY_APPLICATIONS: {},  # Dict of app authentications (multi-app support!)
                ZAUTH_KEY_ACTIVE_APP: None,  # Which app is currently focused?
                ZAUTH_KEY_ACTIVE_CONTEXT: None,  # "zSession", "application", or "dual"
                ZAUTH_KEY_DUAL_MODE: False
            },
            SESSION_KEY_ZCRUMBS: {},
            SESSION_KEY_ZCACHE: {
                ZCACHE_KEY_SYSTEM: {},
                ZCACHE_KEY_PINNED: {},
                ZCACHE_KEY_SCHEMA: {},
                ZCACHE_KEY_PLUGIN: {},
            },
            SESSION_KEY_WIZARD_MODE: {
                WIZARD_KEY_ACTIVE: False,
                WIZARD_KEY_LINES: [],
                WIZARD_KEY_FORMAT: None,
                WIZARD_KEY_TRANSACTION: False
            },
            SESSION_KEY_ZSPARK: zSpark_value,
            SESSION_KEY_VIRTUAL_ENV: virtual_env,
            SESSION_KEY_SYSTEM_ENV: system_env,
            SESSION_KEY_ZVARS: {},
            SESSION_KEY_ZSHORTCUTS: {},
        }

        # Initialize logger now that session is created with zLogger level
        # Use zConfig's create_logger method to avoid late imports
        logger = self.zconfig.create_logger(session)

        # Store logger in session for easy access
        session[SESSION_KEY_LOGGER_INSTANCE] = logger

        return session

    def detect_zMode(self) -> str:
        """
        Detect zMode based on zSpark override, fallback to Terminal.
        
        Returns:
            "Terminal" or "zBifrost" based on zSpark or default
        """
        # Check zSpark for explicit zMode setting (highest priority)
        zMode = self._get_zSpark_value(ZSPARK_KEY_ZMODE)
        if zMode and zMode in VALID_ZMODES:
            return zMode

        # Default to Terminal if no valid zMode specified
        return ZMODE_TERMINAL

    def _detect_logger_level(self) -> str:
        """
        Detect logger level following hierarchy:
        1. zSpark override (if provided) - EXPLICIT user choice
        2. Virtual environment variable
        3. System environment variable
        4. zConfig.zEnvironment.yaml file
        5. Default (deployment-aware: Production→ERROR, Debug/Info→INFO)
        
        Note:
            Production deployment defaults to ERROR logging for minimal output.
            "PROD" log level provides silent console with DEBUG file logging.
        
        Returns:
            Logger level string (e.g., "INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL", "PROD")
        """
        from zCLI.utils import print_if_not_prod
        import warnings
        
        # Track if logger was explicitly set (for smart Production defaults)
        explicit_logger = False
        
        # 1. Check zSpark for logger setting (EXPLICIT override)
        zSpark_logger = self._get_zSpark_value(ZSPARK_KEY_LOGGER)
        if zSpark_logger:
            explicit_logger = True
            level = str(zSpark_logger).upper()
            
            # Only print if not in Production (deployment-aware)
            if not self.environment.is_production():
                print(f"{LOG_PREFIX} Logger level from zSpark: {level}")
            
            return level

        # 2. Check virtual environment variable (if in venv) - EXPLICIT override
        if self.environment.is_in_venv():
            venv_logger = self.environment.get_env_var(ENV_VAR_LOGGER)
            if venv_logger:
                explicit_logger = True
                level = str(venv_logger).upper()
                
                # Only print if not in Production
                if not self.environment.is_production():
                    print(f"{LOG_PREFIX} Logger level from virtual env: {level}")
                return level

        # 3. Check system environment variable - EXPLICIT override
        system_logger = self.environment.get_env_var(ENV_VAR_LOGGER)
        if system_logger:
            explicit_logger = True
            level = str(system_logger).upper()
            
            # Only print if not in Production
            if not self.environment.is_production():
                print(f"{LOG_PREFIX} Logger level from system env: {level}")
            return level

        # 4. Check zConfig.zEnvironment.yaml file (NOT explicit if Production)
        logging_config = self.environment.get(CONFIG_KEY_LOGGING, {})
        if isinstance(logging_config, dict):
            # Check new nested app config structure first
            app_config = logging_config.get("app", {})
            level = app_config.get(CONFIG_KEY_LEVEL, None) if isinstance(app_config, dict) else None
            
            # Backward compatibility: fall back to old logging.level format
            if not level:
                level = logging_config.get(CONFIG_KEY_LEVEL, None)
                if level and not self.environment.is_production():
                    warnings.warn(
                        "logging.level is deprecated. Use logging.app.level instead.",
                        DeprecationWarning,
                        stacklevel=2
                    )
            
            if level:
                # Smart default: If Production deployment and config has INFO (default),
                # treat it as implicit and use ERROR instead for minimal logging
                if self.environment.is_production() and str(level).upper() == "INFO" and not explicit_logger:
                    level = "ERROR"
                    if not self.environment.is_production():
                        print(f"{LOG_PREFIX} Production mode: Logger defaulting to ERROR (override with explicit logger setting)")
                else:
                    # Only print if not in Production
                    if not self.environment.is_production():
                        print(f"{LOG_PREFIX} Logger level from zEnvironment config: {level}")
                
                return level

        # 5. Default fallback (deployment-aware)
        # Production deployment defaults to ERROR, others default to INFO
        if self.environment.is_production():
            default = "ERROR"
            # Silent in Production, no need to print
        else:
            default = DEFAULT_LOG_LEVEL
            print(f"{LOG_PREFIX} Logger level defaulting to: {default}")
        
        return default
    
    def _detect_logger_path(self) -> Optional[str]:
        """
        Detect custom logger path from zSpark (highest priority).
        
        Returns:
            Custom logger path string if provided, None for default system path
        """
        # Check zSpark for logger_path override
        logger_path = self._get_zSpark_value(ZSPARK_KEY_LOGGER_PATH)
        if logger_path:
            # Only print if not in Production
            if not self.environment.is_production():
                print(f"{LOG_PREFIX} Logger path from zSpark: {logger_path}")
            return str(logger_path)
        
        # No custom path specified, return None (use default system path)
        return None
