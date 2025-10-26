"""
RBAC Module - Role-Based Access Control (v1.5.4+)

This module handles role and permission checks,
as well as permission grant/revoke operations.
"""

from datetime import datetime
from pathlib import Path


class RBAC:
    """
    Role-Based Access Control with permissions.
    
    Features:
    - Role-based access checks (single or multiple roles)
    - Permission-based access checks
    - Permission grant/revoke (admin operations)
    - SQLite-backed permissions database
    - Integration with persistent sessions (role storage)
    """
    
    def __init__(self, zcli):
        """Initialize RBAC module.
        
        Args:
            zcli: zCLI instance (provides access to session, data, loader, logger)
        """
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self._permissions_db_initialized = False
    
    def has_role(self, required_role):
        """Check if the current user has the required role.
        
        Args:
            required_role: Role name (str) or list of role names (list)
                         - str: User must have this exact role
                         - list: User must have ANY of these roles (OR logic)
                         - None: Public access (always returns True)
        
        Returns:
            bool: True if user has the required role(s), False otherwise
            
        Example:
            >>> rbac = RBAC(zcli)
            >>> rbac.has_role("admin")  # Check for admin role
            True
            >>> rbac.has_role(["admin", "moderator"])  # Either role (OR)
            True
            >>> rbac.has_role(None)  # Public access
            True
        """
        # None = public access (override file-level restrictions)
        if required_role is None:
            return True
        
        # Check if user is authenticated first
        if not self._is_authenticated():
            self.logger.debug("[RBAC] User not authenticated, role check failed")
            return False
        
        # Get user's current role from session
        user_role = self.session.get("zAuth", {}).get("role")
        
        if not user_role:
            self.logger.debug("[RBAC] User has no role assigned")
            return False
        
        # Single role check (str)
        if isinstance(required_role, str):
            return user_role == required_role
        
        # Multiple roles check (list) - OR logic
        if isinstance(required_role, list):
            return user_role in required_role
        
        self.logger.warning(f"[RBAC] Invalid role type: {type(required_role)}")
        return False
    
    def has_permission(self, required_permission):
        """Check if the current user has the required permission.
        
        Args:
            required_permission: Permission name (str) or list of permissions (list)
                               - str: User must have this exact permission
                               - list: User must have ANY of these permissions (OR logic)
        
        Returns:
            bool: True if user has the required permission(s), False otherwise
            
        Example:
            >>> rbac = RBAC(zcli)
            >>> rbac.has_permission("users.delete")
            True
            >>> rbac.has_permission(["users.edit", "users.delete"])
            True
            
        Implementation:
            Queries the user_permissions table from zSchema.permissions.yaml
            to check if the user has been granted the specified permission.
        """
        # Check if user is authenticated first
        if not self._is_authenticated():
            self.logger.debug("[RBAC] User not authenticated, permission check failed")
            return False
        
        # Get user ID from session
        user_id = self.session.get("zAuth", {}).get("id")
        if not user_id:
            self.logger.debug("[RBAC] No user_id in session")
            return False
        
        try:
            # Ensure permissions database is loaded
            self.ensure_permissions_db()
            
            # Single permission check (str)
            if isinstance(required_permission, str):
                results = self.zcli.data.select(
                    table="user_permissions",
                    where=f"user_id = '{user_id}' AND permission = '{required_permission}'",
                    limit=1
                )
                return len(results) > 0 if results else False
            
            # Multiple permissions check (list) - OR logic
            if isinstance(required_permission, list):
                for perm in required_permission:
                    results = self.zcli.data.select(
                        table="user_permissions",
                        where=f"user_id = '{user_id}' AND permission = '{perm}'",
                        limit=1
                    )
                    if results and len(results) > 0:
                        return True
                return False
            
            self.logger.warning(f"[RBAC] Invalid permission type: {type(required_permission)}")
            return False
            
        except Exception as e:
            self.logger.error(f"[RBAC] Error checking permission: {e}")
            return False
    
    def grant_permission(self, user_id, permission, granted_by=None):
        """Grant a permission to a user (admin-only operation).
        
        Args:
            user_id: User ID to grant permission to
            permission: Permission name (e.g., "users.delete", "system.shutdown")
            granted_by: Optional admin username who granted this permission
        
        Returns:
            bool: True if permission was granted successfully, False otherwise
            
        Example:
            >>> rbac = RBAC(zcli)
            >>> rbac.grant_permission("user123", "users.delete", granted_by="admin")
            True
            
        Security:
            This should only be callable by users with admin role.
            The calling code should check `has_role("admin")` before calling.
        """
        try:
            # Ensure permissions database is loaded
            self.ensure_permissions_db()
            
            # Check if permission already exists
            existing = self.zcli.data.select(
                table="user_permissions",
                where=f"user_id = '{user_id}' AND permission = '{permission}'",
                limit=1
            )
            
            if existing and len(existing) > 0:
                self.logger.info(f"[RBAC] Permission '{permission}' already granted to user '{user_id}'")
                return True
            
            # Get current admin's username if not provided
            if not granted_by:
                granted_by = self.session.get("zAuth", {}).get("username", "system")
            
            # Insert new permission
            self.zcli.data.insert(
                table="user_permissions",
                fields=["user_id", "permission", "granted_by", "granted_at"],
                values=[user_id, permission, granted_by, datetime.now().isoformat()]
            )
            
            self.logger.info(f"[RBAC] Granted permission '{permission}' to user '{user_id}' by '{granted_by}'")
            return True
            
        except Exception as e:
            self.logger.error(f"[RBAC] Error granting permission: {e}")
            return False
    
    def revoke_permission(self, user_id, permission):
        """Revoke a permission from a user (admin-only operation).
        
        Args:
            user_id: User ID to revoke permission from
            permission: Permission name to revoke
        
        Returns:
            bool: True if permission was revoked successfully, False otherwise
            
        Example:
            >>> rbac = RBAC(zcli)
            >>> rbac.revoke_permission("user123", "users.delete")
            True
            
        Security:
            This should only be callable by users with admin role.
            The calling code should check `has_role("admin")` before calling.
        """
        try:
            # Ensure permissions database is loaded
            self.ensure_permissions_db()
            
            # Delete permission
            self.zcli.data.delete(
                table="user_permissions",
                where=f"user_id = '{user_id}' AND permission = '{permission}'"
            )
            
            self.logger.info(f"[RBAC] Revoked permission '{permission}' from user '{user_id}'")
            return True
            
        except Exception as e:
            self.logger.error(f"[RBAC] Error revoking permission: {e}")
            return False
    
    def ensure_permissions_db(self):
        """Ensure the permissions database is initialized (internal helper).
        
        Uses the unified auth schema (zSchema.auth.yaml) which contains both
        sessions and user_permissions tables. This method should be called
        after SessionPersistence.ensure_sessions_db() has loaded the schema.
        """
        # Skip if already initialized
        if self._permissions_db_initialized:
            return
        
        try:
            # Check if auth database is already loaded
            if self.zcli.data.handler and self.zcli.data.schema.get("Meta", {}).get("Data_Label") == "auth":
                # Auth schema already loaded - just ensure table exists
                if not self.zcli.data.table_exists("user_permissions"):
                    self.zcli.data.create_table("user_permissions")
                    self.logger.info("[RBAC] User permissions table created")
                self._permissions_db_initialized = True
                return
            
            # If not loaded yet, load the unified auth schema
            # Get absolute path to zSchema.auth.yaml (it's part of zCLI package)
            auth_dir = Path(__file__).parent.parent  # Go up to zAuth directory
            schema_path = auth_dir / "zSchema.auth.yaml"
            
            if not schema_path.exists():
                self.logger.warning(f"[RBAC] Auth schema not found: {schema_path}")
                return
            
            # Load schema directly using zParser (bypass zLoader for package-internal files)
            from pathlib import Path as PathlibPath
            schema_content = PathlibPath(schema_path).read_text()
            parsed_schema = self.zcli.zparser.parse_file_content(schema_content, ".yaml")
            
            if not parsed_schema:
                self.logger.warning("[RBAC] Failed to parse auth schema")
                return
            
            # Load into zData
            self.zcli.data.load_schema(parsed_schema)
            
            # Verify handler was created
            if not self.zcli.data.handler:
                self.logger.error("[RBAC] Failed to create data handler after loading schema")
                return
            
            # Verify correct schema is loaded
            loaded_label = self.zcli.data.schema.get("Meta", {}).get("Data_Label")
            if loaded_label != "auth":
                self.logger.error(f"[RBAC] Wrong schema loaded: {loaded_label} (expected: auth)")
                return
            
            # CREATE both tables if they don't exist (unified schema)
            if not self.zcli.data.table_exists("sessions"):
                self.zcli.data.create_table("sessions")
                self.logger.info("[RBAC] Sessions table created")
            
            if not self.zcli.data.table_exists("user_permissions"):
                self.zcli.data.create_table("user_permissions")
                self.logger.info("[RBAC] User permissions table created")
            
            self.logger.info("[RBAC] Auth database initialized (sessions + permissions)")
            self._permissions_db_initialized = True
            
        except Exception as e:
            self.logger.error(f"[RBAC] Error initializing permissions database: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
    
    def _is_authenticated(self):
        """Check if user is authenticated (internal helper).
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return (self.session and 
                self.session.get("zAuth", {}).get("username") is not None and
                self.session.get("zAuth", {}).get("API_Key") is not None)

