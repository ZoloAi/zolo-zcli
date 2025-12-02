# ═══════════════════════════════════════════════════════════
# Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_secure.py
# ═══════════════════════════════════════════════════════════
"""
Level 2.iii - Secure WebSocket Connections

This demo shows how to add authentication to your WebSocket server using:
- Token-based authentication (from .zEnv file)
- Origin validation (CORS/CSRF protection)
- Connection rejection for unauthorized clients

Key Features:
    - require_auth: True → Enables token validation
    - allowed_origins → Whitelist for CORS protection
    - WEBSOCKET_TOKEN → Store tokens securely in .zEnv

What you'll discover:
    - How to enable WebSocket security
    - How to store tokens in .zEnv (never hardcode!)
    - How clients connect with authentication
    - How zCLI rejects unauthorized connections automatically
"""

from zCLI import zCLI

# ═══════════════════════════════════════════════════════════
# zSpark Configuration (Production-ready with authentication)
# ═══════════════════════════════════════════════════════════

zSpark = {
    "deployment": "Production",
    "title": "websocket-secure",
    "logger": "INFO",
    "logger_path": "./logs",
    "websocket": {
        "require_auth": True,  # 🔒 Enable authentication
        "allowed_origins": [
            "http://localhost",
            "http://127.0.0.1",
            "file://",  # Allow local HTML files
        ],
    }
}

z = zCLI(zSpark)

# ═══════════════════════════════════════════════════════════
# Secure Echo Handler (Only authenticated clients can echo)
# ═══════════════════════════════════════════════════════════

async def secure_echo_handler(websocket, message):
    """Echo messages from authenticated clients only."""
    # Get client auth info
    auth_info = z.comm.websocket.auth.get_client_info(websocket)
    client_addr = auth_info.get('addr', 'unknown') if auth_info else 'unknown'
    
    # Echo message with client identifier
    echo_msg = f"[Secure Echo from {client_addr}]: {message}"
    await websocket.send(echo_msg)

# ═══════════════════════════════════════════════════════════
# Start Secure Server
# ═══════════════════════════════════════════════════════════

print("\n📍 Starting secure WebSocket server (requires authentication)...")
print("   → Clients MUST provide token in URL: ws://127.0.0.1:8765?token=YOUR_TOKEN")
print("   → Token is stored in .zEnv file (WEBSOCKET_TOKEN=demo_secure_token_123)")
print("   → Open 3_client_secure.html to test with correct token")
print("   → Connections without valid token will be rejected")
print("\n⏳ Server running on ws://127.0.0.1:8765 (Press Ctrl+C to stop)")
print("=" * 70)

z.comm.websocket.start(host="127.0.0.1", port=8765, handler=secure_echo_handler)

