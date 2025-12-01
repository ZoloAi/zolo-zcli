#!/usr/bin/env python3
"""
Level 3: Getting Started - HTTP Server
Mirrors Flask Blog Tutorial Part 1: Getting Started

Flask Part 1:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/")
    @app.route("/home")
    def home():
        return "<h1>Home Page</h1>"
    
    @app.route("/about")
    def about():
        return "<h1>About Page</h1>"
    
    app.run(debug=True)

zCLI Part 1:
    - Run zServer (HTTP) with declarative routes
    - No WebSocket yet (that comes later!)
    - Declarative YAML instead of decorators

Goal: Serve simple HTML strings via HTTP (exactly like Flask Part 1)
"""
import time
import os
from zCLI import zCLI

current_dir = os.path.dirname(os.path.abspath(__file__))

z = zCLI({
    "zWorkspace": current_dir,
    "zSpace": current_dir,
    "zMode": "Terminal"
})

# Use absolute path to zServer.routes.yaml (proper zCLI naming convention)
routes_file = os.path.abspath(os.path.join(current_dir, "zServer.routes.yaml"))

z.server = z.comm.create_http_server(
    port=8000,
    host="127.0.0.1",
    serve_path=current_dir,
    routes_file=routes_file  # Absolute path to routes file
)

# Debug: Check if router was loaded
if z.server.router:
    print(f"✓ Routes loaded: {len(z.server.router.route_map)} routes")
else:
    print("✗ WARNING: No routes loaded! Check zServer.routes.yaml")

z.server.start()

# Keep server running (zServer runs in background thread)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nShutting down...")
    z.server.stop()
    print("Server stopped.")
