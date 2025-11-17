"""
Level 0: Hello zCLI (zBifrost Mode)
====================================

The SAME code as hello_terminal.py, but rendered in a browser!

What this demonstrates:
- Zero-config initialization (with zBifrost mode)
- Same display code works in Terminal AND browser
- WebSocket-based rendering
- Declare once—run everywhere!

How to run:
1. python3 hello_bifrost.py
2. Open hello_client.html in your browser
3. Click "Connect to Server"
4. See the same output in your browser!
"""

from zCLI import zCLI

# Initialize zCLI in zBifrost mode (WebSocket server)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

# Define the display logic (SAME as terminal version!)
async def handle_show_hello(_websocket, _message_data):
    """
    Handle request to display hello message - works in Terminal AND browser!
    
    🎉 NEW: These z.display calls now automatically broadcast to WebSocket!
    No manual JSON construction needed - the same code works everywhere.
    """
    # These are the SAME display calls as hello_terminal.py!
    z.display.success("Hello from zCLI!")
    z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")
    z.display.info(f"Workspace: {z.config.sys_paths.workspace_dir}")
    z.display.info(f"Deployment: {z.session.get('deployment', 'Debug')}")
    z.display.success("✨ All subsystems loaded and ready!")
    z.display.info("💡 z.display now broadcasts automatically in zBifrost mode!")
    # Separator
    z.display.text("", break_after=False)

    # Hero Header (indent=0 → centered, large, prominent)
    z.display.header("🎨 zDisplay Events Showcase", color="CYAN", indent=0)

    # Explain what just happened with the signals
    z.display.text("💬 Notice: The colored signals above will auto-fade after 5 seconds!", indent=0, break_after=False)
    z.display.text("   You can also dismiss them manually with the × button.", indent=0, break_after=False)
    z.display.text("   This is zTheme's toast-style alert system - pure CSS!", indent=0, break_after=False)
    z.display.text("", break_after=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Header Demo - indent 0 = HERO, indent 1-6 = h1-h6 (semantic HTML headers)
    # ═══════════════════════════════════════════════════════════════════════════
    z.display.text("Below are examples of all header levels (h1-h6):", indent=0, break_after=False)
    z.display.text("", break_after=False)
    z.display.header("Level 1 Header (h1)", color="CYAN", indent=1)
    z.display.header("Level 2 Header (h2)", color="CYAN", indent=2)
    z.display.header("Level 3 Header (h3)", color="CYAN", indent=3)
    z.display.header("Level 4 Header (h4)", color="CYAN", indent=4)
    z.display.header("Level 5 Header (h5)", color="CYAN", indent=5)
    z.display.header("Level 6 Header (h6)", color="CYAN", indent=6)

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
    z.display.list(subsystems, style="bullet", indent=1)

# Register the handler for the client to trigger display
# Note: _event_map is the documented way to register custom handlers (see zBifrost demos)
if z.comm.websocket:
    z.comm.websocket._event_map['show_hello'] = handle_show_hello  # noqa: SLF001
    print("✓ Hello handler registered!")
else:
    print("✗ Warning: Could not register hello handler")

# Start the WebSocket server
z.walker.run()

