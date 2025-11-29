# zCLI/subsystems/zWalker/zWalker.py

"""
zWalker Subsystem - Orchestration & Navigation Engine for YAML-driven UI/Menu systems.

This module provides the top-level orchestration layer for zCLI's interactive UI mode,
coordinating navigation, menu rendering, breadcrumb tracking, and dual-mode execution
(Terminal and zBifrost WebSocket). zWalker extends zWizard to leverage its loop engine
while adding walker-specific navigation and session management.

────────────────────────────────────────────────────────────────────────────────
ARCHITECTURE: ORCHESTRATOR PATTERN
────────────────────────────────────────────────────────────────────────────────

zWalker is a pure orchestrator - it delegates all operations to specialized subsystems:

    ┌──────────────────────────────────────────────────────────────┐
    │                    ZWALKER (ORCHESTRATOR)                    │
    ├──────────────────────────────────────────────────────────────┤
    │                                                              │
    │  INHERITANCE:                                                │
    │      zWalker extends zWizard (for execute_loop)             │
    │                                                              │
    │  ORCHESTRATION MAP:                                          │
    │      ┌────────────────────────────────────────┐              │
    │      │  run()                                 │              │
    │      │    ├─→ session.get("zMode")           │              │
    │      │    │   └─→ "zBifrost" → _start_bifrost_server()  │  │
    │      │    │                                    │              │
    │      │    ├─→ loader.handle(zVaFile)          │              │
    │      │    ├─→ _init_walker_session()          │              │
    │      │    └─→ zBlock_loop(root_zBlock)        │              │
    │      │                                         │              │
    │      │  zBlock_loop()                         │              │
    │      │    ├─→ display.zDeclare()              │              │
    │      │    ├─→ navigation.handle_zCrumbs()     │              │
    │      │    ├─→ navigation.handle_zBack()       │              │
    │      │    ├─→ dispatch.handle()               │              │
    │      │    └─→ execute_loop() (from zWizard)   │              │
    │      │                                         │              │
    │      │  _start_bifrost_server()               │              │
    │      │    └─→ comm.websocket.start_socket_server() │        │
    │      └────────────────────────────────────────┘              │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────────────────
DUAL-MODE ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────

zWalker supports two execution modes, determined by zSession's zMode:

**Terminal Mode (Default):**
    - Traditional CLI menu navigation
    - Readline-based input with history
    - ASCII-formatted display via zDisplay
    - Direct keyboard input (STDIN)
    - Synchronous execution

**zBifrost Mode (WebSocket):**
    - WebSocket-based client-server architecture
    - JSON message protocol for commands/events
    - HTML-formatted display via zDisplay
    - Remote client input (WebSocket messages)
    - Asynchronous execution via asyncio

Mode Detection:
    ```python
    if self.session.get("zMode") == "zBifrost":
        return self._start_bifrost_server()  # WebSocket mode
    else:
        return self.zBlock_loop(...)  # Terminal mode (default)
    ```

────────────────────────────────────────────────────────────────────────────────
NAVIGATION CALLBACKS PATTERN
────────────────────────────────────────────────────────────────────────────────

zWalker defines 4 navigation callbacks passed to zWizard's execute_loop:

**on_back(result):**
    - Triggered by zBack navigation action
    - Calls navigation.handle_zBack() to pop breadcrumb stack
    - Recursively calls zBlock_loop with previous block
    - Returns to previous menu level

**on_exit(result):**
    - Soft exit - returns control to caller (zShell or script)
    - Displays "Walker session completed" message
    - Returns {"exit": "completed"} dict
    - Does NOT terminate process (graceful return)

**on_stop(result):**
    - Hard stop - terminates entire system
    - Displays "You've stopped the system!" message
    - Calls sys.exit() to terminate process
    - Used for user-requested full shutdown

**on_error(error_or_result, key):**
    - Error handling for failed dispatch operations
    - Displays "Error Returned" message
    - Calls sys.exit() to cleanly exit
    - Logs error context for debugging

────────────────────────────────────────────────────────────────────────────────
BREADCRUMB TRACKING
────────────────────────────────────────────────────────────────────────────────

zWalker maintains navigation history in zSession["zCrumbs"] for:
    - Back navigation (zBack action)
    - Navigation history display
    - Current location tracking

Format:
    ```python
    zSession["zCrumbs"] = {
        "@.zUI.main_menu.MainMenu": ["dashboard", "settings"],
        "@.zUI.settings_menu.SettingsMenu": ["profile"]
    }
    ```

Breadcrumb Path Construction:
    - Full path: zVaFile + "." + zBlock
    - Example: "@.zUI.users_menu" + ".MainMenu" = "@.zUI.users_menu.MainMenu"

────────────────────────────────────────────────────────────────────────────────
DEPENDENCIES
────────────────────────────────────────────────────────────────────────────────

**Subsystems (All from zcli instance):**
    - zWizard: Loop engine (via inheritance)
    - zNavigation: Breadcrumbs, menus, back navigation, inter-file linking
    - zDisplay: Mode-agnostic output (Terminal + Bifrost)
    - zDispatch: Command routing and execution
    - zLoader: YAML file loading (zVaFile)
    - zConfig: Session management (zMode, zCrumbs, zBlock)
    - zComm: WebSocket server (zBifrost mode)
    - zFunc: Function execution (via dispatch)
    - zOpen: File/URL opening (via dispatch)
    - zUtils: Plugin system (via dispatch)

**External Modules:**
    - sys: For sys.exit() in hard stop
    - asyncio: For zBifrost server (imported inline)

────────────────────────────────────────────────────────────────────────────────
USAGE
────────────────────────────────────────────────────────────────────────────────

**Terminal Mode:**
    ```python
    from zCLI.subsystems.zWalker import zWalker
    
    walker = zWalker(zcli)
    walker.run()  # Starts terminal-based menu navigation
    ```

**zBifrost Mode (WebSocket):**
    ```python
    # Set mode before walker initialization
    zcli.session["zMode"] = "zBifrost"
    
    walker = zWalker(zcli)
    walker.run()  # Starts WebSocket server instead of terminal loop
    ```

**From zShell (Launch Walker from Shell):**
    ```python
    # User types: launch @.zUI.main_menu
    # zShell creates walker and calls run()
    ```

────────────────────────────────────────────────────────────────────────────────
NOTES
────────────────────────────────────────────────────────────────────────────────

- zWalker is intentionally kept as a single file (pure orchestrator, no submodules)
- All heavy lifting delegated to subsystems (no local instances)
- Navigation logic centralized in zNavigation (Week 6.7)
- Loop engine inherited from zWizard (Week 6.14)
- Dual-mode support via mode-agnostic zDisplay (Week 6.4)
- Session state managed via zConfig (Week 6.2)
"""

from typing import Any, Dict, Optional, List
from zCLI import sys
from zCLI.subsystems.zWizard import zWizard

# ============================================================
# SESSION KEYS
# ============================================================
SESSION_KEY_MODE = "zMode"
SESSION_KEY_CRUMBS = "zCrumbs"
SESSION_KEY_BLOCK = "zBlock"
SESSION_KEY_VAFILE = "zVaFile"

# ============================================================
# ZSPARK KEYS
# ============================================================
ZSPARK_KEY_VAFILE = "zVaFile"
ZSPARK_KEY_BLOCK = "zBlock"
ZSPARK_DEFAULT_ROOT = "root"

# ============================================================
# MODES
# ============================================================
MODE_DEBUG = "Debug"
MODE_BIFROST = "zBifrost"
MODE_TERMINAL = "Terminal"

# ============================================================
# DISPLAY CONSTANTS
# ============================================================
COLOR_MAIN = "MAIN"
INDENT_NORMAL = 0
INDENT_ERROR = 2
STYLE_FULL = "full"
STYLE_MINIMAL = "~"

# ============================================================
# MESSAGES
# ============================================================
MSG_WALKER_READY = "zWalker Ready"
MSG_WALKER_LOOP = "zWalker Loop"
MSG_SESSION_COMPLETED = "Walker session completed"
MSG_SYSTEM_STOPPED = "You've stopped the system!"
MSG_ERROR_RETURNED = "Error Returned"
MSG_BIFROST_STARTING = "Starting zBifrost WebSocket server..."
MSG_WALKER_INIT = "zWalker initialized (fully modernized architecture)"

# ============================================================
# ERROR MESSAGES
# ============================================================
ERROR_NO_VAFILE = "No zVaFile specified"
ERROR_FAILED_LOAD = "Failed to load zVaFile"
ERROR_BLOCK_NOT_FOUND = "Root zBlock not found"
ERROR_EXECUTION_FAILED = "zWalker execution failed"

# ============================================================
# DICT KEYS (for return values)
# ============================================================
DICT_KEY_ERROR = "error"
DICT_KEY_EXIT = "exit"
DICT_VALUE_COMPLETED = "completed"

# ============================================================
# SPECIAL DICT KEYS (zWizard detection)
# ============================================================
SPECIAL_KEY_ZWIZARD = "zWizard"

# ============================================================
# NAVIGATION CALLBACK KEYS
# ============================================================
CALLBACK_ON_BACK = "on_back"
CALLBACK_ON_EXIT = "on_exit"
CALLBACK_ON_STOP = "on_stop"
CALLBACK_ON_ERROR = "on_error"

# ============================================================
# LOGGER LEVELS
# ============================================================
LOGGER_LEVEL_DEBUG = "DEBUG"
LOGGER_LEVEL_INFO = "INFO"

# ============================================================
# LOG MESSAGES
# ============================================================
LOG_ERROR_NO_VAFILE = "No zVaFile specified in zSpark_obj"
LOG_ERROR_FAILED_LOAD = "Failed to load zVaFile: %s"
LOG_ERROR_BLOCK_NOT_FOUND = "Root zBlock '%s' not found in zVaFile"
LOG_ERROR_EXECUTION = "zWalker execution failed: %s"
LOG_DEBUG_ACTIVE_BLOCK = "active_zBlock: %s"
LOG_DEBUG_WALKING_HORIZONTAL = "\nWalking zHorizontal:\n%s"
LOG_DEBUG_ZWIZARD_SKIP = "zWizard key detected; breadcrumb tracking skipped for %s"
LOG_DEBUG_ZWIZARD_EXECUTE = "Executing zWizard directly (bypass dispatch)"
LOG_DEBUG_BREADCRUMB = "Initialized breadcrumb: %s"
LOG_DEBUG_DISPATCH_EXIT = "Dispatch returned exit"
LOG_DEBUG_DISPATCH_STOP = "Dispatch returned stop"
LOG_WARNING_INVALID_CRUMB = "Skipping invalid crumb: %s not in %s"
LOG_DEBUG_DUPLICATE_CRUMB = "Skipping duplicate crumb: %s already last in %s"
LOG_INFO_ERROR_AFTER_KEY = "Error after key: %s"


class zWalker(zWizard):
    """
    Orchestration & Navigation Engine for YAML-driven UI/Menu systems.
    
    zWalker extends zWizard to provide top-level orchestration for interactive
    menu navigation, breadcrumb tracking, and dual-mode execution (Terminal and
    zBifrost WebSocket). It delegates all operations to specialized subsystems
    while coordinating their interactions.
    
    Attributes:
        zcli (Any): Main zCLI instance with all subsystems
        zSpark_obj (Dict[str, Any]): Boot configuration (zVaFile, zBlock, etc.)
        session (Dict[str, Any]): Session state (zMode, zCrumbs, zBlock)
        display (Any): zDisplay instance for mode-agnostic output
        dispatch (Any): zDispatch instance for command routing
        navigation (Any): zNavigation instance for breadcrumbs, menus, linking
        loader (Any): zLoader instance for YAML file loading
        zfunc (Any): zFunc instance for function execution
        open (Any): zOpen instance for file/URL opening
        plugins (Dict[str, Any]): Direct access to loaded plugins
        logger (Any): Logger instance (inherited from zWizard)
    
    Methods:
        __init__(zcli): Initialize zWalker with zCLI instance
        _configure_logger(): Set logger level based on session mode
        run(): Main entry point - dispatches to Terminal or zBifrost mode
        _start_bifrost_server(): Start WebSocket server for zBifrost mode
        _init_walker_session(): Initialize session for walker mode (breadcrumbs)
        zBlock_loop(active_zBlock_dict, zBlock_keys, zKey): Main walker loop
    
    Inheritance:
        Extends zWizard for execute_loop() method (loop engine)
    
    Orchestration Pattern:
        - run() → Detects mode → Terminal or zBifrost
        - Terminal: run() → zBlock_loop() → execute_loop() (zWizard)
        - zBifrost: run() → _start_bifrost_server() → asyncio
        - All operations delegate to subsystems (no local logic)
    
    Navigation Callbacks:
        - on_back: Handle zBack navigation (pop breadcrumb, previous block)
        - on_exit: Soft exit - return to caller (zShell or script)
        - on_stop: Hard stop - terminate entire system (sys.exit)
        - on_error: Error handling - display error and exit
    
    Examples:
        >>> # Terminal mode (default)
        >>> walker = zWalker(zcli)
        >>> walker.run()
        # [User navigates menus, exits with zBack or exit action]
        
        >>> # zBifrost mode (WebSocket)
        >>> zcli.session["zMode"] = "zBifrost"
        >>> walker = zWalker(zcli)
        >>> walker.run()
        # [WebSocket server starts, waits for client connections]
        
        >>> # From zShell (launch walker from shell)
        >>> # User types: launch @.zUI.main_menu
        >>> # zShell creates walker and calls run()
    
    Notes:
        - Pure orchestrator - no local subsystem instances
        - All subsystems accessed via zcli instance
        - Single file design (no submodules needed)
        - Mode-agnostic via zDisplay (Terminal + Bifrost)
        - Session state managed via zConfig
        - Navigation via zNavigation (breadcrumbs, menus, linking)
    """
    
    def __init__(self, zcli: Any) -> None:
        """
        Initialize zWalker with zCLI instance and all subsystems.
        
        Extends zWizard parent class and sets up orchestration by storing
        references to all required subsystems from zcli instance. Configures
        logger based on session mode and displays ready message.
        
        Args:
            zcli: zCLI instance with all core subsystems initialized
                  (display, dispatch, navigation, loader, session, etc.)
        
        Returns:
            None
        
        Examples:
            >>> walker = zWalker(zcli)
            # Output: "zWalker Ready" (via zDisplay)
            # Logger: "zWalker initialized (fully modernized architecture)"
            
        Notes:
            - Calls super().__init__(zcli=zcli, walker=self) to initialize zWizard
            - walker=self allows zWizard to delegate back to walker if needed
            - All subsystems accessed via zcli (no local instances)
            - Logger level auto-configured based on zSession["zMode"]
        """
        # Initialize ZWizard parent first
        super().__init__(zcli=zcli, walker=self)
        
        # Use all core subsystems (no local instances)
        self.zcli: Any = zcli
        self.zSpark_obj: Dict[str, Any] = zcli.zspark_obj
        self.session: Dict[str, Any] = zcli.session
        self.display: Any = zcli.display
        self.dispatch: Any = zcli.dispatch
        self.navigation: Any = zcli.navigation  # Unified navigation system (menus, breadcrumbs, linking)
        self.loader: Any = zcli.loader
        self.zfunc: Any = zcli.zfunc
        self.open: Any = zcli.open
        self.plugins: Dict[str, Any] = zcli.utils.plugins  # Direct access to loaded plugins
        
        # Walker-specific configuration
        self._configure_logger()
        
        # Display ready message using modern zDisplay
        self.display.zDeclare(MSG_WALKER_READY, color=COLOR_MAIN, indent=INDENT_NORMAL, style=STYLE_FULL)
        
        self.logger.framework.debug(MSG_WALKER_INIT)

    def _configure_logger(self) -> None:
        """
        Configure logger level based on session mode.
        
        Sets logger to DEBUG level if zSession["zMode"] == "Debug",
        otherwise sets to INFO level. Gracefully handles missing
        session keys or errors.
        
        Returns:
            None
        
        Examples:
            >>> # Debug mode
            >>> zcli.session["zMode"] = "Debug"
            >>> walker = zWalker(zcli)
            # Logger level: DEBUG
            
            >>> # Normal mode
            >>> zcli.session["zMode"] = "Terminal"
            >>> walker = zWalker(zcli)
            # Logger level: INFO
        
        Notes:
            - Called automatically during __init__
            - Catches all exceptions to prevent init failure
            - logger inherited from zWizard parent class
        """
        try:
            if self.session.get(SESSION_KEY_MODE) == MODE_DEBUG:
                self.logger.setLevel(LOGGER_LEVEL_DEBUG)
            else:
                self.logger.setLevel(LOGGER_LEVEL_INFO)
        except Exception:
            pass

    def run(self) -> Dict[str, Any]:
        """
        Main entry point for zWalker execution.
        
        Detects execution mode (Terminal or zBifrost) and dispatches to
        appropriate handler. Loads zVaFile from zSpark_obj, initializes
        walker session, and starts either terminal loop or WebSocket server.
        
        Returns:
            Dict[str, Any]: Result dictionary with structure:
                - Terminal mode: {"exit": "completed"} or error dict
                - zBifrost mode: Never returns (blocking server)
                - Error: {"error": "error message"}
        
        Examples:
            >>> # Terminal mode (default)
            >>> walker = zWalker(zcli)
            >>> result = walker.run()
            # [User navigates menus, exits]
            >>> print(result)
            {"exit": "completed"}
            
            >>> # zBifrost mode
            >>> zcli.session["zMode"] = "zBifrost"
            >>> walker = zWalker(zcli)
            >>> walker.run()
            # [WebSocket server starts, blocks forever]
            
            >>> # Error case - no zVaFile
            >>> zcli.zspark_obj.pop("zVaFile")
            >>> result = walker.run()
            >>> print(result)
            {"error": "No zVaFile specified"}
        
        Notes:
            - Mode detection via zSession["zMode"]
            - zBifrost mode: starts server, blocks forever (asyncio.run)
            - Terminal mode: runs zBlock_loop until user exits
            - All errors logged and returned as error dict
            - zVaFile and zBlock loaded from zSpark_obj
        """
        try:
            # Check if in zBifrost mode and start server instead
            if self.session.get(SESSION_KEY_MODE) == MODE_BIFROST:
                return self._start_bifrost_server()
            
            # Get zVaFile from zSpark_obj
            zVaFile: Optional[str] = self.zSpark_obj.get(ZSPARK_KEY_VAFILE)
            if not zVaFile:
                self.logger.error(LOG_ERROR_NO_VAFILE)
                return {DICT_KEY_ERROR: ERROR_NO_VAFILE}

            # Load the YAML file
            raw_zFile: Optional[Dict[str, Any]] = self.loader.handle(zVaFile)
            if not raw_zFile:
                self.logger.error(LOG_ERROR_FAILED_LOAD, zVaFile)
                return {DICT_KEY_ERROR: f"{ERROR_FAILED_LOAD}: {zVaFile}"}

            # Get the root zBlock
            root_zBlock: str = self.zSpark_obj.get(ZSPARK_KEY_BLOCK, ZSPARK_DEFAULT_ROOT)
            if root_zBlock not in raw_zFile:
                self.logger.error(LOG_ERROR_BLOCK_NOT_FOUND, root_zBlock)
                return {DICT_KEY_ERROR: f"{ERROR_BLOCK_NOT_FOUND}: '{root_zBlock}'"}

            # Initialize session for walker mode
            self._init_walker_session()

            # Start the walker loop
            return self.zBlock_loop(raw_zFile[root_zBlock])

        except Exception as e:
            self.logger.error(LOG_ERROR_EXECUTION, e, exc_info=True)
            return {DICT_KEY_ERROR: str(e)}

    def _start_bifrost_server(self) -> Dict[str, Any]:
        """
        Start zBifrost WebSocket server for remote client connections.
        
        Creates or retrieves WebSocket instance from zComm subsystem,
        updates walker reference, and starts asyncio server (blocking).
        
        Returns:
            Dict[str, Any]: Never returns normally (server blocks forever)
                            May raise exceptions if server fails to start
        
        Examples:
            >>> zcli.session["zMode"] = "zBifrost"
            >>> walker = zWalker(zcli)
            >>> walker.run()
            # [WebSocket server starts on configured port]
            # [Waits for client connections indefinitely]
        
        Notes:
            - Imports asyncio inline (only needed for zBifrost mode)
            - Gets or creates WebSocket instance from zComm
            - Updates walker reference on existing WebSocket
            - Also updates walker in dispatch_handler if present
            - Blocks forever via asyncio.run() until server stopped
            - Server handles JSON messages for commands/events
        """
        import asyncio
        
        self.logger.info(MSG_BIFROST_STARTING)
        
        # Get or create WebSocket instance
        bifrost: Any = self.zcli.comm.websocket
        if not bifrost:
            bifrost = self.zcli.comm.create_websocket(walker=self)
        else:
            # Update walker on existing instance (created before walker existed)
            bifrost.walker = self
            # Also update walker in dispatch events handler
            if hasattr(bifrost, 'dispatch_handler') and bifrost.dispatch_handler:
                bifrost.dispatch_handler.walker = self
        
        # Start server (blocking)
        asyncio.run(bifrost.start_socket_server(asyncio.Event()))
    
    def _init_walker_session(self) -> None:
        """
        Initialize session state for walker mode.
        
        Sets up breadcrumb tracking in zSession["zCrumbs"] with initial
        breadcrumb path constructed from zVaFile and root zBlock. Preserves
        original zMode (Terminal or zBifrost).
        
        Returns:
            None
        
        Examples:
            >>> # Before: zSession["zCrumbs"] not present
            >>> walker._init_walker_session()
            >>> # After: zSession["zCrumbs"] = {
            >>>    "@.zUI.main_menu.MainMenu": []
            >>> }
            
        Notes:
            - Creates zSession["zCrumbs"] dict if not present
            - Constructs full breadcrumb path: zVaFile.zBlock
            - Example path: "@.zUI.users_menu.MainMenu"
            - Initializes breadcrumb trail as empty list
            - Sets zSession["zBlock"] to root_zBlock
            - Walker runs within existing mode context (no mode change)
        """
        # Preserve original zMode (Terminal or zBifrost)
        # Walker runs within the existing mode context
        
        # Initialize zCrumbs for walker navigation
        if SESSION_KEY_CRUMBS not in self.session:
            self.session[SESSION_KEY_CRUMBS] = {}
        
        # Set initial zBlock - construct full breadcrumb path
        root_zBlock: str = self.zSpark_obj.get(ZSPARK_KEY_BLOCK, ZSPARK_DEFAULT_ROOT)
        zVaFile: str = self.zSpark_obj.get(ZSPARK_KEY_VAFILE, "")
        
        # Construct full breadcrumb path: zVaFile.zBlock
        # Example: "@.zUI.users_menu" + ".MainMenu" = "@.zUI.users_menu.MainMenu"
        full_crumb_path: str = f"{zVaFile}.{root_zBlock}" if zVaFile else root_zBlock
        
        self.session[SESSION_KEY_CRUMBS][full_crumb_path] = []
        self.session[SESSION_KEY_BLOCK] = root_zBlock
        
        self.logger.debug(LOG_DEBUG_BREADCRUMB, full_crumb_path)

    def zBlock_loop(
        self, 
        active_zBlock_dict: Dict[str, Any], 
        zBlock_keys: Optional[List[str]] = None, 
        zKey: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main walker loop for processing zBlocks and navigation.
        
        Orchestrates menu rendering, breadcrumb tracking, dispatch routing,
        and navigation callbacks. Delegates to zWizard's execute_loop for
        actual iteration logic, providing walker-specific dispatch and
        callback functions.
        
        Args:
            active_zBlock_dict: Dictionary of zBlock keys and values (menu items)
            zBlock_keys: Optional list of keys to process (defaults to all keys)
            zKey: Optional starting key (defaults to first key)
        
        Returns:
            Dict[str, Any]: Result from execute_loop or navigation callbacks:
                - {"exit": "completed"} - soft exit to caller
                - Recursive call to zBlock_loop - navigation
                - sys.exit() - hard stop (never returns)
        
        Examples:
            >>> # Basic usage (internal call from run())
            >>> result = walker.zBlock_loop(raw_zFile["MainMenu"])
            # [Displays menu, user navigates, exits]
            >>> print(result)
            {"exit": "completed"}
            
            >>> # With specific keys (internal call from navigation)
            >>> result = walker.zBlock_loop(
            >>>     active_zBlock_dict=menu_dict,
            >>>     zBlock_keys=["dashboard", "settings"],
            >>>     zKey="dashboard"
            >>> )
        
        Notes:
            - Defines 5 nested functions (walker_dispatch, 4 callbacks)
            - walker_dispatch: handles breadcrumb tracking + dispatch routing
            - on_back: pops breadcrumb, recursively calls zBlock_loop
            - on_exit: soft exit, returns control to caller
            - on_stop: hard stop, calls sys.exit()
            - on_error: displays error, calls sys.exit()
            - All navigation delegates to zNavigation subsystem
            - All dispatch delegates to zDispatch subsystem
            - Special case: zWizard key bypasses dispatch
        """
        if zBlock_keys is None:
            zBlock_keys = list(active_zBlock_dict.keys())

        self.display.zDeclare(MSG_WALKER_LOOP, color=COLOR_MAIN, indent=INDENT_NORMAL, style=STYLE_FULL)
        
        # Custom dispatch function that handles breadcrumb tracking
        def walker_dispatch(key: str, value: Any) -> Any:
            """
            Walker-specific dispatch function with breadcrumb tracking.
            
            Handles breadcrumb trail updates, special zWizard key detection,
            and delegates to zDispatch for actual command routing.
            
            Args:
                key: Command/action key from zBlock
                value: Command/action value (dict, string, etc.)
            
            Returns:
                Any: Result from dispatch.handle() or self.handle() (zWizard)
            
            Notes:
                - Tracks breadcrumbs via navigation.handle_zCrumbs()
                - Skips breadcrumb tracking for zWizard keys
                - Special case: zWizard key executes directly via self.handle()
                - Validates key is part of active block before tracking
            """
            active_zBlock: str = next(reversed(self.session[SESSION_KEY_CRUMBS]))
            self.logger.debug(LOG_DEBUG_ACTIVE_BLOCK, active_zBlock)
            self.logger.debug(LOG_DEBUG_WALKING_HORIZONTAL, value)
            
            # [BREADCRUMB] Track breadcrumb trail for navigation/history
            if not (isinstance(value, dict) and SPECIAL_KEY_ZWIZARD in value):
                trail: List[str] = self.session[SESSION_KEY_CRUMBS].get(active_zBlock, [])
                if not trail or trail[-1] != key:
                    # validate key is really part of the active block
                    if key in active_zBlock_dict:
                        self.navigation.handle_zCrumbs(active_zBlock, key, walker=self)
                    else:
                        self.logger.warning(LOG_WARNING_INVALID_CRUMB, key, active_zBlock)
                else:
                    self.logger.debug(LOG_DEBUG_DUPLICATE_CRUMB, key, active_zBlock)
            else:
                self.logger.debug(LOG_DEBUG_ZWIZARD_SKIP, key)
            
            # [SPECIAL CASE] zWizard key requires direct execution
            # The value IS the zWizard dict (step definitions)
            if key == SPECIAL_KEY_ZWIZARD:
                self.logger.debug(LOG_DEBUG_ZWIZARD_EXECUTE)
                return self.handle(value)  # zWalker inherits from zWizard
            
            # Dispatch action with walker context
            return self.dispatch.handle(key, value, walker=self)
        
        # Navigation callbacks for Walker-specific behavior
        def on_back(result: Any) -> Dict[str, Any]:  # pylint: disable=unused-argument
            """
            Handle zBack navigation - pop breadcrumb and return to previous block.
            
            Args:
                result: Unused (required for callback signature)
            
            Returns:
                Dict[str, Any]: Result from recursive zBlock_loop call
            
            Notes:
                - Calls navigation.handle_zBack() to pop breadcrumb stack
                - Recursively calls zBlock_loop with previous block
                - show_banner=False to avoid duplicate "zWalker Loop" message
            """
            active_zBlock_dict_new: Dict[str, Any]
            zBlock_keys_new: List[str]
            zKey_new: Optional[str]
            active_zBlock_dict_new, zBlock_keys_new, zKey_new = self.navigation.handle_zBack(
                show_banner=False, 
                walker=self
            )
            return self.zBlock_loop(active_zBlock_dict_new, zBlock_keys_new, zKey_new)
        
        def on_exit(result: Any) -> Dict[str, Any]:  # pylint: disable=unused-argument
            """
            Handle soft exit - return control to caller (zShell or script).
            
            Args:
                result: Unused (required for callback signature)
            
            Returns:
                Dict[str, Any]: {"exit": "completed"} - soft exit status
            
            Notes:
                - Displays "Walker session completed" message
                - Returns to caller (does NOT terminate process)
                - Used when user exits walker gracefully
            """
            self.logger.debug(LOG_DEBUG_DISPATCH_EXIT)
            self.display.zDeclare(MSG_SESSION_COMPLETED, color=COLOR_MAIN, indent=INDENT_NORMAL, style=STYLE_MINIMAL)
            return {DICT_KEY_EXIT: DICT_VALUE_COMPLETED}  # Soft exit - returns control to caller
        
        def on_stop(result: Any) -> None:  # pylint: disable=unused-argument
            """
            Handle hard stop - terminate entire system.
            
            Args:
                result: Unused (required for callback signature)
            
            Returns:
                None (never returns - sys.exit() terminates process)
            
            Notes:
                - Displays "You've stopped the system!" message
                - Calls sys.exit() to terminate entire process
                - Used for user-requested full shutdown
                - Different from on_exit (which returns to caller)
            """
            self.logger.debug(LOG_DEBUG_DISPATCH_STOP)
            self.display.zDeclare(MSG_SYSTEM_STOPPED, color=COLOR_MAIN, indent=INDENT_NORMAL, style=STYLE_FULL)
            sys.exit()  # Hard stop - terminates everything
        
        def on_error(error_or_result: Any, key: str) -> None:  # pylint: disable=unused-argument
            """
            Handle error during dispatch operation.
            
            Args:
                error_or_result: Error object or result dict
                key: Command key that caused error
            
            Returns:
                None (never returns - sys.exit() terminates process)
            
            Notes:
                - Logs error context for debugging
                - Displays "Error Returned" message
                - Calls sys.exit() to cleanly exit
                - Used when dispatch.handle() fails
            """
            self.logger.info(LOG_INFO_ERROR_AFTER_KEY, key)
            self.display.zDeclare(MSG_ERROR_RETURNED, color=COLOR_MAIN, indent=INDENT_ERROR, style=STYLE_MINIMAL)
            sys.exit()  # Exit cleanly
        
        # Use parent's execute_loop with Walker-specific navigation
        return self.execute_loop(
            items_dict=active_zBlock_dict,
            dispatch_fn=walker_dispatch,
            navigation_callbacks={
                CALLBACK_ON_BACK: on_back,
                CALLBACK_ON_EXIT: on_exit,
                CALLBACK_ON_STOP: on_stop,
                CALLBACK_ON_ERROR: on_error
            },
            start_key=zKey
        )
