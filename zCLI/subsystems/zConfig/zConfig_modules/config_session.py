# zCLI/subsystems/zConfig/zConfig_modules/config_session.py
"""Session configuration and management as part of zConfig."""

from zCLI import os, secrets

class SessionConfig:
    """Manages session configuration and creation."""

    def __init__(self, machine_config, environment_config, zcli, zSpark_obj=None, zconfig=None):
        """Initialize session configuration with machine, environment, zCLI, 
        optional zSpark configs, and zConfig instance."""
        if zcli is None:
            raise ValueError("SessionConfig requires a zCLI instance")
        if zconfig is None:
            raise ValueError("SessionConfig requires a zConfig instance")

        self.machine = machine_config
        self.environment = environment_config
        self.zcli = zcli
        self.zSpark = zSpark_obj
        self.zconfig = zconfig
        self.mycolor = "MAIN"

        # Print ready message
        from ..zConfig import zConfig
        zConfig.print_config_ready("SessionConfig Ready")

    def generate_id(self, prefix: str = "zS") -> str:
        """Generate random session ID with prefix (default: 'zS') -> 'zS_a1b2c3d4'."""
        random_hex = secrets.token_hex(4)  # 8 character hex string
        return f"{prefix}_{random_hex}"

    def create_session(self, machine_config=None):
        """
        Create isolated session instance for zCLI with optional machine config.
        Also initializes the logger using the detected logger level.
        """
        # Use provided machine config or get from machine config instance
        if machine_config is None:
            machine_config = self.machine.get_all()

        # Environment detection priority: zSpark > virtual environment > system environment
        zSpark_value = self.zSpark
        virtual_env = self.environment.get_venv_path() if self.environment.is_in_venv() else None
        system_env = self.environment.get_env_var("PATH")

        # Determine zWorkspace: zSpark > getcwd
        zWorkspace = os.getcwd()  # Default to current working directory
        if self.zSpark is not None and isinstance(self.zSpark, dict):
            if "zWorkspace" in self.zSpark:
                zWorkspace = self.zSpark["zWorkspace"]

        # Create session dict
        session = {
            "zS_id": self.generate_id(),
            "zWorkspace": zWorkspace,
            "zVaFile_path": None,
            "zVaFilename": None,
            "zBlock": None,
            "zMode": self.detect_zMode(),
            "zLogger": self._detect_logger_level(),
            "zMachine": machine_config,
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            },
            "zCrumbs": {},
            "zCache": {
                "system_cache": {},
                "pinned_cache": {},
                "schema_cache": {},
            },
            "wizard_mode": {
                "active": False,
                "lines": [],
                "format": None,
                "transaction": False
            },
            "zSpark": zSpark_value,  # 1. zSpark value
            "virtual_env": virtual_env,  # 2. virtual environment
            "system_env": system_env,  # 3. system environment
        }
        
        # Initialize logger now that session is created with zLogger level
        # Use zConfig's create_logger method to avoid late imports
        logger = self.zconfig.create_logger(session)
        
        # Store logger in session for easy access
        session["logger_instance"] = logger
        
        return session

    def detect_zMode(self):
        """Detect zMode based on zSpark_obj zMode setting, fallback to Terminal."""
        # 1. Check zSpark_obj for explicit zMode setting (highest priority)
        if self.zSpark is not None and isinstance(self.zSpark, dict):
            zMode = self.zSpark.get("zMode")
            if zMode and zMode in ("Terminal", "GUI", "WebSocket", "Walker"):
                return zMode
        
        # 2. Default to Terminal if no valid zMode specified
        return "Terminal"

    def _detect_logger_level(self):
        """
        Detect logger level following hierarchy:
        1. zSpark_obj (if provided)
        2. Virtual environment variable
        3. System environment variable
        4. zConfig.zEnvironment.yaml file
        5. Default to INFO
        """
        # 1. Check zSpark_obj for logger setting
        if self.zSpark is not None and isinstance(self.zSpark, dict):
            if "logger" in self.zSpark:
                level = str(self.zSpark["logger"]).upper()
                print(f"[SessionConfig] Logger level from zSpark: {level}")
                return level
        
        # 2. Check virtual environment variable (if in venv)
        if self.environment.is_in_venv():
            venv_logger = self.environment.get_env_var("ZOLO_LOGGER")
            if venv_logger:
                level = str(venv_logger).upper()
                print(f"[SessionConfig] Logger level from virtual env: {level}")
                return level
        
        # 3. Check system environment variable
        system_logger = self.environment.get_env_var("ZOLO_LOGGER")
        if system_logger:
            level = str(system_logger).upper()
            print(f"[SessionConfig] Logger level from system env: {level}")
            return level
        
        # 4. Check zConfig.zEnvironment.yaml file
        logging_config = self.environment.get("logging", {})
        if isinstance(logging_config, dict):
            level = logging_config.get("level", "INFO")
            print(f"[SessionConfig] Logger level from zEnvironment config: {level}")
            return level
        
        # 5. Default fallback
        print("[SessionConfig] Logger level defaulting to: INFO")
        return "INFO"
