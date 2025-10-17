# zCLI/subsystems/zAuth/zAuth_modules/remote_auth.py

"""
zAuth/zAuth_modules/remote_auth.py
Remote API authentication
"""

import os


def authenticate_remote(zcli, username, password, server_url=None):
    """Authenticate via Flask API (remote server)."""
    logger = zcli.logger
    
    # Get server URL from environment or default
    if not server_url:
        server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
    
    # Authenticate via Flask API
    logger.info("[*] Authenticating with remote server: %s", server_url)
    
    try:
        result = zcli.comm.login(
            {"username": username, "password": password, "mode": "Terminal"},
            url=f"{server_url}/zAuth"
        )
        
        if result and result.get("status") == "success":
            user = result.get("user", {})
            
            # Store credentials locally
            credentials = {
                "username": user.get("username"),
                "api_key": user.get("api_key"),
                "role": user.get("role"),
                "user_id": user.get("id"),
                "server_url": server_url
            }
            
            logger.info("[OK] Remote authentication successful: %s (role=%s)", 
                      credentials["username"], credentials["role"])
            
            # Display success message
            zcli.display.handle({"event": "text", "content": ""})
            zcli.display.handle({"event": "text", "content": f"[OK] Logged in as: {credentials['username']} ({credentials['role']})"})
            zcli.display.handle({"event": "text", "content": f"     API Key: {credentials['api_key'][:20]}..."})
            zcli.display.handle({"event": "text", "content": f"     Server: {server_url}"})
            
            return {"status": "success", "credentials": credentials}
        
        else:
            logger.warning("[FAIL] Remote authentication failed")
            zcli.display.handle({"event": "text", "content": ""})
            zcli.display.handle({"event": "error", "content": "[FAIL] Authentication failed: Invalid credentials"})
            zcli.display.handle({"event": "text", "content": ""})
            return {"status": "fail", "reason": "Invalid credentials"}
    
    except Exception as e:
        logger.error("[ERROR] Remote authentication error: %s", e)
        zcli.display.handle({"event": "text", "content": ""})
        zcli.display.handle({"event": "error", "content": f"[ERROR] Error connecting to remote server: {e}"})
        zcli.display.handle({"event": "text", "content": ""})
        return {"status": "error", "reason": str(e)}

