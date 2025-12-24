# zCLI/subsystems/zNavigation/navigation_modules/navigation_linking.py

"""
Inter-File Linking (zLink) for zNavigation - Navigation Flow Component.

This module provides the Linking class, which handles inter-file navigation via
zLink expressions. It parses zLink syntax, validates RBAC permissions, loads
target files, and orchestrates navigation to the linked block.

Architecture
------------
The Linking class is a Tier 1 (Foundation) component that manages zLink navigation:

1. **Parse zLink Expression** (parse_zLink_expression)
   - Extracts file path and optional permission requirements
   - Supports: zLink(path) or zLink(path, {"role": "admin"})
   - Uses zParser.zExpr_eval() for permission dict parsing

2. **Check RBAC Permissions** (check_zLink_permissions)
   - Validates user permissions against required permissions
   - Reads from session[SESSION_KEY_ZAUTH]
   - Denies access if permissions don't match

3. **Execute Navigation** (handle)
   - Orchestrates the full linking flow
   - Updates session with new file/block context
   - Delegates to zLoader for file loading
   - Delegates to zWalker for block execution

zLink Syntax
------------
Basic link (no permissions)::

    zLink(@.zUI.settings.NetworkSettings)

Link with permission requirements::

    zLink(@.zUI.admin.UserManagement, {"role": "admin"})
    zLink(@.zUI.finance.Reports, {"role": "finance", "level": "manager"})

Path Format:
- @ = Base path (workspace root)
- zUI = UI directory
- filename = YAML file name (without extension)
- BlockName = Target block within file

RBAC Integration
----------------
Permission checking uses the zAuth subsystem:

1. Retrieves user auth data from session[SESSION_KEY_ZAUTH]
2. Compares user attributes with required permissions (exact match)
3. Denies access if any required permission doesn't match
4. Allows access if no permissions specified (public link)

Example::

    # User in session
    session[SESSION_KEY_ZAUTH] = {"role": "admin", "level": "manager"}
    
    # Required permissions
    required = {"role": "admin"}
    
    # Check: user["role"] == required["role"] → True (access granted)

Session Updates
---------------
The linking process updates the following session keys:

- SESSION_KEY_ZVAFOLDER: Folder containing the file
- SESSION_KEY_ZVAFILE: Filename (without extension)
- SESSION_KEY_ZBLOCK: Target block name

These session keys are used by zLoader and zWalker to maintain navigation context.

Layer Position
--------------
Layer 1, Position 4 (zNavigation) - Tier 1 (Foundation)

Integration
-----------
- Called by: zNavigation facade, dispatch_launcher (3 call sites)
- Uses: zParser (zExpr_eval), zLoader (file loading), zWalker (block execution)
- Session: Reads SESSION_KEY_ZAUTH, writes SESSION_KEY_ZVAFOLDER, etc.
- Logging: Debug for flow, info for parsing, warning for permission denials

Forward Dependencies
--------------------
This module depends on:

1. **zParser (Week 6.8):**
   - zExpr_eval() for parsing permission dict strings
   
2. **zLoader (Week 6.9):**
   - loader.handle() for loading target YAML files
   
3. **zWalker (Week 6.11):**
   - walker.display for UI declarations
   - walker.loader for file loading
   - walker.zCrumbs for breadcrumb management
   - walker.zBlock_loop() for executing target block

Usage Examples
--------------
Parse a basic zLink::

    linking = Linking(navigation_system)
    path, perms = linking.parse_zLink_expression(walker, "zLink(@.zUI.settings.Main)")
    # path = "@.zUI.settings.Main"
    # perms = {}

Parse a zLink with permissions::

    path, perms = linking.parse_zLink_expression(
        walker,
        'zLink(@.zUI.admin.Users, {"role": "admin"})'
    )
    # path = "@.zUI.admin.Users"
    # perms = {"role": "admin"}

Check permissions::

    has_access = linking.check_zLink_permissions(walker, {"role": "admin"})
    # Returns True if user has admin role, False otherwise

Execute full linking flow::

    result = linking.handle(walker, 'zLink(@.zUI.settings.Network)')
    # Navigates to Network block in settings file

Module Constants
----------------
DISPLAY_* : str
    Display settings (color, styles, indents)
STATUS_* : str
    Status values for navigation results
MSG_* : str
    Message strings for permission denials and errors
LOG_* : str
    Log message templates
PARSE_* : str
    Parsing literals for zLink expression syntax
PATH_* : str
    Path parsing constants
"""

from zCLI import Any, Dict, Tuple
from zCLI.subsystems.zParser.parser_modules.parser_utils import zExpr_eval
from zCLI.subsystems.zConfig.zConfig_modules.config_session import (
    SESSION_KEY_ZAUTH,
    SESSION_KEY_ZVAFOLDER,
    SESSION_KEY_ZVAFILE,
    SESSION_KEY_ZBLOCK,
    SESSION_KEY_ZCRUMBS,
)

# ============================================================================
# Module Constants
# ============================================================================

# Display Settings
DISPLAY_COLOR_ZLINK: str = "ZLINK"
DISPLAY_STYLE_FULL: str = "full"
DISPLAY_STYLE_SINGLE: str = "single"
DISPLAY_INDENT_HANDLE: int = 1
DISPLAY_INDENT_PARSE: int = 2
DISPLAY_INDENT_AUTH: int = 2

# Display Messages
DISPLAY_MSG_HANDLE: str = "Handle zLink"
DISPLAY_MSG_PARSE: str = "zLink Parsing"
DISPLAY_MSG_AUTH: str = "zLink Auth"

# Status Values
STATUS_STOP: str = "stop"

# Messages
MSG_PERMISSION_DENIED: str = "Permission denied for this section."
MSG_NO_WALKER: str = "[ERROR] No walker instance provided to zLink."

# Log Messages
LOG_INCOMING_REQUEST: str = "incoming zLink request: %s"
LOG_ZLINK_PATH: str = "zLink_path: %s"
LOG_REQUIRED_PERMS: str = "required_perms: %s"
LOG_ZFILE_PARSED: str = "zFile_parsed: %s"
LOG_RAW_EXPRESSION: str = "Raw zLink expression: %s"
LOG_STRIPPED_INNER: str = "Stripped inner contents: %s"
LOG_PATH_PART: str = "Path part: %s"
LOG_PERMS_PART_RAW: str = "Permissions part (raw): %s"
LOG_PARSED_PERMS: str = "Parsed required permissions: %s"
LOG_WARN_NON_DICT: str = "strict_eval returned non-dict permissions. Defaulting to empty."
LOG_NO_PERMS_BLOCK: str = "[INFO] No permission block found. Path: %s"
LOG_ZAUTH_USER: str = "zAuth user: %s"
LOG_REQUIRED_PERMS_CHECK: str = "Required permissions: %s"
LOG_NO_PERMS_REQUIRED: str = "No permissions required - allowing access."
LOG_CHECK_PERM_KEY: str = "Checking permission key: %s | expected=%s, actual=%s"
LOG_WARN_PERM_DENIED: str = "Permission denied. Required %s=%s, but got %s"
LOG_ALL_PERMS_MATCHED: str = "All required permissions matched."

# Parsing Literals
PARSE_PREFIX_ZLINK: str = "zLink("
PARSE_SUFFIX_RPAREN: str = ")"
PARSE_PERMS_SEPARATOR: str = ", {"
PARSE_BRACE_OPEN: str = "{"
PARSE_BRACE_CLOSE: str = "}"

# Path Parsing
PATH_SEPARATOR: str = "."
PATH_INDEX_LAST: int = -1
PATH_INDEX_BLOCK: int = -1
PATH_INDEX_FILENAME_START: int = -2
PATH_PARTS_MIN: int = 2
PATH_PARTS_BASE_OFFSET: int = -2
PATH_DEFAULT_BASE: str = ""


# ============================================================================
# Linking Class
# ============================================================================

class Linking:
    """
    Inter-file linking manager for zNavigation.
    
    Handles zLink expressions for navigating between files and blocks. Parses
    zLink syntax, validates RBAC permissions, loads target files, and orchestrates
    navigation flow via zWalker.
    
    Attributes
    ----------
    navigation : Any
        Reference to parent navigation system
    zcli : Any
        Reference to zCLI core instance
    logger : Any
        Logger instance for linking operations
    zSession : Dict[str, Any]
        Direct reference to zcli.session (for convenience)
    
    Methods
    -------
    handle(walker, zHorizontal)
        Execute full zLink navigation flow
    parse_zLink_expression(walker, expr)
        Parse zLink expression to extract path and permissions
    check_zLink_permissions(walker, required)
        Check if user has required permissions
    
    Private Methods
    ---------------
    _update_session_path(zLink_path, selected_zBlock)
        Update session with new file/block context
    
    Examples
    --------
    Execute a zLink::
    
        linking = Linking(navigation_system)
        result = linking.handle(walker, 'zLink(@.zUI.settings.Network)')
    
    Parse and check permissions::
    
        path, perms = linking.parse_zLink_expression(
            walker,
            'zLink(@.zUI.admin.Users, {"role": "admin"})'
        )
        has_access = linking.check_zLink_permissions(walker, perms)
    
    Integration
    -----------
    - Parent: zNavigation system
    - Session: Reads SESSION_KEY_ZAUTH, writes SESSION_KEY_ZVAFOLDER/ZVAFILENAME/ZBLOCK
    - Walker: Passed as parameter for display, loader, zCrumbs, zBlock_loop access
    - Logging: Debug for flow, info for parsing, warning for denials
    
    Forward Dependencies
    --------------------
    - zParser: zExpr_eval() for permission dict parsing
    - zLoader: walker.loader.handle() for file loading
    - zWalker: walker.display, walker.zCrumbs, walker.zBlock_loop()
    """

    # Class-level type declarations
    navigation: Any  # Navigation system reference
    zcli: Any  # zCLI core instance
    logger: Any  # Logger instance
    zSession: Dict[str, Any]  # Direct reference to session

    def __init__(self, navigation: Any) -> None:
        """
        Initialize linking manager.
        
        Args
        ----
        navigation : Any
            Parent navigation system instance that provides access to zcli and logger
        
        Notes
        -----
        Stores references to the parent navigation system, zcli core, logger, and
        session for use during linking operations. The zSession reference is stored
        for convenience to avoid repeated `self.zcli.session` lookups.
        
        Session Dependencies
        --------------------
        This module manages the following session keys:
        - SESSION_KEY_ZAUTH: Read for permission checking
        - SESSION_KEY_ZVAFOLDER: Written during navigation
        - SESSION_KEY_ZVAFILE: Written during navigation
        - SESSION_KEY_ZBLOCK: Written during navigation
        """
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger
        self.zSession = self.zcli.session  # Store for convenience

    def handle(self, walker: Any, zHorizontal: str) -> str:
        """
        Handle zLink navigation request.
        
        Orchestrates the full linking flow: display declaration, parsing, permission
        checking, file loading, session updates, breadcrumb tracking, and block execution.
        
        Args
        ----
        walker : Any
            Walker instance providing display, loader, zCrumbs, and zBlock_loop access
        zHorizontal : str
            zLink expression to execute (e.g., 'zLink(@.zUI.settings.Network)')
        
        Returns
        -------
        str
            Navigation result:
            - STATUS_STOP if permission denied or walker is None
            - Result from walker.zBlock_loop() on success
        
        Examples
        --------
        Basic zLink (no permissions)::
        
            result = linking.handle(walker, 'zLink(@.zUI.settings.Main)')
            # Navigates to Main block in settings file
        
        zLink with permissions::
        
            result = linking.handle(
                walker,
                'zLink(@.zUI.admin.Users, {"role": "admin"})'
            )
            # Checks permissions, then navigates if allowed
        
        Handle permission denial::
        
            result = linking.handle(walker, 'zLink(@.zUI.admin.Users, {"role": "admin"})')
            if result == STATUS_STOP:
                print("Permission denied or error occurred")
        
        Notes
        -----
        - **Display Declaration**: Shows "Handle zLink" banner
        - **Parsing**: Extracts path and permissions from expression
        - **Permission Check**: Validates RBAC if permissions specified
        - **File Loading**: Uses walker.loader.handle() to load target file
        - **Session Update**: Updates file path, filename, and block in session
        - **Breadcrumb Tracking**: Calls walker.zCrumbs.handle_zCrumbs()
        - **Block Execution**: Returns result from walker.zBlock_loop()
        
        Algorithm
        ---------
        1. Display "Handle zLink" declaration
        2. Log incoming request
        3. Parse zLink expression (path + permissions)
        4. Log parsed values
        5. If permissions required and check fails, deny access (return STATUS_STOP)
        6. Load target file via walker.loader.handle()
        7. Extract target block name from path
        8. Update session with new file/block context
        9. Validate walker instance exists
        10. Track breadcrumb (walker.zCrumbs.handle_zCrumbs)
        11. Execute target block (walker.zBlock_loop)
        12. Return result
        """
        # Display declaration
        walker.display.zDeclare(
            DISPLAY_MSG_HANDLE,
            color=DISPLAY_COLOR_ZLINK,
            indent=DISPLAY_INDENT_HANDLE,
            style=DISPLAY_STYLE_FULL
        )

        # Log incoming request
        self.logger.debug(LOG_INCOMING_REQUEST, zHorizontal)
        
        # Extract zLink value from dictionary
        if isinstance(zHorizontal, dict):
            zLink_expr = zHorizontal.get('zLink', '')
        else:
            zLink_expr = zHorizontal
        
        # Parse zLink expression
        zLink_path, required_perms = self.parse_zLink_expression(walker, zLink_expr)

        # Log parsed values
        self.logger.debug(LOG_ZLINK_PATH, zLink_path)
        self.logger.debug(LOG_REQUIRED_PERMS, required_perms)
        
        # ====================================================================
        # HTTP ROUTE DETECTION (v1.5.4 Phase 3 - Demo 4)
        # ====================================================================
        # Detect if zLink is an HTTP route (starts with "/")
        # This enables dual-mode behavior: Terminal (file paths) vs Web (HTTP routes)
        if zLink_path.startswith("/"):
            self.logger.info(f"[zLink] HTTP route detected: {zLink_path}")
            
            # Get display mode from session
            from zCLI.subsystems.zConfig.zConfig_modules.config_session import SESSION_KEY_ZMODE
            mode = walker.session.get(SESSION_KEY_ZMODE, "Terminal")
            
            if mode == "Web":
                # WEB MODE: Return metadata for HTML link rendering
                # The page renderer will convert this to <a href="/route">
                self.logger.debug(f"[zLink] Web mode - returning redirect metadata")
                return {
                    "type": "http_redirect",
                    "url": zLink_path,
                    "mode": "web"
                }
            else:
                # TERMINAL MODE: HTTP routes don't make sense in terminal
                # User likely mixed Web and Terminal zUI patterns
                self.logger.warning(f"[zLink] HTTP route '{zLink_path}' in Terminal mode - skipping navigation")
                walker.display.handle({
                    "event": "warning",
                    "content": f"HTTP route '{zLink_path}' cannot be navigated in Terminal mode",
                    "indent": 1
                })
                return STATUS_STOP
        
        # ====================================================================
        # FILE-BASED NAVIGATION (Original logic - Terminal/Bifrost mode)
        # ====================================================================

        # Check permissions if required
        if required_perms and not self.check_zLink_permissions(walker, required_perms):
            print(MSG_PERMISSION_DENIED)
            return STATUS_STOP

        # Extract target block name from path (last element)
        path_parts = zLink_path.split(PATH_SEPARATOR)
        selected_zBlock = path_parts[PATH_INDEX_BLOCK]
        
        # Extract file path (everything except the last element = block name)
        zFile_path = PATH_SEPARATOR.join(path_parts[:-1])
        
        # Load target file (without block name)
        zFile_parsed = walker.loader.handle(zFile_path)
        self.logger.debug(LOG_ZFILE_PARSED, zFile_parsed)

        # ====================================================================
        # BREADCRUMB FIX: Capture SOURCE context BEFORE navigation
        # ====================================================================
        # Get source location (where we're navigating FROM) before session update
        from zCLI.subsystems.zConfig.zConfig_modules.config_session import SESSION_KEY_ZCRUMBS
        # Phase 0.5: Handle enhanced format
        crumbs_dict = walker.session.get(SESSION_KEY_ZCRUMBS, {})
        
        # CHECK NAVBAR FLAG: Detect if this navigation is from navbar (for OP_RESET)
        is_navbar_navigation = crumbs_dict.get("_navbar_navigation", False)
        if is_navbar_navigation:
            self.logger.info(f"[zLink] Navbar navigation detected → will trigger OP_RESET")
        
        # Get trails from enhanced format or use old format
        if 'trails' in crumbs_dict:
            trails = crumbs_dict['trails']
        else:
            trails = crumbs_dict
        
        source_block_path = next(reversed(trails)) if trails else None
        
        # NAVBAR NAVIGATION: Skip source breadcrumb recording (will be cleared by RESET anyway)
        if not is_navbar_navigation:
            # REGULAR NAVIGATION: Use the active source scope (where we're navigating FROM)
            if source_block_path and source_block_path in trails:
                # Get the last key in the source scope's trail (the key that triggered this zLink)
                source_trail = trails[source_block_path]
                source_zKey = source_trail[-1] if source_trail else None
                
                # Record source breadcrumb (ensures parent scope has the calling key)
                # Note: walker_dispatch already added this, but handle_zCrumbs prevents duplicates
                # Session still points to SOURCE at this point, so handle_zCrumbs will use source block
                if source_zKey:
                    walker.navigation.breadcrumbs.handle_zCrumbs(source_zKey, walker=walker)
                    self.logger.debug(f"Recorded source breadcrumb: {source_block_path}[{source_zKey}]")
        else:
            self.logger.debug("[zLink] Skipping source breadcrumb (navbar navigation will RESET)")

        # Update session to TARGET location
        self._update_session_path(zLink_path, selected_zBlock)

        # Get block dict and keys with auto-discovery fallback
        # FALLBACK CHAIN:
        # 1. Try finding block in loaded file
        # 2. If not found, try loading from zUI.{blockName}.yaml
        if selected_zBlock in zFile_parsed:
            # Block found in loaded file
            active_zBlock_dict = zFile_parsed[selected_zBlock]
            self.logger.debug(f"[zLink] Block '{selected_zBlock}' found in loaded file")
        else:
            # AUTO-DISCOVERY: Try loading from separate file
            self.logger.debug(
                f"[zLink] Block '{selected_zBlock}' not in file, trying auto-discovery..."
            )
            
            # Strip navigation modifiers (^ ~) from block name for file path
            # File names don't have modifiers, but blocks inside do
            # Example: ^zLogin block → zUI.zLogin.yaml file (not zUI.^zLogin.yaml)
            file_block_name = selected_zBlock.lstrip("^~")
            
            # Construct fallback zPath: same directory, different file
            # Example: @.UI.zUI.zVaF → @.UI.zUI.zLogin (stripped ^)
            if zFile_path.startswith("@"):
                path_parts = zFile_path.split(".")
                # Replace last part with file_block_name (without modifiers)
                fallback_path_parts = path_parts[:-1] + [file_block_name]
                fallback_zPath = ".".join(fallback_path_parts)
            else:
                fallback_zPath = f"@.UI.zUI.{file_block_name}"
            
            self.logger.debug(f"[zLink] Trying fallback: {fallback_zPath} (stripped modifiers from '{selected_zBlock}')")
            
            try:
                fallback_zFile = walker.loader.handle(fallback_zPath)
                if fallback_zFile and isinstance(fallback_zFile, dict):
                    # Get first block from fallback file
                    if selected_zBlock in fallback_zFile:
                        active_zBlock_dict = fallback_zFile[selected_zBlock]
                        self.logger.info(
                            f"✓ [zLink] Auto-discovered block '{selected_zBlock}' from: {fallback_zPath}"
                        )
                    else:
                        raise KeyError(f"Block '{selected_zBlock}' not found in {fallback_zPath}")
                else:
                    raise ValueError(f"Failed to load {fallback_zPath}")
            except Exception as e:
                self.logger.error(
                    f"Block '{selected_zBlock}' not found:\n"
                    f"  - Not in loaded file: {zFile_path}\n"
                    f"  - Fallback failed: {fallback_zPath}\n"
                    f"  - Error: {e}"
                )
                return STATUS_STOP
        
        zBlock_keys = list(active_zBlock_dict.keys())

        # Validate walker instance
        if walker is None:
            self.logger.error(MSG_NO_WALKER)
            return STATUS_STOP

        # DO NOT initialize target breadcrumb scope here - let walker_dispatch handle it naturally
        # The key insight: walker_dispatch will create and populate the target scope as keys execute
        # When the target block completes and zBack is called, the target trail will have items
        # zBack's algorithm will pop from the target trail, and when it empties, move to parent
        self.logger.debug(f"Navigating to target block: {zLink_path}")

        # BLOCK-LEVEL BOUNCE-BACK: Detect ^ modifier on block name
        # If block name starts with ^, execute and then bounce back
        should_bounce_back = selected_zBlock.startswith("^")
        self.logger.debug(f"[zNavigation] Block name: '{selected_zBlock}', should_bounce_back: {should_bounce_back}")
        
        # BREADCRUMB SNAPSHOT: Save current breadcrumb state before executing bounce-back block
        breadcrumb_snapshot = None
        if should_bounce_back:
            self.logger.info(f"[zNavigation] ⬅️  Block-level bounce-back enabled for: {selected_zBlock}")
            
            # Save a deep copy of the current breadcrumb state
            import copy
            breadcrumb_snapshot = copy.deepcopy(walker.zcli.session.get(SESSION_KEY_ZCRUMBS, {}))
            self.logger.debug(f"[zNavigation] 📸 Saved breadcrumb snapshot: {breadcrumb_snapshot}")
        
        # Execute target block
        result = walker.zBlock_loop(active_zBlock_dict, zBlock_keys)
        self.logger.debug(f"[zNavigation] Block execution result: {result}, should_bounce_back: {should_bounce_back}")
        
        # If block-level bounce-back was flagged, restore breadcrumb snapshot and continue
        if should_bounce_back:
            # Skip bounce-back if user already navigated away (zBack, exit, etc.)
            if isinstance(result, dict) or result in ["zBack", "exit", "stop"]:
                self.logger.debug(f"[zNavigation] Skipping bounce-back restoration, result: {result}")
                return result
            
            self.logger.info("[zNavigation] ⬅️  Restoring breadcrumbs from snapshot!")
            
            # Restore the breadcrumb state to what it was BEFORE entering the ^ block
            if breadcrumb_snapshot is not None:
                # Clear the _navbar_navigation flag before restoration to prevent duplicate RESET
                if '_navbar_navigation' in breadcrumb_snapshot:
                    del breadcrumb_snapshot['_navbar_navigation']
                    self.logger.debug("[zNavigation] Cleared _navbar_navigation flag from snapshot")
                
                walker.zcli.session[SESSION_KEY_ZCRUMBS] = breadcrumb_snapshot
                self.logger.debug(f"[zNavigation] ✅ Restored breadcrumbs: {breadcrumb_snapshot}")
                
                # Now we need to continue the walker by re-loading the current block
                # Get the active crumb from the restored snapshot (handle enhanced format with 'trails' wrapper)
                if 'trails' in breadcrumb_snapshot:
                    # Enhanced format: trails are inside 'trails' dict
                    trail_keys = list(breadcrumb_snapshot['trails'].keys())
                else:
                    # Legacy format: filter out metadata keys starting with _
                    trail_keys = [k for k in breadcrumb_snapshot.keys() if not k.startswith('_')]
                active_zCrumb = trail_keys[-1] if trail_keys else None
                
                if active_zCrumb:
                    # Parse the active crumb to get file/block info
                    crumb_parts = active_zCrumb.split(".")
                    if len(crumb_parts) >= 3:
                        # Extract path, filename, and block
                        zVaFolder = ".".join(crumb_parts[:-2])
                        zVaFile = ".".join(crumb_parts[-2:-1])
                        zBlock = crumb_parts[-1]
                        
                        # Construct zPath and reload file
                        zPath = f"{zVaFolder}.{zVaFile}"
                        self.logger.debug(f"[zNavigation] Reloading file for bounce-back: {zPath}")
                        
                        # Load the file
                        raw_zFile = walker.loader.handle(zPath=zPath)
                        
                        # Get the block directly from raw_zFile
                        if zBlock in raw_zFile:
                            block_dict = raw_zFile[zBlock]
                            block_keys = list(block_dict.keys())
                        else:
                            self.logger.warning(f"[zNavigation] Block '{zBlock}' not found in {zPath}")
                            return result
                        
                        # Get the start key from the restored trail (handle enhanced format with 'trails' wrapper)
                        if 'trails' in breadcrumb_snapshot:
                            trail = breadcrumb_snapshot['trails'].get(active_zCrumb, [])
                        else:
                            trail = breadcrumb_snapshot.get(active_zCrumb, [])
                        start_key = trail[-1] if trail else None
                        
                        self.logger.debug(f"[zNavigation] Continuing from: {zBlock}, start_key: {start_key}")
                        
                        # Re-execute the block to continue the walker
                        bounce_result = walker.zBlock_loop(block_dict, block_keys, start_key)
                        
                        # Convert soft exit dict to signal string
                        if isinstance(bounce_result, dict) and bounce_result.get("exit") == "completed":
                            self.logger.debug("[zNavigation] User exited after bounce-back - converting to signal")
                            return "exit"  # Return signal string, not dict
                        
                        # Otherwise, return the result as-is
                        return bounce_result
                    else:
                        self.logger.warning(f"[zNavigation] Invalid crumb format: {active_zCrumb}")
                        return result
                else:
                    self.logger.warning("[zNavigation] No active crumb in restored snapshot!")
                    return result
            else:
                self.logger.warning("[zNavigation] No breadcrumb snapshot to restore!")
                return result
        
        return result

    def parse_zLink_expression(
        self,
        walker: Any,
        expr: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Parse zLink expression to extract path and permissions.
        
        Parses zLink syntax to extract the file path and optional permission
        requirements. Uses zParser.zExpr_eval() to parse permission dict strings.
        
        Args
        ----
        walker : Any
            Walker instance providing display for UI declarations
        expr : str
            zLink expression string to parse
        
        Returns
        -------
        Tuple[str, Dict[str, Any]]
            Tuple of (path, permissions):
            - path (str): File path (e.g., "@.zUI.settings.Network")
            - permissions (Dict[str, Any]): Required permissions dict (empty if none)
        
        Examples
        --------
        Parse basic zLink (no permissions)::
        
            path, perms = linking.parse_zLink_expression(
                walker,
                "zLink(@.zUI.settings.Main)"
            )
            # path = "@.zUI.settings.Main"
            # perms = {}
        
        Parse zLink with permissions::
        
            path, perms = linking.parse_zLink_expression(
                walker,
                'zLink(@.zUI.admin.Users, {"role": "admin"})'
            )
            # path = "@.zUI.admin.Users"
            # perms = {"role": "admin"}
        
        Parse zLink with multiple permissions::
        
            path, perms = linking.parse_zLink_expression(
                walker,
                'zLink(@.zUI.finance.Reports, {"role": "finance", "level": "manager"})'
            )
            # path = "@.zUI.finance.Reports"
            # perms = {"role": "finance", "level": "manager"}
        
        Notes
        -----
        - **Display Declaration**: Shows "zLink Parsing" banner
        - **Syntax**: zLink(path) or zLink(path, {"key": "value"})
        - **Permission Parsing**: Uses zParser.zExpr_eval() to convert string to dict
        - **Error Handling**: Defaults to empty dict if parsing fails or returns non-dict
        - **Logging**: Info for expressions and parsed values, warning for non-dict results
        
        Algorithm
        ---------
        1. Display "zLink Parsing" declaration
        2. Log raw expression
        3. Strip "zLink(" prefix and ")" suffix
        4. Log stripped inner contents
        5. Check if ", {" exists (indicates permissions)
        6. If permissions:
           a. Split on ", {" to separate path and permissions
           b. Reconstruct permission dict string with braces
           c. Log path and permissions parts
           d. Parse permissions with zExpr_eval()
           e. Validate result is dict (default to {} if not)
           f. Log parsed permissions
        7. If no permissions:
           a. Use inner contents as path
           b. Set permissions to empty dict
           c. Log info message
        8. Return (path, permissions) tuple
        """
        # Display declaration
        walker.display.zDeclare(
            DISPLAY_MSG_PARSE,
            color=DISPLAY_COLOR_ZLINK,
            indent=DISPLAY_INDENT_PARSE,
            style=DISPLAY_STYLE_SINGLE
        )

        # Log raw expression
        self.logger.info(LOG_RAW_EXPRESSION, expr)

        # Check if expression has "zLink(" wrapper (imperative) or is raw path (declarative YAML)
        if expr.startswith(PARSE_PREFIX_ZLINK) and expr.endswith(PARSE_SUFFIX_RPAREN):
            # Imperative format: zLink(@.path) → strip wrapper
            inner = expr[len(PARSE_PREFIX_ZLINK):-1].strip()
        else:
            # Declarative YAML format: already a raw path → use as-is
            inner = expr.strip()
        
        self.logger.info(LOG_STRIPPED_INNER, inner)

        # Check if permissions are specified
        if PARSE_PERMS_SEPARATOR in inner:
            # Split path and permissions
            path_str, perms_str = inner.rsplit(PARSE_PERMS_SEPARATOR, 1)
            zLink_path = path_str.strip()
            
            # Reconstruct permission dict string
            perms_str = (
                PARSE_BRACE_OPEN +
                perms_str.strip().rstrip(PARSE_BRACE_CLOSE) +
                PARSE_BRACE_CLOSE
            )
            
            # Log parts
            self.logger.info(LOG_PATH_PART, zLink_path)
            self.logger.info(LOG_PERMS_PART_RAW, perms_str)

            # Parse permissions with zExpr_eval
            required = zExpr_eval(perms_str, self.logger)
            
            # Validate result is dict
            if not isinstance(required, dict):
                self.logger.warning(LOG_WARN_NON_DICT)
                required = {}
            else:
                self.logger.info(LOG_PARSED_PERMS, required)
        else:
            # No permissions specified
            zLink_path = inner
            required = {}
            self.logger.debug(LOG_NO_PERMS_BLOCK, zLink_path)
        
        return zLink_path, required

    def check_zLink_permissions(
        self,
        walker: Any,
        required: Dict[str, Any]
    ) -> bool:
        """
        Check if user has required permissions.
        
        Validates user permissions from session against required permissions dict.
        Uses exact matching: each required permission key must exist in user dict
        with the exact same value.
        
        Args
        ----
        walker : Any
            Walker instance providing display for UI declarations
        required : Dict[str, Any]
            Required permissions dict (e.g., {"role": "admin"})
        
        Returns
        -------
        bool
            True if user has all required permissions (or no permissions required),
            False if any permission check fails
        
        Examples
        --------
        Check admin role::
        
            # User: {"role": "admin"}
            has_access = linking.check_zLink_permissions(
                walker,
                {"role": "admin"}
            )
            # Returns: True
        
        Check multiple permissions::
        
            # User: {"role": "finance", "level": "manager"}
            has_access = linking.check_zLink_permissions(
                walker,
                {"role": "finance", "level": "manager"}
            )
            # Returns: True
        
        Permission mismatch::
        
            # User: {"role": "user"}
            has_access = linking.check_zLink_permissions(
                walker,
                {"role": "admin"}
            )
            # Returns: False (logs warning)
        
        No permissions required (public link)::
        
            has_access = linking.check_zLink_permissions(walker, {})
            # Returns: True (always allows access)
        
        Notes
        -----
        - **Display Declaration**: Shows "zLink Auth" banner
        - **User Data**: Reads from session[SESSION_KEY_ZAUTH]
        - **Exact Matching**: user[key] must == required[key] for all keys
        - **No Permissions**: Returns True if required dict is empty
        - **Missing Keys**: Returns False if user dict doesn't have required key
        - **Logging**: Debug for checks, warning for denials
        
        Algorithm
        ---------
        1. Display "zLink Auth" declaration
        2. Get user dict from session[SESSION_KEY_ZAUTH]
        3. Log user dict and required permissions
        4. If no permissions required, allow access (return True)
        5. For each required permission key:
           a. Get actual value from user dict
           b. Log comparison (key, expected, actual)
           c. If actual != expected, log warning and deny (return False)
        6. Log success message
        7. Return True (all permissions matched)
        """
        # Display declaration
        walker.display.zDeclare(
            DISPLAY_MSG_AUTH,
            color=DISPLAY_COLOR_ZLINK,
            indent=DISPLAY_INDENT_AUTH,
            style=DISPLAY_STYLE_SINGLE
        )

        # Get user auth data from session
        user = self.zSession.get(SESSION_KEY_ZAUTH, {})
        
        # Log user and required permissions
        self.logger.debug(LOG_ZAUTH_USER, user)
        self.logger.debug(LOG_REQUIRED_PERMS_CHECK, required)

        # If no permissions required, allow access
        if not required:
            self.logger.debug(LOG_NO_PERMS_REQUIRED)
            return True

        # Check each required permission
        for key, expected in required.items():
            actual = user.get(key)
            self.logger.debug(LOG_CHECK_PERM_KEY, key, expected, actual)
            
            if actual != expected:
                self.logger.warning(LOG_WARN_PERM_DENIED, key, expected, actual)
                return False

        # All permissions matched
        self.logger.debug(LOG_ALL_PERMS_MATCHED)
        return True

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _update_session_path(
        self,
        zLink_path: str,
        selected_zBlock: str
    ) -> None:
        """
        Update session with new file/block context.
        
        Parses the zLink path to extract base path, filename, and block name,
        then updates the session accordingly.
        
        Args
        ----
        zLink_path : str
            Full zLink path (e.g., "@.zUI.settings.NetworkSettings")
        selected_zBlock : str
            Target block name (e.g., "NetworkSettings")
        
        Notes
        -----
        DRY Helper: Centralizes session path updates.
        
        Session Keys Updated:
        - SESSION_KEY_ZVAFOLDER: Folder path (e.g., "")
        - SESSION_KEY_ZVAFILE: Filename (e.g., "zUI.settings")
        - SESSION_KEY_ZBLOCK: Block name (e.g., "NetworkSettings")
        
        Algorithm
        ---------
        1. Extract path to file (everything except last part)
        2. Split path into parts by "."
        3. If >= 2 parts:
           a. Extract base path (all parts except last 2)
           b. Set zVaFolder to joined base path (or "" if empty)
           c. Set zVaFile to last 2 parts joined
        4. Else (< 2 parts):
           a. Set zVaFolder to ""
           b. Set zVaFile to entire path
        5. Set zBlock to selected_zBlock
        """
        # Extract path to file (without block name)
        path_to_file = zLink_path.rsplit(PATH_SEPARATOR, 1)[0]
        parts = path_to_file.split(PATH_SEPARATOR)
        
        # Parse path components
        if len(parts) >= PATH_PARTS_MIN:
            base_path_parts = parts[:PATH_PARTS_BASE_OFFSET]
            self.zSession[SESSION_KEY_ZVAFOLDER] = (
                PATH_SEPARATOR.join(base_path_parts) if base_path_parts else PATH_DEFAULT_BASE
            )
            self.zSession[SESSION_KEY_ZVAFILE] = PATH_SEPARATOR.join(
                parts[PATH_INDEX_FILENAME_START:]
            )
        else:
            self.zSession[SESSION_KEY_ZVAFOLDER] = PATH_DEFAULT_BASE
            self.zSession[SESSION_KEY_ZVAFILE] = path_to_file
        
        # Set block name
        self.zSession[SESSION_KEY_ZBLOCK] = selected_zBlock
