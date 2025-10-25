# zCLI/subsystems/zConfig/zConfig_modules/config_paths.py
"""Cross-platform configuration path resolution with platformdirs."""

from zCLI import platform, Path, sys, Colors, platformdirs, load_dotenv

class zConfigPaths:
    """Cross-platform path resolver for zolo-zcli configuration using native OS conventions."""

    def __init__(self, zSpark_obj=None):
        self.app_name = "zolo-zcli"
        self.app_author = "zolo"
        self.os_type = platform.system()  # 'Linux', 'Darwin', 'Windows'
        self.zSpark = zSpark_obj if isinstance(zSpark_obj, dict) else None

        # Validate OS type
        valid_os_types = ("Linux", "Darwin", "Windows")
        if self.os_type not in valid_os_types:
            print(f"{Colors.ERROR}[zConfigPaths] ERROR: Unsupported OS type '{self.os_type}'{Colors.RESET}")
            print(f"{Colors.WARNING}[zConfigPaths] Supported OS types: {', '.join(valid_os_types)}{Colors.RESET}")
            print(f"{Colors.WARNING}[zConfigPaths] Please report this issue or add support for your OS{Colors.RESET}")
            sys.exit(1)

        print(f"[zConfigPaths] Initialized for OS: {self.os_type}")

        # Detect workspace and dotenv path early for reuse across modules
        self.workspace_dir = self._detect_workspace_dir()
        self._dotenv_path = self._detect_dotenv_file()

        if self.workspace_dir:
            print(f"[zConfigPaths] Workspace directory: {self.workspace_dir}")
        if self._dotenv_path:
            print(f"[zConfigPaths] Dotenv path resolved: {self._dotenv_path}")

    # ═══════════════════════════════════════════════════════════
    # Workspace & dotenv detection helpers
    # ═══════════════════════════════════════════════════════════

    def _detect_workspace_dir(self):
        """Determine workspace directory using zSpark hint or current directory."""
        if self.zSpark:
            workspace = self.zSpark.get("zWorkspace")
            if workspace:
                try:
                    return Path(workspace).expanduser().resolve()
                except Exception:  # pragma: no cover - defensive fallback
                    print(
                        f"{Colors.WARNING}[zConfigPaths] Unable to resolve zWorkspace '{workspace}',"
                        f" defaulting to current directory{Colors.RESET}"
                    )

        try:
            return Path.cwd()
        except Exception:  # pragma: no cover - defensive fallback
            return Path.home()

    def _resolve_explicit_dotenv_path(self):
        """Check zSpark configuration for explicitly provided dotenv path."""
        if not self.zSpark:
            return None

        dotenv_keys = (
            "env_file",
            "envFile",
            "dotenv",
            "dotenv_file",
            "dotenvFile",
            "dotenv_path",
            "dotenvPath",
        )

        for key in dotenv_keys:
            candidate = self.zSpark.get(key)
            if candidate:
                try:
                    return Path(candidate).expanduser().resolve()
                except Exception:  # pragma: no cover - defensive fallback
                    print(
                        f"{Colors.WARNING}[zConfigPaths] Invalid dotenv path '{candidate}' from zSpark key '{key}'{Colors.RESET}"
                    )
        return None

    def _detect_dotenv_file(self):
        """Determine dotenv file location from zSpark overrides or workspace."""
        explicit = self._resolve_explicit_dotenv_path()
        if explicit:
            return explicit

        if self.workspace_dir:
            return self.workspace_dir / ".env"

        return None

    def get_dotenv_path(self):
        """Return resolved dotenv path (may not exist)."""
        return self._dotenv_path

    def load_dotenv(self, override=True):
        """Load environment variables from resolved dotenv file if available."""
        dotenv_path = self.get_dotenv_path()
        if not dotenv_path:
            print("[zConfigPaths] No dotenv path resolved")
            return None

        if not dotenv_path.exists():
            print(f"{Colors.WARNING}[zConfigPaths] Dotenv file not found at: {dotenv_path}{Colors.RESET}")
            return None

        loaded = load_dotenv(dotenv_path, override=override)
        if loaded:
            print(f"[zConfigPaths] Loaded environment variables from: {dotenv_path}")
        else:
            print(f"{Colors.WARNING}[zConfigPaths] Dotenv file present but no variables loaded: {dotenv_path}{Colors.RESET}")

        return dotenv_path

    # ═══════════════════════════════════════════════════════════
    # Resolves standard OS locations for zolo system folders
    # ═══════════════════════════════════════════════════════════
    @property
    def system_config_dir(self):
        r"""
        System config location (discovery only; not created).
        
        Linux/macOS: /etc/zolo-zcli
        Windows:     C:\\ProgramData\\zolo-zcli
        """
        if self.os_type in ("Linux", "Darwin"):
            # Unix-like systems use /etc for system config
            return Path("/etc/zolo-zcli")

        # Windows: use platformdirs
        return Path(platformdirs.site_config_dir(self.app_name, self.app_author))

    @property
    def user_config_dir(self):
        r"""
        User config location (OS-native).

        Linux:   ~/.config/zolo-zcli
        macOS:   ~/Library/Application Support/zolo-zcli 
        Windows: %APPDATA%\zolo-zcli
        """
        return Path(platformdirs.user_config_dir(self.app_name, self.app_author))

    @property
    def user_config_dir_legacy(self):
        """
        Legacy dotfile configuration directory (backward compatibility).
        
        All OS: ~/.zolo-zcli
        
        Checked for backward compatibility with older installations.
        """
        return Path.home() / ".zolo-zcli"

    @property
    def user_zconfigs_dir(self):
        """
        User zConfigs directory for configuration files.
        
        Location: user_config_dir/zConfigs/
        Contains: zConfig.default.yaml, zConfig.dev.yaml, etc.
        """
        return self.user_config_dir / "zConfigs"

    @property
    def user_data_dir(self):
        r"""
        User data directory (databases, files).
        
        Linux:   ~/.local/share/zolo-zcli
        macOS:   ~/Library/Application Support/zolo-zcli
        Windows: %LOCALAPPDATA%\zolo-zcli
        """
        return Path(platformdirs.user_data_dir(self.app_name, self.app_author))

    @property
    def user_cache_dir(self):
        r"""
        User cache directory (temporary data).
        
        Linux:   ~/.cache/zolo-zcli
        macOS:   ~/Library/Caches/zolo-zcli
        Windows: %LOCALAPPDATA%\zolo-zcli\Cache
        """
        return Path(platformdirs.user_cache_dir(self.app_name, self.app_author))

    @property
    def user_logs_dir(self):
        r"""
        User logs directory for application logs.
        
        Linux:   ~/.local/share/zolo-zcli/logs
        macOS:   ~/Library/Application Support/zolo-zcli/logs
        Windows: %LOCALAPPDATA%\zolo-zcli\logs
        """
        return self.user_data_dir / "logs"

    # ═══════════════════════════════════════════════════════════
    # System Config Files
    # ═══════════════════════════════════════════════════════════

    @property
    def system_config_defaults(self):
        """
        System default configuration file.
        
        Location: system_config_dir/zConfig.defaults.yaml
        Created on first run with base configuration.
        """
        return self.system_config_dir / "zConfig.defaults.yaml"

    @property
    def system_machine_config(self):
        """
        System machine configuration file (zMachine zVaFile).
        
        Location: system_config_dir/zMachine.yaml
        Contains machine identity and capabilities.
        """
        return self.system_config_dir / "zMachine.yaml"

    # ═══════════════════════════════════════════════════════════
    # Config File Hierarchy
    # ═══════════════════════════════════════════════════════════

    def get_config_file_hierarchy(self):
        """
        Get list of config file paths to check, in priority order.
        
        Returns:
            List of (Path, priority, description) tuples
            
        Config Hierarchy (lowest to highest priority):
        1. System defaults (zConfig.defaults.yaml) - Base configuration
        2. User config - Per-user overrides
        3. Environment variables / dotenv - Runtime exports (TODO)
        4. Session runtime - In-memory overrides (handled elsewhere)
        """
        configs = []
        
        # 1. System defaults (lowest priority - base config)
        if self.system_config_defaults.exists():
            configs.append((self.system_config_defaults, 1, "system-defaults"))
        
        # 2. User config (primary native path)
        user_config = self.user_config_dir / "zConfigs" / "zConfig.yaml"
        if user_config.exists():
            configs.append((user_config, 2, "user"))
        
        # 3. User config (legacy dotfile path - backward compat)
        user_config_legacy = self.user_config_dir_legacy / "zConfig.yaml"
        if user_config_legacy.exists():
            configs.append((user_config_legacy, 3, "user-legacy"))
        
        # 4. Environment variables / dotenv (highest priority before runtime overrides)
        dotenv_path = self.get_dotenv_path()
        if dotenv_path:
            if dotenv_path.exists():
                configs.append((dotenv_path, 4, "env-dotenv"))
            else:
                print(
                    f"{Colors.WARNING}[zConfigPaths] Dotenv path resolved but file missing: {dotenv_path}{Colors.RESET}"
                )
        else:
            print("[zConfigPaths] No dotenv path detected for hierarchy")

        # Note: Session runtime overrides (highest priority) are handled
        # in-memory by zSession subsystem, not in this file hierarchy
        
        # Sort by priority
        configs.sort(key=lambda x: x[1])
        
        return configs
    
    def ensure_user_config_dir(self):
        """
        Ensure user config directory exists.
        
        Creates the directory if it doesn't exist.
        """
        config_dir = self.user_config_dir
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
            print(f"[zConfigPaths] Created user config directory: {config_dir}")
        
        return config_dir
    
    def get_info(self):
        """
        Get path information for debugging.
        
        Returns:
            Dict with all path information
        """
        return {
            "os": self.os_type,
            "system_config_dir": str(self.system_config_dir),
            "system_config_defaults": str(self.system_config_defaults),
            "system_machine_config": str(self.system_machine_config),
            "user_config_dir": str(self.user_config_dir),
            "user_config_legacy": str(self.user_config_dir_legacy),
            "user_zconfigs_dir": str(self.user_zconfigs_dir),
            "user_data_dir": str(self.user_data_dir),
            "user_cache_dir": str(self.user_cache_dir),
            "user_logs_dir": str(self.user_logs_dir),
        }

