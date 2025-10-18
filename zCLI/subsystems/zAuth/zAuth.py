# zCLI/subsystems/zAuth/zAuth.py
"""Authentication subsystem for zCLI - session-only authentication."""

from zCLI import os
from .zAuth_modules.remote_auth import authenticate_remote

class zAuth:
    """Authentication subsystem for zCLI - session-only (no persistence)."""

    def __init__(self, zcli):
        """Initialize authentication subsystem."""
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZAUTH"  # Orange-brown bg (Authentication)
        
        # Display ready message
        self.zcli.display.zDeclare("zAuth Ready", color=self.mycolor, indent=0, style="full")
    
    def login(self, username=None, password=None, server_url=None):
        """Authenticate user for this session only (no persistence)."""
        # Prompt for credentials if not provided using zDisplay events
        if not username or not password:
            creds = self.zcli.display.zEvents.zAuth.login_prompt(username, password)
            if creds:
                username = creds.get("username")
                password = creds.get("password")
            else:
                # GUI mode - credentials will be sent via bifrost
                return {"status": "pending", "reason": "Awaiting GUI response"}
        
        # Try remote authentication
        if os.getenv("ZOLO_USE_REMOTE_API", "false").lower() == "true":
            result = authenticate_remote(self.zcli, username, password, server_url)
            if result.get("status") == "success":
                # Update session with auth result
                credentials = result.get("credentials")
                if credentials and self.session:
                    self.session["zAuth"].update({
                        "id": credentials.get("user_id"),
                        "username": credentials.get("username"),
                        "role": credentials.get("role"),
                        "API_Key": credentials.get("api_key")
                    })
                    # Display success using zDisplay events
                    self.zcli.display.zEvents.zAuth.login_success({
                        "username": credentials.get("username"),
                        "role": credentials.get("role"),
                        "user_id": credentials.get("user_id"),
                        "api_key": credentials.get("api_key")
                    })
                return result
        
        # Authentication failed - use zDisplay events
        self.logger.warning("[FAIL] Authentication failed: Invalid credentials")
        self.zcli.display.zEvents.zAuth.login_failure("Invalid credentials")
        return {"status": "fail", "reason": "Invalid credentials"}
    
    def logout(self):
        """Clear session authentication and logout."""
        is_logged_in = self.is_authenticated()
        
        # Clear session auth
        if self.session:
            self.session["zAuth"] = {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        
        # Display using zDisplay events
        if is_logged_in:
            self.zcli.display.zEvents.zAuth.logout_success()
        else:
            self.zcli.display.zEvents.zAuth.logout_warning()
        
        return {"status": "success"}
    
    def status(self):
        """Show current authentication status."""
        if self.is_authenticated():
            auth_data = self.session["zAuth"]
            # Display using zDisplay events
            self.zcli.display.zEvents.zAuth.status_display(auth_data)
            return {"status": "authenticated", "user": auth_data}
        else:
            # Display using zDisplay events
            self.zcli.display.zEvents.zAuth.status_not_authenticated()
            return {"status": "not_authenticated"}
    
    def is_authenticated(self):
        """Check if user is currently authenticated in session."""
        return (self.session and 
                self.session.get("zAuth", {}).get("username") is not None and
                self.session.get("zAuth", {}).get("API_Key") is not None)
    
    def get_credentials(self):
        """Get current session authentication data."""
        if self.is_authenticated():
            return self.session["zAuth"]
        return None
    
