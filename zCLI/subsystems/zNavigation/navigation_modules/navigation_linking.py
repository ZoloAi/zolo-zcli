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

- SESSION_KEY_ZVAFILE_PATH: Base path to file
- SESSION_KEY_ZVAFILENAME: Filename (without extension)
- SESSION_KEY_ZBLOCK: Target block name

These session keys are used by zLoader and zWalker to maintain navigation context.

Layer Position
--------------
Layer 1, Position 4 (zNavigation) - Tier 1 (Foundation)

Integration
-----------
- Called by: zNavigation facade, dispatch_launcher (3 call sites)
- Uses: zParser (zExpr_eval), zLoader (file loading), zWalker (block execution)
- Session: Reads SESSION_KEY_ZAUTH, writes SESSION_KEY_ZVAFILE_PATH, etc.
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
    SESSION_KEY_ZVAFILE_PATH,
    SESSION_KEY_ZVAFILENAME,
    SESSION_KEY_ZBLOCK,
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
    - Session: Reads SESSION_KEY_ZAUTH, writes SESSION_KEY_ZVAFILE_PATH/ZVAFILENAME/ZBLOCK
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
        - SESSION_KEY_ZVAFILE_PATH: Written during navigation
        - SESSION_KEY_ZVAFILENAME: Written during navigation
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
        
        # Parse zLink expression
        zLink_path, required_perms = self.parse_zLink_expression(walker, zHorizontal)

        # Log parsed values
        self.logger.debug(LOG_ZLINK_PATH, zLink_path)
        self.logger.debug(LOG_REQUIRED_PERMS, required_perms)

        # Check permissions if required
        if required_perms and not self.check_zLink_permissions(walker, required_perms):
            print(MSG_PERMISSION_DENIED)
            return STATUS_STOP

        # Load target file
        zFile_parsed = walker.loader.handle(zLink_path)
        self.logger.debug(LOG_ZFILE_PARSED, zFile_parsed)

        # Extract target block name from path
        selected_zBlock = zLink_path.split(PATH_SEPARATOR)[PATH_INDEX_BLOCK]

        # Update session with new file/block context
        self._update_session_path(zLink_path, selected_zBlock)

        # Get block dict and keys
        active_zBlock_dict = zFile_parsed[selected_zBlock]
        zBlock_keys = list(active_zBlock_dict.keys())

        # Validate walker instance
        if walker is None:
            self.logger.error(MSG_NO_WALKER)
            return STATUS_STOP

        # Track breadcrumb
        walker.zCrumbs.handle_zCrumbs(zLink_path, zBlock_keys[0])

        # Execute target block
        return walker.zBlock_loop(active_zBlock_dict, zBlock_keys)

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

        # Strip "zLink(" prefix and ")" suffix
        inner = expr[len(PARSE_PREFIX_ZLINK):-1].strip()
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
        - SESSION_KEY_ZVAFILE_PATH: Base path (e.g., "")
        - SESSION_KEY_ZVAFILENAME: Filename (e.g., "zUI.settings")
        - SESSION_KEY_ZBLOCK: Block name (e.g., "NetworkSettings")
        
        Algorithm
        ---------
        1. Extract path to file (everything except last part)
        2. Split path into parts by "."
        3. If >= 2 parts:
           a. Extract base path (all parts except last 2)
           b. Set zVaFile_path to joined base path (or "" if empty)
           c. Set zVaFilename to last 2 parts joined
        4. Else (< 2 parts):
           a. Set zVaFile_path to ""
           b. Set zVaFilename to entire path
        5. Set zBlock to selected_zBlock
        """
        # Extract path to file (without block name)
        path_to_file = zLink_path.rsplit(PATH_SEPARATOR, 1)[0]
        parts = path_to_file.split(PATH_SEPARATOR)
        
        # Parse path components
        if len(parts) >= PATH_PARTS_MIN:
            base_path_parts = parts[:PATH_PARTS_BASE_OFFSET]
            self.zSession[SESSION_KEY_ZVAFILE_PATH] = (
                PATH_SEPARATOR.join(base_path_parts) if base_path_parts else PATH_DEFAULT_BASE
            )
            self.zSession[SESSION_KEY_ZVAFILENAME] = PATH_SEPARATOR.join(
                parts[PATH_INDEX_FILENAME_START:]
            )
        else:
            self.zSession[SESSION_KEY_ZVAFILE_PATH] = PATH_DEFAULT_BASE
            self.zSession[SESSION_KEY_ZVAFILENAME] = path_to_file
        
        # Set block name
        self.zSession[SESSION_KEY_ZBLOCK] = selected_zBlock
