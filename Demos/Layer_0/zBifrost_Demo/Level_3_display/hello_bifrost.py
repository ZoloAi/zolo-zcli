"""
Level 3: Hello zCLI (zBifrost Mode)
====================================

The SAME display code as hello_terminal.py (Level 0), but rendered in a browser!

What this demonstrates:
- Zero-config initialization (with zBifrost mode for WebSocket server)
- Same z.display code works in Terminal AND browser
- Auto-broadcast: z.display calls automatically send to WebSocket
- Declare once—run everywhere!

Compare with Level 0:
- Level 0 (Terminal): python3 hello_terminal.py
- Level 3 (Browser):  python3 hello_bifrost.py + open hello_client.html

Same Python code, different rendering target. That's zCLI!
"""

from zCLI import zCLI

print("🌉 Starting Hello zCLI Server (zBifrost mode)...")
print("📝 Same code as hello_terminal.py, different rendering target!")
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

# Define the display logic (SAME as hello_terminal.py!)
async def handle_show_hello(_websocket, _message_data):
    """
    Handle request to display hello message.
    
    🎉 These z.display calls are IDENTICAL to hello_terminal.py!
    The only difference: zMode="zBifrost" makes them auto-broadcast via WebSocket.
    Same code, different rendering target. That's the magic!
    """
    # IDENTICAL to hello_terminal.py - just works in browser via WebSocket!
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
    
    # Hierarchical indentation demo
    z.display.text("", break_after=False)
    z.display.text("Hierarchical content with indentation:", indent=0, break_after=False)
    z.display.text("📦 Root Level", indent=0, break_after=False)
    z.display.text("📂 Child Level", indent=1, break_after=False)
    z.display.text("📄 Grandchild Level", indent=2, break_after=False)
    z.display.text("📝 Great-grandchild Level", indent=3, break_after=False)

# Register the handler for the client to trigger display
# Note: _event_map is the documented way to register custom handlers (see zBifrost demos)
if z.comm.websocket:
    z.comm.websocket._event_map['show_hello'] = handle_show_hello  # noqa: SLF001
    print("✓ Handler registered: 'show_hello'")
else:
    print("✗ Warning: Could not register handler")

print()
print("✅ Server is running on ws://127.0.0.1:8765")
print("👉 Open hello_client.html in your browser")
print("👉 Click 'Connect to Server' to see the same output!")
print()
print("Compare the browser output with hello_terminal.py - identical!")
print("Same z.display code, different rendering. That's zCLI! 🚀")
print()
print("Press Ctrl+C to stop the server")
print()

# Start the WebSocket server
z.walker.run()

