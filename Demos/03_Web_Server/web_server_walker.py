#!/usr/bin/env python3
"""Web Server Layer Demo - Declarative Routing + RBAC (v1.5.4 Phase 2)"""

from zCLI import zCLI

# Step 1: Import zCLI
# Step 2: Create spark
z = zCLI({
    "zWorkspace": ".",
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server",
    "zMode": "Terminal"
})

# Step 3: Create HTTP server with declarative routing
# Use absolute path for routes file  
routes_file = "/Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server/zServer_routes.yaml"

server = z.comm.create_http_server(
    port=8080,
    serve_path="/Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server/public",
    routes_file=routes_file  # Declarative routing!
)

# Start server in background
server.start()

# Display server info
print("\n" + "="*70)
print("🌐 zServer Demo - Declarative Routing + RBAC")
print("="*70)
print(f"📍 Server URL:   {server.get_url()}")
print(f"📊 Health:       {server.health_check()}")
print(f"📁 Serving:      {server.serve_path}")
print(f"🗺️  Routes File:  zServer_routes.yaml")
print("="*70)

# Show route information
print("\n📋 Declared Routes:")
print("   → /              (public)  →  index.html")
print("   → /test          (public)  →  test_page.html")
print("   → /secure        (zTester) →  secure_page.html [RBAC PROTECTED]")
print("   → /*             (public)  →  wildcard fallback")

# Show RBAC status
print("\n" + "="*70)
print("🔒 Role-Based Access Control")
print("="*70)

has_tester_role = z.auth.has_role("zTester")

print(f"📋 Role Check:   z.auth.has_role('zTester')")
print(f"📊 Result:       {has_tester_role}")
print(f"🎯 Enforcement:  Backend router (HTTPRouter + handler.py)")

if has_tester_role:
    print(f"✅ /secure:      GRANTED - User has zTester role")
else:
    print(f"❌ /secure:      DENIED - Redirects to access_denied.html")

print("="*70)

print("\n💡 How It Works:")
print("   1. Routes defined declaratively in zServer_routes.yaml")
print("   2. HTTPRouter matches incoming paths (/secure)")
print("   3. RBAC checked via z.auth.has_role('zTester')")
print("   4. Access denied → Serves access_denied.html")
print("   5. Auto-redirect countdown (10s) to home page")
print("   6. No manual Python checks - fully declarative!")

print("\n🔗 Try these URLs:")
print(f"   → {server.get_url()}/           (works)")
print(f"   → {server.get_url()}/test       (works)")
print(f"   → {server.get_url()}/secure     (denied → redirects)")

print("\n⌨️  Press Enter to stop server...\n")

# Wait for user input
try:
    input()
except KeyboardInterrupt:
    print("\n")

# Clean shutdown
print("🛑 Stopping server...")
server.stop()
print("✅ Server stopped. Declarative routing demo complete!")

