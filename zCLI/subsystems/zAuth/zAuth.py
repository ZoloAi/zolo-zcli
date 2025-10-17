# zCLI/subsystems/zAuth/zAuth.py

# zCLI/subsystems/zAuth.py — Authentication Subsystem
# ───────────────────────────────────────────────────────────────

"""Authentication subsystem for zCLI."""

import os
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
        
        # Note: Credentials are NOT automatically restored on initialization
        # Users must explicitly login to populate zSession authentication
    
    def login(self, username=None, password=None, server_url=None):
        """Authenticate user and store credentials locally."""
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ").strip()
        if not password:
            password = getpass("Password: ")
        
        # Check for local backend admin user (for testing/development)
        # pylint: disable=unsubscriptable-object,assignment-from-none
        local_result = authenticate_local(username, password, self.logger)
        if local_result:
            self.credentials.save(local_result, self.logger)
            
            # Update zSession with authenticated user info
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
            self.zcli.display.handle({"event": "text", "content": f"     Credentials saved to: {self.credentials.credentials_file}"})
            self.zcli.display.handle({"event": "text", "content": ""})
            
            return {"status": "success", "user": local_result}
        
        # If local auth fails, try Flask API (if configured)
        if os.getenv("ZOLO_USE_REMOTE_API", "false").lower() == "true":
            result = authenticate_remote(self.zcli, username, password, server_url)
            if result.get("status") == "success":
                # Save credentials and show path
                credentials = result.get("credentials")
                self.credentials.save(credentials, self.logger)
                self.zcli.display.handle({"event": "text", "content": f"     Credentials saved to: {self.credentials.credentials_file}"})
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
        """Clear stored credentials and logout."""
        try:
            if self.credentials.delete(self.logger):
                self.zcli.display.handle({"event": "text", "content": ""})
                self.zcli.display.handle({"event": "text", "content": "[OK] Logged out successfully"})
                self.zcli.display.handle({"event": "text", "content": ""})
            else:
                self.zcli.display.handle({"event": "text", "content": ""})
                self.zcli.display.handle({"event": "warning", "content": "[WARN] Not currently logged in"})
                self.zcli.display.handle({"event": "text", "content": ""})
            
            # Clear session auth
            if self.session:
                self.session["zAuth"] = {
                    "id": None,
                    "username": None,
                    "role": None,
                    "API_Key": None
                }
            
            return {"status": "success"}
        
        except Exception as e:
            self.logger.error("Error during logout: %s", e)
            return {"status": "error", "reason": str(e)}
    
    def status(self):
        """Show current authentication status."""
        creds = self.credentials.load(self.logger)
        
        if creds:
            self.zcli.display.handle({"event": "text", "content": ""})
            self.zcli.display.handle({"event": "text", "content": "[*] Authentication Status"})
            self.zcli.display.handle({"event": "text", "content": "═" * 50})
            self.zcli.display.handle({"event": "text", "content": f"Username:   {creds.get('username')}"})
            self.zcli.display.handle({"event": "text", "content": f"Role:       {creds.get('role')}"})
            self.zcli.display.handle({"event": "text", "content": f"User ID:    {creds.get('user_id')}"})
            self.zcli.display.handle({"event": "text", "content": f"API Key:    {creds.get('api_key', '')[:20]}..."})
            self.zcli.display.handle({"event": "text", "content": f"Server:     {creds.get('server_url')}"})
            self.zcli.display.handle({"event": "text", "content": "═" * 50})
            self.zcli.display.handle({"event": "text", "content": ""})
            
            return {"status": "authenticated", "user": creds}
        else:
            self.zcli.display.handle({"event": "text", "content": ""})
            self.zcli.display.handle({"event": "warning", "content": "[WARN] Not authenticated. Run 'auth login' to authenticate."})
            self.zcli.display.handle({"event": "text", "content": ""})
            return {"status": "not_authenticated"}
    
    def is_authenticated(self):
        """Check if user is currently authenticated."""
        creds = self.credentials.load(self.logger)
        return creds is not None and creds.get("api_key") is not None
    
    def get_credentials(self):
        """Get stored credentials."""
        return self.credentials.load(self.logger)
    
    def validate_api_key(self, api_key=None, server_url=None):
        """Validate API key against server."""
        if not api_key:
            creds = self.credentials.load(self.logger)
            if not creds:
                return {"valid": False, "reason": "No credentials found"}
            api_key = creds.get("api_key")
            server_url = creds.get("server_url")
        
        if not server_url:
            server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
        
        return validate_key(self.zcli, api_key, server_url)
    
    def restore_session(self):
        """Restore zSession authentication from saved credentials file."""
        self.credentials.restore_to_session(self.session, self.logger)
