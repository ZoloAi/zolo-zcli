# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/zAuth.py

"""zAuth events - authentication input/output for both Terminal and GUI modes."""


class zAuthEvents:
    """Authentication events for dual-mode (Terminal/GUI) authentication flows."""

    def __init__(self, display_instance):
        """Initialize zAuthEvents with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        self.BasicOutputs = None  # Will be set after zEvents initialization
        self.Signals = None  # Will be set after zEvents initialization

    def login_prompt(self, username=None, password=None):
        """Prompt for authentication credentials.
        
        Terminal: Interactive prompts for username/password.
        GUI: Sends clean event with form fields for frontend rendering.
        
        Args:
            username (str, optional): Pre-filled username.
            password (str, optional): Pre-filled password (not recommended).
        
        Returns:
            dict: {"username": str, "password": str} or None if cancelled.
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("auth_login_prompt", {
            "username": username,
            "password": password,
            "fields": ["username", "password"]
        }):
            # GUI mode - frontend will send response via bifrost
            return None
        
        # Terminal mode - interactive prompts
        if not username:
            username = self.zPrimitives.read_string("Username: ")
        
        if not password:
            password = self.zPrimitives.read_password("Password: ")
        
        return {"username": username, "password": password}

    def login_success(self, user_data):
        """Display successful login message.
        
        Terminal: Formatted success message with user details.
        GUI: Sends clean event with user data for frontend rendering.
        
        Args:
            user_data (dict): User information (username, role, id, api_key).
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_login_success", {
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "user_id": user_data.get("user_id"),
            "api_key": user_data.get("api_key", "")[:20] + "..." if user_data.get("api_key") else None
        }):
            return
        
        # Terminal mode - formatted display
        if self.Signals:
            self.Signals.success(f"[OK] Logged in as: {user_data.get('username')} ({user_data.get('role')})")
        if self.BasicOutputs:
            self.BasicOutputs.text(f"     User ID: {user_data.get('user_id')}", break_after=False)
            if user_data.get("api_key"):
                self.BasicOutputs.text(f"     API Key: {user_data.get('api_key')[:20]}...", break_after=False)

    def login_failure(self, reason="Invalid credentials"):
        """Display login failure message.
        
        Terminal: Error message with reason.
        GUI: Sends clean event with error for frontend rendering.
        
        Args:
            reason (str): Reason for authentication failure.
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_login_failure", {
            "reason": reason
        }):
            return
        
        # Terminal mode
        if self.Signals:
            self.Signals.error(f"[FAIL] Authentication failed: {reason}")

    def logout_success(self):
        """Display successful logout message.
        
        Terminal: Success message.
        GUI: Sends clean event for frontend rendering.
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_logout_success", {}):
            return
        
        # Terminal mode
        if self.Signals:
            self.Signals.success("[OK] Logged out successfully")

    def logout_warning(self):
        """Display warning when logout attempted but not logged in.
        
        Terminal: Warning message.
        GUI: Sends clean event for frontend rendering.
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_logout_warning", {}):
            return
        
        # Terminal mode
        if self.Signals:
            self.Signals.warning("[WARN] Not currently logged in")

    def status_display(self, auth_data):
        """Display authentication status.
        
        Terminal: Formatted table with auth details.
        GUI: Sends clean event with auth data for frontend rendering.
        
        Args:
            auth_data (dict): Authentication data (username, role, id, api_key).
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_status", {
            "authenticated": True,
            "username": auth_data.get("username"),
            "role": auth_data.get("role"),
            "user_id": auth_data.get("id"),
            "api_key": auth_data.get("API_Key", "")[:20] + "..." if auth_data.get("API_Key") else None
        }):
            return
        
        # Terminal mode - formatted display
        if self.BasicOutputs:
            self.BasicOutputs.header("[*] Authentication Status")
            self.BasicOutputs.text(f"Username:   {auth_data.get('username')}", indent=1, break_after=False)
            self.BasicOutputs.text(f"Role:       {auth_data.get('role')}", indent=1, break_after=False)
            self.BasicOutputs.text(f"User ID:    {auth_data.get('id')}", indent=1, break_after=False)
            self.BasicOutputs.text(f"API Key:    {auth_data.get('API_Key', '')[:20]}...", indent=1, break_after=False)

    def status_not_authenticated(self):
        """Display not authenticated status.
        
        Terminal: Warning message.
        GUI: Sends clean event for frontend rendering.
        """
        # Try GUI mode first
        if self.zPrimitives.send_gui_event("auth_status", {
            "authenticated": False
        }):
            return
        
        # Terminal mode
        if self.Signals:
            self.Signals.warning("[WARN] Not authenticated. Run 'auth login' to authenticate.")

