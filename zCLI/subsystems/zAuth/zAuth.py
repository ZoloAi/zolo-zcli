# zCLI/subsystems/zAuth/zAuth.py
"""Authentication subsystem for zCLI with bcrypt password hashing (v1.5.4+)."""

from zCLI import os
import bcrypt
import secrets
from datetime import datetime, timedelta
from pathlib import Path


class zAuth:
    """
    Authentication subsystem for zCLI with bcrypt password hashing.
    
    v1.5.4+: Passwords are hashed using bcrypt (12 rounds).
    BREAKING CHANGE: Plaintext passwords no longer supported.
    """

    def __init__(self, zcli):
        """Initialize authentication subsystem with bcrypt support and persistent sessions."""
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZAUTH"  # Orange-brown bg (Authentication)
        
        # Session persistence (v1.5.4+ Week 3.2)
        self.sessions_db_label = "sessions"
        self.session_duration_days = 7
        
        # Display ready message
        self.zcli.display.zDeclare("zAuth Ready (bcrypt + persistent sessions)", color=self.mycolor, indent=0, style="full")
        
        # Initialize sessions database and restore any existing session
        self._ensure_sessions_db()
        self._load_session()
    
    # ════════════════════════════════════════════════════════════
    # Password Hashing (bcrypt) - NEW in v1.5.4
    # ════════════════════════════════════════════════════════════
    
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        
        Args:
            plain_password: Plaintext password string
            
        Returns:
            str: bcrypt hashed password (UTF-8 decoded)
            
        Raises:
            ValueError: If password is empty or None
            
        Example:
            >>> auth = zAuth(zcli)
            >>> hashed = auth.hash_password("mypassword")
            >>> print(hashed[:7])
            '$2b$12$'
            
        Security:
            - Uses bcrypt with 12 rounds (good balance of security/speed)
            - Each hash includes a random salt
            - Same password produces different hashes (salted)
            - One-way: cannot recover plaintext from hash
            - Passwords > 72 bytes are truncated (bcrypt limit)
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")
        
        # bcrypt has a 72-byte limit - truncate if necessary
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            self.logger.warning(f"[zAuth] Password > 72 bytes, truncating (bcrypt limit)")
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash (12 rounds = ~0.3s on modern hardware)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string (bcrypt returns bytes)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a bcrypt hash.
        
        Args:
            plain_password: Plaintext password to verify
            hashed_password: bcrypt hashed password (from database/storage)
            
        Returns:
            bool: True if password matches, False otherwise
            
        Example:
            >>> auth = zAuth(zcli)
            >>> hashed = auth.hash_password("correct_password")
            >>> auth.verify_password("correct_password", hashed)
            True
            >>> auth.verify_password("wrong_password", hashed)
            False
            
        Security:
            - Timing-safe comparison (constant time)
            - Handles invalid hashes gracefully (returns False)
            - Logs errors without exposing password details
            - Truncates passwords > 72 bytes (to match hash_password behavior)
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            # Truncate to 72 bytes (same as hash_password)
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            return bcrypt.checkpw(
                password_bytes,
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"[zAuth] Password verification error: {e}")
            return False
    
    # ════════════════════════════════════════════════════════════
    # Persistent Sessions (SQLite-based) - NEW in v1.5.4 Week 3.2
    # ════════════════════════════════════════════════════════════
    
    def _ensure_sessions_db(self):
        """Ensure the sessions database is initialized (declarative zCLI way).
        
        This method:
        1. Loads zSchema.sessions.yaml from zAuth subsystem directory
        2. Initializes zData handler
        3. Creates sessions table if it doesn't exist (CREATE vs INSERT!)
        4. Cleans up any expired sessions
        """
        try:
            # Get path to zSchema.sessions.yaml (in zAuth subsystem directory)
            auth_dir = Path(__file__).parent
            schema_path = auth_dir / "zSchema.sessions.yaml"
            
            if not schema_path.exists():
                self.logger.warning(f"[zAuth] Sessions schema not found: {schema_path}")
                return
            
            # Load schema using zCLI's loader (declarative!)
            schema_loaded = self.zcli.loader.handle(f"~{schema_path}")
            
            if not schema_loaded:
                self.logger.warning("[zAuth] Failed to load sessions schema")
                return
            
            # CREATE TABLE if it doesn't exist (separate from INSERT!)
            if not self.zcli.data.table_exists("sessions"):
                self.zcli.data.create_table("sessions")
                self.logger.info("[zAuth] Sessions table created")
            
            self.logger.info("[zAuth] Sessions database initialized")
            
            # Clean up expired sessions on startup
            self._cleanup_expired()
            
        except Exception as e:
            self.logger.error(f"[zAuth] Error initializing sessions database: {e}")
    
    def _load_session(self):
        """Load and restore persistent session on startup (if exists and valid).
        
        Checks sessions.db for a valid (non-expired) session and restores it
        to the in-memory session state, enabling "Remember me" functionality.
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.sessions_db_label:
                self.logger.debug("[zAuth] Sessions database not loaded, skipping restore")
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
                self.logger.debug("[zAuth] No valid persistent session found")
                return
            
            # Restore session to in-memory state
            session_data = results[0]
            
            self.session["zAuth"].update({
                "id": session_data.get("user_id"),
                "username": session_data.get("username"),
                "role": None,  # Not stored in persistent sessions (privacy)
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
            
            self.logger.info(f"[zAuth] Restored persistent session for user: {session_data.get('username')}")
            
        except Exception as e:
            self.logger.error(f"[zAuth] Error loading persistent session: {e}")
    
    def _save_session(self, username, password_hash, user_id=None):
        """Save current session to persistent storage (sessions.db).
        
        Creates a new session record with 7-day expiry, enabling "Remember me"
        functionality across app restarts.
        
        Args:
            username: Username for the session
            password_hash: bcrypt password hash for verification
            user_id: Optional user ID (defaults to username)
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.sessions_db_label:
                self.logger.warning("[zAuth] Sessions database not loaded, cannot persist session")
                return
            
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
                self.logger.debug(f"[zAuth] No existing sessions to delete: {e}")
            
            # Insert new session record (declarative zData way!)
            self.zcli.data.insert(
                table="sessions",
                fields=["session_id", "user_id", "username", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
                values=[session_id, user_id, username, password_hash, token, created_at, expires_at, last_accessed]
            )
            
            # Update in-memory session with session_id
            self.session["zAuth"]["session_id"] = session_id
            
            self.logger.info(f"[zAuth] Persistent session saved for user: {username} (expires: {expires_at})")
            
        except Exception as e:
            self.logger.error(f"[zAuth] Error saving persistent session: {e}")
    
    def _cleanup_expired(self):
        """Remove expired sessions from database (housekeeping).
        
        Called automatically on startup and can be called manually.
        Removes any sessions where expires_at < current time.
        """
        try:
            # Check if zData is initialized with sessions schema
            if not self.zcli.data.handler or self.zcli.data.schema.get("Meta", {}).get("Data_Label") != self.sessions_db_label:
                self.logger.debug("[zAuth] Sessions database not loaded, skipping cleanup")
                return
            
            # Delete expired sessions
            now = datetime.now().isoformat()
            
            deleted = self.zcli.data.delete(
                table="sessions",
                where=f"expires_at <= '{now}'"
            )
            
            if deleted and deleted > 0:
                self.logger.info(f"[zAuth] Cleaned up {deleted} expired session(s)")
            else:
                self.logger.debug("[zAuth] No expired sessions to clean up")
                
        except Exception as e:
            self.logger.error(f"[zAuth] Error cleaning up expired sessions: {e}")
    
    # ════════════════════════════════════════════════════════════
    # Session Authentication
    # ════════════════════════════════════════════════════════════
    
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
                    
                    # Persist session if requested (v1.5.4 Week 3.2)
                    if persist:
                        # Hash the password for persistent storage
                        password_hash = self.hash_password(password)
                        self._save_session(
                            username=credentials.get("username"),
                            password_hash=password_hash,
                            user_id=credentials.get("user_id")
                        )
                return result
        
        # Authentication failed - use zDisplay events
        self.logger.warning("[FAIL] Authentication failed: Invalid credentials")
        self.zcli.display.zEvents.zAuth.login_failure("Invalid credentials")
        return {"status": "fail", "reason": "Invalid credentials"}
    
    def logout(self):
        """Clear session authentication and delete persistent session."""
        is_logged_in = self.is_authenticated()
        username = self.session.get("zAuth", {}).get("username")
        
        # Delete persistent session if exists (v1.5.4 Week 3.2)
        if username:
            try:
                if self.zcli.data.handler and self.zcli.data.schema.get("Meta", {}).get("Data_Label") == self.sessions_db_label:
                    self.zcli.data.delete(
                        table="sessions",
                        where=f"username = '{username}'"
                    )
                    self.logger.info(f"[zAuth] Persistent session deleted for user: {username}")
            except Exception as e:
                self.logger.error(f"[zAuth] Error deleting persistent session: {e}")
        
        # Clear in-memory session auth
        if self.session:
            self.session["zAuth"] = {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None,
                "session_id": None
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

