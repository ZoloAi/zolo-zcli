# zCLI/subsystems/zDispatch/dispatch_modules/dispatch_launcher.py

"""
Command Launcher for zDispatch Subsystem.

This module provides the CommandLauncher class, which handles routing and execution
of commands within the zCLI framework. It acts as a central dispatcher for various
command types (string-based and dict-based), routing them to appropriate subsystem
handlers.

Architecture:
    The CommandLauncher follows a command routing pattern with two main pathways:
    
    1. String Commands:
       - Format: "zFunc(...)", "zLink(...)", "zOpen(...)", "zWizard(...)", "zRead(...)"
       - Parsed and routed to appropriate subsystem handlers
       - Special handling for plain strings in Bifrost mode (zUI resolution)
    
    2. Dict Commands:
       - Format: {"zFunc": ...}, {"zLink": ...}, {"zDelta": ...}, {"zDialog": ...}, etc.
       - Direct key-based routing to subsystem handlers
       - Support for CRUD operations and legacy zDisplay format
    
    Command Routing Flow:
        launch() -> Type Detection (str vs dict)
                |
        _launch_string() or _launch_dict()
                |
        Specific handler (_handle_wizard_string, _handle_read_dict, etc.)
                |
        Subsystem execution (zFunc, zNavigation, zOpen, zWizard, zData, etc.)

Mode-Specific Behavior:
    Terminal Mode:
        - Plain strings: Return None (no navigation)
        - zWizard: Returns "zBack" for navigation
        - zFunc/zOpen/zLink/zDelta: Returns subsystem result
    
    Bifrost Mode:
        - Plain strings: Resolve from zUI or return {"message": str}
        - zWizard: Returns zHat (actual result) for API consumption
        - zFunc/zOpen/zLink/zDelta: Returns subsystem result
        - Supports recursive resolution (zUI key -> dict with zFunc)

Forward Dependencies:
    This module integrates with 8 subsystems that will be refactored in future weeks:
    
    - zFunc (Week 6.10): Function execution and plugin invocation
    - zNavigation (Week 6.7): zLink handling (inter-file) and menu creation
    - zWalker: zDelta handling (intra-file block navigation)
    - zOpen (Week 6.12): File/URL opening
    - zWizard (Week 6.14): Multi-step workflow execution
    - zLoader (Week 6.9): zUI file loading and parsing
    - zParser (Week 6.8): Plugin invocation resolution
    - zData (Week 6.16): CRUD operations and data management
    - zDialog (Week 6.11): Interactive forms and user input

Plugin Support:
    Supports plugin invocations via "&" prefix in zFunc commands:
    - String: "zFunc(&my_plugin)"
    - Dict: {"zFunc": "&my_plugin"}
    - Resolved via zParser.resolve_plugin_invocation()

CRUD Detection:
    Smart fallback for generic CRUD operations that don't use zRead/zData wrappers:
    - Detects presence of CRUD keys: action, model, table, fields, values, etc.
    - Automatically routes to zData.handle_request()
    - Sets default action to "read" if not specified

Usage Examples:
    # String commands
    launcher.launch("zFunc(my_function)")
    launcher.launch("zLink(menu:users)")
    launcher.launch("zOpen(https://example.com)")
    launcher.launch("zWizard({'steps': [...]})")
    launcher.launch("zRead(users)")
    
    # Dict commands
    launcher.launch({"zFunc": "my_function"})
    launcher.launch({"zLink": "menu:users"})
    launcher.launch({"zDelta": "%Demo_Block"})
    launcher.launch({"zDialog": {"fields": [...]}})
    launcher.launch({"zRead": {"model": "users", "where": {"id": 1}}})
    launcher.launch({"zData": {"action": "create", "model": "users", "values": {...}}})
    
    # Generic CRUD (auto-detected)
    launcher.launch({"action": "read", "model": "users"})
    
    # Legacy zDisplay format (backward compatibility)
    launcher.launch({"zDisplay": {"event": "text", "content": "Hello"}})
    
    # Plain string in Bifrost mode (zUI resolution)
    launcher.launch("my_button_key", context={"mode": "zBifrost"})

Thread Safety:
    - Relies on thread-safe logger and display instances from zCLI
    - Mode detection reads from session context (context dict)
    - No internal state mutation during command execution

Integration with zSession:
    - Mode detection: Uses SESSION_KEY_ZMODE from context
    - Context passing: All handlers accept optional context parameter
    - Session access: Via self.zcli.session (centralized session management)

zAuth Integration:
    - Implicit via context: Authentication state passed through context dict
    - No direct zAuth calls: Command handlers are responsible for auth checks
    - Mode-specific returns: Bifrost mode may return different data structures

Constants:
    All magic strings are replaced with module constants to improve maintainability
    and reduce the risk of typos. See module-level constants below for complete list.
"""

import ast
from typing import Any, Optional, Dict, Union

# Import ACTION_PLACEHOLDER from zConfig
from zCLI.subsystems.zConfig.zConfig_modules import ACTION_PLACEHOLDER

# Import zConfig session constants for modernization
# TODO: Week 6.2 (zConfig) - Use SESSION_KEY_ZMODE instead of "mode" raw string
# Note: Temporarily using raw "mode" until zConfig constants are finalized
# from zCLI.subsystems.zConfig.config_modules.config_constants import SESSION_KEY_ZMODE

# ============================================================================
# MODULE CONSTANTS - Command Prefixes (String Format)
# ============================================================================

CMD_PREFIX_ZFUNC = "zFunc("
CMD_PREFIX_ZLINK = "zLink("
CMD_PREFIX_ZOPEN = "zOpen("
CMD_PREFIX_ZWIZARD = "zWizard("
CMD_PREFIX_ZREAD = "zRead("

# ============================================================================
# MODULE CONSTANTS - Dict Keys (Dict Format)
# ============================================================================

KEY_ZFUNC = "zFunc"
KEY_ZLINK = "zLink"
KEY_ZDELTA = "zDelta"
KEY_ZOPEN = "zOpen"
KEY_ZWIZARD = "zWizard"
KEY_ZREAD = "zRead"
KEY_ZDATA = "zData"
KEY_ZDIALOG = "zDialog"
KEY_ZDISPLAY = "zDisplay"
KEY_ZLOGIN = "zLogin"
KEY_ZLOGOUT = "zLogout"

# ============================================================================
# MODULE CONSTANTS - Context Keys (Session/Mode Detection)
# ============================================================================

KEY_MODE = "mode"  # TODO: Replace with SESSION_KEY_ZMODE from zConfig
KEY_ZVAFILE = "zVaFile"
KEY_ZBLOCK = "zBlock"

# ============================================================================
# MODULE CONSTANTS - Mode Values
# ============================================================================

MODE_BIFROST = "zBifrost"
MODE_TERMINAL = "Terminal"
MODE_WALKER = "Walker"

# ============================================================================
# MODULE CONSTANTS - Display Labels (zDeclare messages)
# ============================================================================

LABEL_LAUNCHER = "zLauncher"
LABEL_HANDLE_ZFUNC = "[HANDLE] zFunc"
LABEL_HANDLE_ZFUNC_DICT = "[HANDLE] zFunc (dict)"
LABEL_HANDLE_ZLINK = "[HANDLE] zLink"
LABEL_HANDLE_ZDELTA = "[HANDLE] zDelta"
LABEL_HANDLE_ZOPEN = "[HANDLE] zOpen"
LABEL_HANDLE_ZWIZARD = "[HANDLE] zWizard"
LABEL_HANDLE_ZREAD_STRING = "[HANDLE] zRead (string)"
LABEL_HANDLE_ZREAD_DICT = "[HANDLE] zRead (dict)"
LABEL_HANDLE_ZDATA_DICT = "[HANDLE] zData (dict)"
LABEL_HANDLE_CRUD_DICT = "[HANDLE] zCRUD (dict)"
LABEL_HANDLE_ZLOGIN = "[HANDLE] zLogin"
LABEL_HANDLE_ZLOGOUT = "[HANDLE] zLogout"

# ============================================================================
# MODULE CONSTANTS - Display Event Keys (Legacy zDisplay format)
# ============================================================================

EVENT_TEXT = "text"
EVENT_SYSMSG = "sysmsg"
EVENT_HEADER = "header"
EVENT_SUCCESS = "success"
EVENT_ERROR = "error"
EVENT_WARNING = "warning"
EVENT_INFO = "info"
EVENT_LINE = "line"
EVENT_LIST = "list"

# ============================================================================
# MODULE CONSTANTS - Data Keys (Common dict keys)
# ============================================================================

KEY_ACTION = "action"
KEY_MODEL = "model"
KEY_TABLE = "table"
KEY_TABLES = "tables"
KEY_FIELDS = "fields"
KEY_VALUES = "values"
KEY_FILTERS = "filters"
KEY_WHERE = "where"
KEY_ORDER_BY = "order_by"
KEY_LIMIT = "limit"
KEY_OFFSET = "offset"
KEY_CONTENT = "content"
KEY_INDENT = "indent"
KEY_EVENT = "event"
KEY_LABEL = "label"
KEY_COLOR = "color"
KEY_STYLE = "style"
KEY_MESSAGE = "message"

# ============================================================================
# MODULE CONSTANTS - Default Values
# ============================================================================

DEFAULT_ACTION_READ = "read"
DEFAULT_ZBLOCK = "root"
DEFAULT_CONTENT = ""
DEFAULT_INDENT = 0
DEFAULT_INDENT_LAUNCHER = 4
DEFAULT_INDENT_HANDLER = 5
DEFAULT_STYLE_SINGLE = "single"
DEFAULT_LABEL = ""

# ============================================================================
# MODULE CONSTANTS - Navigation
# ============================================================================

NAV_ZBACK = "zBack"

# ============================================================================
# MODULE CONSTANTS - Plugin Detection
# ============================================================================

PLUGIN_PREFIX = "&"


class CommandLauncher:
    """
    Central command launcher for zDispatch subsystem.
    
    Routes string and dict commands to appropriate subsystem handlers, with mode-aware
    behavior for Terminal vs. Bifrost execution environments.
    
    Attributes:
        dispatch: Parent zDispatch instance
        zcli: Root zCLI instance
        logger: Logger instance from zCLI
        display: zDisplay instance for UI output
    
    Methods:
        launch(): Main entry point for command routing (type detection)
        _launch_string(): Route string-based commands (zFunc(), zLink(), etc.)
        _launch_dict(): Route dict-based commands ({zFunc:, zLink:, etc.})
        _handle_wizard_string(): Parse and execute wizard from string
        _handle_wizard_dict(): Execute wizard from dict
        _handle_read_string(): Handle zRead string -> zData
        _handle_read_dict(): Handle zRead dict -> zData
        _handle_data_dict(): Handle zData dict -> zData
        _handle_crud_dict(): Handle generic CRUD dict -> zData
        
        Helper methods (DRY):
        _is_bifrost_mode(): Check if context is in Bifrost mode
        _display_handler(): Display handler label with consistent styling
        _log_detected(): Log detected command with consistent format
        _check_walker(): Validate walker instance for zLink commands
        _set_default_action(): Set default action for data requests
    
    Integration:
        - zConfig: Uses session constants (TODO: SESSION_KEY_ZMODE)
        - zDisplay: UI output via zDeclare() and text()
        - zSession: Mode detection via context dict
        - Forward dependencies: 8 subsystems (see module docstring)
    """
    
    # Class-level type declarations
    dispatch: Any  # zDispatch instance
    zcli: Any  # zCLI instance
    logger: Any  # Logger instance
    display: Any  # zDisplay instance

    def __init__(self, dispatch: Any) -> None:
        """
        Initialize command launcher with parent dispatch instance.
        
        Args:
            dispatch: Parent zDispatch instance providing access to zCLI, logger, and display
        
        Raises:
            AttributeError: If dispatch is missing required attributes (zcli, logger)
        
        Example:
            launcher = CommandLauncher(dispatch)
        """
        self.dispatch = dispatch
        self.zcli = dispatch.zcli
        self.logger = dispatch.logger
        self.display = dispatch.zcli.display

    # ========================================================================
    # PUBLIC METHODS - Main Entry Points
    # ========================================================================

    def launch(
        self,
        zHorizontal: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        walker: Optional[Any] = None
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Launch appropriate handler for zHorizontal command with optional context and walker.
        
        This is the main entry point for command routing. It detects the type of command
        (string vs. dict) and delegates to the appropriate handler.
        
        Args:
            zHorizontal: Command to execute (string format like "zFunc(...)" or dict format)
            context: Optional context dict with mode, session, and other metadata
            walker: Optional walker instance for navigation commands (zLink, zWizard)
        
        Returns:
            Command execution result, or None if command type is unknown or execution fails.
            Return type varies by command:
            - zFunc: Function result (any type)
            - zLink: Navigation result (str or dict)
            - zWizard: "zBack" (Terminal) or zHat result (Bifrost)
            - zRead/zData: Data result (dict or list)
            - Plain string (Bifrost): {"message": str} or resolved zUI value
            - Unknown: None
        
        Examples:
            # String commands
            result = launcher.launch("zFunc(my_function)")
            result = launcher.launch("zLink(menu:users)", walker=walker_instance)
            result = launcher.launch("zRead(users)", context={"mode": "Terminal"})
            
            # Dict commands
            result = launcher.launch({"zFunc": "my_function"})
            result = launcher.launch({"zDialog": {"fields": [...]}})
            
            # Plain string in Bifrost mode
            result = launcher.launch("my_button_key", context={"mode": "zBifrost"})
        
        Notes:
            - Displays "zLauncher" label via zDeclare for visual feedback
            - Unknown command types (not str or dict) return None
            - Mode-specific behavior handled by individual command handlers
        """
        self._display_handler(LABEL_LAUNCHER, DEFAULT_INDENT_LAUNCHER)

        # Early return for placeholder actions (development/testing)
        if zHorizontal == ACTION_PLACEHOLDER:
            self.logger.debug(f"[CommandLauncher] Placeholder action detected: '{ACTION_PLACEHOLDER}' - no-op")
            return None

        if isinstance(zHorizontal, str):
            return self._launch_string(zHorizontal, context, walker)
        elif isinstance(zHorizontal, dict):
            return self._launch_dict(zHorizontal, context, walker)
        elif isinstance(zHorizontal, list):
            return self._launch_list(zHorizontal, context, walker)
        
        # Unknown type - return None
        return None

    # ========================================================================
    # PRIVATE METHODS - List Command Routing (Sequential Execution)
    # ========================================================================

    def _launch_list(
        self,
        zHorizontal: list,
        context: Optional[Dict[str, Any]],
        walker: Optional[Any]
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Execute a list of commands sequentially.
        
        This enables streamlined YAML where multiple zDisplay events (or other commands)
        can be listed directly under a key without requiring intermediate named sub-keys.
        
        Examples:
            # YAML Pattern - List of zDisplay events
            Hero_Section:
              - zDisplay:
                  event: header
                  content: "Zolo"
              - zDisplay:
                  event: header
                  content: "A digital solution"
              - zDisplay:
                  event: text
                  content: "Build intelligent CLI..."
        
        Args:
            zHorizontal: List of commands (dicts, strings, or nested lists)
            context: Optional context dict
            walker: Optional walker instance
        
        Returns:
            Result from the last item in the list, or None
        """
        if not zHorizontal:
            return None
        
        result = None
        for item in zHorizontal:
            # Recursively launch each item (supports dict, str, or nested list)
            if isinstance(item, dict):
                result = self._launch_dict(item, context, walker)
            elif isinstance(item, str):
                result = self._launch_string(item, context, walker)
            elif isinstance(item, list):
                result = self._launch_list(item, context, walker)
            
            # Check for navigation signals (stop processing if user wants to go back/exit)
            if result in ('zBack', 'exit', 'stop', 'error'):
                return result
        
        return result

    # ========================================================================
    # PRIVATE METHODS - String Command Routing
    # ========================================================================

    def _launch_string(
        self,
        zHorizontal: str,
        context: Optional[Dict[str, Any]],
        walker: Optional[Any]
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Handle string-based launch commands.
        
        Routes string commands with the following prefixes:
        - "zFunc(...)": Function execution
        - "zLink(...)": Navigation link
        - "zOpen(...)": File/URL opening
        - "zWizard(...)": Multi-step workflow
        - "zRead(...)": Data read operation
        
        Plain strings (no prefix):
        - Terminal mode: Return None (no navigation)
        - Bifrost mode: Resolve from zUI file or return {"message": str}
        
        Args:
            zHorizontal: String command to execute
            context: Optional context dict with mode and session metadata
            walker: Optional walker instance for navigation commands
        
        Returns:
            Command execution result, or None if command is unhandled.
            Return type varies by command (see launch() docstring).
        
        Examples:
            # Function call
            result = _launch_string("zFunc(calculate)", context, walker)
            
            # Navigation
            result = _launch_string("zLink(menu:users)", context, walker)
            
            # Plain string in Bifrost mode (zUI resolution)
            result = _launch_string("submit_button", {"mode": "zBifrost"}, walker)
            # Returns: {"message": "submit_button"} or resolved dict from zUI
        
        Notes:
            - zLink and zWizard require walker instance
            - Bifrost mode enables recursive zUI resolution
            - Plain strings in Terminal mode return None (display-only)
        
        TODO: Week 6.10 (zFunc) - Update zfunc.handle() call after refactor
        TODO: Week 6.7 (zNavigation) - Update handle_zLink() call after refactor
        TODO: Week 6.12 (zOpen) - Update open.handle() call after refactor
        TODO: Week 6.14 (zWizard) - Update wizard.handle() call after refactor
        TODO: Week 6.9 (zLoader) - Update loader.handle() call after refactor
        """
        # Route: zFunc()
        if zHorizontal.startswith(CMD_PREFIX_ZFUNC):
            self._log_detected("zFunc request")
            self._display_handler(LABEL_HANDLE_ZFUNC, DEFAULT_INDENT_HANDLER)
            # TODO: Week 6.10 (zFunc) - Verify zfunc.handle() signature after refactor
            return self.zcli.zfunc.handle(zHorizontal)

        # Route: zLink()
        if zHorizontal.startswith(CMD_PREFIX_ZLINK):
            if not self._check_walker(walker, "zLink"):
                return None
            self._log_detected("zLink request")
            self._display_handler(LABEL_HANDLE_ZLINK, DEFAULT_INDENT_LAUNCHER)
            # TODO: Week 6.7 (zNavigation) - Verify handle_zLink() signature after refactor
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        # Route: zOpen()
        if zHorizontal.startswith(CMD_PREFIX_ZOPEN):
            self._log_detected("zOpen request")
            self._display_handler(LABEL_HANDLE_ZOPEN, DEFAULT_INDENT_LAUNCHER)
            # TODO: Week 6.12 (zOpen) - Verify open.handle() signature after refactor
            return self.zcli.open.handle(zHorizontal)

        # Route: zWizard()
        if zHorizontal.startswith(CMD_PREFIX_ZWIZARD):
            return self._handle_wizard_string(zHorizontal, walker, context)

        # Route: zRead()
        if zHorizontal.startswith(CMD_PREFIX_ZREAD):
            return self._handle_read_string(zHorizontal, context)

        # Plain string - mode-specific handling
        if self._is_bifrost_mode(context):
            # Bifrost mode: Attempt to resolve from zUI file
            zVaFile = self.zcli.zspark_obj.get(KEY_ZVAFILE)
            zBlock = self.zcli.zspark_obj.get(KEY_ZBLOCK, DEFAULT_ZBLOCK)
            
            if zVaFile and zBlock:
                try:
                    # TODO: Week 6.9 (zLoader) - Verify loader.handle() signature after refactor
                    raw_zFile = self.zcli.loader.handle(zVaFile)
                    if raw_zFile and zBlock in raw_zFile:
                        block_dict = raw_zFile[zBlock]
                        
                        # Look up the key in the block
                        if zHorizontal in block_dict:
                            resolved_value = block_dict[zHorizontal]
                            self.logger.framework.debug(
                                f"[{MODE_BIFROST}] Resolved key '{zHorizontal}' from zUI to: {resolved_value}"
                            )
                            # Recursively launch with the resolved value (could be dict with zFunc)
                            return self.launch(resolved_value, context=context, walker=walker)
                        else:
                            self.logger.framework.debug(
                                f"[{MODE_BIFROST}] Key '{zHorizontal}' not found in zUI block '{zBlock}'"
                            )
                except Exception as e:
                    self.logger.warning(f"[{MODE_BIFROST}] Error resolving key from zUI: {e}")
            
            # If we couldn't resolve it, return as display message
            self.logger.framework.debug(f"Plain string in {MODE_BIFROST} mode - returning as message")
            return {KEY_MESSAGE: zHorizontal}
        
        # Terminal mode: Plain strings are displayed but return None for navigation
        return None

    # ========================================================================
    # PRIVATE METHODS - Dict Command Routing
    # ========================================================================

    def _launch_dict(
        self,
        zHorizontal: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        walker: Optional[Any]
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """Handle dict-based launch commands.
        
        Routes dict commands with the following keys:
        - "zDisplay": Legacy display format (text, sysmsg events)
        - "zFunc": Function execution
        - "zDialog": Interactive form/dialog
        - "zLink": Navigation link
        - "zWizard": Multi-step workflow
        - "zRead": Data read operation
        - "zData": Generic data operation
        - CRUD keys: Generic CRUD operation (action, model, table, etc.)
        
        Args:
            zHorizontal: Dict command to execute
            context: Optional context dict with mode and session metadata
            walker: Optional walker instance for navigation commands
        
        Returns:
            Command execution result, or None if command is unhandled.
            Return type varies by command (see launch() docstring).
        
        Examples:
            # Function call
            result = _launch_dict({"zFunc": "calculate"}, context, walker)
            
            # Plugin invocation
            result = _launch_dict({"zFunc": "&my_plugin"}, context, walker)
            
            # Dialog
            result = _launch_dict({"zDialog": {"fields": [...]}}, context, walker)
            
            # Data operation
            result = _launch_dict({"zRead": {"model": "users"}}, context, walker)
            
            # Generic CRUD
            result = _launch_dict({"action": "read", "model": "users"}, context, walker)
            
            # Legacy display format
            result = _launch_dict({"zDisplay": {"event": "text", "content": "Hello"}}, context, walker)
        
        Notes:
            - Plugin invocations: Detect "&" prefix in zFunc value
            - CRUD detection: Fallback for dicts with action/model/table keys
            - Legacy zDisplay: Backward compatibility only (modern API preferred)
        
        TODO: Week 6.10 (zFunc) - Update zfunc.handle() call after refactor
        TODO: Week 6.8 (zParser) - Update resolve_plugin_invocation() call after refactor
        TODO: Week 6.7 (zNavigation) - Update handle_zLink() call after refactor
        TODO: Week 6.14 (zWizard) - Update wizard.handle() call after refactor
        TODO: Week 6.16 (zData) - Update data.handle_request() call after refactor
        """
        # ========================================================================
        # PRELIMINARY CHECKS
        # ========================================================================
        # Known subsystem command keys
        subsystem_keys = {KEY_ZDISPLAY, KEY_ZFUNC, KEY_ZDIALOG, KEY_ZLINK, KEY_ZWIZARD, KEY_ZREAD, KEY_ZDATA}
        
        # Get content keys (exclude metadata keys starting with _)
        content_keys = [k for k in zHorizontal.keys() if not k.startswith('_')]
        
        # Check if this is a direct subsystem call
        is_subsystem_call = any(k in zHorizontal for k in subsystem_keys)
        
        # Check for CRUD keys (fallback pattern)
        crud_keys = {'action', 'model', 'table', 'collection'}
        is_crud_call = any(k in zHorizontal for k in crud_keys)
        
        # SPECIAL CASE: Single "Content" key with optional _zClass metadata
        # Common UI pattern: {_zClass: "...", Content: [events]}
        # Unwrap and dispatch the Content directly
        if len(content_keys) == 1 and content_keys[0] == 'Content':
            self._log_detected("Content wrapper (unwrapping)")
            content_value = zHorizontal['Content']
            # Recursively dispatch the unwrapped Content
            # This handles both lists and nested dicts
            return self.launch(content_value, context=context, walker=walker)
        
        # ========================================================================
        # BLOCK-LEVEL DATA RESOLUTION (v1.5.12 - Flask/Jinja Pattern)
        # ========================================================================
        # If dict has _data block, resolve queries BEFORE processing children
        # This is the zCLI equivalent of Flask's route handler pattern
        
        if "_data" in zHorizontal and not is_subsystem_call:
            self.logger.framework.info("[zCLI Data] Detected _data block, resolving queries...")
            resolved_data = self._resolve_block_data(zHorizontal["_data"], context)
            if resolved_data:
                # Store in context for child blocks to access via %data.* syntax
                if "_resolved_data" not in context:
                    context["_resolved_data"] = {}
                context["_resolved_data"].update(resolved_data)
                self.logger.framework.info(f"[zCLI Data] Resolved {len(resolved_data)} data queries for block")
            else:
                self.logger.framework.warning("[zCLI Data] _data block present but no data resolved")
        
        # ========================================================================
        # ORGANIZATIONAL STRUCTURE DETECTION (zCLI Way)
        # ========================================================================
        # If dict has only nested dicts/lists (no direct actions), it's organizational
        # Recurse into it rather than treating as implicit wizard
        # This enables flexible YAML organization with nested containers
        
        if not is_subsystem_call and not is_crud_call and len(content_keys) > 0:
            # Check if ALL content values are dicts or lists (organizational structure)
            all_nested = all(
                isinstance(zHorizontal[k], (dict, list))
                for k in content_keys
            )
            
            # If purely organizational (no direct actions), recurse into nested structures
            if all_nested:
                self.logger.framework.debug(f"[zCLI Recursion] Organizational structure detected ({len(content_keys)} keys), recursing...")
                
                result = None
                for key in content_keys:
                    value = zHorizontal[key]
                    self.logger.framework.debug(f"[zCLI Recursion] Processing nested key: {key} (type: {type(value).__name__})")
                    
                    # Recursively process nested content
                    if isinstance(value, dict):
                        result = self._launch_dict(value, context, walker)
                    elif isinstance(value, list):
                        result = self._launch_list(value, context, walker)
                    
                    # Check for navigation signals
                    if result in ('zBack', 'exit', 'stop', 'error'):
                        self.logger.framework.debug(f"[zCLI Recursion] Navigation signal received: {result}")
                        return result
                
                self.logger.framework.debug(f"[zCLI Recursion] Completed organizational recursion, returning: {result}")
                return result
        
        # ========================================================================
        # IMPLICIT WIZARD DETECTION
        # ========================================================================
        # If dict has multiple non-metadata, non-subsystem keys with mixed types
        # (not purely organizational), treat as wizard steps
        
        # If multiple content keys and NOT purely organizational -> implicit wizard
        if not is_subsystem_call and not is_crud_call and len(content_keys) > 1:
            self._log_detected("Implicit zWizard (multi-step)")
            # Call wizard with proper context - use walker if available for proper dispatch routing
            if walker:
                zHat = walker.handle(zHorizontal)
            else:
                zHat = self.zcli.wizard.handle(zHorizontal)
            
            # For implicit wizards (nested sections), return zHat to continue execution
            # Don't return 'zBack' as that would trigger navigation and create loops
            # The walker will continue to the next key in the parent block
            return zHat
        
        # ========================================================================
        # EXPLICIT SUBSYSTEM ROUTING
        # ========================================================================
        # Route: zDisplay (legacy format)
        if KEY_ZDISPLAY in zHorizontal:
            self._log_detected("zDisplay (wrapped)")
            display_data = zHorizontal[KEY_ZDISPLAY]
            
            if isinstance(display_data, dict):
                # NEW v1.5.12: Pass context for %data.* variable resolution
                # This enables templates to reference database query results
                if context and "_resolved_data" in context:
                    display_data["_context"] = context
                
                # Use display.handle() to pass through ALL parameters automatically
                # This ensures new parameters like 'class' work without updating this code
                self.display.handle(display_data)
                
                # Legacy explicit routing (DEPRECATED - kept for reference only)
                # event = display_data.get(KEY_EVENT)
                # if event == EVENT_TEXT:
                #     content = display_data.get(KEY_CONTENT, DEFAULT_CONTENT)
                #     indent = display_data.get(KEY_INDENT, DEFAULT_INDENT)
                #     self.display.text(content, indent)
                # elif event == EVENT_HEADER:
                #     content = display_data.get(KEY_CONTENT, DEFAULT_CONTENT)
                #     color = display_data.get(KEY_COLOR, "RESET")
                #     indent = display_data.get(KEY_INDENT, DEFAULT_INDENT)
                #     style = display_data.get(KEY_STYLE, "full")
                #     self.display.header(content, color=color, indent=indent, style=style)
                # elif event == EVENT_SUCCESS: ...
                # elif event == EVENT_ERROR: ...
                # elif event == EVENT_WARNING: ...
                # elif event == EVENT_INFO: ...
                # elif event == EVENT_LINE: ...
                # elif event == EVENT_LIST: ...
                # All events now handled by display.handle() above
            return None

        # Route: zFunc
        if KEY_ZFUNC in zHorizontal:
            self._log_detected("zFunc (dict)")
            self._display_handler(LABEL_HANDLE_ZFUNC_DICT, DEFAULT_INDENT_HANDLER)
            func_spec = zHorizontal[KEY_ZFUNC]
            
            # Check if it's a plugin invocation (starts with &)
            if isinstance(func_spec, str) and func_spec.startswith(PLUGIN_PREFIX):
                self._log_detected(f"plugin invocation in zFunc: {func_spec}")
                # Route plugin invocations through parser with context support
                return self.zcli.zparser.resolve_plugin_invocation(func_spec, context=context)
            
            # Non-plugin zFunc calls
            return self.zcli.zfunc.handle(func_spec, zContext=context)

        # Route: zDialog
        if KEY_ZDIALOG in zHorizontal:
            # ✅ Week 6.11 (zDialog) - handle_zDialog() signature verified and compatible
            from ...zDialog import handle_zDialog
            self._log_detected("zDialog")
            return handle_zDialog(zHorizontal, zcli=self.zcli, walker=walker, context=context)

        # Route: zLogin (Built-in Authentication Action)
        if KEY_ZLOGIN in zHorizontal:
            self._display_handler(LABEL_HANDLE_ZLOGIN, DEFAULT_INDENT_HANDLER)
            self._log_detected(f"zLogin: {zHorizontal[KEY_ZLOGIN]}")
            
            # Get app name from zLogin value (string)
            app_or_type = zHorizontal[KEY_ZLOGIN]
            
            # Get zConv and model from context (set by zDialog)
            # The context from zDialog submission contains both zConv and model
            # Context is passed from walker, which gets it from dialog submission
            zConv = context.get("zConv", {}) if context else {}
            model = context.get("model") if context else None
            
            # If model wasn't in context, check if it was injected into zHorizontal by dialog_submit
            if not model and "model" in zHorizontal:
                model = zHorizontal["model"]
            
            # Build zContext for zLogin - include model and other dialog context
            zContext = {
                "model": model,
                "fields": context.get("fields", []) if context else [],
                "zConv": zConv
            }
            
            # Import and call handle_zLogin
            from zCLI.subsystems.zAuth.zAuth_modules import handle_zLogin
            
            self.logger.debug(f"[zLauncher] Calling zLogin with zConv keys: {list(zConv.keys())}, model: {model}")
            
            result = handle_zLogin(
                app_or_type=app_or_type,
                zConv=zConv,
                zContext=zContext,
                zcli=self.zcli
            )
            
            self.logger.debug(f"[zLauncher] zLogin result: {result}")
            return result

        # Route: zLogout (Built-in Logout Action)
        if KEY_ZLOGOUT in zHorizontal:
            self._display_handler(LABEL_HANDLE_ZLOGOUT, DEFAULT_INDENT_HANDLER)
            self._log_detected(f"zLogout: {zHorizontal[KEY_ZLOGOUT]}")
            
            # Get app name from zLogout value (string)
            app_name = zHorizontal[KEY_ZLOGOUT]
            
            # zLogout doesn't need zConv/model (no form data), but we pass empty dicts
            # for consistency with handle_zLogout signature
            zConv = {}
            zContext = {}
            
            # Import and call handle_zLogout
            from zCLI.subsystems.zAuth.zAuth_modules import handle_zLogout
            
            self.logger.debug(f"[zLauncher] Calling zLogout for app: {app_name}")
            
            result = handle_zLogout(
                app_name=app_name,
                zConv=zConv,
                zContext=zContext,
                zcli=self.zcli
            )
            
            self.logger.debug(f"[zLauncher] zLogout result: {result}")
            return result

        # Route: zLink
        if KEY_ZLINK in zHorizontal:
            if not self._check_walker(walker, "zLink"):
                return None
            self._log_detected("zLink")
            # TODO: Week 6.7 (zNavigation) - Verify handle_zLink() signature after refactor
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        # Route: zDelta (intra-file block navigation)
        if KEY_ZDELTA in zHorizontal:
            if not self._check_walker(walker, "zDelta"):
                return None
            self._log_detected("zDelta")
            self._display_handler(LABEL_HANDLE_ZDELTA, DEFAULT_INDENT_HANDLER)
            
            # Extract target block name
            target_block_name = zHorizontal[KEY_ZDELTA]
            
            # Strip $ or % prefix if present (delta navigation markers)
            if isinstance(target_block_name, str):
                if target_block_name.startswith(("$", "%")):
                    target_block_name = target_block_name[1:]
            
            self.logger.framework.debug(f"zDelta navigation to block: {target_block_name}")
            
            # Get current zVaFile from session
            current_zVaFile = walker.session.get("zVaFile") or walker.zSpark_obj.get("zVaFile")
            if not current_zVaFile:
                self.logger.error("No zVaFile in session or zspark_obj")
                return None
            
            # Reload the UI file (walker doesn't store it as an instance attribute)
            raw_zFile = walker.loader.handle(current_zVaFile)
            if not raw_zFile:
                self.logger.error(f"Failed to load UI file: {current_zVaFile}")
                return None
            
            # Extract the target block dict from raw_zFile
            # FALLBACK CHAIN:
            # 1. Try finding block in current file
            # 2. If not found, try loading {blockName}.yaml from same directory
            target_block_dict = None
            
            if target_block_name in raw_zFile:
                # Block found in current file
                target_block_dict = raw_zFile[target_block_name]
                self.logger.framework.debug(f"zDelta: Block '{target_block_name}' found in current file")
            else:
                # FALLBACK: Try loading zUI.{blockName}.yaml from same directory
                # zCLI fundamental: UI files MUST be named zUI.*.yaml
                
                # Construct zPath for fallback file
                # Example: current = "@.UI.zUI.index" -> fallback = "@.UI.zUI.zAbout"
                # File naming: zUI.zAbout.yaml -> zPath = "@.UI.zUI.zAbout"
                if current_zVaFile.startswith("@"):
                    # Parse current zPath to get folder
                    # "@.UI.zUI.index" -> ["@", "UI", "zUI", "index"]
                    path_parts = current_zVaFile.split(".")
                    
                    # Replace the last part (filename) with target block name
                    # File is named zUI.{blockName}.yaml, so zPath ends with {blockName}
                    # ["@", "UI", "zUI", "index"] -> ["@", "UI", "zUI", "zAbout"]
                    fallback_path_parts = path_parts[:-1] + [target_block_name]
                    fallback_zPath = ".".join(fallback_path_parts)
                else:
                    # Absolute path - construct relative to current file
                    fallback_zPath = f"@.UI.zUI.{target_block_name}"
                
                self.logger.framework.debug(
                    f"zDelta: Block '{target_block_name}' not in current file, "
                    f"trying fallback zPath: {fallback_zPath}"
                )
                
                # Try loading the fallback file using zParser/zLoader
                try:
                    fallback_zFile = walker.loader.handle(fallback_zPath)
                except Exception as e:
                    self.logger.debug(f"zDelta: Fallback failed: {e}")
                    fallback_zFile = None
                
                if fallback_zFile and isinstance(fallback_zFile, dict):
                    # SUCCESS: Fallback file loaded
                    # Use the entire file content as the block
                    target_block_dict = fallback_zFile
                    self.logger.info(
                        f"✓ zDelta: Auto-discovered block '{target_block_name}' "
                        f"from separate file: {fallback_zPath}"
                    )
                else:
                    # FAILED: Neither current file nor fallback file has the block
                    self.logger.error(
                        f"Block '{target_block_name}' not found:\n"
                        f"  - Not in current file: {current_zVaFile}\n"
                        f"  - Fallback zPath not found: {fallback_zPath}"
                    )
                    return None
            
            # At this point, target_block_dict should be set
            if not target_block_dict:
                self.logger.error(f"Failed to resolve block '{target_block_name}'")
                return None
            
            # Update session zBlock to reflect the target block
            walker.session["zBlock"] = target_block_name
            
            # Initialize new breadcrumb scope for target block (creates new node in zCrumbs)
            # Construct full breadcrumb path: zVaFile.zBlock
            zVaFile = walker.session.get("zVaFile") or current_zVaFile
            full_crumb_path = f"{zVaFile}.{target_block_name}" if zVaFile else target_block_name
            
            # Initialize empty breadcrumb trail for the new scope
            if "zCrumbs" not in walker.session:
                walker.session["zCrumbs"] = {}
            walker.session["zCrumbs"][full_crumb_path] = []
            
            self.logger.framework.debug(f"zDelta: Created new breadcrumb scope: {full_crumb_path}")
            
            # Get block keys
            zBlock_keys = list(target_block_dict.keys())
            
            # Navigate to the target block using walker's zBlock_loop
            result = walker.zBlock_loop(target_block_dict, zBlock_keys)
            return result

        # Route: zWizard
        if KEY_ZWIZARD in zHorizontal:
            return self._handle_wizard_dict(zHorizontal, walker, context)

        # Route: zRead
        if KEY_ZREAD in zHorizontal:
            return self._handle_read_dict(zHorizontal, context)

        # Route: zData
        if KEY_ZDATA in zHorizontal:
            return self._handle_data_dict(zHorizontal, context)

        # Check if it looks like a CRUD operation (has action, table, model, etc.)
        crud_keys = {
            KEY_ACTION, KEY_TABLE, KEY_MODEL, KEY_FIELDS, KEY_VALUES, KEY_WHERE
        }
        if any(key in zHorizontal for key in crud_keys):
            return self._handle_crud_dict(zHorizontal, context)
        
        # No recognized keys found - return None
        self.logger.framework.debug("[zCLI Launcher] No recognized keys found, returning None")
        return None

    # ========================================================================
    # PRIVATE METHODS - Specialized Command Handlers
    # ========================================================================

    def _handle_wizard_string(
        self,
        zHorizontal: str,
        walker: Optional[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[str, Any]]:
        """
        Handle zWizard string command.
        
        Parses the wizard payload from string format and executes it via walker or
        wizard subsystem. Returns mode-specific results (zBack for Terminal, zHat for Bifrost).
        
        Args:
            zHorizontal: String command in format "zWizard(...)"
            walker: Optional walker instance (preferred for navigation context)
            context: Optional context dict with mode metadata
        
        Returns:
            - Bifrost mode: zHat (actual wizard result)
            - Terminal/Walker mode: "zBack" (for navigation) or zHat (no walker)
            - Parse error: None
        
        Example:
            result = _handle_wizard_string("zWizard({'steps': [...])})", walker, context)
        
        Notes:
            - Uses ast.literal_eval() for safe payload parsing
            - Walker extends wizard, so walker.handle() is preferred over wizard.handle()
            - Mode-specific returns enable proper Terminal vs. API behavior
        
        TODO: Week 6.14 (zWizard) - Verify wizard.handle() signature after refactor
        """
        self._log_detected("zWizard request")
        self._display_handler(LABEL_HANDLE_ZWIZARD, DEFAULT_INDENT_LAUNCHER)
        
        # Extract and parse payload
        inner = zHorizontal[len(CMD_PREFIX_ZWIZARD):-1].strip()
        try:
            wizard_obj = ast.literal_eval(inner)
            
            # Use modern OOP API - walker extends wizard, so it has handle()
            # TODO: Week 6.14 (zWizard) - Verify wizard.handle() signature after refactor
            if walker:
                zHat = walker.handle(wizard_obj)
            else:
                zHat = self.zcli.wizard.handle(wizard_obj)
            
            # Mode-specific return behavior
            if self._is_bifrost_mode(context):
                # Bifrost: Return zHat for API consumption
                return zHat
            
            # Terminal/Walker: Return zBack for navigation (or zHat if no walker)
            return NAV_ZBACK if walker else zHat
        except Exception as e:
            self.logger.error(f"Failed to parse zWizard payload: {e}")
            return None

    def _handle_wizard_dict(
        self,
        zHorizontal: Dict[str, Any],
        walker: Optional[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[str, Any]]:
        """
        Handle zWizard dict command.
        
        Executes wizard payload from dict format via walker or wizard subsystem.
        Returns mode-specific results (zBack for Terminal, zHat for Bifrost).
        
        Args:
            zHorizontal: Dict command with "zWizard" key
            walker: Optional walker instance (preferred for navigation context)
            context: Optional context dict with mode metadata
        
        Returns:
            - Bifrost mode: zHat (actual wizard result)
            - Terminal/Walker mode: "zBack" (for navigation) or zHat (no walker)
        
        Example:
            result = _handle_wizard_dict({"zWizard": {"steps": [...]}}, walker, context)
        
        Notes:
            - No parsing needed (already dict format)
            - Walker extends wizard, so walker.handle() is preferred
            - Mode-specific returns enable proper Terminal vs. API behavior
        
        TODO: Week 6.14 (zWizard) - Verify wizard.handle() signature after refactor
        """
        self._log_detected("zWizard (dict)")
        
        # Use modern OOP API - walker extends wizard, so it has handle()
        # TODO: Week 6.14 (zWizard) - Verify wizard.handle() signature after refactor
        if walker:
            zHat = walker.handle(zHorizontal[KEY_ZWIZARD])
        else:
            zHat = self.zcli.wizard.handle(zHorizontal[KEY_ZWIZARD])
        
        # Mode-specific return behavior
        if self._is_bifrost_mode(context):
            # Bifrost: Return zHat for API consumption
            return zHat
        
        # Terminal/Walker: Return zBack for navigation (or zHat if no walker)
        return NAV_ZBACK if walker else zHat

    def _handle_read_string(
        self,
        zHorizontal: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[Any]:
        """
        Handle zRead string command.
        
        Parses the model name from string format and dispatches to zData subsystem
        with default action "read".
        
        Args:
            zHorizontal: String command in format "zRead(...)"
            context: Optional context dict for data operation
        
        Returns:
            Data result from zData.handle_request() (typically dict or list)
        
        Example:
            result = _handle_read_string("zRead(users)", context)
            # Equivalent to: {"action": "read", "model": "users"}
        
        Notes:
            - Empty payload: {"action": "read"} (no model specified)
            - Non-empty payload: {"action": "read", "model": "..."}
            - Dispatched to zData.handle_request()
        
        TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        """
        self._log_detected("zRead request (string)")
        self._display_handler(LABEL_HANDLE_ZREAD_STRING, DEFAULT_INDENT_LAUNCHER)
        
        # Extract and build request
        inner = zHorizontal[len(CMD_PREFIX_ZREAD):-1].strip()
        req = {KEY_ACTION: DEFAULT_ACTION_READ}
        if inner:
            req[KEY_MODEL] = inner
        
        self.logger.framework.debug(f"Dispatching zRead (string) with request: {req}")
        # TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        return self.zcli.data.handle_request(req, context=context)

    def _handle_read_dict(
        self,
        zHorizontal: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Any]:
        """
        Handle zRead dict command.
        
        Extracts the read request from dict format and dispatches to zData subsystem
        with default action "read".
        
        Args:
            zHorizontal: Dict command with "zRead" key
            context: Optional context dict for data operation
        
        Returns:
            Data result from zData.handle_request() (typically dict or list)
        
        Example:
            result = _handle_read_dict({"zRead": {"model": "users", "where": {"id": 1}}}, context)
            # Dispatched as: {"action": "read", "model": "users", "where": {"id": 1}}
        
        Notes:
            - String payload: {"zRead": "users"} -> {"action": "read", "model": "users"}
            - Dict payload: {"zRead": {...}} -> {action: "read", ...}
            - Sets default action if not specified
        
        TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        """
        self._log_detected("zRead (dict)")
        self._display_handler(LABEL_HANDLE_ZREAD_DICT, DEFAULT_INDENT_LAUNCHER)
        
        # Extract and normalize request
        req = zHorizontal.get(KEY_ZREAD) or {}
        if isinstance(req, str):
            req = {KEY_MODEL: req}
        
        self._set_default_action(req, DEFAULT_ACTION_READ)
        
        self.logger.framework.debug(f"Dispatching zRead (dict) with request: {req}")
        # TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        return self.zcli.data.handle_request(req, context=context)

    def _handle_data_dict(
        self,
        zHorizontal: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Any]:
        """
        Handle zData dict command.
        
        Extracts the data request from dict format and dispatches to zData subsystem
        with default action "read".
        
        Args:
            zHorizontal: Dict command with "zData" key
            context: Optional context dict for data operation
        
        Returns:
            Data result from zData.handle_request() (typically dict or list)
        
        Example:
            result = _handle_data_dict({"zData": {"action": "create", "model": "users", ...}}, context)
        
        Notes:
            - String payload: {"zData": "users"} -> {"action": "read", "model": "users"}
            - Dict payload: {"zData": {...}} -> {action: "read" (default), ...}
            - Sets default action if not specified
        
        TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        """
        self._log_detected("zData (dict)")
        self._display_handler(LABEL_HANDLE_ZDATA_DICT, DEFAULT_INDENT_LAUNCHER)
        
        # Extract and normalize request
        req = zHorizontal.get(KEY_ZDATA) or {}
        if isinstance(req, str):
            req = {KEY_MODEL: req}
        
        self._set_default_action(req, DEFAULT_ACTION_READ)
        
        self.logger.framework.debug(f"Dispatching zData (dict) with request: {req}")
        # TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        return self.zcli.data.handle_request(req, context=context)

    def _handle_crud_dict(
        self,
        zHorizontal: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Any]:
        """
        Handle generic CRUD dict command.
        
        Smart fallback for dicts that look like CRUD operations but don't use
        zRead/zData wrappers. Detects CRUD keys and dispatches to zData subsystem.
        
        Args:
            zHorizontal: Dict with CRUD keys (action, model, table, fields, values, etc.)
            context: Optional context dict for data operation
        
        Returns:
            Data result from zData.handle_request(), or None if not a valid CRUD dict
        
        Example:
            result = _handle_crud_dict({"action": "read", "model": "users"}, context)
            result = _handle_crud_dict({"model": "users", "where": {"id": 1}}, context)
            # Second example: action defaults to "read"
        
        Notes:
            - Requires "model" key to be present (validation)
            - Detects CRUD keys: action, model, tables, fields, values, filters, where, order_by, limit, offset
            - Sets default action to "read" if not specified
            - Creates a copy to avoid mutating original dict
        
        TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
        """
        # CRUD key detection
        maybe_crud = {
            KEY_ACTION, KEY_MODEL, KEY_TABLES, KEY_FIELDS, KEY_VALUES,
            KEY_FILTERS, KEY_WHERE, KEY_ORDER_BY, KEY_LIMIT, KEY_OFFSET
        }
        
        # Validate: Must have at least one CRUD key AND "model" key
        if any(k in zHorizontal for k in maybe_crud) and KEY_MODEL in zHorizontal:
            req = dict(zHorizontal)  # Create copy to avoid mutation
            self._set_default_action(req, DEFAULT_ACTION_READ)
            
            self._log_detected(f"generic CRUD dict => {req}")
            self._display_handler(LABEL_HANDLE_CRUD_DICT, DEFAULT_INDENT_LAUNCHER)
            
            # TODO: Week 6.16 (zData) - Verify data.handle_request() signature after refactor
            return self.zcli.data.handle_request(req, context=context)
        
        return None

    # ========================================================================
    # HELPER METHODS - DRY Refactoring
    # ========================================================================

    def _is_bifrost_mode(self, context: Optional[Dict[str, Any]]) -> bool:
        """
        Check if context indicates Bifrost mode execution.
        
        Args:
            context: Optional context dict with mode metadata
        
        Returns:
            True if context exists and mode is "zBifrost", False otherwise
        
        Example:
            if self._is_bifrost_mode(context):
                # Handle Bifrost-specific behavior
        
        Notes:
            - TODO: Replace KEY_MODE with SESSION_KEY_ZMODE from zConfig (Week 6.2)
            - Gracefully handles None context (returns False)
            - Case-sensitive mode comparison
        """
        # TODO: Week 6.2 (zConfig) - Replace KEY_MODE with SESSION_KEY_ZMODE
        return context is not None and context.get(KEY_MODE) == MODE_BIFROST

    def _display_handler(self, label: str, indent: int) -> None:
        """
        Display handler label with consistent styling.
        
        Args:
            label: Handler label to display
            indent: Indentation level (spaces)
        
        Example:
            self._display_handler("[HANDLE] zFunc", 5)
        
        Notes:
            - Uses parent dispatch color for consistency
            - Style is always "single" for handler labels
            - Avoids repeated zDeclare calls with identical styling
        """
        self.display.zDeclare(
            label,
            color=self.dispatch.mycolor,
            indent=indent,
            style=DEFAULT_STYLE_SINGLE
        )

    def _log_detected(self, message: str) -> None:
        """
        Log detected command with consistent format.
        
        Args:
            message: Detection message (e.g., "zFunc request", "plugin invocation")
        
        Example:
            self._log_detected("zFunc request")
            self._log_detected("plugin invocation in zFunc: &my_plugin")
        
        Notes:
            - Prefixes all messages with "Detected " for consistency
            - Uses INFO level for all command detection logs
            - Avoids repeated "Detected" string in calling code
        """
        self.logger.framework.debug(f"Detected {message}")

    def _check_walker(self, walker: Optional[Any], command_name: str) -> bool:
        """
        Validate walker instance for commands that require it.
        
        Args:
            walker: Walker instance to validate (can be None)
            command_name: Name of command requiring walker (for error message)
        
        Returns:
            True if walker is valid (not None), False otherwise
        
        Example:
            if not self._check_walker(walker, "zLink"):
                return None
        
        Notes:
            - Logs warning if walker is None
            - Calling code should return None if validation fails
            - Used by zLink and zWizard commands
        """
        if not walker:
            self.logger.warning(f"{command_name} requires walker instance")
            return False
        return True

    def _set_default_action(self, req: Dict[str, Any], default_action: str) -> None:
        """
        Set default action for data request if not specified.
        
        Args:
            req: Request dict to modify (mutated in place)
            default_action: Default action value (typically "read")
        
        Example:
            req = {"model": "users"}
            self._set_default_action(req, "read")
            # req is now: {"model": "users", "action": "read"}
        
        Notes:
            - Mutates req dict in place
            - Uses dict.setdefault() to avoid overwriting existing action
            - Eliminates repeated setdefault calls in handler methods
        """
        req.setdefault(KEY_ACTION, default_action)
    
    def _resolve_block_data(self, data_block: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data queries defined in block-level _data (zCLI declarative pattern).
        
        This enables Jinja-like templating in YAML where data queries are co-located
        with UI definitions, but with better security (credentials in .zEnv).
        
        Args:
            data_block: _data section from zUI block
            context: Current execution context (for accessing session, etc.)
        
        Returns:
            Dictionary of query results: {"user": {...}, "stats": [...]}
        
        Examples:
            # In zUI.zAccount.yaml:
            zAccount:
              _data:
                user: "@.models.zSchema.contacts"  # Shorthand
                stats:
                  zData:  # Explicit
                    action: read
                    model: "@.models.zSchema.user_stats"
        
        Security:
            - Model paths (@.models.zSchema.contacts) are safe to commit
            - Actual DB connections (postgresql://...) are in .zEnv
            - Session-based auto-filtering prevents unauthorized data access
        """
        results = {}
        
        for key, query_def in data_block.items():
            try:
                # Handle shorthand: user: "@.models.zSchema.contacts"
                if isinstance(query_def, str) and query_def.startswith('@.models.'):
                    # Shorthand model reference - convert to zData request
                    # Auto-filter by authenticated user ID for security
                    
                    # Get authenticated user ID from zAuth (supports 3-layer architecture)
                    zauth = self.zcli.session.get('zAuth', {})
                    active_app = zauth.get('active_app')
                    
                    # Try app-specific auth first (applications layer)
                    if active_app:
                        app_auth = zauth.get('applications', {}).get(active_app, {})
                        user_id = app_auth.get('id')
                    else:
                        # Fallback to Zolo platform auth (zSession layer - future SSO)
                        user_id = zauth.get('zSession', {}).get('id')
                    
                    query_def = {
                        "zData": {
                            "action": "read",
                            "model": query_def,
                            "options": {
                                "where": f"id = {user_id}" if user_id else "1 = 0",  # Security: no ID = no results
                                "limit": 1
                            }
                        }
                    }
                
                # Handle explicit zData block
                if isinstance(query_def, dict) and "zData" in query_def:
                    # Execute zData query via subsystem in SILENT mode (v1.5.12)
                    # Silent mode: returns rows without displaying, works in any zMode
                    query_def["zData"]["silent"] = True
                    
                    result = self.zcli.data.handle_request(query_def["zData"], context)
                    
                    # Extract first record if limit=1 (single record query)
                    if isinstance(result, list) and query_def["zData"].get("options", {}).get("limit") == 1 and len(result) > 0:
                        results[key] = result[0]  # Return dict instead of list for single record
                    else:
                        results[key] = result
                    
                    result_type = type(results[key]).__name__
                    result_count = len(result) if isinstance(result, list) else 1
                    self.logger.framework.debug(f"[zCLI Data] Query '{key}' returned {result_type} ({result_count} records)")
                else:
                    self.logger.framework.warning(f"[zCLI Data] Invalid _data entry: {key}")
                    results[key] = None
                    
            except Exception as e:
                self.logger.framework.error(f"[zCLI Data] Query '{key}' failed: {e}")
                results[key] = None
        
        return results
