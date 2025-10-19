# zCLI/subsystems/zAuth/zAuth.py
"""Authentication subsystem for zCLI - session-only authentication."""

from zCLI import os


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
            result = self._authenticate_remote(username, password, server_url)
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
    
    def _authenticate_remote(self, username, password, server_url=None):
        """Authenticate via Flask API (remote server)."""
        # Get server URL from environment or default
        if not server_url:
            server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
        
        # Authenticate via Flask API
        self.logger.info("[*] Authenticating with remote server: %s", server_url)
        
        try:
            # Use zComm for pure HTTP communication
            response = self.zcli.comm.http_post(
                f"{server_url}/zAuth",
                data={"username": username, "password": password, "mode": "Terminal"}
            )
            
            if not response:
                return {"status": "fail", "reason": "Connection failed"}
                
            result = response.json()
            
            if result and result.get("status") == "success":
                user = result.get("user", {})
                
                # Prepare credentials for session (no persistence)
                credentials = {
                    "username": user.get("username"),
                    "api_key": user.get("api_key"),
                    "role": user.get("role"),
                    "user_id": user.get("id"),
                    "server_url": server_url
                }
                
                self.logger.info("[OK] Remote authentication successful: %s (role=%s)", 
                              credentials["username"], credentials["role"])
                
                # Display success message
                self.zcli.display.text("")
                self.zcli.display.success(f"[OK] Logged in as: {credentials['username']} ({credentials['role']})")
                self.zcli.display.text(f"     API Key: {credentials['api_key'][:20]}...", indent=1)
                self.zcli.display.text(f"     Server: {server_url}", indent=1)
                
                return {"status": "success", "credentials": credentials}
            
            self.logger.warning("[FAIL] Remote authentication failed")
            self.zcli.display.text("")
            self.zcli.display.error("[FAIL] Authentication failed: Invalid credentials")
            self.zcli.display.text("")
            return {"status": "fail", "reason": "Invalid credentials"}
        
        except Exception as e:
            self.logger.error("[ERROR] Remote authentication error: %s", e)
            self.zcli.display.text("")
            self.zcli.display.error(f"[ERROR] Error connecting to remote server: {e}")
            self.zcli.display.text("")
            return {"status": "error", "reason": str(e)}

