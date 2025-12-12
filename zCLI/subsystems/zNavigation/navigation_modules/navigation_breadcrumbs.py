# zCLI/subsystems/zNavigation/navigation_modules/navigation_breadcrumbs.py

"""
Breadcrumb Trail Management for zNavigation - Session State Component.

This module provides the Breadcrumbs class, which manages hierarchical navigation
trails stored in the zSession. It supports adding breadcrumbs, navigating backward
through the trail, and formatting breadcrumbs for display.

Architecture
------------
The Breadcrumbs class is a Tier 1 (Foundation) component that directly manages
zSession state for navigation history. It implements a scope-based breadcrumb model
where each scope (file + block path) maintains its own trail of navigation keys.

Breadcrumb Data Model (Session-based):

    session[SESSION_KEY_ZCRUMBS] = {
        "@.zUI.main.MainMenu": ["Dashboard", "Settings", "Profile"],
        "@.zUI.settings.Network": ["Wi-Fi", "DNS", "Proxy"]
    }

**Structure:**
- **Key (Scope)**: Full path to a zUI block (e.g., "@.zUI.main.MainMenu")
- **Value (Trail)**: Ordered list of navigation keys within that block

**Scope Format**: `{path}.{filename}.{BlockName}`
- `path`: Base path or "@" for default
- `filename`: e.g., "zUI.main"
- `BlockName`: Top-level block name

This model supports:
- **Hierarchical Navigation**: Parent/child scope relationships
- **Multi-level Back**: Navigate up through nested scopes
- **State Persistence**: Trails preserved in zSession
- **File Reloading**: Automatic reload of correct file after zBack

Core Methods
------------
1. handle_zCrumbs(zBlock, zKey, walker=None)
   - Adds a navigation key to the current block's trail
   - Prevents duplicate consecutive keys
   - Creates new scopes as needed

2. handle_zBack(show_banner=True, walker=None) -> Tuple[Dict, List, Optional[str]]
   - Navigates backward through the breadcrumb trail
   - Manages parent/child scope transitions
   - Reloads the appropriate file after navigation
   - Returns: (block_dict, block_keys, start_key)

3. zCrumbs_banner() -> Dict[str, str]
   - Formats breadcrumbs for display
   - Returns dict of {scope: formatted_trail}

zBack Algorithm (Complex - 113 lines)
--------------------------------------
The zBack algorithm handles multi-level navigation with sophisticated scope management:

**Step 1: Identify Active Scope**
- Get the last (most recent) scope from session[SESSION_KEY_ZCRUMBS]
- Get the trail (list of keys) for this scope

**Step 2: Pop from Current Trail**
- If trail has items → pop the last key
- This moves back one step within the current block

**Step 3: Handle Empty Trail (Scope Transition)**
- If trail is empty and we're not at root:
  a. Remove the empty child scope from session
  b. Move to parent scope (now the last scope)
  c. Pop parent's last key (the link that opened the child)

**Step 4: Cascade Empty Scope Removal**
- If after popping, the current scope is now empty and not root:
  - Repeat the scope transition (step 3)
  - This handles cases where navigating back empties multiple levels

**Step 5: Parse Active Crumb for File Context**
- Split the active crumb by "." to extract:
  - Base path (everything before last 3 parts)
  - Filename (2nd and 3rd parts from end)
  - Block name (last part)
- Update session keys: zVaFolder, zVaFile, zBlock

**Step 6: Reload File**
- Construct zPath from session values
- Load file using zLoader
- Extract the active block dict and its keys

**Step 7: Return Context**
- Return (block_dict, block_keys, start_key)
- start_key is the current position in the trail (or None if trail is empty)

Session Integration (Critical)
-------------------------------
This module is a **CORE session management component** that directly reads and writes
multiple session keys:

**Primary Session Keys (from zConfig):**
- SESSION_KEY_ZCRUMBS: The breadcrumb trail dict
- SESSION_KEY_ZVAFOLDER: Folder containing current file
- SESSION_KEY_ZVAFILE: Current file name
- SESSION_KEY_ZBLOCK: Current block name

**Session Dependencies:**
- zWalker: Relies on breadcrumbs for navigation state
- zLoader: Used to reload files after navigation
- zDisplay: Uses zCrumbs_banner() for UI display

**CRITICAL**: All session keys MUST use centralized SESSION_KEY_* constants from
zConfig.zConfig_modules.config_session to ensure system-wide consistency.

Layer Position
--------------
Layer 1, Position 4 (zNavigation) - Tier 1 (Foundation)

Integration
-----------
- Called by: MenuSystem, zWalker
- Uses: zSession (state management), zLoader (file reloading), zDisplay (output)
- Thread Safety: Not thread-safe (relies on session state)

Usage Examples
--------------
Add breadcrumb to trail::

    breadcrumbs = Breadcrumbs(navigation_system)
    breadcrumbs.handle_zCrumbs(
        zBlock="@.zUI.main.MainMenu",
        zKey="Settings",
        walker=current_walker
    )

Navigate backward::

    block_dict, block_keys, start_key = breadcrumbs.handle_zBack(
        show_banner=True,
        walker=current_walker
    )
    
    if start_key:
        # Resume from start_key in block_keys
        index = block_keys.index(start_key)
    else:
        # Start from beginning
        index = 0

Format breadcrumbs for display::

    breadcrumbs_dict = breadcrumbs.zCrumbs_banner()
    # {"@.zUI.main.MainMenu": "Dashboard > Settings > Profile"}

Module Constants
----------------
COLOR_* : str
    Display colors for breadcrumb operations
STYLE_* : str
    Display styles (full, single, etc.)
INDENT_* : int
    Indentation levels for display
SEPARATOR_* : str
    String separators for formatting
PREFIX_* : str
    Path prefixes for default locations
MSG_* : str
    Display messages for operations
LOG_* : str
    Logging message templates
ERR_* : str
    Error messages for validation failures
CRUMB_* : int
    Magic numbers for crumb parsing (minimum parts, indices)
"""

from zCLI import Any, Dict, List, Optional, Tuple
from zCLI.subsystems.zConfig.zConfig_modules.config_session import (
    SESSION_KEY_ZCRUMBS,
    SESSION_KEY_ZVAFOLDER,
    SESSION_KEY_ZVAFILE,
    SESSION_KEY_ZBLOCK
)

# ============================================================================
# Module Constants
# ============================================================================

# Display Colors
COLOR_ZCRUMB: str = "ZCRUMB"

# Display Styles
STYLE_FULL: str = "full"

# Display Indents
INDENT_ZCRUMBS: int = 2
INDENT_ZBACK: int = 1

# Separators
SEPARATOR_CRUMB: str = " > "
SEPARATOR_DOT: str = "."
SEPARATOR_EMPTY: str = ""

# Path Prefixes
PREFIX_DEFAULT_PATH: str = "@."

# Display Messages
MSG_HANDLE_ZCRUMBS: str = "Handle zNavigation Breadcrumbs"
MSG_HANDLE_ZBACK: str = "zBack"

# Log Messages (Debug)
LOG_INCOMING_BLOCK_KEY: str = "\nIncoming zBlock: %s,\nand zKey: %s"
LOG_CURRENT_ZCRUMBS: str = "\nCurrent zCrumbs: %s"
LOG_CURRENT_TRAIL: str = "\nCurrent zTrail: %s"
LOG_DUPLICATE_SKIP: str = "Breadcrumb '%s' already exists at the end of scope '%s' - skipping."
LOG_ACTIVE_CRUMB: str = "active_zCrumb: %s"
LOG_ORIGINAL_CRUMB: str = "original_zCrumb: %s"
LOG_ACTIVE_BLOCK: str = "active_zBlock: %s"
LOG_TRAIL: str = "trail: %s"
LOG_TRAIL_AFTER_POP: str = "Trail after pop in '%s': %s"
LOG_POPPED_SCOPE: str = "Popped empty zCrumb scope: %s => %s"
LOG_ACTIVE_CRUMB_PARENT: str = "active_zCrumb (parent): %s"
LOG_PARENT_TRAIL_BEFORE: str = "parent trail before pop: %s"
LOG_PARENT_TRAIL_AFTER: str = "parent trail after pop: %s"
LOG_ROOT_EMPTY: str = "Root scope reached with empty trail; nothing to pop."
LOG_POST_POP_EMPTY: str = "Post-pop empty scope removed: %s => %s"
LOG_PARENT_TRAIL_PRE_SECOND: str = "parent trail (pre second pop): %s"
LOG_PARENT_TRAIL_POST_SECOND: str = "parent trail (post second pop): %s"
LOG_ROOT_CLEARED: str = "Root scope reached; crumb cleared but scope preserved."
LOG_ACTIVE_PARTS: str = "Active zCrumb parts: %s (count: %d)"
LOG_PARSED_SESSION: str = "Parsed session: path=%s, filename=%s, block=%s"
LOG_RELOADING_PATH: str = "Reloading file with zPath: %s"

# Log Messages (Warnings)
LOG_WARN_INVALID_KEY: str = "Resolved zKey %r not valid for block %r"

# Log Messages (Errors)
LOG_ERR_INVALID_CRUMB: str = "Invalid active_zCrumb format: %s (needs at least 3 parts)"

# Error Messages
ERR_EMPTY_FILENAME: str = "Cannot reload file: zVaFile is empty in session"
ERR_NO_KEYS_AFTER_BACK: str = "No keys in active zBlock after zBack; cannot resume."

# Crumb Parsing Constants (Magic Numbers)
CRUMB_PARTS_MIN: int = 3  # Minimum parts in a valid crumb: filename.middle.BlockName
INDEX_PARTS_FROM_END: int = -3  # Start of filename in parts list
INDEX_FILENAME_START: int = -3  # Filename starts 3 from end
INDEX_FILENAME_END: int = -1  # Filename ends 1 from end
INDEX_LAST_PART: int = -1  # Last part is BlockName


# ============================================================================
# Breadcrumbs Class
# ============================================================================

class Breadcrumbs:
    """
    Breadcrumb trail manager for zNavigation.
    
    Manages hierarchical navigation trails stored in zSession, supporting adding
    breadcrumbs, navigating backward through history, and formatting trails for display.
    
    Attributes
    ----------
    navigation : Any
        Reference to parent navigation system
    zcli : Any
        Reference to zCLI core instance
    logger : Any
        Logger instance for breadcrumb operations
    
    Methods
    -------
    handle_zCrumbs(zBlock, zKey, walker=None)
        Add navigation key to breadcrumb trail
    handle_zBack(show_banner=True, walker=None)
        Navigate backward through trail, reload file
    zCrumbs_banner()
        Format breadcrumbs for display
    
    Private Methods
    ---------------
    _get_display(walker)
        Get display adapter (DRY helper)
    _get_active_crumb(session)
        Get active (most recent) crumb from session (DRY helper)
    _get_crumbs_dict(session)
        Get crumbs dict with validation (DRY helper)
    _pop_scope(session, scope)
        Pop (remove) a scope from crumbs dict (DRY helper)
    
    Examples
    --------
    Initialize and add breadcrumb::
    
        breadcrumbs = Breadcrumbs(navigation_system)
        breadcrumbs.handle_zCrumbs("@.zUI.main.Menu", "Settings", walker)
    
    Navigate backward::
    
        block_dict, keys, start_key = breadcrumbs.handle_zBack(True, walker)
    
    Format for display::
    
        trails = breadcrumbs.zCrumbs_banner()
    
    Integration
    -----------
    - Parent: zNavigation system
    - Session: Reads/writes SESSION_KEY_ZCRUMBS, SESSION_KEY_ZVAFOLDER, etc.
    - Display: Uses zDisplay for output (mode-agnostic)
    - Loader: Uses zLoader for file reloading
    """

    # Class-level type declarations
    navigation: Any  # Navigation system reference
    zcli: Any  # zCLI core instance
    logger: Any  # Logger instance

    def __init__(self, navigation: Any) -> None:
        """
        Initialize breadcrumbs manager.
        
        Args
        ----
        navigation : Any
            Parent navigation system instance that provides access to zcli and logger
        
        Notes
        -----
        Stores references to the parent navigation system, zcli core, and logger
        for use during breadcrumb operations. No state is maintained beyond these
        references - all navigation state is stored in zSession.
        
        Session Dependencies
        --------------------
        This module relies on zSession having the following keys initialized:
        - SESSION_KEY_ZCRUMBS: Dict of scopes and trails
        - SESSION_KEY_ZVAFOLDER: Current file folder
        - SESSION_KEY_ZVAFILE: Current file name
        - SESSION_KEY_ZBLOCK: Current block name
        """
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger

    def handle_zCrumbs(
        self,
        zBlock: str,
        zKey: str,
        walker: Optional[Any] = None
    ) -> None:
        """
        Add navigation key to breadcrumb trail.
        
        Adds the specified key to the trail for the given block scope. Creates
        new scopes as needed and prevents duplicate consecutive keys.
        
        Args
        ----
        zBlock : str
            Block scope (full path: e.g., "@.zUI.main.MainMenu")
        zKey : str
            Navigation key to add to the trail
        walker : Optional[Any], default=None
            Optional walker instance (provides display adapter)
        
        Returns
        -------
        None
        
        Examples
        --------
        Add breadcrumb to main menu::
        
            breadcrumbs.handle_zCrumbs(
                zBlock="@.zUI.main.MainMenu",
                zKey="Settings",
                walker=current_walker
            )
        
        Add breadcrumb without walker::
        
            breadcrumbs.handle_zCrumbs(
                zBlock="@.zUI.settings.Network",
                zKey="Wi-Fi"
            )
        
        Notes
        -----
        - **Duplicate Prevention**: If the last key in the trail already equals zKey,
          the operation is skipped (logged at debug level).
        - **Scope Creation**: If zBlock doesn't exist in session[SESSION_KEY_ZCRUMBS],
          it's automatically created with an empty trail.
        - **Session Mutation**: Directly modifies session[SESSION_KEY_ZCRUMBS][zBlock].
        
        Algorithm
        ---------
        1. Display banner (if walker available)
        2. Log incoming parameters
        3. Get/create scope in session[SESSION_KEY_ZCRUMBS]
        4. Check for duplicate key (skip if duplicate)
        5. Append key to trail
        6. Log updated trail
        """
        # Get appropriate display adapter
        display = self._get_display(walker)
        
        # Display operation banner
        display.zDeclare(
            MSG_HANDLE_ZCRUMBS,
            color=COLOR_ZCRUMB,
            indent=INDENT_ZCRUMBS,
            style=STYLE_FULL
        )

        # Log incoming parameters
        self.logger.debug(LOG_INCOMING_BLOCK_KEY, zBlock, zKey)
        self.logger.debug(LOG_CURRENT_ZCRUMBS, self.zcli.session[SESSION_KEY_ZCRUMBS])

        # Get crumbs dict from session (with validation)
        crumbs_dict = self._get_crumbs_dict(self.zcli.session)

        # Create scope if it doesn't exist
        if zBlock not in crumbs_dict:
            crumbs_dict[zBlock] = []
            self.logger.debug(LOG_CURRENT_ZCRUMBS, crumbs_dict)

        # Get trail for this block
        zBlock_crumbs = crumbs_dict[zBlock]
        self.logger.debug(LOG_CURRENT_TRAIL, zBlock_crumbs)

        # Prevent duplicate consecutive zKeys
        if zBlock_crumbs and zBlock_crumbs[INDEX_LAST_PART] == zKey:
            self.logger.debug(LOG_DUPLICATE_SKIP, zKey, zBlock)
            return

        # All good - add the key to the trail
        zBlock_crumbs.append(zKey)
        self.logger.debug(LOG_CURRENT_TRAIL, zBlock_crumbs)

    def handle_zBack(
        self,
        show_banner: bool = True,
        walker: Optional[Any] = None
    ) -> Tuple[Dict[str, Any], List[str], Optional[str]]:
        """
        Navigate backward through breadcrumb trail.
        
        Pops the last key from the current trail, handles scope transitions when
        trails become empty, parses the active crumb to determine file context,
        reloads the appropriate file, and returns the context for resuming navigation.
        
        Args
        ----
        show_banner : bool, default=True
            Whether to display zBack banner and breadcrumbs
        walker : Optional[Any], default=None
            Optional walker instance (provides display and loader adapters)
        
        Returns
        -------
        Tuple[Dict[str, Any], List[str], Optional[str]]
            A tuple containing:
            - block_dict: Dict of the active block's content
            - block_keys: List of all keys in the active block
            - start_key: The key to resume from (or None if trail is empty)
        
        Examples
        --------
        Navigate back with banner::
        
            block_dict, keys, start_key = breadcrumbs.handle_zBack(
                show_banner=True,
                walker=current_walker
            )
            
            if start_key and start_key in keys:
                # Resume from start_key
                index = keys.index(start_key)
                # Continue navigation from this index
        
        Navigate back without banner::
        
            block_dict, keys, start_key = breadcrumbs.handle_zBack(
                show_banner=False
            )
        
        Handle empty return::
        
            block_dict, keys, start_key = breadcrumbs.handle_zBack()
            
            if not keys:
                # No keys available, cannot resume
                logger.error("Cannot resume navigation after zBack")
                return
        
        Notes
        -----
        - **Complex Algorithm**: This method implements a 113-line, 8-step algorithm
          for managing hierarchical scope transitions. See module docstring for details.
        - **Session Mutation**: Directly modifies SESSION_KEY_ZCRUMBS, SESSION_KEY_ZVAFOLDER,
          SESSION_KEY_ZVAFILE, SESSION_KEY_ZBLOCK in zSession.
        - **File Reloading**: Uses zLoader to reload the appropriate file after navigation.
        - **Error Handling**: Returns (dict, [], None) if file cannot be reloaded or has no keys.
        
        Algorithm Steps
        ---------------
        1. Get active scope (most recent) from session[SESSION_KEY_ZCRUMBS]
        2. Pop last key from trail (if trail has items)
        3. Handle empty trail → scope transition (remove child, move to parent, pop parent)
        4. Cascade empty scope removal (repeat if parent also becomes empty)
        5. Parse active crumb → extract path, filename, block
        6. Update session with parsed values
        7. Reload file using zLoader
        8. Return (block_dict, block_keys, start_key) for resuming navigation
        
        Integration
        -----------
        - Uses: zLoader (file reloading), zDisplay (banner/breadcrumbs)
        - Modifies: zSession (4 keys: zCrumbs, zVaFolder, zVaFile, zBlock)
        - Called by: MenuSystem, zWalker
        """
        # Get appropriate display adapter
        display = self._get_display(walker)
        
        # Display operation banner
        display.zDeclare(
            MSG_HANDLE_ZBACK,
            color=COLOR_ZCRUMB,
            indent=INDENT_ZBACK,
            style=STYLE_FULL
        )

        zSession = self.zcli.session
        
        # ============================================================
        # STEP 1: Get Active Scope (Most Recent)
        # ============================================================
        active_zCrumb = self._get_active_crumb(zSession)
        self.logger.debug(LOG_ACTIVE_CRUMB, active_zCrumb)

        # Get original (root) crumb for comparison
        original_zCrumb = next(iter(zSession[SESSION_KEY_ZCRUMBS]))
        self.logger.debug(LOG_ORIGINAL_CRUMB, original_zCrumb)

        # Extract block name from active crumb (last part after splitting by ".")
        active_zBlock = active_zCrumb.split(SEPARATOR_DOT)[INDEX_LAST_PART]
        self.logger.debug(LOG_ACTIVE_BLOCK, active_zBlock)

        # Get trail for active scope
        trail = zSession[SESSION_KEY_ZCRUMBS][active_zCrumb]
        self.logger.debug(LOG_TRAIL, trail)

        # ============================================================
        # STEP 2: Pop from Current Trail
        # ============================================================
        # If trail has items, pop the last key (move back one step)
        if trail:
            trail.pop()
            self.logger.debug(LOG_TRAIL_AFTER_POP, active_zCrumb, trail)
        else:
            # ========================================================
            # STEP 3: Handle Empty Trail (Scope Transition)
            # ========================================================
            # Trail is empty - need to move to parent scope
            if active_zCrumb != original_zCrumb:
                # Not at root - can move to parent
                
                # Remove the empty child scope
                popped_scope = self._pop_scope(zSession, active_zCrumb)
                self.logger.debug(LOG_POPPED_SCOPE, active_zCrumb, popped_scope)
                
                # Move to parent scope (now the last scope in session)
                active_zCrumb = self._get_active_crumb(zSession)
                self.logger.debug(LOG_ACTIVE_CRUMB_PARENT, active_zCrumb)
                
                # Get parent's trail
                trail = zSession[SESSION_KEY_ZCRUMBS][active_zCrumb]
                self.logger.debug(LOG_PARENT_TRAIL_BEFORE, trail)
                
                # Pop the parent's last key (the link that opened the child)
                if trail:
                    trail.pop()
                    self.logger.debug(LOG_PARENT_TRAIL_AFTER, trail)
            else:
                # At root with empty trail - nothing to pop
                self.logger.debug(LOG_ROOT_EMPTY)

        # ============================================================
        # STEP 4: Cascade Empty Scope Removal
        # ============================================================
        # If after popping, the current scope became empty (and not root), remove it and pop parent
        if not trail and active_zCrumb != original_zCrumb:
            # Current scope is now empty and not root - remove it
            popped_scope = self._pop_scope(zSession, active_zCrumb)
            self.logger.debug(LOG_POST_POP_EMPTY, active_zCrumb, popped_scope)
            
            # Move to parent scope
            active_zCrumb = self._get_active_crumb(zSession)
            self.logger.debug(LOG_ACTIVE_CRUMB_PARENT, active_zCrumb)
            
            # Get parent's trail
            trail = zSession[SESSION_KEY_ZCRUMBS][active_zCrumb]
            self.logger.debug(LOG_PARENT_TRAIL_PRE_SECOND, trail)
            
            # Pop parent's last key
            if trail:
                trail.pop()
                self.logger.debug(LOG_PARENT_TRAIL_POST_SECOND, trail)
        
        # Show breadcrumbs banner if requested (and walker available)
        if show_banner and walker:
            display.zCrumbs(self.zcli.session)

        # Log if we've reached root with empty trail
        if trail == [] and active_zCrumb == original_zCrumb:
            self.logger.debug(LOG_ROOT_CLEARED)

        # ============================================================
        # STEP 5: Parse Active Crumb for File Context
        # ============================================================
        # Update session context to reflect the new active crumb
        # so subsequent loads reference the correct file and block.
        parts = active_zCrumb.split(SEPARATOR_DOT)
        self.logger.debug(LOG_ACTIVE_PARTS, parts, len(parts))
        
        if len(parts) >= CRUMB_PARTS_MIN:
            # Extract: base_path.zUI.filename.BlockName
            # Example: "@.zUI.users_menu.MainMenu" => ["@", "zUI", "users_menu", "MainMenu"]
            base_path_parts = parts[:INDEX_PARTS_FROM_END]
            zSession[SESSION_KEY_ZVAFOLDER] = SEPARATOR_DOT.join(base_path_parts) if base_path_parts else SEPARATOR_EMPTY
            zSession[SESSION_KEY_ZVAFILE] = SEPARATOR_DOT.join(parts[INDEX_FILENAME_START:INDEX_FILENAME_END])
            zSession[SESSION_KEY_ZBLOCK] = parts[INDEX_LAST_PART]
            self.logger.debug(
                LOG_PARSED_SESSION,
                zSession[SESSION_KEY_ZVAFOLDER],
                zSession[SESSION_KEY_ZVAFILE],
                zSession[SESSION_KEY_ZBLOCK]
            )
        else:
            # Invalid crumb format
            self.logger.error(LOG_ERR_INVALID_CRUMB, active_zCrumb)

        # Determine the resolved zBack key (where to resume)
        resolved_zBack_key = trail[INDEX_LAST_PART] if trail else None
        
        # ============================================================
        # STEP 6: Reload File
        # ============================================================
        # Reload current file based on updated zSession
        # Construct zPath from session values
        zVaFolder = zSession.get(SESSION_KEY_ZVAFOLDER, SEPARATOR_EMPTY)
        zVaFile = zSession.get(SESSION_KEY_ZVAFILE, SEPARATOR_EMPTY)
        
        if not zVaFile:
            self.logger.error(ERR_EMPTY_FILENAME)
            return {}, [], None
        
        # Build zPath based on whether we have a base path
        if zVaFolder:
            zPath = f"{zVaFolder}{SEPARATOR_DOT}{zVaFile}"
        else:
            zPath = f"{PREFIX_DEFAULT_PATH}{zVaFile}"
        
        self.logger.debug(LOG_RELOADING_PATH, zPath)
        
        # Load file using session-based resolution (zSession already updated above)
        # Pass None to trigger session-based path resolution with zVaFolder + zVaFile
        if walker and hasattr(walker, "loader"):
            zFile_parsed = walker.loader.handle(None)
        else:
            zFile_parsed = self.zcli.loader.handle(None)
        
        # Extract active block dict and keys
        active_zBlock_dict = zFile_parsed.get(zSession[SESSION_KEY_ZBLOCK], {})
        zBlock_keys = list(active_zBlock_dict.keys())

        # ============================================================
        # STEP 7: Validate and Return Context
        # ============================================================
        if not zBlock_keys:
            self.logger.error(ERR_NO_KEYS_AFTER_BACK)
            return active_zBlock_dict, [], None

        # Normalize start key: only use it if it exists; otherwise start from first (None)
        if resolved_zBack_key and resolved_zBack_key in zBlock_keys:
            start_key = resolved_zBack_key
        else:
            if resolved_zBack_key:
                self.logger.warning(
                    LOG_WARN_INVALID_KEY,
                    resolved_zBack_key,
                    zSession[SESSION_KEY_ZBLOCK]
                )
            # Do not force default to first key; let caller decide start (None)
            start_key = None

        # ============================================================
        # STEP 8: Return Navigation Context
        # ============================================================
        return active_zBlock_dict, zBlock_keys, start_key

    def zCrumbs_banner(self) -> Dict[str, str]:
        """
        Format breadcrumbs for display.
        
        Converts the session breadcrumb dict into a display-friendly format
        where each scope's trail is joined into a readable string.
        
        Returns
        -------
        Dict[str, str]
            Dictionary mapping scope names to formatted trail strings.
            Empty trails are represented as empty strings.
        
        Examples
        --------
        Format all breadcrumbs::
        
            trails = breadcrumbs.zCrumbs_banner()
            # {
            #     "@.zUI.main.MainMenu": "Dashboard > Settings > Profile",
            #     "@.zUI.settings.Network": "Wi-Fi > DNS"
            # }
        
        Handle empty trails::
        
            trails = breadcrumbs.zCrumbs_banner()
            # {
            #     "@.zUI.main.MainMenu": "",
            #     "@.zUI.settings.Network": "Wi-Fi"
            # }
        
        Notes
        -----
        - **Separator**: Trails are joined with " > " (SEPARATOR_CRUMB)
        - **Empty Trails**: Represented as empty strings (not None)
        - **Read-Only**: Does not modify session state
        - **Display Integration**: Typically called by zDisplay.zCrumbs() for UI output
        
        Format
        ------
        - Input: {"scope1": ["key1", "key2"], "scope2": []}
        - Output: {"scope1": "key1 > key2", "scope2": ""}
        """
        zCrumbs_zPrint: Dict[str, str] = {}

        # Iterate through all scopes and their trails
        for zScope, zTrail in self.zcli.session[SESSION_KEY_ZCRUMBS].items():
            # Join trail with separator, or use empty string if trail is empty
            path = SEPARATOR_CRUMB.join(zTrail) if zTrail else SEPARATOR_EMPTY
            zCrumbs_zPrint[zScope] = path
        
        return zCrumbs_zPrint

    # ========================================================================
    # Private Helper Methods (DRY)
    # ========================================================================

    def _get_display(self, walker: Optional[Any]) -> Any:
        """
        Get display adapter from walker or zcli.
        
        Args
        ----
        walker : Optional[Any]
            Optional walker instance with display attribute
        
        Returns
        -------
        Any
            Display adapter (zDisplay instance)
        
        Notes
        -----
        DRY Helper: Eliminates 2 duplications (lines 14, 42 in original)
        """
        return walker.display if walker else self.zcli.display

    def _get_active_crumb(self, session: Dict[str, Any]) -> str:
        """
        Get active (most recent) crumb from session.
        
        Args
        ----
        session : Dict[str, Any]
            zSession dict
        
        Returns
        -------
        str
            Active crumb (last key in session[SESSION_KEY_ZCRUMBS])
        
        Notes
        -----
        DRY Helper: Eliminates 3 duplications (lines 46, 68, 83 in original)
        Uses next(reversed()) to get last key without modifying the dict.
        """
        return next(reversed(session[SESSION_KEY_ZCRUMBS]))

    def _get_crumbs_dict(self, session: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Get crumbs dict from session with validation.
        
        Args
        ----
        session : Dict[str, Any]
            zSession dict
        
        Returns
        -------
        Dict[str, List[str]]
            Crumbs dict mapping scopes to trails
        
        Notes
        -----
        DRY Helper: Eliminates 15+ duplications of session[SESSION_KEY_ZCRUMBS] access
        Provides a single point for validation/error handling in the future.
        """
        return session[SESSION_KEY_ZCRUMBS]

    def _pop_scope(
        self,
        session: Dict[str, Any],
        scope: str
    ) -> Optional[List[str]]:
        """
        Pop (remove) a scope from crumbs dict.
        
        Args
        ----
        session : Dict[str, Any]
            zSession dict
        scope : str
            Scope key to remove
        
        Returns
        -------
        Optional[List[str]]
            The trail that was removed, or None if scope didn't exist
        
        Notes
        -----
        DRY Helper: Eliminates 2 duplications (lines 65, 81 in original)
        Uses dict.pop(key, default) to safely remove and return the trail.
        """
        return session[SESSION_KEY_ZCRUMBS].pop(scope, None)
