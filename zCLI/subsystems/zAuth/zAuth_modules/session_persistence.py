"""
Session Persistence Module - SQLite-based session management (v1.5.4+)

This module handles persistent session storage in SQLite, enabling
"Remember me" functionality across app restarts.
"""

import secrets
from datetime import datetime, timedelta
from pathlib import Path


class SessionPersistence:
    """
    SQLite-based persistent session management.
    
    Features:
    - Store sessions in SQLite database
    - 7-day session expiration (configurable)
    - Automatic cleanup of expired sessions
    - Cross-platform paths via platformdirs
    - Declarative zData operations (no raw SQL)
    """
    
    def __init__(self, zcli, session_duration_days=7):
        """Initialize session persistence module.
        
        Args:
            zcli: zCLI instance (provides access to data, loader, logger, session)
            session_duration_days: Session expiration period (default: 7 days)
        """
        self.zcli = zcli
        self.logger = zcli.logger
        self.session = zcli.session
        self.session_duration_days = session_duration_days
        self.auth_db_label = "auth"  # Unified auth database (sessions + permissions)
    
    def ensure_sessions_db(self):
        """Ensure the sessions database is initialized (declarative zCLI way).
        
        This method:
        1. Loads zSchema.sessions.yaml from zAuth subsystem directory
        2. Initializes zData handler
        3. Creates sessions table if it doesn't exist (CREATE vs INSERT!)
        4. Cleans up any expired sessions
        """
        try:
            # Get absolute path to zSchema.auth.yaml (it's part of zCLI package)
            auth_dir = Path(__file__).parent.parent  # Go up to zAuth directory
            schema_path = auth_dir / "zSchema.auth.yaml"
            
            if not schema_path.exists():
                self.logger.warning(f"[SessionPersistence] Auth schema not found: {schema_path}")
                return
            
            # Load schema directly using zParser (bypass zLoader for package-internal files)
            from pathlib import Path as PathlibPath
            schema_content = PathlibPath(schema_path).read_text()
            parsed_schema = self.zcli.zparser.parse_file_content(schema_content, ".yaml")
            
            if not parsed_schema:
                self.logger.warning("[SessionPersistence] Failed to parse auth schema")
                return
            
            # Load into zData
            self.zcli.data.load_schema(parsed_schema)
            
            # Verify handler was created
            if not self.zcli.data.handler:
                self.logger.error("[SessionPersistence] Failed to create data handler after loading schema")
                return
            
            # Verify correct schema is loaded
            loaded_label = self.zcli.data.schema.get("Meta", {}).get("Data_Label")
            if loaded_label != self.auth_db_label:
                self.logger.error(f"[SessionPersistence] Wrong schema loaded: {loaded_label} (expected: {self.auth_db_label})")
                return
            
            # CREATE both tables if they don't exist (unified schema)
            if not self.zcli.data.table_exists("sessions"):
                self.zcli.data.create_table("sessions")
                self.logger.info("[SessionPersistence] Sessions table created")
            
            if not self.zcli.data.table_exists("user_permissions"):
                self.zcli.data.create_table("user_permissions")
                self.logger.info("[SessionPersistence] User permissions table created")
            
            self.logger.info("[SessionPersistence] Auth database initialized (sessions + permissions)")
            
            # Clean up expired sessions on startup
            self.cleanup_expired()
            
        except Exception as e:
            self.logger.error(f"[SessionPersistence] Error initializing sessions database: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
    
    def load_session(self):
        """Load and restore persistent session on startup (if exists and valid).
        
        Checks sessions.db for a valid (non-expired) session and restores it
        to the in-memory session state, enabling "Remember me" functionality.
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.auth_db_label:
                self.logger.debug("[SessionPersistence] Sessions database not loaded, skipping restore")
                return
            
            # Query for the most recent valid session (not expired)
            now = datetime.now().isoformat()
            
            results = self.zcli.data.select(
                table="sessions",
                where=f"expires_at > '{now}'",
                order="last_accessed DESC",
                limit=1
            )
            
            if not results or len(results) == 0:
                self.logger.debug("[SessionPersistence] No valid persistent session found")
                return
            
            # Restore session to in-memory state
            session_data = results[0]
            
            self.session["zAuth"].update({
                "id": session_data.get("user_id"),
                "username": session_data.get("username"),
                "role": session_data.get("role", "user"),  # Restore role from persistent sessions
                "API_Key": session_data.get("token"),
                "session_id": session_data.get("session_id")
            })
            
            # Update last_accessed timestamp
            self.zcli.data.update(
                table="sessions",
                fields=["last_accessed"],
                values=[datetime.now().isoformat()],
                where=f"session_id = '{session_data.get('session_id')}'"
            )
            
            self.logger.info(f"[SessionPersistence] Restored persistent session for user: {session_data.get('username')}")
            
        except Exception as e:
            self.logger.error(f"[SessionPersistence] Error loading persistent session: {e}")
    
    def save_session(self, username, password_hash, user_id=None, role="user"):
        """Save current session to persistent storage (sessions.db).
        
        Creates a new session record with 7-day expiry, enabling "Remember me"
        functionality across app restarts.
        
        Args:
            username: Username for the session
            password_hash: bcrypt password hash for verification
            user_id: Optional user ID (defaults to username)
            role: User role (default: "user")
        
        Returns:
            str: session_id if successful, None otherwise
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.auth_db_label:
                # Try to ensure DB is loaded
                self.logger.debug("[SessionPersistence] Auth DB not loaded, attempting to initialize...")
                self.ensure_sessions_db()
                
                # Check again
                if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.auth_db_label:
                    self.logger.warning("[SessionPersistence] Auth database not loaded, cannot persist session")
                    return None
            
            # Generate unique session ID and token
            session_id = secrets.token_urlsafe(32)
            token = secrets.token_urlsafe(32)
            
            # Calculate expiration (7 days from now)
            expires_at = (datetime.now() + timedelta(days=self.session_duration_days)).isoformat()
            created_at = datetime.now().isoformat()
            last_accessed = created_at
            
            # Use user_id or fall back to username
            if not user_id:
                user_id = username
            
            # Delete any existing sessions for this user (single session per user)
            try:
                self.zcli.data.delete(
                    table="sessions",
                    where=f"username = '{username}'"
                )
            except Exception as e:
                self.logger.debug(f"[SessionPersistence] No existing sessions to delete: {e}")
            
            # Insert new session record (declarative zData way!)
            self.zcli.data.insert(
                table="sessions",
                fields=["session_id", "user_id", "username", "role", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
                values=[session_id, user_id, username, role, password_hash, token, created_at, expires_at, last_accessed]
            )
            
            # Update in-memory session with session_id
            self.session["zAuth"]["session_id"] = session_id
            
            self.logger.info(f"[SessionPersistence] Persistent session saved for user: {username} (expires: {expires_at})")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"[SessionPersistence] Error saving persistent session: {e}")
            return None
    
    def cleanup_expired(self):
        """Remove expired sessions from database (housekeeping).
        
        Called automatically on startup and can be called manually.
        Removes any sessions where expires_at < current time.
        
        Returns:
            int: Number of sessions deleted
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.auth_db_label:
                self.logger.debug("[SessionPersistence] Sessions database not loaded, skipping cleanup")
                return 0
            
            # Delete expired sessions
            now = datetime.now().isoformat()
            
            deleted = self.zcli.data.delete(
                table="sessions",
                where=f"expires_at <= '{now}'"
            )
            
            if deleted and deleted > 0:
                self.logger.info(f"[SessionPersistence] Cleaned up {deleted} expired session(s)")
                return deleted
            else:
                self.logger.debug("[SessionPersistence] No expired sessions to clean up")
                return 0
                
        except Exception as e:
            self.logger.error(f"[SessionPersistence] Error cleaning up expired sessions: {e}")
            return 0

