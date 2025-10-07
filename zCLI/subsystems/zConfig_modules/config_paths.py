# zCLI/subsystems/zConfig_modules/config_paths.py
"""
Cross-platform configuration path resolution.

Uses platformdirs for OS-native paths with dotfile fallback.
"""

import platform
from pathlib import Path
from platformdirs import user_config_dir, site_config_dir, user_data_dir, user_cache_dir
from zCLI.utils.logger import get_logger

logger = get_logger(__name__)


class ZConfigPaths:
    """
    Cross-platform path resolver for zolo-zcli configuration.
    
    Provides OS-native paths for:
    - System configuration (admin/root)
    - User configuration (per-user settings)
    - User data (databases, files)
    - Cache (temporary data)
    
    Platform Support:
    - Linux: Uses XDG Base Directory spec
    - macOS: Uses Apple conventions
    - Windows: Uses AppData conventions
    """
    
    def __init__(self):
        self.app_name = "zolo-zcli"
        self.app_author = "zolo"
        self.os_type = platform.system()  # 'Linux', 'Darwin', 'Windows'
        
        logger.debug("[ZConfigPaths] Initialized for OS: %s", self.os_type)
    
    # ═══════════════════════════════════════════════════════════
    # System Paths (requires admin/root)
    # ═══════════════════════════════════════════════════════════
    
    @property
    def system_config_dir(self):
        r"""
        System-wide configuration directory.
        
        Linux:   /etc/zolo-zcli
        macOS:   /Library/Application Support/zolo-zcli
        Windows: C:\ProgramData\zolo-zcli
        
        Requires: Admin/root permissions to write
        """
        if self.os_type in ("Linux", "Darwin"):
            # Unix-like: prefer /etc for system config
            return Path("/etc/zolo-zcli")
        else:
            # Windows: use platformdirs
            return Path(site_config_dir(self.app_name, self.app_author))
    
    # ═══════════════════════════════════════════════════════════
    # User Paths (per-user, no admin needed)
    # ═══════════════════════════════════════════════════════════
    
    @property
    def user_config_dir_native(self):
        r"""
        User configuration directory (OS-native location).
        
        Linux:   ~/.config/zolo-zcli
        macOS:   ~/Library/Application Support/zolo-zcli
        Windows: %APPDATA%\zolo-zcli
        """
        return Path(user_config_dir(self.app_name, self.app_author))
    
    @property
    def user_config_dir_dotfile(self):
        """
        User configuration directory (dotfile convention).
        
        All OS: ~/.zolo-zcli
        
        Fallback for users who prefer dotfiles.
        """
        return Path.home() / ".zolo-zcli"
    
    @property
    def user_config_dir(self):
        """
        User configuration directory (auto-detect).
        
        Checks both native and dotfile, returns whichever exists.
        Prefers native path for new installations.
        """
        # Check dotfile first (for backward compatibility)
        if self.user_config_dir_dotfile.exists():
            return self.user_config_dir_dotfile
        
        # Use native path (creates if needed)
        return self.user_config_dir_native
    
    @property
    def user_data_dir(self):
        r"""
        User data directory (databases, files).
        
        Linux:   ~/.local/share/zolo-zcli
        macOS:   ~/Library/Application Support/zolo-zcli
        Windows: %LOCALAPPDATA%\zolo-zcli
        """
        return Path(user_data_dir(self.app_name, self.app_author))
    
    @property
    def user_cache_dir(self):
        r"""
        User cache directory (temporary data).
        
        Linux:   ~/.cache/zolo-zcli
        macOS:   ~/Library/Caches/zolo-zcli
        Windows: %LOCALAPPDATA%\zolo-zcli\Cache
        """
        return Path(user_cache_dir(self.app_name, self.app_author))
    
    # ═══════════════════════════════════════════════════════════
    # Project Paths (current working directory)
    # ═══════════════════════════════════════════════════════════
    
    @property
    def project_config_file(self):
        """
        Project-local config file.
        
        All OS: ./config.yaml (current directory)
        """
        return Path.cwd() / "config.yaml"
    
    @property
    def project_config_file_dotfile(self):
        """
        Project-local config file (dotfile style).
        
        All OS: ./.zolo-zcli.yaml (current directory)
        """
        return Path.cwd() / ".zolo-zcli.yaml"
    
    # ═══════════════════════════════════════════════════════════
    # Config File Hierarchy
    # ═══════════════════════════════════════════════════════════
    
    def get_config_file_hierarchy(self):
        """
        Get list of config file paths to check, in priority order.
        
        Returns:
            List of (Path, priority, description) tuples
            
        Priority:
        1 = lowest (system)
        5 = highest (project)
        """
        configs = []
        
        # 1. System config (lowest priority)
        system_config = self.system_config_dir / "config.yaml"
        if system_config.exists():
            configs.append((system_config, 1, "system"))
        
        # 2. User config (native path)
        user_config_native = self.user_config_dir_native / "config.yaml"
        if user_config_native.exists():
            configs.append((user_config_native, 2, "user-native"))
        
        # 3. User config (dotfile path - for backward compat)
        user_config_dotfile = self.user_config_dir_dotfile / "config.yaml"
        if user_config_dotfile.exists():
            configs.append((user_config_dotfile, 3, "user-dotfile"))
        
        # 4. Project config (standard)
        if self.project_config_file.exists():
            configs.append((self.project_config_file, 4, "project"))
        
        # 5. Project config (dotfile - highest priority)
        if self.project_config_file_dotfile.exists():
            configs.append((self.project_config_file_dotfile, 5, "project-dotfile"))
        
        # Sort by priority
        configs.sort(key=lambda x: x[1])
        
        return configs
    
    def ensure_user_config_dir(self):
        """
        Ensure user config directory exists.
        
        Creates the directory if it doesn't exist.
        Uses native path by default.
        """
        config_dir = self.user_config_dir_native
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[ZConfigPaths] Created user config directory: %s", config_dir)
        
        return config_dir
    
    def get_info(self):
        """
        Get path information for debugging.
        
        Returns:
            Dict with all path information
        """
        return {
            "os": self.os_type,
            "system_config": str(self.system_config_dir),
            "user_config_native": str(self.user_config_dir_native),
            "user_config_dotfile": str(self.user_config_dir_dotfile),
            "user_config_active": str(self.user_config_dir),
            "user_data": str(self.user_data_dir),
            "user_cache": str(self.user_cache_dir),
            "project_config": str(self.project_config_file),
            "project_config_dotfile": str(self.project_config_file_dotfile),
        }

