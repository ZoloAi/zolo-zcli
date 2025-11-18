"""
Level 2: Config & Session
==========================

Demonstrates zConfig's core capabilities:
- Machine detection (OS, hostname, architecture, Python version)
- Configuration hierarchy (machine → environment → session)
- Environment variables (read from .zEnv automatically)
- Path resolution (@ shortcuts for workspace-relative paths)
- Session variables (zVars) - Store user-defined values

Key Concept: Zero-config initialization with hierarchical overrides
"""

from zCLI import zCLI

# Initialize zCLI (auto-loads .zEnv if present)
z = zCLI()

# ============================================
# 1. Machine Detection (auto-detected)
# ============================================
z.display.header("Machine Information", color="CYAN")
z.display.text("Auto-detected on first run:")

machine_info = [
    ("OS", z.config.get_machine("os")),
    ("OS Name", z.config.get_machine("os_name")),
    ("Hostname", z.config.get_machine("hostname")),
    ("Architecture", z.config.get_machine("architecture")),
    ("Processor", z.config.get_machine("processor")),
    ("Python Version", z.config.get_machine("python_version")),
    ("Python Implementation", z.config.get_machine("python_impl")),
]

for label, value in machine_info:
    z.display.info(f"{label}: {value}")

z.display.text("")

# ============================================
# 2. User Tools Detection
# ============================================
z.display.header("User Tools", color="GREEN")
z.display.text("Detected from environment or auto-detected:")

tools_info = [
    ("Browser", z.config.get_machine("browser")),
    ("IDE/Editor", z.config.get_machine("ide")),
    ("Terminal", z.config.get_machine("terminal")),
    ("Shell", z.config.get_machine("shell")),
]

for label, value in tools_info:
    z.display.info(f"{label}: {value}")

z.display.text("")

# ============================================
# 3. Environment Configuration
# ============================================
z.display.header("Environment Configuration", color="YELLOW")
z.display.text("Settings from zConfig.environment.yaml:")

z.display.info(f"Deployment: {z.session.get('deployment', 'Debug')}")
z.display.info(f"Logger Level: {z.session.get('zLogger', 'INFO')}")
z.display.info(f"Workspace: {z.config.sys_paths.workspace_dir}")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")

z.display.text("")

# ============================================
# 4. Environment Variables (.zEnv)
# ============================================
z.display.header("Environment Variables", color="MAGENTA")
z.display.text("Loaded from .zEnv file in workspace:")

# Try to read from .zEnv
app_name = z.config.environment.get_env_var("APP_NAME")
api_url = z.config.environment.get_env_var("API_URL")
debug = z.config.environment.get_env_var("DEBUG")

if app_name:
    z.display.success(f"APP_NAME: {app_name}")
    z.display.success(f"API_URL: {api_url}")
    z.display.success(f"DEBUG: {debug}")
else:
    z.display.warning("No .zEnv file found (this is OK!)")
    z.display.info("Create one to see environment variable loading:")
    z.display.text('  echo "APP_NAME=MyApp" > .zEnv', indent=1)
    z.display.text('  echo "API_URL=https://api.example.com" >> .zEnv', indent=1)
    z.display.text('  echo "DEBUG=True" >> .zEnv', indent=1)

z.display.text("")

# ============================================
# 5. Path Resolution
# ============================================
z.display.header("Path Resolution", color="BLUE")
z.display.text("Declarative paths with @ shortcuts:")

paths_to_resolve = [
    ("Current workspace (@.)", "@."),
    ("User home (@~)", "@~"),
    ("zSchema directory (@.zSchema)", "@.zSchema"),
    ("zUI directory (@.zUI)", "@.zUI"),
]

for label, path in paths_to_resolve:
    try:
        resolved = z.zparser.resolve_data_path(path)
        z.display.info(f"{label}: {resolved}")
    except Exception as e:
        z.display.warning(f"{label}: {e}")

z.display.text("")

# ============================================
# 6. Configuration File Locations
# ============================================
z.display.header("Configuration Files", color="CYAN")
z.display.text("Where zConfig stores persistent settings:")

config_paths = [
    ("User config directory", z.config.sys_paths.user_config_dir),
    ("Workspace directory", z.config.sys_paths.workspace_dir),
]

for label, path in config_paths:
    z.display.info(f"{label}: {path}")

z.display.text("")

# ============================================
# 7. Session Context (Runtime)
# ============================================
z.display.header("Session Context", color="GREEN")
z.display.text("Ephemeral runtime state (not persisted):")

# Show key session values
session_data = {
    "zMode": z.session.get("zMode"),
    "zWorkspace": z.session.get("zWorkspace"),
    "deployment": z.session.get("deployment"),
    "zVars": len(z.session.get("zVars", {})),
    "zAuth": "logged_in" if z.session.get("zAuth") else "not logged in",
}

z.display.json_data(session_data)
z.display.text("")

# ============================================
# 8. Session Variables (zVars)
# ============================================
z.display.header("Session Variables (zVars)", color="BLUE")
z.display.text("Store user-defined values for the session:")

# Initialize zVars if not exists
if "zVars" not in z.session:
    z.session["zVars"] = {}

# Set some example variables
z.session["zVars"]["app_mode"] = "demo"
z.session["zVars"]["user_role"] = "developer"
z.session["zVars"]["theme"] = "dark"

z.display.success("Stored 3 variables in session['zVars']:")
z.display.text(f"  app_mode: {z.session['zVars']['app_mode']}", indent=1)
z.display.text(f"  user_role: {z.session['zVars']['user_role']}", indent=1)
z.display.text(f"  theme: {z.session['zVars']['theme']}", indent=1)

z.display.text("")
z.display.info("💡 zVars persist for the entire session")
z.display.info("💡 Work across Terminal AND Bifrost modes")
z.display.info("💡 Perfect for storing user inputs and preferences")
z.display.text("")

# ============================================
# Summary
# ============================================
z.display.header("Summary", color="MAGENTA")
z.display.success("You've learned about:")
features_learned = [
    "Machine detection - OS, hostname, Python version (auto-detected)",
    "User tools - Browser, IDE, terminal, shell",
    "Environment config - Deployment mode, logger level",
    "Environment variables - Read from .zEnv automatically",
    "Path resolution - @ shortcuts for workspace-relative paths",
    "Session variables (zVars) - Store user values across the session",
    "Configuration hierarchy - 5-tier resolution (defaults → session)"
]
z.display.list(features_learned)

z.display.text("")
z.display.info("💡 Next: Level 3 teaches user input and validation!")
z.display.text("Run: cd ../Level_3_Input && python3 input_demo.py")

