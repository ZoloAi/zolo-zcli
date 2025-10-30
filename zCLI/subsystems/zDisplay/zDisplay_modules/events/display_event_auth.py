# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_auth.py
"""
zAuthEvents - Authentication UI Events for zDisplay (v1.5.4+)

This module provides authentication user interface events for the zDisplay subsystem,
enabling dual-mode (Terminal + Bifrost) authentication flows with full integration
into zAuth's three-tier authentication architecture.

═══════════════════════════════════════════════════════════════════════════
ARCHITECTURE: zAuth Integration Bridge
═══════════════════════════════════════════════════════════════════════════

zAuthEvents serves as the UI presentation layer for zAuth subsystem operations,
translating authentication state changes into user-visible feedback across both
Terminal and Bifrost (GUI) modes.

Integration Flow:
    zAuth subsystem → zAuthEvents → zDisplay → zPrimitives → Terminal/Bifrost

Example:
    # zAuth calls zAuthEvents for UI feedback
    zcli.auth.login(username, password)
        → authentication.py validates credentials
        → calls display.zEvents.zAuth.login_success(user_data)
        → zAuthEvents formats and displays success message
        → User sees "✓ Logged in as: admin (admin)"


═══════════════════════════════════════════════════════════════════════════
THREE-TIER AUTHENTICATION AWARENESS (zAuth v1.5.4+)
═══════════════════════════════════════════════════════════════════════════

zAuth supports three distinct authentication layers that can operate independently
or simultaneously. zAuthEvents is aware of these contexts and uses standardized
constants for all authentication data access.

Layer 1 - zSession Auth (Internal zCLI/Zolo Users):
    Purpose:     Premium zCLI features, plugins, Zolo cloud services
    Triggered:   zcli.auth.login()
    Session Key: session["zAuth"]["zSession"] (ZAUTH_KEY_ZSESSION)
    Contains:    authenticated, id, username, role, api_key
    Example:     Developer authenticating to access premium zCLI features

Layer 2 - Application Auth (External App Users, Multi-App Support):
    Purpose:     Users of applications BUILT on zCLI
    Triggered:   zcli.auth.authenticate_app_user(app_name, token, config)
    Session Key: session["zAuth"]["applications"][app_name] (ZAUTH_KEY_APPLICATIONS)
    Contains:    authenticated, id, username, role, api_key (per app)
    Example:     Store customer authenticating to an eCommerce app built on zCLI
    Note:        Multiple apps can be authenticated simultaneously

Layer 3 - Dual-Auth (Simultaneous zSession + Application):
    Purpose:     Developer working on their own application
    Session Key: session["zAuth"]["dual_mode"] = True (ZAUTH_KEY_DUAL_MODE)
    Example:     Store owner (zSession user) logged into their store (app user)
    
Context Management:
    session["zAuth"]["active_context"]:  "zSession", "application", or "dual"
    session["zAuth"]["active_app"]:      Current focused app (for multi-app)


═══════════════════════════════════════════════════════════════════════════
ZAUTH CONSTANTS INTEGRATION
═══════════════════════════════════════════════════════════════════════════

All authentication data keys use standardized constants from zConfig to ensure
consistency with zAuth subsystem and enable safe refactoring.

Imported Constants (13):
    ZAUTH_KEY_ZSESSION       - "zSession"     (Layer 1 dict key)
    ZAUTH_KEY_APPLICATIONS   - "applications" (Layer 2 dict key)
    ZAUTH_KEY_ACTIVE_APP     - "active_app"   (Focused app name)
    ZAUTH_KEY_AUTHENTICATED  - "authenticated" (Auth status flag)
    ZAUTH_KEY_ID             - "id"           (User ID - NOT "user_id"!)
    ZAUTH_KEY_USERNAME       - "username"     (Username)
    ZAUTH_KEY_ROLE           - "role"         (User role)
    ZAUTH_KEY_API_KEY        - "api_key"      (API key - NOT "API_Key"!)
    ZAUTH_KEY_ACTIVE_CONTEXT - "active_context" (Current context)
    ZAUTH_KEY_DUAL_MODE      - "dual_mode"    (Dual auth flag)
    CONTEXT_ZSESSION         - "zSession"     (zSession context value)
    CONTEXT_APPLICATION      - "application"  (App context value)
    CONTEXT_DUAL             - "dual"         (Dual context value)

Usage Example:
    # ❌ OLD (Legacy, inconsistent, error-prone):
    username = user_data.get("username")
    user_id = user_data.get("user_id")  # Wrong key!
    api_key = user_data.get("API_Key")  # Wrong case!
    
    # ✅ NEW (Modern, consistent, refactor-safe):
    username = user_data.get(ZAUTH_KEY_USERNAME)
    user_id = user_data.get(ZAUTH_KEY_ID)      # Correct!
    api_key = user_data.get(ZAUTH_KEY_API_KEY)  # Correct!


═══════════════════════════════════════════════════════════════════════════
DUAL-MODE I/O PATTERN
═══════════════════════════════════════════════════════════════════════════

All methods follow the GUI-first, Terminal-fallback pattern established by
zDisplay's dual-mode architecture:

1. Try Bifrost (GUI) mode first via send_gui_event()
2. If GUI mode succeeds (returns True), return immediately
3. If GUI mode unavailable (returns False), fall back to Terminal mode
4. Terminal mode uses composition: BasicOutputs for text, Signals for status

Example Flow:
    login_success(user_data)
    ├─ GUI Mode:      Send "auth_login_success" event to Bifrost
    │                 → Frontend shows success modal/notification
    │                 → Return immediately
    └─ Terminal Mode: Use Signals.success() for colored message
                      Use BasicOutputs.text() for detailed info


═══════════════════════════════════════════════════════════════════════════
COMPOSITION PATTERN
═══════════════════════════════════════════════════════════════════════════

zAuthEvents depends on two sibling event packages via composition:

Dependencies:
    BasicOutputs (display_event_outputs.py):
        - header():  Display section headers ("[*] Authentication Status")
        - text():    Display formatted text with indentation
        - Used for: Detailed authentication status display
    
    Signals (display_event_signals.py):
        - success(): Display success messages (green ✓)
        - error():   Display error messages (red ✗)
        - warning(): Display warning messages (yellow ⚠)
        - Used for: Quick status feedback (login/logout results)

Cross-Reference:
    zAuthEvents depends on: BasicOutputs, Signals
    No other packages depend on zAuthEvents (leaf node in dependency graph)


═══════════════════════════════════════════════════════════════════════════
METHODS PROVIDED
═══════════════════════════════════════════════════════════════════════════

Authentication Flow:
    login_prompt():           Collect username/password credentials
    login_success():          Display successful login message
    login_failure():          Display login failure message
    logout_success():         Display successful logout message
    logout_warning():         Display "not logged in" warning

Status Display:
    status_display():         Display full authentication status (logged in)
    status_not_authenticated(): Display "not authenticated" message

Helper Methods (Private):
    _try_gui_event():         DRY helper for GUI event dispatch
    _signal():                DRY helper for Signal messages
    _output_text():           DRY helper for BasicOutputs text
    _truncate_api_key():      DRY helper for secure API key truncation


═══════════════════════════════════════════════════════════════════════════
USAGE EXAMPLES
═══════════════════════════════════════════════════════════════════════════

1. Login Flow (called by zAuth.login):
    ```python
    # zAuth validates credentials, then calls zAuthEvents for UI feedback
    user_data = {
        ZAUTH_KEY_AUTHENTICATED: True,
        ZAUTH_KEY_ID: 12345,
        ZAUTH_KEY_USERNAME: "admin",
        ZAUTH_KEY_ROLE: "admin",
        ZAUTH_KEY_API_KEY: "sk_live_abc123..."
    }
    zcli.display.zEvents.zAuth.login_success(user_data)
    
    # Output (Terminal):
    # ✓ [OK] Logged in as: admin (admin)
    #      User ID: 12345
    #      API Key: sk_live_abc123...
    ```

2. Status Display (called by zAuth.status):
    ```python
    auth_data = zcli.session["zAuth"]["zSession"]
    if auth_data.get(ZAUTH_KEY_AUTHENTICATED):
        zcli.display.zEvents.zAuth.status_display(auth_data)
    else:
        zcli.display.zEvents.zAuth.status_not_authenticated()
    
    # Output (Terminal):
    # [*] Authentication Status
    #     Username:   admin
    #     Role:       admin
    #     User ID:    12345
    #     API Key:    sk_live_abc123...
    ```

3. Login Prompt (interactive):
    ```python
    credentials = zcli.display.zEvents.zAuth.login_prompt()
    # Terminal prompts:
    # Username: admin
    # Password: ******
    # Returns: {"username": "admin", "password": "secret"}
    ```


═══════════════════════════════════════════════════════════════════════════
FUTURE ENHANCEMENTS (Document for Week 6.5+)
═══════════════════════════════════════════════════════════════════════════

1. Context-Aware Display:
   - Add optional 'context' parameter to methods: login_success(user_data, context="zSession")
   - Display different messages for zSession vs application vs dual auth
   - Example: "✓ Logged in as: admin (zSession)" vs "✓ Logged in as: customer (eCommerce Store)"

2. Multi-App Status Display:
   - Add app_list_display() method to show all authenticated applications
   - status_display() should list all active apps when multiple apps authenticated
   - Show active app indicator with ➤ or [ACTIVE] badge

3. Dual-Mode Indicator:
   - When session["zAuth"]["dual_mode"] == True, show dual-mode badge
   - Display both identities side-by-side:
     "✓ Dual Auth: admin (zSession) + store_owner (eCommerce Store)"

4. Enhanced Security Display:
   - Show session expiration time
   - Show last login timestamp
   - Show authentication method (password, token, OAuth)
   - Add session_info_display() method


═══════════════════════════════════════════════════════════════════════════
THREAD SAFETY
═══════════════════════════════════════════════════════════════════════════

Instance is thread-safe (read-only access to parent display instance).
All state is stored in zAuth subsystem's session dict, not in zAuthEvents.


═══════════════════════════════════════════════════════════════════════════
MODULE CONSTANTS
═══════════════════════════════════════════════════════════════════════════

See below for 30+ module-level constants defining event names, dict keys,
messages, prompts, formatting strings, and default values.
"""

from typing import Any, Optional, Dict

# Import zAuth constants from zConfig (standardized authentication keys)
# Note: Additional constants (ZAUTH_KEY_ZSESSION, ZAUTH_KEY_APPLICATIONS, etc.)
# are documented in module docstring for future Week 6.5+ enhancements but not
# yet used in current implementation
from zCLI.subsystems.zConfig.zConfig_modules import (
    ZAUTH_KEY_AUTHENTICATED,   # "authenticated" - auth status flag
    ZAUTH_KEY_ID,              # "id" - user ID (NOT "user_id"!)
    ZAUTH_KEY_USERNAME,        # "username" - username
    ZAUTH_KEY_ROLE,            # "role" - user role
    ZAUTH_KEY_API_KEY,         # "api_key" - API key (NOT "API_Key"!)
)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Event Names (Bifrost WebSocket Events)
EVENT_AUTH_LOGIN_PROMPT = "auth_login_prompt"      # Request credentials from GUI
EVENT_AUTH_LOGIN_SUCCESS = "auth_login_success"    # Login succeeded
EVENT_AUTH_LOGIN_FAILURE = "auth_login_failure"    # Login failed
EVENT_AUTH_LOGOUT_SUCCESS = "auth_logout_success"  # Logout succeeded
EVENT_AUTH_LOGOUT_WARNING = "auth_logout_warning"  # Logout warning (not logged in)
EVENT_AUTH_STATUS = "auth_status"                  # Authentication status

# Local Dictionary Keys (for GUI events, not session data)
KEY_FIELDS = "fields"                              # Array of field names for form
KEY_REASON = "reason"                              # Failure reason message
KEY_PASSWORD = "password"                          # Password field

# Success Messages (Terminal Output)
MSG_LOGIN_SUCCESS = "[OK] Logged in as: {username} ({role})"  # Login success format
MSG_LOGOUT_SUCCESS = "[OK] Logged out successfully"           # Logout success
MSG_STATUS_HEADER = "[*] Authentication Status"               # Status display header

# Warning Messages (Terminal Output)
MSG_LOGOUT_WARNING = "[WARN] Not currently logged in"                         # Not logged in
MSG_NOT_AUTHENTICATED = "[WARN] Not authenticated. Run 'auth login' to authenticate."  # Auth required

# Error Message Format (Terminal Output)
MSG_LOGIN_FAILURE = "[FAIL] Authentication failed: {reason}"  # Login failure format

# Prompts (Terminal Input)
PROMPT_USERNAME = "Username: "   # Username input prompt
PROMPT_PASSWORD = "Password: "   # Password input prompt

# Formatting Constants (Terminal Status Display)
FORMAT_USERNAME = "Username:   {value}"  # Username display format (aligned)
FORMAT_ROLE = "Role:       {value}"      # Role display format (aligned)
FORMAT_USER_ID = "User ID:    {value}"   # User ID display format (aligned)
FORMAT_API_KEY = "API Key:    {value}"   # API key display format (aligned)

# Default Values
DEFAULT_LOGIN_FAILURE_REASON = "Invalid credentials"  # Default failure reason
DEFAULT_TRUNCATE_LENGTH = 20                          # API key display length (security)
DEFAULT_TRUNCATE_SUFFIX = "..."                       # Truncation suffix

# Field List Constant (for login form)
FIELDS_LOGIN = [ZAUTH_KEY_USERNAME, KEY_PASSWORD]     # Login form fields


# ═══════════════════════════════════════════════════════════════════════════
# ZAUTHEVENTS CLASS
# ═══════════════════════════════════════════════════════════════════════════

class zAuthEvents:
    """
    Authentication UI Events for zDisplay (Dual-Mode Terminal + Bifrost).
    
    Provides user interface presentation for zAuth subsystem operations,
    translating authentication state changes into user-visible feedback
    across both Terminal and Bifrost (GUI) modes.
    
    Integration:
        zAuth subsystem → zAuthEvents → zDisplay → Terminal/Bifrost
    
    Three-Tier Authentication Awareness:
        This class uses standardized constants from zConfig to access
        authentication data, ensuring consistency with zAuth's three-tier
        model (zSession, application, dual contexts).
    
    Composition:
        Depends on: BasicOutputs (formatted text), Signals (status messages)
        Used by: zAuth subsystem (authentication.py)
    
    Methods:
        Authentication Flow:
            - login_prompt():           Interactive credential collection
            - login_success():          Success message display
            - login_failure():          Failure message display
            - logout_success():         Logout confirmation
            - logout_warning():         "Not logged in" warning
        
        Status Display:
            - status_display():         Full auth status (logged in)
            - status_not_authenticated(): "Not authenticated" message
        
        Helper Methods (Private):
            - _try_gui_event():         GUI event dispatch helper
            - _signal():                Signal message helper
            - _output_text():           BasicOutputs text helper
            - _truncate_api_key():      Secure API key truncation
    
    Dual-Mode Pattern:
        All methods follow GUI-first, Terminal-fallback:
        1. Try Bifrost (GUI) via send_gui_event()
        2. If GUI succeeds, return immediately
        3. If GUI unavailable, fall back to Terminal output
    
    Usage:
        # Called by zAuth subsystem
        user_data = {
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "admin",
            ZAUTH_KEY_ROLE: "admin"
        }
        zcli.display.zEvents.zAuth.login_success(user_data)
    """
    
    # Class-level type declarations
    display: Any                           # Parent zDisplay instance
    zPrimitives: Any                       # Primitives for I/O operations
    zColors: Any                           # Colors for Terminal output
    BasicOutputs: Optional[Any]            # BasicOutputs event package (set after init)
    Signals: Optional[Any]                 # Signals event package (set after init)

    def __init__(self, display_instance: Any) -> None:
        """
        Initialize zAuthEvents with reference to parent zDisplay instance.
        
        Args:
            display_instance: Parent zDisplay instance (provides access to
                            zPrimitives, zColors, and will provide BasicOutputs
                            and Signals after zEvents initialization completes)
        
        Returns:
            None
        
        Notes:
            - BasicOutputs and Signals are set to None initially
            - They will be populated by zEvents.__init__ after all event
              packages are instantiated (to avoid circular dependencies)
            - This is part of zDisplay's cross-reference architecture
        """
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        self.BasicOutputs = None  # Will be set after zEvents initialization
        self.Signals = None  # Will be set after zEvents initialization


    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS (Private)
    # ═══════════════════════════════════════════════════════════════════════

    def _try_gui_event(self, event_name: str, data: Dict[str, Any]) -> bool:
        """
        Try to send GUI event to Bifrost mode (DRY helper).
        
        Args:
            event_name: WebSocket event name (e.g., "auth_login_success")
            data: Event data dictionary to send to frontend
        
        Returns:
            bool: True if GUI mode succeeded (message sent), False if Terminal mode
        
        Usage:
            if self._try_gui_event(EVENT_AUTH_LOGIN_SUCCESS, {"username": "admin"}):
                return  # GUI handled it
            # Fall back to Terminal mode
        """
        return self.zPrimitives.send_gui_event(event_name, data)

    def _signal(self, method_name: str, message: str) -> None:
        """
        Send signal message if Signals package available (DRY helper).
        
        Args:
            method_name: Signal method to call ("success", "error", "warning")
            message: Message to display
        
        Returns:
            None
        
        Usage:
            self._signal("success", MSG_LOGIN_SUCCESS.format(username="admin", role="admin"))
        """
        if self.Signals:
            getattr(self.Signals, method_name)(message)

    def _output_text(self, content: str, indent: int = 0, break_after: bool = True) -> None:
        """
        Output text if BasicOutputs package available (DRY helper).
        
        Args:
            content: Text content to display
            indent: Indentation level (default: 0)
            break_after: Add line break after text (default: True)
        
        Returns:
            None
        
        Usage:
            self._output_text(FORMAT_USERNAME.format(value="admin"), indent=1, break_after=False)
        """
        if self.BasicOutputs:
            self.BasicOutputs.text(content, indent=indent, break_after=break_after)

    def _truncate_api_key(self, api_key: str) -> str:
        """
        Truncate API key for secure display (DRY helper).
        
        Args:
            api_key: Full API key string
        
        Returns:
            str: Truncated API key (e.g., "sk_live_abc123..." for security)
        
        Example:
            "sk_live_abc123def456ghi789" → "sk_live_abc123..."
        
        Security Note:
            Only first 20 characters are shown to prevent API key leakage
            in logs, screenshots, or screen recordings.
        """
        if not api_key:
            return ""
        return api_key[:DEFAULT_TRUNCATE_LENGTH] + DEFAULT_TRUNCATE_SUFFIX


    # ═══════════════════════════════════════════════════════════════════════
    # AUTHENTICATION FLOW METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def login_prompt(
        self, 
        username: Optional[str] = None, 
        password: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Prompt for username/password credentials in Terminal or Bifrost mode.
        
        Args:
            username: Pre-filled username (optional, if already known)
            password: Pre-filled password (optional, for auto-login)
        
        Returns:
            Optional[Dict[str, str]]: Credentials dict with "username" and "password" keys
                                     (Terminal mode), or None (Bifrost mode, async response)
        
        Bifrost Mode:
            - Sends "auth_login_prompt" event to frontend
            - Frontend displays login form (modal or page)
            - User submits credentials → sent back via WebSocket
            - Returns None immediately (async flow)
        
        Terminal Mode:
            - Prompts for username (if not provided)
            - Prompts for password (masked input)
            - Returns credentials dict immediately
        
        Usage:
            # Interactive login (Terminal)
            credentials = zcli.display.zEvents.zAuth.login_prompt()
            # Terminal shows:
            # Username: admin
            # Password: ******
            # Returns: {"username": "admin", "password": "secret"}
            
            # Pre-filled username (Terminal)
            credentials = zcli.display.zEvents.zAuth.login_prompt(username="admin")
            # Terminal shows:
            # Password: ******
            # Returns: {"username": "admin", "password": "secret"}
        
        Notes:
            - Password input is always masked in Terminal mode
            - Bifrost mode uses async WebSocket response (handled by zAuth)
            - Pre-filled values are sent to Bifrost for form pre-population
        """
        # Try Bifrost (GUI) mode first - send login form request
        if self._try_gui_event(EVENT_AUTH_LOGIN_PROMPT, {
            ZAUTH_KEY_USERNAME: username,
            KEY_PASSWORD: password,
            KEY_FIELDS: FIELDS_LOGIN
        }):
            # Bifrost mode - frontend will send response via WebSocket
            return None

        # Terminal mode - interactive prompts
        if not username:
            username = self.zPrimitives.read_string(PROMPT_USERNAME)

        if not password:
            password = self.zPrimitives.read_password(PROMPT_PASSWORD)

        return {ZAUTH_KEY_USERNAME: username, KEY_PASSWORD: password}

    def login_success(self, user_data: Dict[str, Any]) -> None:
        """
        Display successful login message with user details in Terminal or Bifrost mode.
        
        Args:
            user_data: Authentication data dict containing:
                      - ZAUTH_KEY_USERNAME: Username
                      - ZAUTH_KEY_ROLE: User role
                      - ZAUTH_KEY_ID: User ID
                      - ZAUTH_KEY_API_KEY: API key (optional)
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_login_success" event with user data
            - Frontend displays success notification/modal
            - Returns immediately
        
        Terminal Mode:
            - Displays success message with username and role
            - Displays user ID and truncated API key (if present)
            - Uses Signals.success() for colored output
        
        Usage:
            user_data = {
                ZAUTH_KEY_AUTHENTICATED: True,
                ZAUTH_KEY_ID: 12345,
                ZAUTH_KEY_USERNAME: "admin",
                ZAUTH_KEY_ROLE: "admin",
                ZAUTH_KEY_API_KEY: "sk_live_abc123..."
            }
            zcli.display.zEvents.zAuth.login_success(user_data)
            
            # Terminal Output:
            # ✓ [OK] Logged in as: admin (admin)
            #      User ID: 12345
            #      API Key: sk_live_abc123...
        
        Notes:
            - API key is truncated for security (only first 20 chars shown)
            - Uses zAuth constants for all dict key access
            - Green colored output in Terminal via Signals.success()
        """
        # Try Bifrost (GUI) mode first
        api_key = user_data.get(ZAUTH_KEY_API_KEY, "")
        if self._try_gui_event(EVENT_AUTH_LOGIN_SUCCESS, {
            ZAUTH_KEY_USERNAME: user_data.get(ZAUTH_KEY_USERNAME),
            ZAUTH_KEY_ROLE: user_data.get(ZAUTH_KEY_ROLE),
            ZAUTH_KEY_ID: user_data.get(ZAUTH_KEY_ID),
            ZAUTH_KEY_API_KEY: self._truncate_api_key(api_key) if api_key else None
        }):
            return

        # Terminal mode - formatted display
        username = user_data.get(ZAUTH_KEY_USERNAME)
        role = user_data.get(ZAUTH_KEY_ROLE)
        self._signal("success", MSG_LOGIN_SUCCESS.format(username=username, role=role))
        
        user_id = user_data.get(ZAUTH_KEY_ID)
        self._output_text(f"     User ID: {user_id}", break_after=False)
        
        if api_key:
            truncated_key = self._truncate_api_key(api_key)
            self._output_text(f"     API Key: {truncated_key}", break_after=False)

    def login_failure(self, reason: str = DEFAULT_LOGIN_FAILURE_REASON) -> None:
        """
        Display login failure message in Terminal or Bifrost mode.
        
        Args:
            reason: Failure reason message (default: "Invalid credentials")
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_login_failure" event with reason
            - Frontend displays error notification/modal
            - Returns immediately
        
        Terminal Mode:
            - Displays error message with failure reason
            - Uses Signals.error() for red colored output
        
        Usage:
            zcli.display.zEvents.zAuth.login_failure()
            # Terminal Output: ✗ [FAIL] Authentication failed: Invalid credentials
            
            zcli.display.zEvents.zAuth.login_failure("User not found")
            # Terminal Output: ✗ [FAIL] Authentication failed: User not found
        
        Notes:
            - Default reason is "Invalid credentials"
            - Red colored output in Terminal via Signals.error()
        """
        # Try Bifrost (GUI) mode first
        if self._try_gui_event(EVENT_AUTH_LOGIN_FAILURE, {KEY_REASON: reason}):
            return

        # Terminal mode - error message
        self._signal("error", MSG_LOGIN_FAILURE.format(reason=reason))

    def logout_success(self) -> None:
        """
        Display successful logout message in Terminal or Bifrost mode.
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_logout_success" event
            - Frontend displays logout confirmation
            - Returns immediately
        
        Terminal Mode:
            - Displays success message
            - Uses Signals.success() for green colored output
        
        Usage:
            zcli.display.zEvents.zAuth.logout_success()
            # Terminal Output: ✓ [OK] Logged out successfully
        
        Notes:
            - Simple confirmation message
            - No user data needed (session already cleared)
        """
        # Try Bifrost (GUI) mode first
        if self._try_gui_event(EVENT_AUTH_LOGOUT_SUCCESS, {}):
            return

        # Terminal mode - success message
        self._signal("success", MSG_LOGOUT_SUCCESS)

    def logout_warning(self) -> None:
        """
        Display warning when attempting to logout while not logged in.
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_logout_warning" event
            - Frontend displays warning notification
            - Returns immediately
        
        Terminal Mode:
            - Displays warning message
            - Uses Signals.warning() for yellow colored output
        
        Usage:
            zcli.display.zEvents.zAuth.logout_warning()
            # Terminal Output: ⚠ [WARN] Not currently logged in
        
        Notes:
            - Called when user tries to logout without being authenticated
            - Yellow colored output in Terminal via Signals.warning()
        """
        # Try Bifrost (GUI) mode first
        if self._try_gui_event(EVENT_AUTH_LOGOUT_WARNING, {}):
            return

        # Terminal mode - warning message
        self._signal("warning", MSG_LOGOUT_WARNING)


    # ═══════════════════════════════════════════════════════════════════════
    # STATUS DISPLAY METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def status_display(self, auth_data: Dict[str, Any]) -> None:
        """
        Display full authentication status in Terminal or Bifrost mode.
        
        Args:
            auth_data: Authentication data dict containing:
                      - ZAUTH_KEY_AUTHENTICATED: True (must be authenticated)
                      - ZAUTH_KEY_USERNAME: Username
                      - ZAUTH_KEY_ROLE: User role
                      - ZAUTH_KEY_ID: User ID
                      - ZAUTH_KEY_API_KEY: API key (optional)
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_status" event with full auth data
            - Frontend displays status panel/card
            - Returns immediately
        
        Terminal Mode:
            - Displays formatted status with header
            - Shows username, role, user ID, API key (truncated)
            - Uses BasicOutputs.header() and .text() for formatting
        
        Usage:
            auth_data = zcli.session["zAuth"]["zSession"]
            zcli.display.zEvents.zAuth.status_display(auth_data)
            
            # Terminal Output:
            # [*] Authentication Status
            #     Username:   admin
            #     Role:       admin
            #     User ID:    12345
            #     API Key:    sk_live_abc123...
        
        Notes:
            - Called when user is authenticated (ZAUTH_KEY_AUTHENTICATED == True)
            - API key is truncated for security
            - Aligned formatting for readability
            - Uses zAuth constants for all dict key access
        
        Future Enhancement (Week 6.5+):
            - Add context parameter to show zSession vs application context
            - Add multi-app display (list all authenticated apps)
            - Add dual-mode indicator (when both zSession and app active)
            - Add session expiration time
        """
        # Try Bifrost (GUI) mode first
        api_key = auth_data.get(ZAUTH_KEY_API_KEY, "")
        if self._try_gui_event(EVENT_AUTH_STATUS, {
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: auth_data.get(ZAUTH_KEY_USERNAME),
            ZAUTH_KEY_ROLE: auth_data.get(ZAUTH_KEY_ROLE),
            ZAUTH_KEY_ID: auth_data.get(ZAUTH_KEY_ID),
            ZAUTH_KEY_API_KEY: self._truncate_api_key(api_key) if api_key else None
        }):
            return

        # Terminal mode - formatted status display
        if self.BasicOutputs:
            self.BasicOutputs.header(MSG_STATUS_HEADER)
            
            username = auth_data.get(ZAUTH_KEY_USERNAME)
            self._output_text(FORMAT_USERNAME.format(value=username), indent=1, break_after=False)
            
            role = auth_data.get(ZAUTH_KEY_ROLE)
            self._output_text(FORMAT_ROLE.format(value=role), indent=1, break_after=False)
            
            user_id = auth_data.get(ZAUTH_KEY_ID)
            self._output_text(FORMAT_USER_ID.format(value=user_id), indent=1, break_after=False)
            
            if api_key:
                truncated_key = self._truncate_api_key(api_key)
                self._output_text(FORMAT_API_KEY.format(value=truncated_key), indent=1, break_after=False)

    def status_not_authenticated(self) -> None:
        """
        Display "not authenticated" message in Terminal or Bifrost mode.
        
        Returns:
            None
        
        Bifrost Mode:
            - Sends "auth_status" event with authenticated: False
            - Frontend displays "not authenticated" state
            - Returns immediately
        
        Terminal Mode:
            - Displays warning message with instructions
            - Uses Signals.warning() for yellow colored output
        
        Usage:
            if not zcli.auth.is_authenticated():
                zcli.display.zEvents.zAuth.status_not_authenticated()
            
            # Terminal Output:
            # ⚠ [WARN] Not authenticated. Run 'auth login' to authenticate.
        
        Notes:
            - Called when user is not authenticated
            - Includes helpful instruction to run 'auth login'
            - Yellow colored output in Terminal via Signals.warning()
        """
        # Try Bifrost (GUI) mode first
        if self._try_gui_event(EVENT_AUTH_STATUS, {ZAUTH_KEY_AUTHENTICATED: False}):
            return

        # Terminal mode - warning message
        self._signal("warning", MSG_NOT_AUTHENTICATED)
