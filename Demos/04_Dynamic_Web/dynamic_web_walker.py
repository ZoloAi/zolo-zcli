#!/usr/bin/env python3
"""
Demo 4 - Dynamic Web UI Walker
v1.5.4 Phase 3 - zUI → HTML Rendering

This demo proves server-side HTML rendering from zUI YAML files.
Unlike Demo 3 (static HTML), this generates pages dynamically from zUI.

Flow:
    1. Browser requests /dashboard
    2. zServer matches dynamic route
    3. Loads zUI.web_dashboard.yaml
    4. Renders zUI events to HTML
    5. Returns complete HTML page
    
Key Innovation: Same zUI works in Terminal AND Web modes!
"""

from zCLI import zCLI
import os

# Step 1: Import zCLI
# Step 2: Create spark
z = zCLI({
    "zWorkspace": ".",
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/04_Dynamic_Web",
    "zMode": "Terminal"  # Walker runs in Terminal, but serves Web pages
})

# Step 3: Create HTTP server with declarative routing
# Use absolute path for routes file
routes_file = os.path.join(os.getcwd(), "zServer_routes.yaml")

server = z.comm.create_http_server(
    port=8081,
    serve_path="./public",
    routes_file=routes_file
)

# Start server in background
server.start()

# Display server info
print("\n" + "="*70)
print("🎨 Demo 4: Dynamic Web UI - zUI → HTML Rendering")
print("="*70)
print(f"📍 Server URL:   {server.get_url()}")
print(f"📊 Health:       {server.health_check()}")
print(f"📁 Serving:      {server.serve_path}")
print(f"🗺️  Routes:      zServer_routes.yaml")
print("="*70)

print("\n📋 Declared Routes:")
print("   → /dashboard     (dynamic) →  zUI.web_dashboard.yaml")
print("   → /users         (dynamic) →  zUI.web_users.yaml")
print("   → /about         (dynamic) →  zUI.web_about.yaml")
print("   → /style.css     (static)  →  public/style.css")
print("   → /script.js     (static)  →  public/script.js")

print("\n" + "="*70)
print("🎯 What's Different from Demo 3?")
print("="*70)
print("   Demo 3: Static HTML files (hand-coded)")
print("   Demo 4: Dynamic HTML from zUI YAML (generated)")
print("="*70)

print("\n💡 How It Works:")
print("   1. Browser requests /dashboard")
print("   2. HTTPRouter matches type: dynamic route")
print("   3. PageRenderer loads zUI.web_dashboard.yaml")
print("   4. zUI events render to HTML (text, header, menu)")
print("   5. HTML wrapped in template and served")
print("   6. Same zUI works in Terminal AND Web!")

print("\n🔗 Try these URLs:")
print(f"   → {server.get_url()}/dashboard  (zUI → HTML)")
print(f"   → {server.get_url()}/users      (with zData)")
print(f"   → {server.get_url()}/about      (simple content)")

print("\n⚠️  Current Status: MVP - Basic rendering only")
print("   ✅ Dynamic routes configured")
print("   ✅ Page renderer created")
print("   ✅ HTTPRouter integration")
print("   ⏳ Full HTML rendering (in progress)")
print("   ⏳ zLink HTTP route support (pending)")

print("\n⌨️  Press Enter to stop server...\n")

# Wait for user input
try:
    input()
except KeyboardInterrupt:
    print("\n")

# Clean shutdown
print("🛑 Stopping server...")
server.stop()
print("✅ Server stopped. Demo 4 session complete!")

