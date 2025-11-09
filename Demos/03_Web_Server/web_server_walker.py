#!/usr/bin/env python3
"""Web Server Layer Demo - Covers 3.1"""

from zCLI import zCLI

# Step 1: Import zCLI
# Step 2: Create spark
z = zCLI({
    "zWorkspace": ".",
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server",
    "zMode": "Terminal"
})

# Step 3: Create HTTP server via zComm factory
server = z.comm.create_http_server(
    port=8080,
    serve_path="./public"
)

# Start server in background
server.start()

# Display server info
print("\n" + "="*60)
print("🌐 zServer Demo - Static Website")
print("="*60)
print(f"📍 Server URL:  {server.get_url()}")
print(f"📊 Health:      {server.health_check()}")
print(f"📁 Serving:     ./public/")
print("="*60)
print("\n🔗 Open in browser:")
print(f"   → {server.get_url()}/index.html")
print(f"   → {server.get_url()}/test_page.html")
print("\n⌨️  Press Enter to stop server...\n")

# Wait for user input
try:
    input()
except KeyboardInterrupt:
    print("\n")

# Clean shutdown
print("🛑 Stopping server...")
server.stop()
print("✅ Server stopped. Demo complete!")

