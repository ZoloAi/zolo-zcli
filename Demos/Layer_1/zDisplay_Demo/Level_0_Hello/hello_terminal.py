"""
Level 0: Hello zCLI (Terminal Mode)
====================================

Your first zCLI program—just 3 lines!

What this demonstrates:
- Zero-config initialization
- Basic display output (success, info signals)
- Session context (checking mode)
- Terminal rendering (ANSI colors)

No setup required. Just run it!
"""

from zCLI import zCLI

# Initialize zCLI (zero config!)
z = zCLI()

# Print to Terminal
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")
z.display.info(f"Workspace: {z.config.sys_paths.workspace_dir}")
z.display.info(f"Deployment: {z.session.get('deployment', 'Debug')}")

# Separator
z.display.text("", break_after=False)

# Show what we have access to
z.display.text("Available subsystems:", indent=0, break_after=False)
subsystems = [
    "z.config   - Configuration management",
    "z.display  - Output & rendering",
    "z.comm     - HTTP client & services",
    "z.auth     - Authentication",
    "z.data     - Database operations",
    "z.dialog   - Forms & validation",
    "z.func     - Python execution",
    "z.loader   - File loading",
    "z.logger   - Logging",
    "z.navigation - Menus & breadcrumbs",
    "z.parser   - Path resolution",
    "z.session  - Runtime context",
    "z.walker   - UI orchestration",
    "z.wizard   - Multi-step workflows",
]

for subsystem in subsystems:
    z.display.text(f"  • {subsystem}", indent=1, break_after=False)

z.display.text("", break_after=False)
z.display.success("✨ All subsystems loaded and ready!")

