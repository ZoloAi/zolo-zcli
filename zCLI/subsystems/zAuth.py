# zCLI/subsystems/zAuth.py — Authentication Subsystem
# ───────────────────────────────────────────────────────────────

"""
Authentication subsystem for zCLI.

Handles:
- User login/logout
- Credential storage (~/.zolo/credentials)
- API key validation
- Authentication status checks
"""

import os
import json
from pathlib import Path
from getpass import getpass
from logger import Logger
from zCLI.subsystems.zSession import zSession_Login


class ZAuth:
    """
    Authentication subsystem for zCLI.
    
    Manages user authentication, credential storage, and API key validation.
    """
    
    def __init__(self, walker=None):
        """
        Initialize authentication subsystem.
        
        Args:
            walker: Parent zCLI instance
        """
        self.walker = walker
        self.zSession = walker.session if walker else None
        self.logger = Logger.get_logger()
        
        # Credentials file location
        self.credentials_dir = Path.home() / ".zolo"
        self.credentials_file = self.credentials_dir / "credentials"
        
        # Ensure credentials directory exists
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        
        # Note: Credentials are NOT automatically restored on initialization
        # Users must explicitly login to populate zSession authentication
    
    def login(self, username=None, password=None, server_url=None):
        """
        Authenticate user and store credentials locally.
        
        Args:
            username: Username (if None, prompt for it)
            password: Password (if None, prompt for it)
            server_url: Flask API URL (default from env or config)
        
        Returns:
            dict: Authentication result with status and user info
        """
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ").strip()
        if not password:
            password = getpass("Password: ")
        
        # Check for local backend admin user (for testing/development)
        local_result = self._authenticate_local(username, password)
        if local_result:
            self._save_credentials(local_result)
            
            # Update zSession with authenticated user info
            if self.zSession:
                self.zSession["zAuth"].update({
                    "id": local_result["user_id"],
                    "username": local_result["username"],
                    "role": local_result["role"],
                    "API_Key": local_result["api_key"]
                })
                logger.debug("Updated zSession['zAuth']: %s", self.zSession["zAuth"])
            
            logger.info("[OK] Local authentication successful: %s (role=%s)", 
                      local_result["username"], local_result["role"])
            
            print(f"\n[OK] Logged in as: {local_result['username']} ({local_result['role']})")
            print(f"     User ID: {local_result['user_id']}")
            print(f"     API Key: {local_result['api_key'][:20]}...")
            print(f"     Mode: Local (development)")
            print(f"     Credentials saved to: {self.credentials_file}\n")
            
            return {"status": "success", "user": local_result}
        
        # If local auth fails, try Flask API (if configured)
        if os.getenv("ZOLO_USE_REMOTE_API", "false").lower() == "true":
            return self._authenticate_remote(username, password, server_url)
        
        # No valid authentication method
        logger.warning("[FAIL] Authentication failed: Invalid credentials")
        print("\n[FAIL] Authentication failed: Invalid credentials")
        print("       No authentication method available\n")
        return {"status": "fail", "reason": "Invalid credentials"}
    
    def _authenticate_local(self, username, password):
        """
        Authenticate against local backend (disabled - no hardcoded users).
        
        Args:
            username: Username
            password: Password
        
        Returns:
            None: Always returns None as hardcoded users have been removed
        """
        # Hardcoded users have been removed for security
        # Authentication must go through proper backend systems
        logger.debug("Local authentication disabled - no hardcoded users available")
        return None
    
    def _authenticate_remote(self, username, password, server_url=None):
        """
        Authenticate via Flask API (remote server).
        
        Args:
            username: Username
            password: Password
            server_url: Flask API URL
        
        Returns:
            dict: Authentication result
        """
        # Get server URL from environment or default
        if not server_url:
            server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
        
        # Authenticate via Flask API
        logger.info("[*] Authenticating with remote server: %s", server_url)
        
        try:
            result = zSession_Login(
                {"username": username, "password": password, "mode": "Terminal"},
                url=f"{server_url}/zAuth",
                session=self.zSession
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
                
                self._save_credentials(credentials)
                
                logger.info("[OK] Remote authentication successful: %s (role=%s)", 
                          credentials["username"], credentials["role"])
                
                print(f"\n[OK] Logged in as: {credentials['username']} ({credentials['role']})")
                print(f"     API Key: {credentials['api_key'][:20]}...")
                print(f"     Server: {server_url}")
                print(f"     Credentials saved to: {self.credentials_file}\n")
                
                return {"status": "success", "user": credentials}
            
            else:
                logger.warning("[FAIL] Remote authentication failed")
                print("\n[FAIL] Authentication failed: Invalid credentials\n")
                return {"status": "fail", "reason": "Invalid credentials"}
        
        except Exception as e:
            logger.error("[ERROR] Remote authentication error: %s", e)
            print(f"\n[ERROR] Error connecting to remote server: {e}\n")
            return {"status": "error", "reason": str(e)}
    
    def logout(self):
        """
        Clear stored credentials and logout.
        
        Returns:
            dict: Logout status
        """
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                logger.info("[*] Logged out - credentials removed")
                print("\n[OK] Logged out successfully\n")
            else:
                print("\n[WARN] Not currently logged in\n")
            
            # Clear session auth
            if self.zSession:
                self.zSession["zAuth"] = {
                    "id": None,
                    "username": None,
                    "role": None,
                    "API_Key": None
                }
            
            return {"status": "success"}
        
        except Exception as e:
            logger.error("Error during logout: %s", e)
            return {"status": "error", "reason": str(e)}
    
    def status(self):
        """
        Show current authentication status.
        
        Returns:
            dict: Current user info or None
        """
        credentials = self._load_credentials()
        
        if credentials:
            print("\n[*] Authentication Status")
            print("═" * 50)
            print(f"Username:   {credentials.get('username')}")
            print(f"Role:       {credentials.get('role')}")
            print(f"User ID:    {credentials.get('user_id')}")
            print(f"API Key:    {credentials.get('api_key', '')[:20]}...")
            print(f"Server:     {credentials.get('server_url')}")
            print("═" * 50 + "\n")
            
            return {"status": "authenticated", "user": credentials}
        else:
            print("\n[WARN] Not authenticated. Run 'auth login' to authenticate.\n")
            return {"status": "not_authenticated"}
    
    def is_authenticated(self):
        """
        Check if user is currently authenticated.
        
        Returns:
            bool: True if authenticated with valid credentials
        """
        credentials = self._load_credentials()
        return credentials is not None and credentials.get("api_key") is not None
    
    def get_credentials(self):
        """
        Get stored credentials.
        
        Returns:
            dict: Credentials or None
        """
        return self._load_credentials()
    
    def validate_api_key(self, api_key=None, server_url=None):
        """
        Validate API key against server.
        
        Args:
            api_key: API key to validate (if None, use stored)
            server_url: Server URL (if None, use stored)
        
        Returns:
            dict: Validation result
        """
        if not api_key:
            credentials = self._load_credentials()
            if not credentials:
                return {"valid": False, "reason": "No credentials found"}
            api_key = credentials.get("api_key")
            server_url = credentials.get("server_url")
        
        if not server_url:
            server_url = os.getenv("ZOLO_API_URL", "http://localhost:5000")
        
        try:
            # Validate via Flask API (using zData subsystem)
            if not self.walker:
                logger.error("Cannot validate API key: No zCLI instance available")
                return {"valid": False, "reason": "No zCLI instance"}
            
            result = self.walker.data.handle_request({
                "action": "read",
                "model": "@.zCloud.schemas.schema.zIndex.zUsers",
                "fields": ["id", "username", "role"],
                "filters": {"api_key": api_key},
                "limit": 1
            })
            
            if result and len(result) > 0:
                user = result[0]
                logger.info("[OK] API key validated for: %s", user.get("username"))
                return {"valid": True, "user": user}
            else:
                logger.warning("[FAIL] Invalid API key")
                return {"valid": False, "reason": "Invalid API key"}
        
        except Exception as e:
            logger.error("Error validating API key: %s", e)
            return {"valid": False, "reason": str(e)}
    
    def _save_credentials(self, credentials):
        """Save credentials to local file."""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Set file permissions to user-only (600)
            os.chmod(self.credentials_file, 0o600)
            
            logger.debug("Credentials saved to: %s", self.credentials_file)
        
        except Exception as e:
            logger.error("Error saving credentials: %s", e)
            raise
    
    def _load_credentials(self):
        """Load credentials from local file."""
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            logger.debug("Credentials loaded from: %s", self.credentials_file)
            return credentials
        
        except Exception as e:
            logger.error("Error loading credentials: %s", e)
            return None
    
    def _restore_session_from_credentials(self):
        """
        Restore zSession authentication from saved credentials file.
        Called on initialization to restore previous login state.
        """
        if not self.zSession:
            return
        
        credentials = self._load_credentials()
        if credentials:
            # Update zSession with saved credentials
            self.zSession["zAuth"].update({
                "id": credentials.get("user_id"),
                "username": credentials.get("username"),
                "role": credentials.get("role"),
                "API_Key": credentials.get("api_key")
            })
            
            logger.debug("Restored zSession from saved credentials: %s", 
                        credentials.get("username"))


# ═══════════════════════════════════════════════════════════════════
# Standalone authentication function
# ═══════════════════════════════════════════════════════════════════

def check_authentication(zcli):
    """
    Check if user is authenticated, prompt if not.
    
    Args:
        zcli: zCLI instance
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not hasattr(zcli, 'auth') or not zcli.auth.is_authenticated():
        print("\n[*] Authentication Required")
        print("═" * 50)
        print("zCLI requires authentication to use.")
        print("Please login with your Zolo credentials.")
        print("═" * 50 + "\n")
        
        # Prompt for login
        choice = input("Login now? (y/n): ").strip().lower()
        if choice == 'y':
            result = zcli.auth.login()
            return result.get("status") == "success"
        else:
            print("\n[X] Authentication required. Exiting.\n")
            return False
    
    return True

