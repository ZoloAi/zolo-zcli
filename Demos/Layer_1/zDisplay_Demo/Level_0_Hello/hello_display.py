from zCLI import zCLI

# Initialize zCLI (zero config!)
z = zCLI({"logger": "PROD"})

# Display information (works in Terminal AND browser with zMode="zBifrost")
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode')}")
z.display.info(f"Workspace: {z.config.sys_paths.workspace_dir}")

# Separator
z.display.text("")

# List all available subsystems (demonstrating text output with indentation)
z.display.text("Available subsystems:", indent=0, break_after=False)
subsystems = [
    "z.config     - Configuration management",
    "z.display    - Output & rendering",
    "z.comm       - HTTP client & services",
    "z.auth       - Authentication",
    "z.data       - Database operations",
    "z.dialog     - Forms & validation",
    "z.func       - Python execution",
    "z.loader     - File loading",
    "z.logger     - Logging",
    "z.navigation - Menus & breadcrumbs",
    "z.parser     - Path resolution",
    "z.session    - Runtime context",
    "z.walker     - UI orchestration",
    "z.wizard     - Multi-step workflows",
]

# Display each subsystem with bullet and indentation
for subsystem in subsystems:
    z.display.text(f"  • {subsystem}", indent=1, break_after=False)

z.display.text("", break_after=False)
z.display.success("✨ All subsystems loaded and ready!")

# Hierarchical indentation demo
z.display.text("", break_after=False)
z.display.text("Hierarchical content with indentation:", indent=0, break_after=False)
z.display.text("📦 Root Level", indent=0, break_after=False)
z.display.text("📂 Child Level", indent=1, break_after=False)
z.display.text("📄 Grandchild Level", indent=2, break_after=False)
z.display.text("📝 Great-grandchild Level", indent=3, break_after=False)

# Try it in browser mode too!
# Change zCLI() to zCLI({"zMode": "zBifrost", "websocket": {...}})
# Same code, different output target. That's declarative zDisplay!

