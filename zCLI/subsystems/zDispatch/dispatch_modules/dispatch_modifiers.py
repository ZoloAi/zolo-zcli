# zCLI/subsystems/zDispatch/dispatch_modules/dispatch_modifiers.py

"""
Modifier Processor for zDispatch Subsystem.

This module provides the ModifierProcessor class, which handles prefix and suffix
modifiers that alter command behavior within the zCLI framework. Modifiers enable
powerful command routing patterns like bounce-back navigation, menu creation, 
required actions, and anchor points.

Architecture:
    The ModifierProcessor follows a detection-and-processing pattern:
    
    1. Detection Phase:
       - check_prefix(): Detects prefix modifiers (^ ~)
       - check_suffix(): Detects suffix modifiers (* !)
    
    2. Processing Phase:
       - process(): Executes modifier-specific behavior
       - Delegates to CommandLauncher for action execution
       - Handles mode-specific return values (Terminal vs. Bifrost)

Modifier Semantics:
    PREFIX MODIFIERS:
    - ^ (caret): "Bounce Back" - Execute action, then return to previous menu
      * Terminal/Walker mode: Returns "zBack" for navigation
      * Bifrost mode: Returns actual result for API consumption
      * Supports ^key resolution from zUI files
    
    - ~ (tilde): "Anchor" - Disable back navigation (used with *)
      * Modifies menu behavior: allow_back=False
      * Creates "anchored" menus with no escape option
      * Often used for required workflows
    
    SUFFIX MODIFIERS:
    - * (asterisk): "Menu" - Create menu from horizontal data
      * Routes to zNavigation.create()
      * Respects ~ anchor modifier
      * Works for both walker and non-walker contexts
    
    - ! (exclamation): "Required" - Retry until success
      * Enters retry loop until action returns truthy result
      * User can abort with "stop" input
      * Useful for validation and mandatory steps

Mode-Specific Behavior:
    Terminal/Walker Mode:
        - ^ modifier: Returns "zBack" for menu navigation
        - All modifiers: Standard navigation flow
        - User interaction: Synchronous input for ! modifier
    
    Bifrost Mode:
        - ^ modifier: Returns actual result (no navigation)
        - All modifiers: API-oriented returns
        - User interaction: Asynchronous input patterns

Forward Dependencies:
    This module integrates with 3 subsystems that will be refactored in future weeks:
    
    - zNavigation (Week 6.7): create() method for menu display
    - zLoader (Week 6.9): handle() method for zUI file loading (^key resolution)
    - CommandLauncher (Week 6.6.2): launch() method for action execution ✅ (COMPLETE)

Usage Examples:
    # Bounce back modifier (^): Execute and return
    modifiers = ["^"]
    result = processor.process(modifiers, "^save", {"zFunc": "save_data"}, context, walker)
    # Terminal: Returns "zBack"
    # Bifrost: Returns save_data result
    
    # Menu modifier (*): Create menu
    modifiers = ["*"]
    result = processor.process(modifiers, "menu*", menu_dict, context, walker)
    # Creates menu via zNavigation.create()
    
    # Anchor modifier (~): Disable back in menu
    modifiers = ["~", "*"]
    result = processor.process(modifiers, "~menu*", menu_dict, context, walker)
    # Creates anchored menu (no back button)
    
    # Required modifier (!): Retry until success
    modifiers = ["!"]
    result = processor.process(modifiers, "validate!", {"zFunc": "validate"}, context, walker)
    # Retries until validate() returns True
    
    # Detection methods
    prefix_mods = processor.check_prefix("^action")  # Returns ["^"]
    suffix_mods = processor.check_suffix("menu*")    # Returns ["*"]
    combo_mods = processor.check_prefix("~menu*") + processor.check_suffix("~menu*")
    # Returns ["~", "*"]

Thread Safety:
    - Relies on thread-safe logger and display instances from zCLI
    - Mode detection reads from context dict (passed as parameter)
    - No internal state mutation during processing

Integration with zSession:
    - Mode detection: Uses SESSION_KEY_ZMODE from context
    - Context passing: All handlers accept optional context parameter
    - Session access: Via self.zcli.session (centralized session management)

zAuth Integration:
    - Implicit via context: Authentication state passed through context dict
    - No direct zAuth calls: Action handlers are responsible for auth checks
    - Mode-specific returns: Bifrost mode may return different data structures

Constants:
    All magic strings are replaced with module constants to improve maintainability
    and reduce the risk of typos. See module-level constants below for complete list.
"""

from typing import Any, Optional, Dict, List, Union

# Import zConfig session constants for modernization
# TODO: Week 6.2 (zConfig) - Use SESSION_KEY_ZMODE instead of "mode" raw string
# Note: Temporarily using raw "mode" until zConfig constants are finalized
# from zCLI.subsystems.zConfig.config_modules.config_constants import SESSION_KEY_ZMODE

# ============================================================================
# MODULE CONSTANTS - Modifier Symbols
# ============================================================================

MOD_CARET = "^"           # Bounce back: Execute action → return to menu
MOD_TILDE = "~"           # Anchor: Disable back navigation (used with *)
MOD_ASTERISK = "*"        # Menu: Create menu from horizontal data
MOD_EXCLAMATION = "!"     # Required: Retry until success

# ============================================================================
# MODULE CONSTANTS - Modifier Sets
# ============================================================================

PREFIX_MODIFIERS = [MOD_CARET, MOD_TILDE]
SUFFIX_MODIFIERS = [MOD_EXCLAMATION, MOD_ASTERISK]
ALL_MODIFIERS = PREFIX_MODIFIERS + SUFFIX_MODIFIERS

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
NAV_ZBACK = "zBack"

# ============================================================================
# MODULE CONSTANTS - Display Labels (zDeclare messages)
# ============================================================================

LABEL_PROCESS_MODIFIERS = "Process Modifiers"
LABEL_ZBOUNCE = "zBounce (execute then back)"
LABEL_ZREQUIRED = "zRequired"
LABEL_ZREQUIRED_RETURN = "zRequired Return"

# ============================================================================
# MODULE CONSTANTS - Log Prefixes
# ============================================================================

LOG_PREFIX_MODIFIERS = "[MODIFIERS]"
LOG_MSG_PARSING_PREFIX = "Parsing prefix modifiers for key: %s"
LOG_MSG_PARSING_SUFFIX = "Parsing suffix modifiers for key: %s"
LOG_MSG_PRE_MODIFIERS = "pre_modifiers: %s"
LOG_MSG_SUF_MODIFIERS = "suf_modifiers: %s"
LOG_MSG_RESOLVED = "Resolved modifiers: %s on key: %s"
LOG_MSG_MENU_DETECTED = "* Modifier detected for %s - invoking menu (anchor=%s)"
LOG_MSG_ZBOUNCE_RESULT = "zBounce action result: %s"
LOG_MSG_ZBOUNCE_CONTEXT = "zBounce context: %s"
LOG_MSG_ZBOUNCE_MODE_CHECK = "zBounce mode check: context=%s, mode=%s"
LOG_MSG_BIFROST_DETECTED = "zBifrost mode detected - returning actual result"
LOG_MSG_REQUIRED_STEP = "Required step: %s"
LOG_MSG_REQUIRED_RESULTS = "zRequired results: %s"
LOG_MSG_REQUIREMENT_NOT_SATISFIED = "Requirement '%s' not satisfied. Retrying..."
LOG_MSG_REQUIREMENT_SATISFIED = "Requirement '%s' satisfied."
LOG_MSG_LOOKING_UP_KEY = f"{LOG_PREFIX_MODIFIERS} Looking up key: '%s' in block_dict keys: %s"
LOG_MSG_RESOLVED_KEY = f"{LOG_PREFIX_MODIFIERS} Resolved ^key '%s' to horizontal value: %s"
LOG_MSG_COULD_NOT_LOAD = "Could not load UI block %s from %s"
LOG_MSG_NO_ZVAFILE = "No zVaFile in zspark_obj"
LOG_MSG_CANNOT_RESOLVE = "Cannot resolve ^key without walker context"

# ============================================================================
# MODULE CONSTANTS - Prompt Text
# ============================================================================

PROMPT_REQUIRED_CONTINUE = "Try again? (press Enter to retry, 'n' or 'stop' to go back): "

# ============================================================================
# MODULE CONSTANTS - User Input
# ============================================================================

INPUT_STOP = "stop"

# ============================================================================
# MODULE CONSTANTS - Default Values
# ============================================================================

DEFAULT_ZBLOCK = "root"
DEFAULT_INDENT_PROCESS = 2
DEFAULT_INDENT_MODIFIER = 3

# ============================================================================
# MODULE CONSTANTS - Style Values
# ============================================================================

STYLE_SINGLE = "single"
STYLE_WAVY = "~"


class ModifierProcessor:
    """
    Modifier processor for zDispatch subsystem.
    
    Handles prefix and suffix modifiers that alter command behavior, including
    bounce-back navigation (^), menu creation (*), required actions (!), and
    anchor points (~).
    
    Attributes:
        dispatch: Parent zDispatch instance
        zcli: Root zCLI instance
        logger: Logger instance from zCLI
    
    Methods:
        check_prefix(): Detect prefix modifiers (^ ~)
        check_suffix(): Detect suffix modifiers (* !)
        process(): Execute modifier-specific behavior
        
        Helper methods (DRY):
        _is_bifrost_mode(): Check if context is in Bifrost mode
        _display_modifier(): Display modifier label with consistent styling
        _resolve_ui_key(): Resolve ^key from zUI file
    
    Integration:
        - zConfig: Uses session constants (TODO: SESSION_KEY_ZMODE)
        - zDisplay: UI output via zDeclare() and read_string()
        - zSession: Mode detection via context dict
        - Forward dependencies: 3 subsystems (see module docstring)
    """
    
    # Class-level type declarations
    dispatch: Any  # zDispatch instance
    zcli: Any  # zCLI instance
    logger: Any  # Logger instance

    def __init__(self, dispatch: Any) -> None:
        """
        Initialize modifier processor with parent dispatch instance.
        
        Args:
            dispatch: Parent zDispatch instance providing access to zCLI and logger
        
        Example:
            processor = ModifierProcessor(dispatch)
        """
        self.dispatch = dispatch
        self.zcli = dispatch.zcli
        self.logger = dispatch.logger

    # ========================================================================
    # PUBLIC METHODS - Modifier Detection
    # ========================================================================

    def check_prefix(self, zKey: str) -> List[str]:
        """
        Check for prefix modifiers at the start of a key.
        
        Detects the following prefix modifiers:
        - ^ (caret): Bounce back modifier
        - ~ (tilde): Anchor modifier
        
        Args:
            zKey: Key string to check for prefix modifiers
        
        Returns:
            List of detected prefix modifier symbols (may be empty)
        
        Examples:
            # Single prefix
            check_prefix("^action")  # Returns ["^"]
            check_prefix("~menu*")   # Returns ["~"]
            
            # No prefix
            check_prefix("action")   # Returns []
            check_prefix("menu*")    # Returns []
        
        Notes:
            - Multiple prefixes can be detected (though rare in practice)
            - Detection is order-independent
            - Uses module-level PREFIX_MODIFIERS constant
        """
        self.logger.framework.debug(LOG_MSG_PARSING_PREFIX, zKey)
        pre_modifiers = [sym for sym in PREFIX_MODIFIERS if zKey.startswith(sym)]
        self.logger.framework.debug(LOG_MSG_PRE_MODIFIERS, pre_modifiers)
        return pre_modifiers

    def check_suffix(self, zKey: str) -> List[str]:
        """
        Check for suffix modifiers at the end of a key.
        
        Detects the following suffix modifiers:
        - ! (exclamation): Required modifier
        - * (asterisk): Menu modifier
        
        Args:
            zKey: Key string to check for suffix modifiers
        
        Returns:
            List of detected suffix modifier symbols (may be empty)
        
        Examples:
            # Single suffix
            check_suffix("validate!")  # Returns ["!"]
            check_suffix("menu*")      # Returns ["*"]
            
            # No suffix
            check_suffix("action")     # Returns []
            check_suffix("^action")    # Returns []
        
        Notes:
            - Multiple suffixes can be detected (though rare in practice)
            - Detection is order-independent
            - Uses module-level SUFFIX_MODIFIERS constant
        """
        self.logger.framework.debug(LOG_MSG_PARSING_SUFFIX, zKey)
        suf_modifiers = [sym for sym in SUFFIX_MODIFIERS if zKey.endswith(sym)]
        self.logger.framework.debug(LOG_MSG_SUF_MODIFIERS, suf_modifiers)
        return suf_modifiers

    # ========================================================================
    # PUBLIC METHODS - Modifier Processing
    # ========================================================================

    def process(
        self,
        modifiers: List[str],
        zKey: str,
        zHorizontal: Any,
        context: Optional[Dict[str, Any]] = None,
        walker: Optional[Any] = None
    ) -> Optional[Union[str, Any]]:
        """
        Process modifiers and execute appropriate behavior.
        
        Handles all four modifier types with mode-specific behavior:
        - * (menu): Create menu via zNavigation.create()
        - ^ (bounce): Execute action → return "zBack" (Terminal) or result (Bifrost)
        - ! (required): Retry loop until success, user can abort
        - No modifiers: Pass through to launcher
        
        Args:
            modifiers: List of detected modifier symbols (from check_prefix/check_suffix)
            zKey: Original key with modifiers (for logging/resolution)
            zHorizontal: Command/data to execute (str, dict, or other format)
            context: Optional context dict with mode and session metadata
            walker: Optional walker instance for navigation and display
        
        Returns:
            Modifier-specific result:
            - * modifier: Menu navigation result (from zNavigation.create)
            - ^ modifier: "zBack" (Terminal) or action result (Bifrost)
            - ! modifier: Action result (after successful retry)
            - No modifiers: Action result (from launcher)
            - None: If execution fails or is aborted
        
        Examples:
            # Menu modifier (*)
            result = process(["*"], "menu*", menu_dict, context, walker)
            # Creates menu and returns navigation result
            
            # Bounce modifier (^)
            result = process(["^"], "^save", {"zFunc": "save"}, context, walker)
            # Terminal: Returns "zBack" after executing save
            # Bifrost: Returns save result directly
            
            # Anchor + Menu (~*)
            result = process(["~", "*"], "~menu*", menu_dict, context, walker)
            # Creates anchored menu (no back button)
            
            # Required modifier (!)
            result = process(["!"], "validate!", {"zFunc": "validate"}, context, walker)
            # Retries until validate returns True (or user types "stop")
            
            # No modifiers
            result = process([], "action", {"zFunc": "action"}, context, walker)
            # Direct pass-through to launcher
        
        Notes:
            - Uses walker.display if available, otherwise zcli.display
            - Mode detection via context[KEY_MODE] (TODO: Use SESSION_KEY_ZMODE)
            - Priority order: * (menu) > ^ (bounce) > ! (required) > pass-through
            - Modifier combinations: ~* is common, others are rare
        
        TODO: Week 6.7 (zNavigation) - Verify navigation.create() signature after refactor
        TODO: Week 6.9 (zLoader) - Verify loader.handle() signature after refactor
        """
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display

        self._display_modifier(display, LABEL_PROCESS_MODIFIERS, DEFAULT_INDENT_PROCESS)

        self.logger.framework.debug(LOG_MSG_RESOLVED, modifiers, zKey)

        # Priority 1: Menu modifier (*)
        if MOD_ASTERISK in modifiers:
            # Menu modifier - create menu via zNavigation
            is_anchor = MOD_TILDE in modifiers
            self.logger.debug(LOG_MSG_MENU_DETECTED, zKey, is_anchor)

            # RBAC filtering for navbar menus (dynamic, re-evaluated on every render)
            # Check if this is a navbar key (~zNavBar*) and apply RBAC filtering
            if zKey.startswith("~zNavBar"):
                self.logger.framework.debug(f"[Dispatch] Applying dynamic RBAC filtering for navbar: {zKey}")
                # Filter the navbar items based on current authentication state
                # This extracts clean item names (strings) from mixed list of strings and dicts
                filtered_items = self.zcli.navigation._filter_navbar_by_rbac(zHorizontal)
                self.logger.framework.info(f"[Dispatch] Navbar filtered: {len(zHorizontal)} → {len(filtered_items)} items")
                # Add delta prefix ($) to filtered items for intra-file navigation
                zHorizontal = [f"${item}" for item in filtered_items]

            # Note: Signature verified during Week 6.7.8 refactor - perfect alignment ✅
            result = self.zcli.navigation.create(
                zHorizontal, 
                allow_back=not is_anchor, 
                walker=walker
            )

            # If menu returns a dict (e.g., {zLink: "..."} from $ delta links),
            # re-dispatch it through the command launcher to handle navigation
            if isinstance(result, dict):
                self.logger.framework.debug(f"[Menu] Returned dict, re-dispatching: {result}")
                # Re-dispatch the dict result (e.g., zLink navigation)
                return self.dispatch.launcher.launch(result, context, walker)
            
            return result

        # Priority 2: Bounce modifier (^)
        if MOD_CARET in modifiers:
            # Execute action first, then return to previous menu
            self._display_modifier(display, LABEL_ZBOUNCE, DEFAULT_INDENT_MODIFIER)
            
            # If zHorizontal is still the key with prefix, we need to look it up in walker's UI
            if isinstance(zHorizontal, str) and zHorizontal.startswith(MOD_CARET):
                zHorizontal = self._resolve_ui_key(zHorizontal, walker)
            
            # Execute the action
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.framework.debug(LOG_MSG_ZBOUNCE_RESULT, result)
            
            # DEBUG: Log context to diagnose mode detection
            self.logger.framework.debug(LOG_MSG_ZBOUNCE_CONTEXT, context)
            self.logger.framework.debug(
                LOG_MSG_ZBOUNCE_MODE_CHECK, 
                context is not None, 
                context.get(KEY_MODE) if context else None
            )
            
            # Mode-specific return behavior
            if self._is_bifrost_mode(context):
                # Bifrost: Return actual result for API consumption
                self.logger.framework.debug(LOG_MSG_BIFROST_DETECTED)
                return result
            
            # Terminal/Walker: Return zBack for navigation
            return NAV_ZBACK

        # Priority 3: Required modifier (!)
        if MOD_EXCLAMATION in modifiers:
            self._display_modifier(display, LABEL_ZREQUIRED, DEFAULT_INDENT_MODIFIER)
            self.logger.framework.debug(LOG_MSG_REQUIRED_STEP, zKey)
            
            # Execute action and enter retry loop if needed
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.framework.debug(LOG_MSG_REQUIRED_RESULTS, result)
            
            # Mode-aware retry handling
            is_bifrost = self._is_bifrost_mode(context)
            
            if is_bifrost:
                # Bifrost mode: Frontend handles retry UI
                # Just return result (None = failure shown in browser, True/value = success)
                # The frontend will re-enable the form for user to retry
                if not result:
                    self.logger.info(f"[{MOD_EXCLAMATION}] Bifrost mode - gate failed, frontend will handle retry")
                else:
                    self.logger.info(f"[{MOD_EXCLAMATION}] Bifrost mode - gate passed")
                return result
            
            # Terminal mode: Backend handles retry loop with prompts
            while not result:
                # Check for shutdown signal (Ctrl+C/SIGTERM)
                if hasattr(self.zcli, '_shutdown_requested') and self.zcli._shutdown_requested:
                    self.logger.info(f"[{MOD_EXCLAMATION}] Shutdown requested, aborting retry loop for: {zKey}")
                    return None
                
                self.logger.warning(LOG_MSG_REQUIREMENT_NOT_SATISFIED, zKey)
                if walker:
                    try:
                        choice = display.read_string(PROMPT_REQUIRED_CONTINUE).strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        # Handle Ctrl+C during input prompt
                        self.logger.info(f"[{MOD_EXCLAMATION}] Interrupted during retry prompt for: {zKey}")
                        return None
                    
                    if choice in [INPUT_STOP, 'n', 'no']:
                        # User declined retry - return None to stop retrying without full exit
                        # This allows ^ (bounce-back) blocks to handle navigation properly
                        self.logger.framework.debug(f"[{MOD_EXCLAMATION}] User declined retry for: {zKey}")
                        return None
                result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            
            self.logger.framework.debug(LOG_MSG_REQUIREMENT_SATISFIED, zKey)
            self._display_modifier(display, LABEL_ZREQUIRED_RETURN, DEFAULT_INDENT_MODIFIER, style=STYLE_WAVY)
            return result

        # No modifiers: Pass through to launcher
        return self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)

    # ========================================================================
    # HELPER METHODS - DRY Refactoring
    # ========================================================================

    def _is_bifrost_mode(self, context: Optional[Dict[str, Any]]) -> bool:
        """
        Check if we're in Bifrost mode execution.
        
        Args:
            context: Optional context dict (not used, kept for backwards compatibility)
        
        Returns:
            True if session zMode is "zBifrost", False otherwise
        
        Example:
            if self._is_bifrost_mode(context):
                # Handle Bifrost-specific behavior
        
        Notes:
            - Mode is stored in zcli.session["zMode"], not context
            - Gracefully handles missing zMode (defaults to False/Terminal)
            - Case-sensitive mode comparison
        """
        # Check session for mode (not context - mode is session-level, not context-level)
        return self.zcli.session.get("zMode") == MODE_BIFROST

    def _display_modifier(
        self,
        display: Any,
        label: str,
        indent: int,
        style: str = STYLE_SINGLE
    ) -> None:
        """
        Display modifier label with consistent styling.
        
        Args:
            display: Display instance (walker.display or zcli.display)
            label: Modifier label to display
            indent: Indentation level (spaces)
            style: Display style (default: "single")
        
        Example:
            self._display_modifier(display, LABEL_ZBOUNCE, 3)
        
        Notes:
            - Uses parent dispatch color for consistency
            - Avoids repeated zDeclare calls with identical styling
            - Default style is STYLE_SINGLE ("single")
        """
        display.zDeclare(
            label,
            color=self.dispatch.mycolor,
            indent=indent,
            style=style
        )

    def _resolve_ui_key(self, zHorizontal: str, walker: Optional[Any]) -> Any:
        """
        Resolve ^key from zUI file (for bounce modifier).
        
        When a ^key is encountered, this method attempts to look up the actual
        command from the walker's zUI file. This enables cleaner YAML declarations
        where menu items can reference actions with ^ prefix.
        
        Args:
            zHorizontal: Key string starting with ^ (e.g., "^save")
            walker: Optional walker instance with zUI context
        
        Returns:
            Resolved horizontal value from zUI, or original zHorizontal if resolution fails
        
        Example:
            # In zUI file (root block):
            # save: {zFunc: save_data}
            
            zHorizontal = self._resolve_ui_key("^save", walker)
            # Returns: {zFunc: save_data}
        
        Notes:
            - Requires walker context (returns original if walker is None)
            - Loads zUI file via zLoader (Week 6.9)
            - Strips ^ prefix before lookup
            - Gracefully handles missing files/blocks/keys
        
        TODO: Week 6.9 (zLoader) - Verify loader.handle() signature after refactor
        """
        if walker:
            # Load the UI file to get the block dictionary
            zVaFile = self.zcli.zspark_obj.get(KEY_ZVAFILE)
            zBlock = self.zcli.zspark_obj.get(KEY_ZBLOCK, DEFAULT_ZBLOCK)
            
            if zVaFile:
                # TODO: Week 6.9 (zLoader) - Verify loader.handle() signature after refactor
                raw_zFile = self.zcli.loader.handle(zVaFile)
                if raw_zFile and zBlock in raw_zFile:
                    block_dict = raw_zFile[zBlock]
                    
                    # Strip the ^ prefix to look up the actual key in the UI dict
                    lookup_key = zHorizontal[1:] if zHorizontal.startswith(MOD_CARET) else zHorizontal
                    self.logger.warning(LOG_MSG_LOOKING_UP_KEY, lookup_key, list(block_dict.keys()))
                    
                    # Resolve key or return original if not found
                    resolved = block_dict.get(lookup_key, zHorizontal)
                    self.logger.warning(LOG_MSG_RESOLVED_KEY, lookup_key, resolved)
                    return resolved
                else:
                    self.logger.warning(LOG_MSG_COULD_NOT_LOAD, zBlock, zVaFile)
            else:
                self.logger.warning(LOG_MSG_NO_ZVAFILE)
        else:
            self.logger.warning(LOG_MSG_CANNOT_RESOLVE)
        
        # Return original if resolution fails
        return zHorizontal
