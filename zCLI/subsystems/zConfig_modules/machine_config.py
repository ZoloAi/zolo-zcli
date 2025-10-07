# zCLI/subsystems/zConfig_modules/machine_config.py
"""
Machine-level configuration management.

Loaded once and shared across all sessions.
Contains machine identity and user tool preferences.
"""

import os
import platform
import socket
import shutil
import yaml
from pathlib import Path
from logger import logger


class MachineConfig:
    """
    Machine-level configuration.
    
    Contains:
    - Machine identity (hostname, OS, deployment type)
    - User tool preferences (browser, IDE)
    - System capabilities (CPU, memory)
    - Deployment information (datacenter, role, cluster)
    
    Loaded from:
    1. Auto-detection (hardware, OS, defaults)
    2. System config (/etc/zolo-zcli/machine.yaml)
    3. User config (~/.zolo-zcli/machine.yaml)
    
    Created on first run if doesn't exist.
    """
    
    def __init__(self, paths):
        """
        Initialize machine configuration.
        
        Args:
            paths: ZConfigPaths instance for path resolution
        """
        self.paths = paths
        self.machine = {}
        
        # Load machine config
        self._load()
    
    def _load(self):
        """Load machine configuration from hierarchy."""
        
        # 1. Auto-detect machine defaults
        self.machine = self._auto_detect()
        
        # 2. Load system machine config (if exists)
        system_machine = self.paths.system_config_dir / "machine.yaml"
        if system_machine.exists():
            self._merge_from_file(system_machine, "system")
        
        # 3. Load user machine config (if exists, overrides system)
        user_machine = self.paths.user_config_dir / "machine.yaml"
        if user_machine.exists():
            self._merge_from_file(user_machine, "user")
        else:
            # Create user machine config on first run
            self._create_user_machine_config(user_machine)
    
    def _auto_detect(self):
        """
        Auto-detect machine information.
        
        Returns:
            Dict with machine defaults
        """
        logger.debug("[MachineConfig] Auto-detecting machine information...")
        
        machine = {
            # Identity
            "os": platform.system(),                    # Linux, Darwin, Windows
            "os_version": platform.release(),           # Kernel version
            "hostname": socket.gethostname(),           # Machine name
            "architecture": platform.machine(),         # x86_64, arm64, etc.
            "python_version": platform.python_version(), # 3.12.0
            
            # Deployment (auto-detect or default to dev)
            "deployment": os.getenv("ZOLO_DEPLOYMENT", "dev"),
            "role": os.getenv("ZOLO_ROLE", "development"),
            
            # User tools (system defaults, user can override)
            "browser": self._detect_browser(),
            "ide": self._detect_ide(),
            "terminal": os.getenv("TERM", "unknown"),
            "shell": os.getenv("SHELL", "/bin/sh"),
            
            # System capabilities
            "cpu_cores": os.cpu_count() or 1,
            "memory_gb": self._get_memory_gb(),
        }
        
        logger.debug("[MachineConfig] Detected: %s on %s", 
                    machine["hostname"], machine["os"])
        
        return machine
    
    def _detect_browser(self):
        """
        Detect system default browser.
        
        Returns:
            Browser name (or command)
        """
        system = platform.system()
        
        # Check BROWSER env var first
        browser_env = os.getenv("BROWSER")
        if browser_env:
            return browser_env
        
        # macOS: Query LaunchServices for actual default
        if system == "Darwin":
            try:
                import subprocess
                
                # Method 1: Check LaunchServices database for http handler
                result = subprocess.run(
                    ['defaults', 'read', 'com.apple.LaunchServices/com.apple.launchservices.secure', 'LSHandlers'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parse for common browsers
                output_lower = result.stdout.lower()
                browser_mapping = {
                    'google.chrome': 'Chrome',
                    'chrome': 'Chrome',
                    'firefox': 'Firefox',
                    'safari': 'Safari',
                    'arc': 'Arc',
                    'brave': 'Brave',
                    'edge': 'Edge',
                    'opera': 'Opera',
                }
                
                for key, name in browser_mapping.items():
                    if key in output_lower:
                        logger.debug("[MachineConfig] Found default browser via LaunchServices: %s", name)
                        return name
                
            except Exception as e:
                logger.debug("[MachineConfig] Could not query LaunchServices: %s", e)
            
            # Fallback: Safari is macOS default
            return "Safari"
            
        elif system == "Linux":
            # Try xdg-settings first (most reliable on Linux)
            try:
                import subprocess
                result = subprocess.run(
                    ['xdg-settings', 'get', 'default-web-browser'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    browser_desktop = result.stdout.strip()
                    # Convert .desktop file to friendly name
                    if 'firefox' in browser_desktop.lower():
                        return "firefox"
                    elif 'chrome' in browser_desktop.lower():
                        return "google-chrome"
                    elif 'chromium' in browser_desktop.lower():
                        return "chromium"
                    elif 'brave' in browser_desktop.lower():
                        return "brave-browser"
            except Exception:
                pass
            
            # Fallback: Check for common browsers in PATH
            for browser in ["firefox", "google-chrome", "chromium", "brave-browser"]:
                if shutil.which(browser):
                    return browser
            return "firefox"  # Final fallback
            
        elif system == "Windows":
            # TODO: Query Windows registry for default browser
            # For now, fallback to Edge (Windows 10/11 default)
            return "Edge"
        
        return "unknown"
    
    def _detect_ide(self):
        """
        Detect IDE/code editor for all file types.
        
        Priority:
        1. IDE-specific env vars (IDE, VISUAL_EDITOR, EDITOR, VISUAL)
        2. Modern GUI IDEs (cursor, code, fleet, zed)
        3. Classic IDEs (subl, atom, webstorm, pycharm, idea)
        4. macOS: Xcode (xed)
        5. Fallback to simple editors (nano, vim)
        
        Returns:
            IDE command
        """
        # Check IDE/editor env vars
        for var in ["IDE", "VISUAL_EDITOR", "EDITOR", "VISUAL"]:
            ide_env = os.getenv(var)
            if ide_env:
                logger.debug("[MachineConfig] IDE from env var %s: %s", var, ide_env)
                return ide_env
        
        # Check for modern GUI IDEs (prioritized by popularity/modernity)
        modern_ides = [
            "cursor",       # Cursor AI editor (very modern)
            "code",         # VS Code (most popular)
            "fleet",        # JetBrains Fleet (new)
            "zed",          # Zed editor (modern, fast)
        ]
        
        for ide in modern_ides:
            if shutil.which(ide):
                logger.debug("[MachineConfig] Found modern IDE: %s", ide)
                return ide
        
        # Check for classic IDEs
        classic_ides = [
            "subl",         # Sublime Text
            "atom",         # Atom (discontinued but still used)
            "webstorm",     # JetBrains WebStorm
            "pycharm",      # JetBrains PyCharm
            "idea",         # IntelliJ IDEA
        ]
        
        for ide in classic_ides:
            if shutil.which(ide):
                logger.debug("[MachineConfig] Found classic IDE: %s", ide)
                return ide
        
        # macOS-specific: Check for Xcode
        if platform.system() == "Darwin":
            if shutil.which("xed"):  # Xcode command-line tool
                logger.debug("[MachineConfig] Found Xcode (xed)")
                return "xed"
        
        # Fallback to simple editors
        simple_editors = ["nano", "vim", "nvim", "vi"]
        for editor in simple_editors:
            if shutil.which(editor):
                logger.debug("[MachineConfig] Falling back to simple editor: %s", editor)
                return editor
        
        # Final fallback
        logger.debug("[MachineConfig] Using final fallback: nano")
        return "nano"
    
    def _get_memory_gb(self):
        """
        Get system memory in GB.
        
        Returns:
            Memory in GB (int) or None
        """
        try:
            import psutil
            memory_bytes = psutil.virtual_memory().total
            memory_gb = int(memory_bytes / (1024 ** 3))
            return memory_gb
        except ImportError:
            # psutil not installed, try alternative methods
            pass
        
        try:
            # Linux: read from /proc/meminfo
            if platform.system() == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split()[1])
                            return int(kb / (1024 * 1024))
            
            # macOS: use sysctl
            elif platform.system() == "Darwin":
                import subprocess
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                memory_bytes = int(result.stdout.strip())
                return int(memory_bytes / (1024 ** 3))
        except Exception:
            pass
        
        # Couldn't detect
        return None
    
    def _merge_from_file(self, path, source):
        """
        Load and merge machine config from file.
        
        Args:
            path: Path to machine.yaml
            source: Source description for logging
        """
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                
                if data and "zMachine" in data:
                    self.machine.update(data["zMachine"])
                    logger.info("[MachineConfig] Loaded %s machine config: %s", source, path)
        
        except Exception as e:
            logger.warning("[MachineConfig] Failed to load %s machine config: %s", source, e)
    
    def _create_user_machine_config(self, path):
        """
        Create user machine config file on first run.
        
        Args:
            path: Path to create machine.yaml
        """
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create machine.yaml with current detected values
            content = f"""# zolo-zcli Machine Configuration
# This file was auto-generated on first run.
# You can edit this file to customize your tool preferences.

zMachine:
  # Machine Identity (auto-detected, do not edit unless needed)
  os: "{self.machine.get('os')}"
  hostname: "{self.machine.get('hostname')}"
  architecture: "{self.machine.get('architecture')}"
  python_version: "{self.machine.get('python_version')}"
  
  # Deployment Information (edit for your environment)
  deployment: "{self.machine.get('deployment')}"  # dev, prod, staging, lfs
  role: "{self.machine.get('role')}"              # development, production, testing
  
  # Tool Preferences (customize these to your liking!)
  browser: "{self.machine.get('browser')}"          # Chrome, Firefox, Arc, Safari, etc.
  ide: "{self.machine.get('ide')}"                  # cursor, code, subl, etc.
  terminal: "{self.machine.get('terminal')}"        # Terminal emulator
  shell: "{self.machine.get('shell')}"              # bash, zsh, fish, etc.
  
  # System Capabilities (auto-detected)
  cpu_cores: {self.machine.get('cpu_cores', 'null')}
  memory_gb: {self.machine.get('memory_gb', 'null')}
  
  # Custom Fields (add your own as needed)
  # datacenter: "us-west-2"
  # cluster: "lfs-cluster"
  # lfs_node_id: "node-001"
"""
            
            path.write_text(content)
            logger.info("[MachineConfig] Created user machine config: %s", path)
            logger.info("[MachineConfig] You can edit this file to customize tool preferences")
        
        except Exception as e:
            logger.warning("[MachineConfig] Failed to create user machine config: %s", e)
    
    def get(self, key, default=None):
        """
        Get machine config value.
        
        Args:
            key: Config key
            default: Default value if not found
            
        Returns:
            Config value or default
        """
        return self.machine.get(key, default)
    
    def get_all(self):
        """
        Get complete machine configuration.
        
        Returns:
            Machine config dict (copy)
        """
        return self.machine.copy()
    
    def update(self, key, value):
        """
        Update machine config value (runtime only, doesn't persist).
        
        Args:
            key: Config key
            value: New value
        """
        self.machine[key] = value
    
    def save_user_config(self):
        """
        Save current machine config to user's machine.yaml.
        
        Useful for programmatic updates.
        """
        try:
            path = self.paths.user_config_dir / "machine.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)
            
            content = {"zMachine": self.machine}
            
            with open(path, 'w') as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)
            
            logger.info("[MachineConfig] Saved machine config to: %s", path)
            return True
        
        except Exception as e:
            logger.error("[MachineConfig] Failed to save machine config: %s", e)
            return False

