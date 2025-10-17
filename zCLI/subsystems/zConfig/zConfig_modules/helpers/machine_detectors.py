# zCLI/subsystems/zConfig/zConfig_modules/helpers/machine_detectors.py
"""Helper functions for detecting machine capabilities and tools."""

from zCLI import os, platform, shutil, Colors, subprocess, importlib, Path

def detect_browser():
    """Detect system default browser."""
    browser = os.getenv("BROWSER")  # Check env var first
    if browser:
        return browser

    system = platform.system()
    if system == "Darwin":
        browser = _detect_macos_browser()
    elif system == "Linux":
        browser = _detect_linux_browser()
    elif system == "Windows":
        browser = "Edge"  # TODO: Query Windows registry
    else:
        browser = "unknown"

    return browser


def _detect_macos_browser():
    """Detect default browser on macOS using LaunchServices."""
    try:
        # Method 1: Check LaunchServices database for http handler
        result = subprocess.run(
            ['defaults', 'read', 'com.apple.LaunchServices/com.apple.launchservices.secure', 'LSHandlers'],
            capture_output=True, text=True, timeout=5, check=False
        )

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
                print(f"{Colors.CONFIG}[MachineConfig] Found default browser via LaunchServices: {name}{Colors.RESET}")
                return name

    except Exception as e:
        print(f"{Colors.WARNING}[MachineConfig] Could not query LaunchServices: {e}{Colors.RESET}")

    return "Safari"  # macOS default

def _detect_linux_browser():
    """Detect default browser on Linux using xdg-settings."""
    # Try xdg-settings first
    try:
        result = subprocess.run(
            ['xdg-settings', 'get', 'default-web-browser'],
            capture_output=True, text=True, timeout=5, check=False
        )
        if result.returncode == 0:
            browser_desktop = result.stdout.strip().lower()
            if 'firefox' in browser_desktop:
                return "firefox"
            if 'chrome' in browser_desktop:
                return "google-chrome"
            if 'chromium' in browser_desktop:
                return "chromium"
            if 'brave' in browser_desktop:
                return "brave-browser"
    except Exception:
        pass

    # Check PATH for common browsers
    for browser in ["firefox", "google-chrome", "chromium", "brave-browser"]:
        if shutil.which(browser):
            return browser

    return "firefox"  # Linux default

def detect_ide():
    """Detect IDE/code editor by checking env vars, modern/classic IDEs, and fallback editors."""
    # Check IDE/editor env vars
    for var in ["IDE", "VISUAL_EDITOR", "EDITOR", "VISUAL"]:
        ide_env = os.getenv(var)
        if ide_env:
            print(f"{Colors.CONFIG}[MachineConfig] IDE from env var {var}: {ide_env}{Colors.RESET}")
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
            print(f"{Colors.CONFIG}[MachineConfig] Found modern IDE: {ide}{Colors.RESET}")
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
            print(f"{Colors.CONFIG}[MachineConfig] Found classic IDE: {ide}{Colors.RESET}")
            return ide

    # macOS-specific: Check for Xcode
    if platform.system() == "Darwin":
        if shutil.which("xed"):  # Xcode command-line tool
            print(f"{Colors.CONFIG}[MachineConfig] Found Xcode (xed){Colors.RESET}")
            return "xed"

    # Fallback to simple editors
    simple_editors = ["nano", "vim", "nvim", "vi"]
    for editor in simple_editors:
        if shutil.which(editor):
            print(f"{Colors.CONFIG}[MachineConfig] Falling back to simple editor: {editor}{Colors.RESET}")
            return editor

    # Final fallback
    print(f"{Colors.CONFIG}[MachineConfig] Using final fallback: nano{Colors.RESET}")
    return "nano"

def detect_memory_gb():
    """Detect system memory in GB, returns int or None if detection fails."""
    try:
        psutil = importlib.import_module("psutil")
        memory_bytes = psutil.virtual_memory().total
        return int(memory_bytes / (1024 ** 3))
    except Exception:
        pass

    # Platform-specific fallbacks
    try:
        system = platform.system()

        # Linux: read from /proc/meminfo
        if system == "Linux":
            with open("/proc/meminfo", encoding='utf-8') as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return int(kb / (1024 * 1024))

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
                return int(memory_bytes / (1024 ** 3))
    except Exception:
        pass

    # Couldn't detect
    return None

def create_user_machine_config(path, machine):
    """Create user machine config file on first run with given path and data."""
    try:
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Create YAML content with current detected values
        content = f"""
# zolo-zcli Machine Configuration
# This file was auto-generated on first run.
# You can edit this file to customize your tool preferences.

zMachine:
  # Machine Identity (auto-detected, do not edit unless needed)
  os: "{machine.get('os')}"
  os_version: "{machine.get('os_version')}"
  os_name: "{machine.get('os_name')}"
  hostname: "{machine.get('hostname')}"
  architecture: "{machine.get('architecture')}"

  # Python Runtime (auto-detected)
  python_version: "{machine.get('python_version')}"
  python_impl: "{machine.get('python_impl')}"
  python_build: "{machine.get('python_build')}"
  python_compiler: "{machine.get('python_compiler')}"
  libc_ver: "{machine.get('libc_ver')}"

  # Tool Preferences (customize these to your liking!)
  browser: "{machine.get('browser')}"          # Chrome, Firefox, Arc, Safari, etc.
  ide: "{machine.get('ide')}"                  # cursor, code, subl, etc.
  terminal: "{machine.get('terminal')}"        # Terminal emulator
  shell: "{machine.get('shell')}"              # bash, zsh, fish, etc.
  lang: "{machine.get('lang')}"
  timezone: "{machine.get('timezone')}"

  # Paths (auto-detected)
  home: "{machine.get('home')}"
  cwd: "{machine.get('cwd')}"
  username: "{machine.get('username')}"
  path: "{machine.get('path')}"

  # System Capabilities (auto-detected)
  processor: "{machine.get('processor')}"
  cpu_cores: {machine.get('cpu_cores', 'null')}
  memory_gb: {machine.get('memory_gb', 'null')}
  
  # Custom Fields (add your own as needed)
  # datacenter: "us-west-2"
  # cluster: "lfs-cluster"
  # lfs_node_id: "node-001"
"""

        Path(path).write_text(content, encoding="utf-8")
        print(f"{Colors.CONFIG}[MachineConfig] Created user machine config: {path}{Colors.RESET}")
        print(f"{Colors.CONFIG}[MachineConfig] You can edit this file to customize tool preferences{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.ERROR}[MachineConfig] Failed to create user machine config: {e}{Colors.RESET}")


def auto_detect_machine():
    """Auto-detect machine information and return dict with defaults."""
    from zCLI import os, platform, socket, Path
    
    print(f"{Colors.CONFIG}[MachineConfig] Auto-detecting machine information...{Colors.RESET}")

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
        "libc_ver": platform.libc_ver()[0],         # libc version

        # User tools (system defaults, user can override)
        "browser": detect_browser(),
        "ide": detect_ide(),
        "terminal": os.getenv("TERM", "unknown"),
        "shell": os.getenv("SHELL", "/bin/sh"),
        "lang": os.getenv("LANG", "unknown"),       # System language
        "timezone": os.getenv("TZ", "system"),      # Timezone if set
        "home": str(Path.home()),                   # User's home directory

        # System capabilities
        "cpu_cores": os.cpu_count() or 1,
        "memory_gb": detect_memory_gb(),
        "cwd": os.getcwd(),                        # Current working directory
        "username": os.getenv("USER") or os.getenv("USERNAME", "unknown"),
        "path": os.getenv("PATH", ""),             # System PATH
    }

    print(
        f"{Colors.CONFIG}[MachineConfig] Identity: "
        f"{machine['hostname']} ({machine['username']}) on {machine['os_name']}{Colors.RESET}"
    )
    print(
        f"{Colors.CONFIG}[MachineConfig] System: "
        f"{machine['processor']}, {machine['cpu_cores']} cores, {machine['memory_gb']}GB RAM{Colors.RESET}"
    )
    print(
        f"{Colors.CONFIG}[MachineConfig] Python: "
        f"{machine['python_impl']} {machine['python_version']} on {machine['architecture']}{Colors.RESET}"
    )

    return machine
