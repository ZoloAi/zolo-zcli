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

print("🌉 Starting Hello zCLI Server (zBifrost mode)...")
print("📝 Goal: See the SAME code render in a browser")
print("🎉 NEW: z.display now broadcasts automatically - no manual JSON!")
print()

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
    z.display.text("", break_after=False)
    z.display.info("💡 z.display now broadcasts automatically in zBifrost mode!")

# Register the handler for the client to trigger display
# Note: _event_map is the documented way to register custom handlers (see zBifrost demos)
if z.comm.websocket:
    z.comm.websocket._event_map['show_hello'] = handle_show_hello  # noqa: SLF001
    print("✓ Hello handler registered!")
else:
    print("✗ Warning: Could not register hello handler")

print("✅ Server is running on ws://127.0.0.1:8765")
print("👉 Open hello_client.html in your browser")
print("👉 Click 'Connect to Server' to see the magic!")
print()
print("Press Ctrl+C to stop the server")
print()

# Start the WebSocket server
z.walker.run()

