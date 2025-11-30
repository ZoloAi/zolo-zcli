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

  # CPU Architecture (auto-detected, read-only)
  processor: "{processor}"
  cpu_cores: {cpu_cores}              # Total logical CPUs (backward compatibility)
  cpu_physical: {cpu_physical}        # Physical cores
  cpu_logical: {cpu_logical}          # Logical cores (with hyperthreading)
  cpu_performance: {cpu_performance}  # P-cores (Apple Silicon, null otherwise)
  cpu_efficiency: {cpu_efficiency}    # E-cores (Apple Silicon, null otherwise)
  memory_gb: {memory_gb}              # Total system RAM
  
  # Resource Limits (optional, editable - limit what zCLI can use)
  # cpu_cores_limit: 4                # Limit to 4 cores (even if more detected)
  # memory_gb_limit: 8                # Limit to 8GB (even if more detected)
  
  # GPU Capabilities (auto-detected)
  gpu_available: {gpu_available}
  gpu_type: {gpu_type}
  gpu_vendor: {gpu_vendor}
  gpu_memory_gb: {gpu_memory_gb}
  gpu_compute: {gpu_compute}          # e.g., ["Metal"], ["CUDA"], ["ROCm"]
  
  # Network Interfaces (auto-detected)
  network_interfaces: {network_interfaces}       # All interface names
  network_primary: {network_primary}             # Active interface
  network_ip_local: {network_ip_local}           # Local IP (primary)
  network_mac_address: {network_mac_address}     # MAC (primary)
  network_gateway: {network_gateway}             # Default gateway/router IP
  network_ip_public: {network_ip_public}         # Public IP (optional)
  
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

def detect_cpu_architecture() -> Dict[str, Any]:
    """Detect detailed CPU architecture (physical, logical, P-cores, E-cores)."""
    result = {
        "cpu_physical": None,
        "cpu_logical": None,
        "cpu_performance": None,
        "cpu_efficiency": None,
    }
    
    system = platform.system()
    
    try:
        # Try psutil first (cross-platform)
        psutil = importlib.import_module("psutil")
        result["cpu_logical"] = psutil.cpu_count(logical=True)
        result["cpu_physical"] = psutil.cpu_count(logical=False)
    except Exception:
        pass
    
    # Fallback to os.cpu_count() for logical
    if result["cpu_logical"] is None:
        result["cpu_logical"] = os.cpu_count() or 1
    
    # Platform-specific detection
    try:
        if system == "Darwin":
            # macOS: use sysctl for detailed info
            phys_result = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True, text=True, check=False, timeout=2
            )
            if phys_result.returncode == 0:
                result["cpu_physical"] = int(phys_result.stdout.strip())
            
            # Fallback for physical cores (needed before Apple Silicon detection)
            if result["cpu_physical"] is None:
                result["cpu_physical"] = result["cpu_logical"]
            
            # Apple Silicon: try to detect P-cores and E-cores
            if platform.machine() == "arm64" and result["cpu_physical"]:
                detected = False
                try:
                    # Try to get performance level counts (macOS 12+)
                    perf0_result = subprocess.run(
                        ["sysctl", "-n", "hw.perflevel0.logicalcpu"],
                        capture_output=True, text=True, check=False, timeout=2
                    )
                    perf1_result = subprocess.run(
                        ["sysctl", "-n", "hw.perflevel1.logicalcpu"],
                        capture_output=True, text=True, check=False, timeout=2
                    )
                    
                    if perf0_result.returncode == 0 and perf1_result.returncode == 0:
                        perf0 = int(perf0_result.stdout.strip())
                        perf1 = int(perf1_result.stdout.strip())
                        # Higher count is typically P-cores
                        result["cpu_performance"] = max(perf0, perf1)
                        result["cpu_efficiency"] = min(perf0, perf1)
                        detected = True
                except Exception:
                    pass
                
                # Fallback: Known Apple Silicon configurations
                if not detected:
                    total = result["cpu_physical"]
                    if total == 8:
                        # M1, M2: 4 P-cores + 4 E-cores
                        result["cpu_performance"] = 4
                        result["cpu_efficiency"] = 4
                    elif total == 10:
                        # M1 Pro, M2 Pro (10-core): 8 P-cores + 2 E-cores
                        result["cpu_performance"] = 8
                        result["cpu_efficiency"] = 2
                    elif total == 12:
                        # M2 Pro (12-core): 8 P-cores + 4 E-cores
                        result["cpu_performance"] = 8
                        result["cpu_efficiency"] = 4
        
        elif system == "Linux":
            # Linux: read from /sys or lscpu
            if result["cpu_physical"] is None:
                try:
                    lscpu_result = subprocess.run(
                        ["lscpu", "-p=cpu"],
                        capture_output=True, text=True, check=False, timeout=2
                    )
                    if lscpu_result.returncode == 0:
                        cores = [line for line in lscpu_result.stdout.split('\n') if line and not line.startswith('#')]
                        result["cpu_physical"] = len(cores)
                except Exception:
                    pass
    
    except Exception:
        pass  # Silent fail
    
    # Final fallback if still None (for non-Darwin systems)
    if result["cpu_physical"] is None:
        result["cpu_physical"] = result["cpu_logical"]
    
    return result


def detect_gpu(system_memory_gb: Optional[int] = None) -> Dict[str, Any]:
    """Detect GPU information (type, vendor, memory, compute APIs).
    
    Args:
        system_memory_gb: Total system RAM (for Apple Silicon unified memory)
    """
    result = {
        "gpu_available": False,
        "gpu_type": None,
        "gpu_vendor": None,
        "gpu_memory_gb": None,
        "gpu_compute": [],
    }
    
    system = platform.system()
    
    try:
        if system == "Darwin":
            # macOS: use system_profiler
            profiler_result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, check=False, timeout=5
            )
            
            if profiler_result.returncode == 0:
                output = profiler_result.stdout
                
                # Look for GPU info
                if "Chipset Model:" in output:
                    result["gpu_available"] = True
                    
                    # Extract GPU model
                    for line in output.split('\n'):
                        if "Chipset Model:" in line:
                            result["gpu_type"] = line.split(":", 1)[1].strip()
                        elif "Vendor:" in line:
                            vendor = line.split(":", 1)[1].strip()
                            # Clean up vendor name
                            if "Apple" in vendor or "Apple" in result.get("gpu_type", ""):
                                result["gpu_vendor"] = "Apple"
                            elif "NVIDIA" in vendor:
                                result["gpu_vendor"] = "NVIDIA"
                            elif "AMD" in vendor or "ATI" in vendor:
                                result["gpu_vendor"] = "AMD"
                            elif "Intel" in vendor:
                                result["gpu_vendor"] = "Intel"
                        elif "VRAM (Dynamic, Max):" in line or "VRAM (Total):" in line:
                            # Discrete GPU VRAM
                            memory_str = line.split(":", 1)[1].strip()
                            if "GB" in memory_str:
                                result["gpu_memory_gb"] = int(memory_str.split()[0])
                            elif "MB" in memory_str:
                                result["gpu_memory_gb"] = int(memory_str.split()[0]) // 1024
                
                # Apple Silicon: unified memory (GPU can access all system RAM)
                if result["gpu_vendor"] == "Apple" and result["gpu_memory_gb"] is None:
                    if system_memory_gb:
                        # Use provided system memory (from detect_memory_gb())
                        result["gpu_memory_gb"] = system_memory_gb
                    else:
                        # Fallback: try sysctl if system_memory_gb not provided
                        try:
                            mem_result = subprocess.run(
                                ["sysctl", "-n", "hw.memsize"],
                                capture_output=True, text=True, check=False, timeout=2
                            )
                            if mem_result.returncode == 0:
                                total_ram_gb = int(mem_result.stdout.strip()) // BYTES_PER_GB
                                result["gpu_memory_gb"] = total_ram_gb
                        except Exception:
                            pass
                
                # Detect compute APIs
                if result["gpu_available"]:
                    # Metal is available on all modern macOS GPUs
                    result["gpu_compute"].append("Metal")
        
        elif system == "Linux":
            # Linux: try nvidia-smi for NVIDIA, rocm-smi for AMD
            
            # Check NVIDIA
            nvidia_result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                result["gpu_available"] = True
                result["gpu_vendor"] = "NVIDIA"
                parts = nvidia_result.stdout.strip().split(',')
                result["gpu_type"] = parts[0].strip()
                if len(parts) > 1:
                    memory_str = parts[1].strip()
                    result["gpu_memory_gb"] = int(memory_str.split()[0]) // 1024
                result["gpu_compute"].append("CUDA")
            
            # Check AMD ROCm
            if not result["gpu_available"]:
                rocm_result = subprocess.run(
                    ["rocm-smi", "--showproductname"],
                    capture_output=True, text=True, check=False, timeout=3
                )
                if rocm_result.returncode == 0 and "GPU" in rocm_result.stdout:
                    result["gpu_available"] = True
                    result["gpu_vendor"] = "AMD"
                    result["gpu_compute"].append("ROCm")
        
        elif system == "Windows":
            # Windows: use wmic
            wmic_result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if wmic_result.returncode == 0:
                lines = [line.strip() for line in wmic_result.stdout.split('\n') if line.strip()]
                if len(lines) > 1:  # Skip header
                    result["gpu_available"] = True
                    gpu_line = lines[1]
                    parts = gpu_line.rsplit(None, 1)
                    if len(parts) == 2:
                        result["gpu_type"] = parts[0]
                        try:
                            ram_bytes = int(parts[1])
                            result["gpu_memory_gb"] = ram_bytes // BYTES_PER_GB
                        except ValueError:
                            pass
                    
                    # Detect vendor from name
                    if result["gpu_type"]:
                        if "NVIDIA" in result["gpu_type"]:
                            result["gpu_vendor"] = "NVIDIA"
                            result["gpu_compute"].append("CUDA")
                        elif "AMD" in result["gpu_type"] or "Radeon" in result["gpu_type"]:
                            result["gpu_vendor"] = "AMD"
                        elif "Intel" in result["gpu_type"]:
                            result["gpu_vendor"] = "Intel"
    
    except Exception:
        pass  # Silent fail - GPU detection is optional
    
    return result


def detect_network() -> Dict[str, Any]:
    """Detect network interfaces and IP addresses.
    
    Note: psutil.net_if_addrs() has known memory corruption bugs on some systems.
    We use platform-specific methods (ifconfig, netstat, ip) for reliability.
    
    Returns 6 essential properties:
      - network_interfaces: List of all interface names
      - network_primary: Active interface name
      - network_ip_local: Local IP of primary interface
      - network_mac_address: MAC address of primary interface
      - network_gateway: Default gateway/router IP
      - network_ip_public: Public IP (optional, may be None)
    """
    result = {
        "network_interfaces": [],
        "network_primary": None,
        "network_ip_local": None,
        "network_mac_address": None,
        "network_gateway": None,
        "network_ip_public": None,
    }
    
    system = platform.system()
    
    # Platform-specific detection (primary method - more reliable than psutil)
    try:
        if system in ("Linux", "Darwin"):
            # Use ifconfig for macOS/Linux
            ifconfig_result = subprocess.run(
                ["ifconfig"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if ifconfig_result.returncode == 0:
                output = ifconfig_result.stdout
                current_iface = None
                current_status = "down"
                current_ip = None
                current_mac = None
                
                for line in output.split('\n'):
                    # New interface (line starts without whitespace and has :)
                    if line and not line[0].isspace() and ':' in line:
                        # Save previous interface
                        if current_iface and current_iface != "lo0" and not current_iface.startswith("lo"):
                            result["network_interfaces"].append(current_iface)
                            
                            # Determine primary (first up interface with IP)
                            if result["network_primary"] is None and current_status == "up" and current_ip:
                                result["network_primary"] = current_iface
                                result["network_ip_local"] = current_ip
                                result["network_mac_address"] = current_mac
                        
                        # Start new interface
                        current_iface = line.split(':')[0].strip()
                        current_status = "down"
                        current_ip = None
                        current_mac = None
                        
                        # Check if UP/RUNNING in the first line
                        if "UP" in line and "RUNNING" in line:
                            current_status = "up"
                    
                    # Parse interface details (indented lines)
                    elif current_iface and line.startswith('\t'):
                        line = line.strip()
                        # IPv4 address
                        if line.startswith("inet ") and not line.startswith("inet6"):
                            parts = line.split()
                            if len(parts) >= 2:
                                current_ip = parts[1]
                        # MAC address
                        elif line.startswith("ether "):
                            parts = line.split()
                            if len(parts) >= 2:
                                current_mac = parts[1]
                
                # Save last interface
                if current_iface and current_iface != "lo0" and not current_iface.startswith("lo"):
                    result["network_interfaces"].append(current_iface)
                    if result["network_primary"] is None and current_status == "up" and current_ip:
                        result["network_primary"] = current_iface
                        result["network_ip_local"] = current_ip
                        result["network_mac_address"] = current_mac
        
        elif system == "Windows":
            # Use ipconfig for Windows
            ipconfig_result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if ipconfig_result.returncode == 0:
                # Simplified Windows parsing
                # Full implementation would need more robust parsing
                result["network_interfaces"].append("Ethernet")
                result["network_primary"] = "Ethernet"
    
    except Exception:
        pass  # Silent fail
    
    # Detect default gateway (router IP)
    try:
        if system in ("Darwin", "Linux"):
            # Try netstat first (most reliable on macOS)
            netstat_result = subprocess.run(
                ["netstat", "-rn"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if netstat_result.returncode == 0:
                for line in netstat_result.stdout.split('\n'):
                    # Look for default route
                    if line.startswith("default") or line.startswith("0.0.0.0"):
                        parts = line.split()
                        if len(parts) >= 2:
                            # Second column is usually the gateway
                            gateway = parts[1]
                            # Validate it's an IP address (not a hostname like "UGScg")
                            if '.' in gateway and not gateway[0].isalpha():
                                result["network_gateway"] = gateway
                                break
        
        elif system == "Windows":
            # Use route print for Windows
            route_result = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True, text=True, check=False, timeout=3
            )
            if route_result.returncode == 0:
                for line in route_result.stdout.split('\n'):
                    if "0.0.0.0" in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            # Third column is typically the gateway
                            gateway = parts[2]
                            if '.' in gateway:
                                result["network_gateway"] = gateway
                                break
    
    except Exception:
        pass  # Silent fail
    
    # Try to get public IP (optional, requires network call)
    try:
        import urllib.request
        # Use a fast, reliable service (timeout 2 seconds)
        response = urllib.request.urlopen('https://api.ipify.org', timeout=2)
        result["network_ip_public"] = response.read().decode('utf-8').strip()
    except Exception:
        pass  # Silent fail - public IP is optional
    
    return result


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
    
    # Detect CPU architecture details
    cpu_arch = detect_cpu_architecture()
    
    # Detect memory first (needed for Apple Silicon GPU unified memory)
    system_memory_gb = detect_memory_gb()
    
    # Detect GPU information (pass system memory for unified memory calculation)
    gpu_info = detect_gpu(system_memory_gb=system_memory_gb)
    
    # Detect network interfaces and IPs
    network_info = detect_network()
    
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
        "cpu_cores": os.cpu_count() or 1,           # Total logical CPUs (backward compatibility)
        "cpu_physical": cpu_arch["cpu_physical"],   # Physical cores
        "cpu_logical": cpu_arch["cpu_logical"],     # Logical cores (with hyperthreading)
        "cpu_performance": cpu_arch["cpu_performance"],  # P-cores (Apple Silicon)
        "cpu_efficiency": cpu_arch["cpu_efficiency"],    # E-cores (Apple Silicon)
        "memory_gb": system_memory_gb,              # Total system RAM (already detected)
        
        # GPU capabilities
        "gpu_available": gpu_info["gpu_available"],
        "gpu_type": gpu_info["gpu_type"],
        "gpu_vendor": gpu_info["gpu_vendor"],
        "gpu_memory_gb": gpu_info["gpu_memory_gb"],
        "gpu_compute": gpu_info["gpu_compute"],
        
        # Network interfaces
        "network_interfaces": network_info["network_interfaces"],
        "network_primary": network_info["network_primary"],
        "network_ip_local": network_info["network_ip_local"],
        "network_mac_address": network_info["network_mac_address"],
        "network_gateway": network_info["network_gateway"],
        "network_ip_public": network_info["network_ip_public"],
        
        "cwd": _safe_getcwd(),                     # Current working directory (safe)
        "username": os.getenv("USER") or os.getenv("USERNAME", "unknown"),
        "path": os.getenv("PATH", ""),             # System PATH
    }

    if not is_production:
        print(f"[MachineConfig] Identity: {machine['hostname']} ({machine['username']}) on {machine['os_name']}")
        cpu_info = f"{machine['cpu_physical']} physical, {machine['cpu_logical']} logical"
        if machine['cpu_performance'] and machine['cpu_efficiency']:
            cpu_info += f" ({machine['cpu_performance']} P-cores, {machine['cpu_efficiency']} E-cores)"
        print(f"[MachineConfig] CPU: {machine['processor']}, {cpu_info} cores")
        print(f"[MachineConfig] RAM: {machine['memory_gb']}GB")
        if machine['gpu_available']:
            gpu_mem = f", {machine['gpu_memory_gb']}GB" if machine['gpu_memory_gb'] else ""
            gpu_compute = f", {', '.join(machine['gpu_compute'])}" if machine['gpu_compute'] else ""
            print(f"[MachineConfig] GPU: {machine['gpu_type']}{gpu_mem}{gpu_compute}")
        if machine['network_primary']:
            network_ip = machine['network_ip_local'] or "no IP"
            print(f"[MachineConfig] Network: {machine['network_primary']} ({network_ip})")
        print(f"[MachineConfig] Python: {machine['python_impl']} {machine['python_version']} on {machine['architecture']}")

    return machine
