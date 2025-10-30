"""
Authentication Module - User authentication and session management (v1.5.4+)

This module handles user authentication (local and remote),
session management, and authentication status checks.

Supports three-tier authentication with multi-app capability:

Layer 1 - zSession Auth:
  - Internal zCLI/Zolo users
  - Authenticated via zcli.auth.login()
  - session["zAuth"]["zSession"] contains user credentials
  - Used for zCLI features, premium plugins, Zolo cloud services

Layer 2 - Application Auth (Multi-App Support):
  - External users of applications BUILT on zCLI
  - Authenticated via zcli.auth.authenticate_app_user(app_name, token, config)
  - session["zAuth"]["applications"][app_name] contains app-specific credentials
  - Multiple apps can be authenticated simultaneously
  - Each app can have different user identity, credentials, and permissions
  - Configurable user model per application

Layer 3 - Dual-Auth:
  - Both zSession AND application contexts active simultaneously
  - session["zAuth"]["active_context"] = "dual"
  - session["zAuth"]["dual_mode"] = True
  - Example: Store owner using zCLI analytics on their store

Context Management:
  - session["zAuth"]["active_context"]: "zSession", "application", or "dual"
  - session["zAuth"]["active_app"]: Which app is currently focused (multi-app)
  - session["zAuth"]["dual_mode"]: True if both zSession and app auth active
"""

from zCLI import os, Dict, Optional, Any
from zCLI.subsystems.zConfig.zConfig_modules import (
    ZAUTH_KEY_ZSESSION,
    ZAUTH_KEY_APPLICATIONS,    # Multi-app support
    ZAUTH_KEY_ACTIVE_APP,      # Tracks focused app
    ZAUTH_KEY_AUTHENTICATED,
    ZAUTH_KEY_ID,
    ZAUTH_KEY_USERNAME,
    ZAUTH_KEY_ROLE,
    ZAUTH_KEY_API_KEY,
    ZAUTH_KEY_ACTIVE_CONTEXT,
    ZAUTH_KEY_DUAL_MODE,
    CONTEXT_ZSESSION,
    CONTEXT_APPLICATION,
    CONTEXT_DUAL
)


class Authentication:
    """
    User authentication and session management with multi-app support.
    
    Features:
    - Local and remote authentication (zSession - Layer 1)
    - Application-level authentication (Layer 2)
    - Multi-app simultaneous authentication
    - Context-aware session management (zSession, application, dual)
    - Login/logout operations (context-aware)
    - Authentication status checks
    - Integration with zDisplay for UX
    
    Methods:
        Layer 1 (zSession Auth):
            - login(): Authenticate zCLI/Zolo user
            - is_authenticated(): Check if zSession authenticated
            - get_credentials(): Get zSession credentials
        
        Layer 2 (Application Auth):
            - authenticate_app_user(): Authenticate to specific app
            - switch_app(): Switch between authenticated apps
            - get_app_user(): Get app-specific credentials
        
        Context Management:
            - set_active_context(): Switch between zSession/application/dual
            - get_active_user(): Get current active user
        
        Logout:
            - logout(): Context-aware logout (zSession, app, all_apps, all)
    """
    
    def __init__(self, zcli):
        """Initialize authentication module.
        
        Args:
            zcli: zCLI instance (provides access to session, display, comm, logger)
        """
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
    
    def login(self, username=None, password=None, server_url=None, persist=True):
        """Authenticate user and optionally persist session.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            server_url: Optional remote server URL
            persist: If True, save session to sessions.db (default: True)
        
        Returns:
            dict: {"status": "success"|"fail"|"pending", ...}
        """
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
            result = self.authenticate_remote(username, password, server_url)
            if result.get("status") == "success":
                # Update session with auth result (zSession context)
                credentials = result.get("credentials")
                if credentials and self.session:
                    self.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
                        ZAUTH_KEY_AUTHENTICATED: True,
                        ZAUTH_KEY_ID: credentials.get("user_id"),
                        ZAUTH_KEY_USERNAME: credentials.get("username"),
                        ZAUTH_KEY_ROLE: credentials.get("role"),
                        ZAUTH_KEY_API_KEY: credentials.get("api_key")
                    })
                    # Set active context to zSession
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_ZSESSION
                    # Display success using zDisplay events
                    self.zcli.display.zEvents.zAuth.login_success({
                        "username": credentials.get("username"),
                        "role": credentials.get("role"),
                        "user_id": credentials.get("user_id"),
                        "api_key": credentials.get("api_key")
                    })
                    
                    # Return with persist flag for caller to handle
                    result["persist"] = persist
                    result["password"] = password  # For hashing by caller
                return result
        
        # Authentication failed - use zDisplay events
        self.logger.warning("[FAIL] Authentication failed: Invalid credentials")
        self.zcli.display.zEvents.zAuth.login_failure("Invalid credentials")
        return {"status": "fail", "reason": "Invalid credentials"}
    
    def logout(self, context: str = "zSession", app_name: Optional[str] = None, delete_persistent: bool = True) -> Dict[str, Any]:
        """Clear session authentication (context-aware, multi-app support).
        
        Args:
            context: What to logout from:
                - "zSession": Logout from zCLI/Zolo (default)
                - "application": Logout from specific app (requires app_name)
                - "all_apps": Logout from all applications
                - "all": Logout from everything (zSession + all apps)
            app_name: Required if context="application" - which app to logout from
            delete_persistent: If True, also delete persistent session from DB (zSession only)
        
        Returns:
            dict: {"status": "success", "context": str, "cleared": list}
        
        Example:
            # Logout from zCLI
            zcli.auth.logout("zSession")
            
            # Logout from specific app
            zcli.auth.logout("application", "ecommerce_store")
            
            # Logout from all apps (keep zSession)
            zcli.auth.logout("all_apps")
            
            # Logout from everything
            zcli.auth.logout("all")
        """
        if not self.session:
            return {"status": "error", "reason": "No session available"}
        
        cleared = []
        
        # Check if user is logged in before any logout operations
        is_logged_in = self.is_authenticated()
        
        # Logout from zSession
        if context in ["zSession", "all"]:
            username = self.session.get("zAuth", {}).get(ZAUTH_KEY_ZSESSION, {}).get(ZAUTH_KEY_USERNAME)
            
            self.session["zAuth"][ZAUTH_KEY_ZSESSION] = {
                ZAUTH_KEY_AUTHENTICATED: False,
                ZAUTH_KEY_ID: None,
                ZAUTH_KEY_USERNAME: None,
                ZAUTH_KEY_ROLE: None,
                ZAUTH_KEY_API_KEY: None
            }
            
            # Clear active context if it was zSession
            if self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_CONTEXT) == CONTEXT_ZSESSION:
                self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = None
            
            # If dual mode, switch to application context if apps exist
            if self.session["zAuth"].get(ZAUTH_KEY_DUAL_MODE):
                apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
                if apps:
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_APPLICATION
                    self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = False
                else:
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = None
                    self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = False
            
            cleared.append(f"zSession ({username})")
            
            # Delete persistent session if requested
            if delete_persistent and username:
                try:
                    if hasattr(self.zcli, 'data') and self.zcli.data.handler:
                        self.zcli.data.delete(
                            table="sessions",
                            where=f"username = '{username}'"
                        )
                        self.logger.debug(f"[SessionPersistence] Deleted persistent session for: {username}")
                except Exception as e:
                    self.logger.debug(f"[SessionPersistence] Could not delete session: {e}")
            
        # Display using zDisplay events
        if is_logged_in:
            self.zcli.display.zEvents.zAuth.logout_success()
        else:
            self.zcli.display.zEvents.zAuth.logout_warning()
        
        # Logout from specific application
        if context == "application":
            if not app_name:
                return {"status": "error", "reason": "app_name required for application logout"}
            
            apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
            if app_name in apps:
                app_username = apps[app_name].get(ZAUTH_KEY_USERNAME)
                del self.session["zAuth"][ZAUTH_KEY_APPLICATIONS][app_name]
                cleared.append(f"application/{app_name} ({app_username})")
                
                # If this was the active app, clear it
                if self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_APP) == app_name:
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_APP] = None
                    
                    # If no more apps, clear application context
                    if not self.session["zAuth"][ZAUTH_KEY_APPLICATIONS]:
                        if self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_CONTEXT) == CONTEXT_APPLICATION:
                            self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = None
                        self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = False
                
                self.logger.info(f"[OK] Logged out from application: {app_name}")
            else:
                return {"status": "error", "reason": f"Not authenticated to {app_name}"}
        
        # Logout from all applications
        if context in ["all_apps", "all"]:
            apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
            for app_name, app_data in apps.items():
                app_username = app_data.get(ZAUTH_KEY_USERNAME)
                cleared.append(f"application/{app_name} ({app_username})")
            
            self.session["zAuth"][ZAUTH_KEY_APPLICATIONS] = {}
            self.session["zAuth"][ZAUTH_KEY_ACTIVE_APP] = None
            
            # Update context
            if self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_CONTEXT) in [CONTEXT_APPLICATION, CONTEXT_DUAL]:
                # If zSession still authenticated, switch to it
                if self.session["zAuth"][ZAUTH_KEY_ZSESSION].get(ZAUTH_KEY_AUTHENTICATED):
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_ZSESSION
                else:
                    self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = None
            
            self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = False
            
            self.logger.info(f"[OK] Logged out from all applications ({len(apps)} apps)")
        
        return {
            "status": "success",
            "context": context,
            "cleared": cleared,
            "delete_persistent": delete_persistent if context in ["zSession", "all"] else False
        }
    
    def status(self):
        """Show current authentication status.
        
        Returns:
            dict: {"status": "authenticated"|"not_authenticated", "user": {...}}
        """
        if self.is_authenticated():
            # Get zSession auth data (primary authentication context)
            auth_data = self.session["zAuth"][ZAUTH_KEY_ZSESSION]
            # Display using zDisplay events
            self.zcli.display.zEvents.zAuth.status_display(auth_data)
            return {"status": "authenticated", "user": auth_data}
        else:
            # Display using zDisplay events
            self.zcli.display.zEvents.zAuth.status_not_authenticated()
            return {"status": "not_authenticated"}
    
    def is_authenticated(self):
        """Check if user is currently authenticated in zSession context.
        
        Returns:
            bool: True if zSession authenticated, False otherwise
        """
        if not self.session:
            return False
        
        zsession = self.session.get("zAuth", {}).get(ZAUTH_KEY_ZSESSION, {})
        return (zsession.get(ZAUTH_KEY_AUTHENTICATED, False) and 
                zsession.get(ZAUTH_KEY_USERNAME) is not None)
    
    def get_credentials(self):
        """Get current zSession authentication data.
        
        Returns:
            dict: zSession auth data if authenticated, None otherwise
        """
        if self.is_authenticated():
            return self.session["zAuth"][ZAUTH_KEY_ZSESSION]
        return None
    
    # ═══════════════════════════════════════════════════════════
    # Multi-App Authentication Methods (Layer 2)
    # ═══════════════════════════════════════════════════════════
    
    def authenticate_app_user(self, app_name: str, token: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Authenticate user to a specific application (Layer 2 auth).
        
        Supports multiple simultaneous application authentications in one session.
        Each app can have its own user identity, credentials, and permissions.
        
        Args:
            app_name: Application identifier (e.g., "ecommerce_store", "analytics_dashboard")
            token: API key/token to validate against app's user database
            config: Optional auth configuration dict:
                {
                    "user_model": "@.store_users.users",  # zData model path
                    "id_field": "id",                      # Field name for user ID
                    "username_field": "email",             # Field name for username
                    "role_field": "role",                  # Field name for role
                    "api_key_field": "api_key"             # Field name for API key
                }
        
        Returns:
            dict: {"status": "success"|"fail"|"error", "app_name": str, "user": dict}
        
        Example:
            # Store owner authenticates to their eCommerce store
            result = zcli.auth.authenticate_app_user(
                "ecommerce_store",
                "store_token_xyz",
                {"user_model": "@.store_users.users"}
            )
            
            # Later, same owner authenticates to analytics dashboard
            result = zcli.auth.authenticate_app_user(
                "analytics_dashboard",
                "analytics_token_abc",
                {"user_model": "@.analytics_users.users"}
            )
            
            # Both authentications persist simultaneously!
        """
        if not self.session:
            return {"status": "error", "reason": "No session available"}
        
        # Default configuration
        default_config = {
            "user_model": "@.zCloud.schemas.schema.zIndex.zUsers",
            "id_field": "id",
            "username_field": "username",
            "role_field": "role",
            "api_key_field": "api_key"
        }
        
        # Merge with provided config
        auth_config = {**default_config, **(config or {})}  # pylint: disable=unused-variable  # For future zData integration
        
        try:
            # TODO: Query application user database using zData  # pylint: disable=fixme
            # For now, this is a placeholder that would be implemented with actual zData integration
            # user_data = self.zcli.data.query(
            #     auth_config["user_model"],
            #     where={auth_config["api_key_field"]: token}
            # )
            
            # Placeholder: Simulate successful authentication
            # In production, this would validate token against the user model
            user_data = {
                ZAUTH_KEY_AUTHENTICATED: True,
                ZAUTH_KEY_ID: 12345,  # Would come from database
                ZAUTH_KEY_USERNAME: f"user_from_{app_name}",  # Would come from database
                ZAUTH_KEY_ROLE: "user",  # Would come from database
                ZAUTH_KEY_API_KEY: token
            }
            
            # Store authentication in applications dict
            self.session["zAuth"][ZAUTH_KEY_APPLICATIONS][app_name] = user_data
            
            # Set active app
            self.session["zAuth"][ZAUTH_KEY_ACTIVE_APP] = app_name
            
            # Update active context
            zsession_auth = self.session["zAuth"][ZAUTH_KEY_ZSESSION].get(ZAUTH_KEY_AUTHENTICATED, False)
            if zsession_auth:
                # Both zSession and application authenticated → dual mode
                self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_DUAL
                self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = True
            else:
                # Only application authenticated
                self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_APPLICATION
                self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = False
            
            self.logger.info(
                f"[OK] Application user authenticated: {app_name} "
                f"(username={user_data[ZAUTH_KEY_USERNAME]}, "
                f"context={self.session['zAuth'][ZAUTH_KEY_ACTIVE_CONTEXT]})"
            )
            
            return {
                "status": "success",
                "app_name": app_name,
                "user": user_data,
                "context": self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT]
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] Application authentication failed for {app_name}: {e}")
            return {
                "status": "error",
                "app_name": app_name,
                "reason": str(e)
            }
    
    def switch_app(self, app_name: str) -> bool:
        """Switch focus to a different authenticated application.
        
        Args:
            app_name: Name of the application to switch to
        
        Returns:
            bool: True if successful, False if app not authenticated
        
        Example:
            # User has multiple apps authenticated
            zcli.auth.switch_app("ecommerce_store")  # Switch to store
            zcli.auth.switch_app("analytics_dashboard")  # Switch to analytics
        """
        if not self.session:
            return False
        
        # Check if app is authenticated
        apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
        if app_name not in apps:
            self.logger.warning(f"[WARN] Cannot switch to {app_name}: Not authenticated")
            return False
        
        # Switch active app
        self.session["zAuth"][ZAUTH_KEY_ACTIVE_APP] = app_name
        
        self.logger.info(f"[OK] Switched to application: {app_name}")
        return True
    
    def get_app_user(self, app_name: str) -> Optional[Dict]:
        """Get authentication info for a specific application.
        
        Args:
            app_name: Name of the application
        
        Returns:
            dict: App user data if authenticated, None otherwise
        
        Example:
            store_user = zcli.auth.get_app_user("ecommerce_store")
            analytics_user = zcli.auth.get_app_user("analytics_dashboard")
        """
        if not self.session:
            return None
        
        apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
        return apps.get(app_name)
    
    def set_active_context(self, context: str) -> bool:
        """Set the active authentication context.
        
        Args:
            context: One of "zSession", "application", or "dual"
        
        Returns:
            bool: True if successful, False if invalid or no auth for that context
        
        Example:
            # Switch to zSession context (zCLI user)
            zcli.auth.set_active_context("zSession")
            
            # Switch to application context (app user)
            zcli.auth.set_active_context("application")
            
            # Switch to dual mode (both)
            zcli.auth.set_active_context("dual")
        """
        if not self.session:
            return False
        
        # Validate context value
        valid_contexts = [CONTEXT_ZSESSION, CONTEXT_APPLICATION, CONTEXT_DUAL]
        if context not in valid_contexts:
            self.logger.warning(f"[WARN] Invalid context: {context}")
            return False
        
        # Validate that requested context has authenticated user
        if context == CONTEXT_ZSESSION:
            if not self.session["zAuth"][ZAUTH_KEY_ZSESSION].get(ZAUTH_KEY_AUTHENTICATED):
                self.logger.warning("[WARN] Cannot set zSession context: Not authenticated")
                return False
        
        elif context == CONTEXT_APPLICATION:
            active_app = self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_APP)
            if not active_app:
                self.logger.warning("[WARN] Cannot set application context: No active app")
                return False
            apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
            if active_app not in apps:
                self.logger.warning(f"[WARN] Cannot set application context: {active_app} not authenticated")
                return False
        
        elif context == CONTEXT_DUAL:
            # Dual mode requires both zSession and application authenticated
            zsession_auth = self.session["zAuth"][ZAUTH_KEY_ZSESSION].get(ZAUTH_KEY_AUTHENTICATED)
            active_app = self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_APP)
            apps = self.session["zAuth"].get(ZAUTH_KEY_APPLICATIONS, {})
            
            if not zsession_auth or not active_app or active_app not in apps:
                self.logger.warning("[WARN] Cannot set dual context: Requires both zSession and application auth")
                return False
        
        # Set context
        self.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = context
        self.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = (context == CONTEXT_DUAL)
        
        self.logger.info(f"[OK] Active context set to: {context}")
        return True
    
    def get_active_user(self) -> Optional[Dict]:
        """Get user data for the current active authentication context.
        
        Returns:
            dict: User data based on active context:
                - If zSession context: Returns zSession user data
                - If application context: Returns active app user data
                - If dual context: Returns {"zSession": {...}, "application": {...}}
                - If no authentication: Returns None
        
        Example:
            # Get current active user (whatever context is active)
            user = zcli.auth.get_active_user()
            print(f"Current user: {user['username']}")
        """
        if not self.session:
            return None
        
        active_context = self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_CONTEXT)
        
        if not active_context:
            return None
        
        if active_context == CONTEXT_ZSESSION:
            return self.session["zAuth"][ZAUTH_KEY_ZSESSION]
        
        elif active_context == CONTEXT_APPLICATION:
            active_app = self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_APP)
            if active_app:
                return self.session["zAuth"][ZAUTH_KEY_APPLICATIONS].get(active_app)
            return None
        
        elif active_context == CONTEXT_DUAL:
            active_app = self.session["zAuth"].get(ZAUTH_KEY_ACTIVE_APP)
            return {
                "zSession": self.session["zAuth"][ZAUTH_KEY_ZSESSION],
                "application": self.session["zAuth"][ZAUTH_KEY_APPLICATIONS].get(active_app) if active_app else None
            }
        
        return None
    
    # ═══════════════════════════════════════════════════════════
    # Remote Authentication (Original Methods)
    # ═══════════════════════════════════════════════════════════
    
    def authenticate_remote(self, username, password, server_url=None):
        """Authenticate via Flask API (remote server).
        
        Args:
            username: Username for authentication
            password: Password for authentication
            server_url: Optional server URL (defaults to ZOLO_API_URL env var)
        
        Returns:
            dict: {"status": "success"|"fail"|"error", "credentials": {...}, ...}
        """
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

