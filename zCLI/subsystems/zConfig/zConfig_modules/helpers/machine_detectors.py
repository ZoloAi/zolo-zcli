# zCLI/subsystems/zConfig/zConfig_modules/helpers/machine_detectors.py
"""Helper functions for detecting machine capabilities and tools."""

from zCLI import os, platform, shutil, Colors, subprocess, importlib, socket, Path, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════
# Module-Level Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[MachineDetector]"

# Subprocess timeouts
SUBPROCESS_TIMEOUT_SEC = 5

# Memory conversion constants
BYTES_PER_KB = 1024
KB_PER_MB = 1024
MB_PER_GB = 1024
BYTES_PER_GB = 1024 ** 3

# Browser detection
BROWSER_MAPPING = {
    'google.chrome': 'Chrome',
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'arc': 'Arc',
    'brave': 'Brave',
    'edge': 'Edge',
    'opera': 'Opera',
}
LINUX_BROWSERS = ("firefox", "google-chrome", "chromium", "brave-browser")
DEFAULT_MACOS_BROWSER = "Safari"
DEFAULT_LINUX_BROWSER = "firefox"
DEFAULT_WINDOWS_BROWSER = "Edge"

# IDE detection
IDE_ENV_VARS = ("IDE", "VISUAL_EDITOR", "EDITOR", "VISUAL")
MODERN_IDES = ("cursor", "code", "fleet", "zed")
CLASSIC_IDES = ("subl", "atom", "webstorm", "pycharm", "idea")
SIMPLE_EDITORS = ("nano", "vim", "nvim", "vi")
FALLBACK_EDITOR = "nano"

# Linux browser desktop file mapping (for xdg-settings output parsing)
LINUX_BROWSER_DESKTOP_MAP = {
    'firefox': 'firefox',
    'chrome': 'google-chrome',
    'chromium': 'chromium',
    'brave': 'brave-browser',
}

# Default values for environment variables
DEFAULT_SHELL = "/bin/sh"
DEFAULT_TIMEZONE = "system"

# YAML template for machine config file
MACHINE_CONFIG_TEMPLATE = """
# zolo-zcli Machine Configuration
# This file was auto-generated on first run.
# You can edit this file to customize your tool preferences.

zMachine:
  # Machine Identity (auto-detected, do not edit unless needed)
  os: "{os}"
  os_version: "{os_version}"
  os_name: "{os_name}"
  hostname: "{hostname}"
  architecture: "{architecture}"

  # Python Runtime (auto-detected)
  python_version: "{python_version}"
  python_impl: "{python_impl}"
  python_build: "{python_build}"
  python_compiler: "{python_compiler}"
  libc_ver: "{libc_ver}"
  python_executable: "{python_executable}"
  
  # zCLI Installation (auto-detected, useful for troubleshooting)
  zcli_install_path: "{zcli_install_path}"
  zcli_install_type: "{zcli_install_type}"

  # Tool Preferences (customize these to your liking!)
  browser: "{browser}"          # Chrome, Firefox, Arc, Safari, etc.
  ide: "{ide}"                  # cursor, code, subl, etc.
  terminal: "{terminal}"        # Terminal emulator
  shell: "{shell}"              # bash, zsh, fish, etc.
  lang: "{lang}"
  timezone: "{timezone}"

  # Paths (auto-detected)
  home: "{home}"
  cwd: "{cwd}"
  username: "{username}"
  path: "{path}"

  # System Capabilities (auto-detected)
  processor: "{processor}"
  cpu_cores: {cpu_cores}
  memory_gb: {memory_gb}
  
  # Custom Fields (add your own as needed)
  # datacenter: "us-west-2"
  # cluster: "lfs-cluster"
  # lfs_node_id: "node-001"
"""

# ═══════════════════════════════════════════════════════════
# Logging Helpers
# ═══════════════════════════════════════════════════════════

def _log_info(message: str, log_level: Optional[str] = None, is_production: bool = False) -> None:
    """Print info message (suppressed in Production deployment)."""
    if not is_production:
        print(f"{LOG_PREFIX} {message}")

def _log_warning(message: str, log_level: Optional[str] = None, is_production: bool = False) -> None:
    """Print warning message (suppressed in Production deployment)."""
    if not is_production:
        print(f"{Colors.WARNING}{LOG_PREFIX} {message}{Colors.RESET}")

def _log_error(message: str, log_level: Optional[str] = None, is_production: bool = False) -> None:
    """Print error message (always shown, even in Production)."""
    print(f"{Colors.ERROR}{LOG_PREFIX} {message}{Colors.RESET}")

def _log_config(message: str, log_level: Optional[str] = None, is_production: bool = False) -> None:
    """Print config message (suppressed in Production deployment)."""
    if not is_production:
        print(f"{Colors.CONFIG}{LOG_PREFIX} {message}{Colors.RESET}")


def _safe_getcwd() -> str:
    """Get current directory, falling back to home if deleted."""
    try:
        return os.getcwd()
    except (FileNotFoundError, OSError):
        # Directory was deleted (common in tests with temp directories)
        # Fall back to home directory
        return str(Path.home())


def detect_browser(log_level: Optional[str] = None, is_production: bool = False) -> str:
    """Detect default browser via env var or platform-specific methods."""
    browser = os.getenv("BROWSER")  # Check env var first
    if browser:
        return browser

    system = platform.system()
    if system == "Darwin":
        browser = _detect_macos_browser(log_level, is_production)
    elif system == "Linux":
        browser = _detect_linux_browser(log_level, is_production)
    elif system == "Windows":
        browser = DEFAULT_WINDOWS_BROWSER
    else:
        browser = "unknown"

    return browser


def _detect_macos_browser(log_level: Optional[str] = None, is_production: bool = False) -> str:
    """Query macOS LaunchServices for default browser, fallback to Safari."""
    try:
        # Check LaunchServices database for http handler
        result = subprocess.run(
            ['defaults', 'read', 'com.apple.LaunchServices/com.apple.launchservices.secure', 'LSHandlers'],
            capture_output=True, 
            text=True, 
            timeout=SUBPROCESS_TIMEOUT_SEC, 
            check=False
        )

        output_lower = result.stdout.lower()
        for key, name in BROWSER_MAPPING.items():
            if key in output_lower:
                _log_info(f"Found default browser via LaunchServices: {name}", log_level, is_production)
                return name

    except Exception as e:
        _log_warning(f"Could not query LaunchServices: {e}", log_level, is_production)

    return DEFAULT_MACOS_BROWSER

def _detect_linux_browser(log_level: Optional[str] = None, is_production: bool = False) -> str:
    """Query xdg-settings or PATH for default browser, fallback to firefox."""
    # Try xdg-settings first
    try:
        result = subprocess.run(
            ['xdg-settings', 'get', 'default-web-browser'],
            capture_output=True, 
            text=True, 
            timeout=SUBPROCESS_TIMEOUT_SEC, 
            check=False
        )
        if result.returncode == 0:
            browser_desktop = result.stdout.strip().lower()
            for key, browser in LINUX_BROWSER_DESKTOP_MAP.items():
                if key in browser_desktop:
                    return browser
    except Exception:
        pass  # Fall through to PATH check

    # Check PATH for common browsers
    for browser in LINUX_BROWSERS:
        if shutil.which(browser):
            return browser

    return DEFAULT_LINUX_BROWSER

def get_browser_launch_command(browser_name: str) -> tuple:
    """
    Get platform-specific command to launch a browser.
    
    Args:
        browser_name: Browser name (e.g., "Firefox", "Chrome", "firefox", "chrome")
                     Case-insensitive, normalized internally
    
    Returns:
        Tuple of (command, args_template) where:
        - macOS: ("open", ["-a", "Firefox"]) - use 'open -a "App Name"'
        - Linux: ("firefox", []) - direct executable
        - Windows: ("firefox", []) - direct executable  
        - Unknown: (None, []) - browser not mapped
    
    Examples:
        >>> get_browser_launch_command("firefox")
        # macOS: ("open", ["-a", "Firefox"])
        # Linux: ("firefox", [])
        
        >>> get_browser_launch_command("Chrome")
        # macOS: ("open", ["-a", "Google Chrome"])
        # Linux: ("google-chrome", [])
    """
    system = platform.system()
    browser_lower = browser_name.lower()
    
    # macOS: Use 'open -a "App Name"'
    if system == "Darwin":
        macos_apps = {
            "chrome": "Google Chrome",
            "firefox": "Firefox",
            "safari": "Safari",
            "arc": "Arc",
            "brave": "Brave Browser",
            "edge": "Microsoft Edge",
            "opera": "Opera",
        }
        app_name = macos_apps.get(browser_lower)
        if app_name:
            return ("open", ["-a", app_name])
        return (None, [])
    
    # Linux: Direct executable names
    elif system == "Linux":
        linux_commands = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "chromium": "chromium",
            "brave": "brave-browser",
            "edge": "microsoft-edge",
            "opera": "opera",
        }
        cmd = linux_commands.get(browser_lower)
        if cmd and shutil.which(cmd):
            return (cmd, [])
        return (None, [])
    
    # Windows: Direct executable names
    elif system == "Windows":
        windows_commands = {
            "chrome": "chrome",
            "firefox": "firefox",
            "brave": "brave",
            "edge": "msedge",
            "opera": "opera",
        }
        cmd = windows_commands.get(browser_lower)
        if cmd and shutil.which(cmd):
            return (cmd, [])
        return (None, [])
    
    return (None, [])


def get_ide_launch_command(ide_name: str) -> tuple:
    """
    Get platform-specific command to launch an IDE or text editor.
    
    Args:
        ide_name: IDE/editor name (e.g., "Cursor", "code", "cursor", "subl")
                 Case-insensitive, normalized internally
    
    Returns:
        Tuple of (command, args_template) where:
        - macOS GUI IDEs: ("open", ["-a", "Cursor"]) - use 'open -a "App Name"'
        - macOS CLI tools: ("cursor", []) - direct executable
        - Linux: ("cursor", []) - direct executable
        - Windows: ("cursor", []) - direct executable  
        - Unknown: (None, []) - IDE not mapped
    
    Examples:
        >>> get_ide_launch_command("cursor")
        # macOS: ("open", ["-a", "Cursor"])
        # Linux: ("cursor", []) if in PATH
        
        >>> get_ide_launch_command("code")
        # macOS: ("code", []) - VS Code CLI usually in PATH
        # Linux: ("code", [])
    """
    system = platform.system()
    ide_lower = ide_name.lower()
    
    # macOS: GUI apps need 'open -a', CLI tools use direct command
    if system == "Darwin":
        # macOS GUI app mappings (need 'open -a')
        macos_gui_apps = {
            "cursor": "Cursor",
            "subl": "Sublime Text",
            "sublime": "Sublime Text",
            "atom": "Atom",
            "webstorm": "WebStorm",
            "pycharm": "PyCharm",
            "idea": "IntelliJ IDEA",
            "fleet": "Fleet",
            "zed": "Zed",
        }
        
        # Check if it's a GUI app
        app_name = macos_gui_apps.get(ide_lower)
        if app_name:
            return ("open", ["-a", app_name])
        
        # CLI tools that should work directly on macOS (usually in PATH)
        macos_cli_tools = {
            "code": "code",        # VS Code CLI
            "nano": "nano",
            "vim": "vim",
            "nvim": "nvim",
            "vi": "vi",
            "emacs": "emacs",
            "xed": "xed",         # Xcode editor
        }
        
        cmd = macos_cli_tools.get(ide_lower)
        if cmd and shutil.which(cmd):
            return (cmd, [])
        
        return (None, [])
    
    # Linux: Direct executable names
    elif system == "Linux":
        linux_commands = {
            "cursor": "cursor",
            "code": "code",
            "subl": "subl",
            "sublime": "subl",
            "atom": "atom",
            "webstorm": "webstorm",
            "pycharm": "pycharm",
            "idea": "idea",
            "fleet": "fleet",
            "zed": "zed",
            "nano": "nano",
            "vim": "vim",
            "nvim": "nvim",
            "vi": "vi",
            "emacs": "emacs",
        }
        
        cmd = linux_commands.get(ide_lower)
        if cmd and shutil.which(cmd):
            return (cmd, [])
        
        return (None, [])
    
    # Windows: Direct executable names
    elif system == "Windows":
        windows_commands = {
            "cursor": "cursor",
            "code": "code",
            "subl": "subl",
            "sublime": "subl",
            "atom": "atom",
            "webstorm": "webstorm",
            "pycharm": "pycharm",
            "idea": "idea",
            "fleet": "fleet",
            "zed": "zed",
            "nano": "nano",
            "vim": "vim",
            "nvim": "nvim",
            "notepad": "notepad",
        }
        
        cmd = windows_commands.get(ide_lower)
        if cmd and shutil.which(cmd):
            return (cmd, [])
        
        return (None, [])
    
    return (None, [])


def detect_ide(log_level: Optional[str] = None, is_production: bool = False) -> str:
    """Detect IDE/editor via env vars, PATH search (modern→classic→simple), fallback to nano."""
    # Check IDE/editor env vars
    for var in IDE_ENV_VARS:
        ide_env = os.getenv(var)
        if ide_env:
            _log_config(f"IDE from env var {var}: {ide_env}", log_level, is_production)
            return ide_env

    # Check for modern GUI IDEs (prioritized by popularity/modernity)
    for ide in MODERN_IDES:
        if shutil.which(ide):
            _log_info(f"Found modern IDE: {ide}", log_level, is_production)
            return ide

    # Check for classic IDEs
    for ide in CLASSIC_IDES:
        if shutil.which(ide):
            _log_config(f"Found classic IDE: {ide}", log_level, is_production)
            return ide

    # macOS-specific: Check for Xcode
    if platform.system() == "Darwin":
        if shutil.which("xed"):  # Xcode command-line tool
            _log_config("Found Xcode (xed)", log_level, is_production)
            return "xed"

    # Fallback to simple editors
    for editor in SIMPLE_EDITORS:
        if shutil.which(editor):
            _log_config(f"Falling back to simple editor: {editor}", log_level, is_production)
            return editor

    # Final fallback
    _log_config(f"Using final fallback: {FALLBACK_EDITOR}", is_production=is_production)
    return FALLBACK_EDITOR

def detect_memory_gb() -> Optional[int]:
    """Detect system memory in GB via psutil or platform-specific methods."""
    # Try psutil first (most reliable, cross-platform)
    try:
        psutil = importlib.import_module("psutil")
        memory_bytes = psutil.virtual_memory().total
        return int(memory_bytes / BYTES_PER_GB)
    except Exception:
        pass  # Fall through to platform-specific methods

    # Platform-specific fallbacks
    try:
        system = platform.system()

        # Linux: read from /proc/meminfo
        if system == "Linux":
            with open("/proc/meminfo", encoding='utf-8') as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return int(kb / (KB_PER_MB * MB_PER_GB))

        # macOS: use sysctl
        elif system == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                memory_bytes = int(result.stdout.strip())
                return int(memory_bytes / BYTES_PER_GB)
    except Exception:
        pass  # Silent fail - memory detection is optional

    # Couldn't detect
    return None

def detect_zcli_install_info() -> Dict[str, str]:
    """Detect zCLI installation path and type."""
    import sys
    from importlib.metadata import distribution, PackageNotFoundError
    
    try:
        dist = distribution("zolo-zcli")
        
        # Get installation path
        if dist.files:
            # Get the first file's parent to find site-packages location
            first_file = next(iter(dist.files))
            install_path = str(first_file.locate().parent.parent.resolve())
        else:
            install_path = "unknown"
        
        # Determine install type (editable vs standard)
        try:
            direct_url = dist.read_text('direct_url.json')
            install_type = "editable" if direct_url and "editable" in direct_url else "standard"
        except:
            # Alternative check: if install path contains the package name at root level
            install_type = "editable" if "zolo-zcli" in install_path and "site-packages" not in install_path else "standard"
        
        return {
            "python_executable": sys.executable,
            "zcli_install_path": install_path,
            "zcli_install_type": install_type
        }
    except (PackageNotFoundError, Exception):
        # zCLI not installed or error detecting
        return {
            "python_executable": sys.executable,
            "zcli_install_path": "not_installed",
            "zcli_install_type": "unknown"
        }

def create_user_machine_config(path: Path, machine: Dict[str, Any]) -> None:
    """Create zConfig.machine.yaml with auto-detected values and user-editable preferences."""
    try:
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Format template with machine data (handle None values for YAML)
        content = MACHINE_CONFIG_TEMPLATE.format(
            os=machine.get('os', 'unknown'),
            os_version=machine.get('os_version', 'unknown'),
            os_name=machine.get('os_name', 'unknown'),
            hostname=machine.get('hostname', 'unknown'),
            architecture=machine.get('architecture', 'unknown'),
            python_version=machine.get('python_version', 'unknown'),
            python_impl=machine.get('python_impl', 'unknown'),
            python_build=machine.get('python_build', 'unknown'),
            python_compiler=machine.get('python_compiler', 'unknown'),
            libc_ver=machine.get('libc_ver', 'unknown'),
            python_executable=machine.get('python_executable', 'unknown'),
            zcli_install_path=machine.get('zcli_install_path', 'unknown'),
            zcli_install_type=machine.get('zcli_install_type', 'unknown'),
            browser=machine.get('browser', 'unknown'),
            ide=machine.get('ide', 'unknown'),
            terminal=machine.get('terminal', 'unknown'),
            shell=machine.get('shell', 'unknown'),
            lang=machine.get('lang', 'unknown'),
            timezone=machine.get('timezone', 'unknown'),
            home=machine.get('home', 'unknown'),
            cwd=machine.get('cwd', 'unknown'),
            username=machine.get('username', 'unknown'),
            path=machine.get('path', 'unknown'),
            processor=machine.get('processor', 'unknown'),
            cpu_cores=machine.get('cpu_cores', 'null'),
            memory_gb=machine.get('memory_gb', 'null')
        )

        path.write_text(content, encoding="utf-8")
        # Note: Always show config creation messages (not suppressed by production mode)
        _log_config(f"Created user machine config: {path}")
        _log_config("You can edit this file to customize tool preferences")

    except Exception as e:
        _log_error(f"Failed to create user machine config: {e}")


def auto_detect_machine(log_level: Optional[str] = None, is_production: bool = False) -> Dict[str, Any]:
    """Auto-detect machine identity, Python runtime, tools, and capabilities."""
    if not is_production:
        print("[MachineConfig] Auto-detecting machine information...")

    # Detect zCLI installation info
    zcli_info = detect_zcli_install_info()
    
    # Detect libc version (Linux-specific, handle Windows Store Python edge case)
    try:
        libc_ver = platform.libc_ver()[0]
    except (OSError, PermissionError):
        # Windows Store Python or other restricted environments
        libc_ver = ""
    
    machine = {
        # Identity
        "os": platform.system(),                    # Linux, Darwin, Windows
        "os_version": platform.release(),           # Kernel version
        "os_name": platform.platform(),             # Full OS name with version
        "hostname": socket.gethostname(),           # Machine name
        "architecture": platform.machine(),         # x86_64, arm64, etc.
        "processor": platform.processor(),          # CPU type
        "python_version": platform.python_version(), # 3.12.0
        "python_impl": platform.python_implementation(), # CPython, PyPy, etc.
        "python_build": platform.python_build()[0],  # Build info
        "python_compiler": platform.python_compiler(), # Compiler used
        "libc_ver": libc_ver,                       # libc version (Linux-specific)
        "python_executable": zcli_info["python_executable"],  # Path to Python executable
        "zcli_install_path": zcli_info["zcli_install_path"],  # Where zCLI is installed
        "zcli_install_type": zcli_info["zcli_install_type"],  # editable vs standard

        # User tools (system defaults, user can override)
        "browser": detect_browser(log_level, is_production),
        "ide": detect_ide(log_level, is_production),
        "terminal": os.getenv("TERM", "unknown"),
        "shell": os.getenv("SHELL", DEFAULT_SHELL),
        "lang": os.getenv("LANG", "unknown"),       # System language
        "timezone": os.getenv("TZ", DEFAULT_TIMEZONE),      # Timezone if set
        "home": str(Path.home()),                   # User's home directory

        # System capabilities
        "cpu_cores": os.cpu_count() or 1,
        "memory_gb": detect_memory_gb(),
        "cwd": _safe_getcwd(),                     # Current working directory (safe)
        "username": os.getenv("USER") or os.getenv("USERNAME", "unknown"),
        "path": os.getenv("PATH", ""),             # System PATH
    }

    if not is_production:
        print(f"[MachineConfig] Identity: {machine['hostname']} ({machine['username']}) on {machine['os_name']}")
        print(f"[MachineConfig] System: {machine['processor']}, {machine['cpu_cores']} cores, {machine['memory_gb']}GB RAM")
        print(f"[MachineConfig] Python: {machine['python_impl']} {machine['python_version']} on {machine['architecture']}")

    return machine
