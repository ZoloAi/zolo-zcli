#!/usr/bin/env python3
"""
zServer Auto-Start Demo
========================

Demonstrates HTTP server auto-starting from config.
Server starts automatically when enabled=True in zSpark.

Usage:
    python3 autostart_demo.py

Then open: http://127.0.0.1:8080/demo.html
"""

from pathlib import Path
from zCLI import zCLI
import time

# Create zCLI with auto-start configuration
print("\n" + "="*60)
print("🚀 zServer Auto-Start Demo")
print("="*60)

z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "http_server": {
        "host": "127.0.0.1",
        "port": 8080,
        "serve_path": str(Path(__file__).parent),
        "enabled": True  # Auto-start on zCLI init!
    }
})

# Server already started! Access via z.server
print(f"✅ Server auto-started: {z.server.get_url()}")
print(f"📁 Serving from: {Path(__file__).parent}")
print(f"🎯 Accessed via: z.server")
print("\nAvailable pages:")
print(f"  • {z.server.get_url()}/demo.html")
print(f"  • {z.server.get_url()}/test.html")
print("="*60)
print("\nPress Ctrl+C to stop the server\n")

try:
    # Keep server running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nStopping server...")
    z.server.stop()
    print("✅ Server stopped. Goodbye!")

