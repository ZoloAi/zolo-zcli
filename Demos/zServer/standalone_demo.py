#!/usr/bin/env python3
"""
zServer Standalone Demo
========================

Demonstrates HTTP static file server working independently.

Usage:
    python3 standalone_demo.py

Then open: http://127.0.0.1:8080/demo.html
"""

from pathlib import Path
from zCLI import zCLI
import time

# Create minimal zCLI instance
z = zCLI({"zWorkspace": str(Path(__file__).parent)})

# Create and start HTTP server
print("\n" + "="*60)
print("🌐 zServer Standalone Demo")
print("="*60)

http_server = z.comm.create_http_server(
    port=8080,
    serve_path=str(Path(__file__).parent)
)

http_server.start()

print(f"✅ Server started: {http_server.get_url()}")
print(f"📁 Serving from: {Path(__file__).parent}")
print("\nAvailable pages:")
print(f"  • {http_server.get_url()}/demo.html")
print(f"  • {http_server.get_url()}/test.html")
print("="*60)
print("\nPress Ctrl+C to stop the server\n")

try:
    # Keep server running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nStopping server...")
    http_server.stop()
    print("✅ Server stopped. Goodbye!")

