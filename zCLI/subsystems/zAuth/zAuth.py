# zCLI/subsystems/zAuth/zAuth.py
"""Authentication subsystem for zCLI."""

from zCLI import os
from getpass import getpass
from .zAuth_modules.credentials import CredentialManager
from .zAuth_modules.local_auth import authenticate_local
from .zAuth_modules.remote_auth import authenticate_remote
from .zAuth_modules.validation import validate_api_key as validate_key


class zAuth:
    """Authentication subsystem for zCLI."""

    def __init__(self, zcli):
        """Initialize authentication subsystem."""
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZAUTH"  # Orange-brown bg (Authentication)

        # Credential manager
        self.credentials = CredentialManager()
        
        # Display ready message
        self.zcli.display.handle({
            "event": "sysmsg",
            "label": "zAuth Ready",
            "style": "full",
            "color": self.mycolor,
            "indent": 0
        })
        
        # Note: Authentication is session-only (no persistence)
        # Users must login each session to populate zSession authentication
    
    def login(self, username=None, password=None, server_url=None):
        """Authenticate user for this session only (no persistence)."""
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ").strip()
        if not password:
            password = getpass("Password: ")
        
        # Check for local backend admin user (for testing/development)
        # pylint: disable=unsubscriptable-object,assignment-from-none
        local_result = authenticate_local(username, password, self.logger)
        if local_result:
            # Update zSession with authenticated user info (session only)
            if self.session:
                self.session["zAuth"].update({
                    "id": local_result["user_id"],
                    "username": local_result["username"],
                    "role": local_result["role"],
                    "API_Key": local_result["api_key"]
                })
                self.logger.debug("Updated zSession['zAuth']: %s", self.session["zAuth"])
            
            self.logger.info("[OK] Local authentication successful: %s (role=%s)", 
                      local_result["username"], local_result["role"])
            
            # Display success message
            self.zcli.display.handle({"event": "text", "content": ""})
            self.zcli.display.handle({"event": "text", "content": f"[OK] Logged in as: {local_result['username']} ({local_result['role']})"})
            self.zcli.display.handle({"event": "text", "content": f"     User ID: {local_result['user_id']}"})
            self.zcli.display.handle({"event": "text", "content": f"     API Key: {local_result['api_key'][:20]}..."})
            self.zcli.display.handle({"event": "text", "content": "     Mode: Local (development)"})
            self.zcli.display.handle({"event": "text", "content": "     Session: This session only (no persistence)"})
            self.zcli.display.handle({"event": "text", "content": ""})
            
            return {"status": "success", "user": local_result}
        
        # If local auth fails, try Flask API (if configured)
        if os.getenv("ZOLO_USE_REMOTE_API", "false").lower() == "true":
            result = authenticate_remote(self.zcli, username, password, server_url)
            if result.get("status") == "success":
                # Update session with remote auth result (no persistence)
                credentials = result.get("credentials")
                if credentials and self.session:
                    self.session["zAuth"].update({
                        "id": credentials.get("user_id"),
                        "username": credentials.get("username"),
                        "role": credentials.get("role"),
                        "API_Key": credentials.get("api_key")
                    })
                self.zcli.display.handle({"event": "text", "content": "     Session: This session only (no persistence)"})
                self.zcli.display.handle({"event": "text", "content": ""})
            return result
        
        # No valid authentication method
        self.logger.warning("[FAIL] Authentication failed: Invalid credentials")
        self.zcli.display.handle({"event": "text", "content": ""})
        self.zcli.display.handle({"event": "error", "content": "[FAIL] Authentication failed: Invalid credentials"})
        self.zcli.display.handle({"event": "text", "content": "       No authentication method available"})
        self.zcli.display.handle({"event": "text", "content": ""})
        return {"status": "fail", "reason": "Invalid credentials"}
    
    def logout(self):
        """Clear session authentication and logout."""
        try:
            # Check if currently authenticated in session
            is_logged_in = (self.session and 
                          self.session.get("zAuth", {}).get("username") is not None)
            
            # Clear session auth
            if self.session:
                self.session["zAuth"] = {
                    "id": None,
                    "username": None,
                    "role": None,
                    "API_Key": None
                }
            
            if is_logged_in:
                self.zcli.display.handle({"event": "text", "content": ""})
                self.zcli.display.handle({"event": "text", "content": "[OK] Logged out successfully"})
                self.zcli.display.handle({"event": "text", "content": ""})
            else:
                self.zcli.display.handle({"event": "text", "content": ""})
                self.zcli.display.handle({"event": "warning", "content": "[WARN] Not currently logged in"})
                self.zcli.display.handle({"event": "text", "content": ""})
            
            return {"status": "success"}
        
        except Exception as e:
            self.logger.error("Error during logout: %s", e)
            return {"status": "error", "reason": str(e)}
    
    def status(self):
        """Show current authentication status."""
        # Check session authentication instead of persisted credentials
        if self.session and self.session.get("zAuth", {}).get("username"):
            auth_data = self.session["zAuth"]
            self.zcli.display.handle({"event": "text", "content": ""})
            self.zcli.display.handle({"event": "text", "content": "[*] Authentication Status"})
            self.zcli.display.handle({"event": "text", "content": "═" * 50})
            self.zcli.display.handle({"event": "text", "content": f"Username:   {auth_data.get('username')}"})
            self.zcli.display.handle({"event": "text", "content": f"Role:       {auth_data.get('role')}"})
            self.zcli.display.handle({"event": "text", "content": f"User ID:    {auth_data.get('id')}"})
            self.zcli.display.handle({"event": "text", "content": f"API Key:    {auth_data.get('API_Key', '')[:20]}..."})
            self.zcli.display.handle({"event": "text", "content": "Session:    Current session only (no persistence)"})
            self.zcli.display.handle({"event": "text", "content": "═" * 50})
            self.zcli.display.handle({"event": "text", "content": ""})
            
            return {"status": "authenticated", "user": auth_data}
        else:
            self.zcli.display.handle({"event": "text", "content": ""})
            self.zcli.display.handle({"event": "warning", "content": "[WARN] Not authenticated. Run 'auth login' to authenticate."})
            self.zcli.display.handle({"event": "text", "content": ""})
            return {"status": "not_authenticated"}
    
    def is_authenticated(self):
        """Check if user is currently authenticated in session."""
        return (self.session and 
                self.session.get("zAuth", {}).get("username") is not None and
                self.session.get("zAuth", {}).get("API_Key") is not None)
    
    def get_credentials(self):
        """Get current session authentication data."""
        if (self.session and 
            self.session.get("zAuth") and 
            self.session.get("zAuth", {}).get("username") is not None):
            return self.session["zAuth"]
        return None
    
    def validate_api_key(self, api_key=None, server_url=None):
        """Validate API key against server."""
        if not api_key:
            # Get API key from session instead of persisted credentials
            if self.session and self.session.get("zAuth", {}).get("API_Key"):
                api_key = self.session["zAuth"]["API_Key"]
            else:
                return {"valid": False, "reason": "No API key found in session"}
        
        if not server_url:
            server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
        
        return validate_key(self.zcli, api_key, server_url)
    
