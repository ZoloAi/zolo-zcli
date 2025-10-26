# zCLI/subsystems/zAuth/zAuth.py
"""
Authentication subsystem for zCLI with bcrypt password hashing (v1.5.4+)

Refactored Architecture (Facade Pattern):
- password_security: bcrypt hashing and verification
- session_persistence: SQLite-based persistent sessions
- authentication: User login/logout and remote auth
- rbac: Role-Based Access Control with permissions

This file serves as the orchestrator (facade) that coordinates
the modular components and maintains API compatibility.
"""

from .zAuth_modules import PasswordSecurity, SessionPersistence, Authentication, RBAC


class zAuth:
    """
    Authentication subsystem orchestrator (Facade Pattern).
    
    v1.5.4+: Modularized architecture with:
    - bcrypt password hashing (12 rounds)
    - Persistent sessions (7-day expiry)
    - Role-Based Access Control (RBAC)
    - Permission-based access control
    
    BREAKING CHANGE: Plaintext passwords no longer supported.
    """

    def __init__(self, zcli):
        """Initialize authentication subsystem with modular architecture."""
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZAUTH"  # Orange-brown bg (Authentication)
        
        # Initialize modular components
        self.password_security = PasswordSecurity(logger=self.logger)
        self.session_persistence = SessionPersistence(zcli, session_duration_days=7)
        self.authentication = Authentication(zcli)
        self.rbac = RBAC(zcli)
        
        # Display ready message
        self.zcli.display.zDeclare("zAuth Ready (modular architecture)", color=self.mycolor, indent=0, style="full")
        
        # Note: Database initialization is deferred until after zParser/zLoader are ready
        # Will be called automatically on first use (lazy initialization)
    
    # ════════════════════════════════════════════════════════════
    # Password Hashing (Facade → password_security module)
    # ════════════════════════════════════════════════════════════
    
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        
        Delegates to: password_security.hash_password()
        
        Args:
            plain_password: Plaintext password string
            
        Returns:
            str: bcrypt hashed password (UTF-8 decoded)
            
        Raises:
            ValueError: If password is empty or None
        """
        return self.password_security.hash_password(plain_password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a bcrypt hash.
        
        Delegates to: password_security.verify_password()
        
        Args:
            plain_password: Plaintext password to verify
            hashed_password: bcrypt hashed password (from database/storage)
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return self.password_security.verify_password(plain_password, hashed_password)
    
    # ════════════════════════════════════════════════════════════
    # Authentication (Facade → authentication module)
    # ════════════════════════════════════════════════════════════
    
    def login(self, username=None, password=None, server_url=None, persist=True):
        """
        Authenticate user and optionally persist session.
        
        Delegates to: authentication.login() + session_persistence.save_session()
        
        Args:
            username: Username for authentication
            password: Password for authentication
            server_url: Optional remote server URL
            persist: If True, save session to sessions.db (default: True)
        
        Returns:
            dict: {"status": "success"|"fail"|"pending", ...}
        """
        result = self.authentication.login(username, password, server_url, persist)
        
        # Handle session persistence if login was successful
        if result.get("status") == "success" and result.get("persist"):
            credentials = result.get("credentials")
            password_for_hash = result.get("password")
            
            if credentials and password_for_hash:
                # Hash password and save session
                password_hash = self.hash_password(password_for_hash)
                self.session_persistence.save_session(
                    username=credentials.get("username"),
                    password_hash=password_hash,
                    user_id=credentials.get("user_id"),
                    role=credentials.get("role", "user")
                )
        
        # Clean up sensitive data before returning
        if "password" in result:
            del result["password"]
        if "persist" in result:
            del result["persist"]
        
        return result
    
    def logout(self):
        """
        Clear session authentication and delete persistent session.
        
        Delegates to: authentication.logout() + session_persistence cleanup
        
        Returns:
            dict: {"status": "success"}
        """
        result = self.authentication.logout(delete_persistent=True)
        
        # Delete persistent session if requested
        if result.get("delete_persistent") and result.get("username"):
            try:
                if self.zcli.data.handler and self.zcli.data.schema.get("Meta", {}).get("Data_Label") == "auth":
                    self.zcli.data.delete(
                        table="sessions",
                        where=f"username = '{result.get('username')}'"
                    )
                    self.logger.info(f"[zAuth] Persistent session deleted for user: {result.get('username')}")
            except Exception as e:
                self.logger.error(f"[zAuth] Error deleting persistent session: {e}")
        
        return {"status": "success"}
    
    def status(self):
        """
        Show current authentication status.
        
        Delegates to: authentication.status()
        
        Returns:
            dict: {"status": "authenticated"|"not_authenticated", "user": {...}}
        """
        return self.authentication.status()
    
    def is_authenticated(self):
        """
        Check if user is currently authenticated in session.
        
        Delegates to: authentication.is_authenticated()
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.authentication.is_authenticated()
    
    def get_credentials(self):
        """
        Get current session authentication data.
        
        Delegates to: authentication.get_credentials()
        
        Returns:
            dict: Session auth data if authenticated, None otherwise
        """
        return self.authentication.get_credentials()
    
    # ════════════════════════════════════════════════════════════
    # RBAC (Facade → rbac module)
    # ════════════════════════════════════════════════════════════
    
    def has_role(self, required_role):
        """
        Check if the current user has the required role.
        
        Delegates to: rbac.has_role()
        
        Args:
            required_role: Role name (str) or list of role names (list)
                         - str: User must have this exact role
                         - list: User must have ANY of these roles (OR logic)
                         - None: Public access (always returns True)
        
        Returns:
            bool: True if user has the required role(s), False otherwise
        """
        return self.rbac.has_role(required_role)
    
    def has_permission(self, required_permission):
        """
        Check if the current user has the required permission.
        
        Delegates to: rbac.has_permission()
        
        Args:
            required_permission: Permission name (str) or list of permissions (list)
                               - str: User must have this exact permission
                               - list: User must have ANY of these permissions (OR logic)
        
        Returns:
            bool: True if user has the required permission(s), False otherwise
        """
        return self.rbac.has_permission(required_permission)
    
    def grant_permission(self, user_id, permission, granted_by=None):
        """
        Grant a permission to a user (admin-only operation).
        
        Delegates to: rbac.grant_permission()
        
        Args:
            user_id: User ID to grant permission to
            permission: Permission name (e.g., "users.delete", "system.shutdown")
            granted_by: Optional admin username who granted this permission
        
        Returns:
            bool: True if permission was granted successfully, False otherwise
        """
        return self.rbac.grant_permission(user_id, permission, granted_by)
    
    def revoke_permission(self, user_id, permission):
        """
        Revoke a permission from a user (admin-only operation).
        
        Delegates to: rbac.revoke_permission()
        
        Args:
            user_id: User ID to revoke permission from
            permission: Permission name to revoke
        
        Returns:
            bool: True if permission was revoked successfully, False otherwise
        """
        return self.rbac.revoke_permission(user_id, permission)
    
    # ════════════════════════════════════════════════════════════
    # Internal Helpers (for backwards compatibility)
    # ════════════════════════════════════════════════════════════
    
    def _ensure_sessions_db(self):
        """DEPRECATED: Use session_persistence.ensure_sessions_db() directly.
        
        Kept for backwards compatibility with tests.
        """
        return self.session_persistence.ensure_sessions_db()
    
    def _load_session(self):
        """DEPRECATED: Use session_persistence.load_session() directly.
        
        Kept for backwards compatibility with tests.
        """
        return self.session_persistence.load_session()
    
    def _save_session(self, username, password_hash, user_id=None):
        """DEPRECATED: Use session_persistence.save_session() directly.
        
        Kept for backwards compatibility with tests.
        """
        role = self.session.get("zAuth", {}).get("role", "user")
        return self.session_persistence.save_session(username, password_hash, user_id, role)
    
    def _cleanup_expired(self):
        """DEPRECATED: Use session_persistence.cleanup_expired() directly.
        
        Kept for backwards compatibility with tests.
        """
        return self.session_persistence.cleanup_expired()
    
    def _authenticate_remote(self, username, password, server_url=None):
        """DEPRECATED: Use authentication.authenticate_remote() directly.
        
        Kept for backwards compatibility.
        """
        return self.authentication.authenticate_remote(username, password, server_url)
    
    def _ensure_permissions_db(self):
        """DEPRECATED: Use rbac.ensure_permissions_db() directly.
        
        Kept for backwards compatibility with tests.
        """
        return self.rbac.ensure_permissions_db()
