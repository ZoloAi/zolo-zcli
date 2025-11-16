#!/usr/bin/env python3
"""
Level 4: Templates - Jinja2 Base Layout
Mirrors Flask Blog Tutorial Part 2: Templates

Flask Part 2:
    from flask import Flask, render_template
    app = Flask(__name__)
    
    @app.route("/")
    @app.route("/home")
    def home():
        return render_template('home.html')
    
    @app.route("/about")
    def about():
        return render_template('about.html')
    
    app.run(debug=True)

zCLI Part 2:
    - Jinja2 templates with base layout (layout.html)
    - Multi-zone divs for content injection
    - Declarative routes serving Jinja2 templates

Goal: Server-side rendering with template inheritance
"""
from zCLI import zCLI
import os
import time

print("=" * 60)
print("Level 4: Templates - Jinja2 Base Layout")
print("=" * 60)
print("\nFlask Part 2: render_template('home.html')")
print("zCLI Part 2:  Jinja2 templates with declarative routes")
print("\n" + "=" * 60)

# Initialize zCLI
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

z = zCLI({
    "zWorkspace": current_dir,
    "zSpace": current_dir,
    "zMode": "Terminal"
})

# Create HTTP server with Jinja2 template routes
print("\nStarting zServer (HTTP) on port 8000...")
routes_file = os.path.abspath(os.path.join(current_dir, "zServer.routes.yaml"))

z.server = z.comm.create_http_server(
    port=8000,
    host="127.0.0.1",
    serve_path=current_dir,
    routes_file=routes_file
)

# Debug: Check if router was loaded
if z.server.router:
    print(f"✓ Routes loaded: {len(z.server.router.route_map)} routes")
else:
    print("✗ WARNING: No routes loaded! Check zServer.routes.yaml")

z.server.start()
print("✓ zServer (HTTP) running at http://127.0.0.1:8000")

print("\n" + "=" * 60)
print("Server running!")
print("Routes:")
print("  http://127.0.0.1:8000/       → Home Page (Jinja2 template)")
print("  http://127.0.0.1:8000/home   → Home Page (Jinja2 template)")
print("  http://127.0.0.1:8000/about  → About Page (Jinja2 template)")
print("\nPress Ctrl+C to stop")
print("=" * 60 + "\n")

# Keep server running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nShutting down...")
    z.server.stop()
    print("Server stopped.")

