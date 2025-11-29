# zCLI/subsystems/zNavigation/zNavigation.py

"""
zNavigation - Unified Navigation System Subsystem for zCLI.

This module provides the zNavigation facade class, which serves as the primary
interface for navigation operations in zCLI. It orchestrates four specialized
components to deliver menu creation, breadcrumb management, navigation state
tracking, and inter-file linking.

Facade Pattern
--------------
The zNavigation class implements the Facade pattern, providing a simplified
interface to the complex navigation subsystem. It delegates all operations to
specialized components while maintaining a clean, consistent public API.

**Key Design Principles:**
- Pure delegation (no business logic in facade)
- Clean public API for external clients
- Component encapsulation (internal structure hidden)
- Backward compatibility (standalone functions for Walker)

Component Architecture
----------------------
The zNavigation facade orchestrates four specialized components:

1. **MenuSystem** (navigation_menu_system.py)
   - Menu creation and display (create, select)
   - Orchestrates builder, renderer, and interaction components
   - Supports static, dynamic, and function-based menus
   - Integration: Called by zDispatch for * (menu) modifier

2. **Breadcrumbs** (navigation_breadcrumbs.py)
   - Navigation trail management (zCrumbs)
   - "Back" functionality (zBack)
   - Session breadcrumb storage and retrieval
   - UI file reloading based on breadcrumb state

3. **Navigation** (navigation_state.py)
   - Current navigation location tracking
   - Navigation history management (FIFO overflow)
   - Session state storage with timestamps
   - Location metadata management

4. **Linking** (navigation_linking.py)
   - Inter-file linking (zLink expressions)
   - RBAC permission checking for links
   - Session context updates (zVaFolder, zVaFile, zBlock)
   - Integration: zParser (expression eval), zLoader (file loading)

Public API
----------
The facade exposes 10 methods organized by functional area:

**Menu System (2 methods):**
- create(options, title, allow_back, walker) → str
- select(options, prompt, walker) → str

**Breadcrumbs (2 methods):**
- handle_zCrumbs(zBlock, zKey, walker) → Any
- handle_zBack(show_banner, walker) → str

**Navigation State (3 methods):**
- navigate_to(target, context) → Dict
- get_current_location() → Dict
- get_navigation_history() → List

**Inter-file Linking (1 method):**
- handle_zLink(zHorizontal, walker) → str

Backward Compatibility
----------------------
Two standalone functions maintain backward compatibility with Walker:

- handle_zLink(zHorizontal, walker) → Delegates to facade
- handle_zCrumbs(zBlock, zKey, walker) → Delegates to facade

These functions ensure legacy code continues to work while encouraging
migration to the modern facade API.

Layer Position
--------------
Layer 1, Position 4 (zNavigation) - Facade

Integration
-----------
- Parent: zCLI core (zCLI.py)
- Used By: zDispatch (menu system), zWalker (navigation), external clients
- Uses: MenuSystem, Breadcrumbs, Navigation, Linking components

Usage Examples
--------------
Via facade (recommended)::

    # Initialize zCLI (done automatically)
    zcli = zCLI()
    
    # Create navigation menu
    choice = zcli.navigation.create(
        ["Settings", "Profile", "Logout"],
        title="Main Menu",
        allow_back=True,
        walker=walker
    )
    
    # Handle breadcrumb trail
    zcli.navigation.handle_zCrumbs("menu_block", "option_key", walker)
    
    # Navigate to location
    zcli.navigation.navigate_to("users.menu.list_users")
    
    # Handle inter-file linking
    result = zcli.navigation.handle_zLink("zLink(path.to.file.block)", walker)

Via standalone functions (backward compatibility)::

    # Legacy Walker integration
    from zCLI.subsystems.zNavigation import handle_zLink, handle_zCrumbs
    
    # These delegate to the facade internally
    result = handle_zLink("zLink(path)", walker)
    handle_zCrumbs("block", "key", walker)

See Also
--------
- navigation_modules/ : Component implementations
- zDispatch : Menu system integration (* modifier)
- zWalker : Navigation orchestration
"""

from zCLI import Any, Dict, List, Optional

from .navigation_modules.navigation_menu_system import MenuSystem
from .navigation_modules.navigation_breadcrumbs import Breadcrumbs
from .navigation_modules.navigation_state import Navigation
from .navigation_modules.navigation_linking import Linking

# ============================================================================
# Module Constants
# ============================================================================

# Display Settings
COLOR_MENU: str = "MENU"  # Backward compatibility with legacy MENU color
DISPLAY_MSG_READY: str = "zNavigation Ready"
DISPLAY_INDENT_INIT: int = 0
DISPLAY_STYLE_INIT: str = "full"

# Error Messages
ERROR_MSG_NO_ZCLI: str = "zNavigation requires a zCLI instance"
ERROR_MSG_NO_WALKER: str = "requires walker parameter"

# Log Messages
LOG_MSG_READY: str = "[zNavigation] Unified navigation system ready"


# ============================================================================
# zNavigation Facade Class
# ============================================================================

class zNavigation:
    """
    Unified navigation system facade for zCLI.
    
    Provides a clean, consistent interface to the navigation subsystem by
    orchestrating four specialized components: MenuSystem, Breadcrumbs,
    Navigation, and Linking. Implements the Facade pattern with pure
    delegation (no business logic in facade).
    
    Attributes
    ----------
    zcli : Any
        Reference to zCLI core instance
    session : Dict
        Session dictionary for state management
    logger : Any
        Logger instance for navigation operations
    mycolor : str
        Display color for navigation messages (default: "MENU")
    menu : MenuSystem
        Menu creation and interaction component
    breadcrumbs : Breadcrumbs
        Navigation trail management component
    navigation : Navigation
        Navigation state and history component
    linking : Linking
        Inter-file linking component
    
    Methods
    -------
    create(options, title, allow_back, walker)
        Create and display a menu, return user choice
    select(options, prompt, walker)
        Simple selection menu without complex navigation
    handle_zCrumbs(zBlock, zKey, walker)
        Handle breadcrumb trail management
    handle_zBack(show_banner, walker)
        Handle back navigation
    navigate_to(target, context)
        Navigate to a specific target
    get_current_location()
        Get current navigation location
    get_navigation_history()
        Get navigation history
    handle_zLink(zHorizontal, walker)
        Handle inter-file linking
    
    Examples
    --------
    Create navigation menu::
    
        nav = zNavigation(zcli)
        choice = nav.create(
            ["Settings", "Profile", "Logout"],
            title="Main Menu",
            walker=walker
        )
    
    Handle breadcrumbs::
    
        nav.handle_zCrumbs("menu_block", "option_key", walker)
        result = nav.handle_zBack(show_banner=True, walker=walker)
    
    Navigate to location::
    
        nav.navigate_to("users.menu.list_users")
        location = nav.get_current_location()
    
    Integration
    -----------
    - Initialized by: zCLI.py core
    - Used by: zDispatch, zWalker, external clients
    - Delegates to: MenuSystem, Breadcrumbs, Navigation, Linking
    """

    # Class-level type declarations
    zcli: Any  # zCLI core instance
    session: Dict[str, Any]  # Session dictionary
    logger: Any  # Logger instance
    mycolor: str  # Display color
    menu: MenuSystem  # Menu system component
    breadcrumbs: Breadcrumbs  # Breadcrumbs component
    navigation: Navigation  # Navigation component
    linking: Linking  # Linking component

    def __init__(self, zcli: Any) -> None:
        """
        Initialize zNavigation subsystem with component orchestration.
        
        Args
        ----
        zcli : Any
            zCLI core instance (required)
        
        Raises
        ------
        ValueError
            If zcli parameter is None
        
        Notes
        -----
        Initialization sequence:
        1. Validate zcli parameter
        2. Store references (zcli, session, logger)
        3. Set display color (backward compatibility)
        4. Initialize 4 specialized components
        5. Display ready message
        6. Log initialization
        """
        if zcli is None:
            raise ValueError(ERROR_MSG_NO_ZCLI)

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = COLOR_MENU  # Keep MENU color for backward compatibility

        # Initialize navigation modules (component composition)
        self.menu = MenuSystem(self)
        self.breadcrumbs = Breadcrumbs(self)
        self.navigation = Navigation(self)
        self.linking = Linking(self)

        # Display ready message using modern zDisplay
        self.zcli.display.zDeclare(
            DISPLAY_MSG_READY,
            color=self.mycolor,
            indent=DISPLAY_INDENT_INIT,
            style=DISPLAY_STYLE_INIT
        )

        self.logger.framework.debug(LOG_MSG_READY)

    # ========================================================================
    # Menu System Methods
    # ========================================================================

    def create(
        self,
        options: Any,
        title: Optional[str] = None,
        allow_back: bool = True,
        walker: Optional[Any] = None
    ) -> str:
        """
        Create and display a menu, return user choice.
        
        Delegates to MenuSystem for full-featured menu creation with navigation
        support. Integrates with breadcrumb system and supports "Back" option.
        
        Args
        ----
        options : Any
            List of menu options or dict with options
        title : Optional[str], default=None
            Optional menu title
        allow_back : bool, default=True
            Whether to add "Back" option
        walker : Optional[Any], default=None
            Optional walker instance for context
        
        Returns
        -------
        str
            Selected option string (or "zBack" if back chosen)
        
        Examples
        --------
        Basic menu::
        
            choice = nav.create(
                ["Settings", "Profile", "Logout"],
                title="Main Menu",
                walker=walker
            )
        
        Anchor menu (no back)::
        
            choice = nav.create(
                ["Yes", "No"],
                title="Confirm",
                allow_back=False,
                walker=walker
            )
        
        Notes
        -----
        - Called by zDispatch for * (menu) modifier
        - Delegates to MenuSystem.create()
        - Mode-agnostic (Terminal/Bifrost)
        """
        return self.menu.create(options, title=title, allow_back=allow_back, walker=walker)

    def select(
        self,
        options: List[str],
        prompt: str = "Select option",
        walker: Optional[Any] = None
    ) -> str:
        """
        Simple selection menu without complex navigation.
        
        Delegates to MenuSystem for simplified menu without "Back" option or
        navigation features. Used for quick selections.
        
        Args
        ----
        options : List[str]
            List of options to select from
        prompt : str, default="Select option"
            Prompt text to display
        walker : Optional[Any], default=None
            Optional walker instance for context
        
        Returns
        -------
        str
            Selected option string
        
        Examples
        --------
        Color selection::
        
            color = nav.select(
                ["Red", "Green", "Blue"],
                prompt="Choose a color",
                walker=walker
            )
        
        Quick yes/no::
        
            answer = nav.select(["Yes", "No"], walker=walker)
        
        Notes
        -----
        - No "Back" option (hardcoded allow_back=False)
        - Delegates to MenuSystem.select()
        - Simpler display than create()
        """
        return self.menu.select(options, prompt=prompt, walker=walker)

    # ========================================================================
    # Breadcrumbs Methods
    # ========================================================================

    def handle_zCrumbs(
        self,
        zBlock: str,
        zKey: str,
        walker: Optional[Any] = None
    ) -> Any:
        """
        Handle breadcrumb trail management.
        
        Delegates to Breadcrumbs for adding navigation crumbs to session,
        enabling "Back" functionality and navigation trail display.
        
        Args
        ----
        zBlock : str
            Block identifier for breadcrumb
        zKey : str
            Key identifier for breadcrumb
        walker : Optional[Any], default=None
            Optional walker instance for context
        
        Returns
        -------
        Any
            Breadcrumb operation result
        
        Examples
        --------
        Add breadcrumb::
        
            nav.handle_zCrumbs("users_menu", "list_users_key", walker)
        
        Notes
        -----
        - Stores breadcrumb in session (zCrumbs key)
        - Enables zBack functionality
        - Delegates to Breadcrumbs.handle_zCrumbs()
        """
        return self.breadcrumbs.handle_zCrumbs(zBlock, zKey, walker=walker)

    def handle_zBack(
        self,
        show_banner: bool = True,
        walker: Optional[Any] = None
    ) -> str:
        """
        Handle back navigation.
        
        Delegates to Breadcrumbs for navigating back in the breadcrumb trail,
        reloading the previous UI file and restoring navigation state.
        
        Args
        ----
        show_banner : bool, default=True
            Whether to display "zBack" banner
        walker : Optional[Any], default=None
            Optional walker instance for context
        
        Returns
        -------
        str
            Result of back navigation (typically "zBack")
        
        Examples
        --------
        Navigate back with banner::
        
            result = nav.handle_zBack(show_banner=True, walker=walker)
        
        Silent back navigation::
        
            result = nav.handle_zBack(show_banner=False, walker=walker)
        
        Notes
        -----
        - Pops breadcrumb from session trail
        - Reloads previous UI file
        - Delegates to Breadcrumbs.handle_zBack()
        """
        return self.breadcrumbs.handle_zBack(show_banner=show_banner, walker=walker)

    # ========================================================================
    # Navigation Methods
    # ========================================================================

    def navigate_to(
        self,
        target: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Navigate to a specific target.
        
        Delegates to Navigation for updating current location and adding to
        navigation history with optional context metadata.
        
        Args
        ----
        target : str
            Navigation target (file, block, key, etc.)
        context : Optional[Dict[str, Any]], default=None
            Optional navigation context metadata
        
        Returns
        -------
        Dict[str, Any]
            Navigation result with status and target
        
        Examples
        --------
        Navigate to file/block::
        
            result = nav.navigate_to("users.menu.list_users")
        
        Navigate with context::
        
            result = nav.navigate_to(
                "users.detail",
                context={"user_id": 123}
            )
        
        Notes
        -----
        - Updates session current_location
        - Adds to navigation_history (FIFO overflow)
        - Delegates to Navigation.navigate_to()
        """
        return self.navigation.navigate_to(target, context=context)

    def get_current_location(self) -> Dict[str, Any]:
        """
        Get current navigation location.
        
        Delegates to Navigation for retrieving current location from session,
        including target and context metadata.
        
        Returns
        -------
        Dict[str, Any]
            Current location dict with target, context, timestamp
        
        Examples
        --------
        Get current location::
        
            location = nav.get_current_location()
            print(f"Current: {location['target']}")
        
        Notes
        -----
        - Reads from session (current_location key)
        - Returns empty dict if no location set
        - Delegates to Navigation.get_current_location()
        """
        return self.navigation.get_current_location()

    def get_navigation_history(self) -> List[Dict[str, Any]]:
        """
        Get navigation history.
        
        Delegates to Navigation for retrieving full navigation history from
        session, limited to last 50 entries (FIFO overflow).
        
        Returns
        -------
        List[Dict[str, Any]]
            List of navigation history entries
        
        Examples
        --------
        Get history::
        
            history = nav.get_navigation_history()
            for entry in history:
                print(f"Visited: {entry['target']}")
        
        Notes
        -----
        - Reads from session (navigation_history key)
        - Limited to 50 entries (FIFO overflow)
        - Delegates to Navigation.get_navigation_history()
        """
        return self.navigation.get_navigation_history()

    # ========================================================================
    # Linking Methods
    # ========================================================================

    def handle_zLink(
        self,
        zHorizontal: str,
        walker: Optional[Any] = None
    ) -> str:
        """
        Handle inter-file linking.
        
        Delegates to Linking for parsing zLink expressions, checking RBAC
        permissions, loading target files, and updating session context.
        
        Args
        ----
        zHorizontal : str
            zLink expression (e.g., "zLink(path.to.file.block)")
        walker : Optional[Any], default=None
            Optional walker instance for context
        
        Returns
        -------
        str
            Result of link navigation
        
        Examples
        --------
        Basic link::
        
            result = nav.handle_zLink(
                "zLink(users.menu.list_users)",
                walker=walker
            )
        
        Link with permissions::
        
            result = nav.handle_zLink(
                "zLink(admin.settings, {role: 'admin'})",
                walker=walker
            )
        
        Notes
        -----
        - Parses zLink expression (zParser integration)
        - Checks RBAC permissions if specified
        - Loads target file (zLoader integration)
        - Updates session context (zVaFolder, zVaFile, zBlock)
        - Delegates to Linking.handle()
        """
        return self.linking.handle(walker=walker, zHorizontal=zHorizontal)


# ============================================================================
# Standalone Functions (Backward Compatibility)
# ============================================================================

def handle_zLink(zHorizontal: str, walker: Optional[Any] = None) -> str:
    """
    Standalone link handler function for Walker compatibility.
    
    Provides backward compatibility with legacy Walker code by maintaining
    the standalone function interface while delegating to the modern facade.
    
    Args
    ----
    zHorizontal : str
        zLink expression to handle
    walker : Optional[Any], default=None
        Walker instance (required)
    
    Returns
    -------
    str
        Result of link navigation
    
    Raises
    ------
    ValueError
        If walker parameter is not provided
    
    Examples
    --------
    Legacy Walker usage::
    
        from zCLI.subsystems.zNavigation import handle_zLink
        result = handle_zLink("zLink(path)", walker)
    
    Notes
    -----
    - Backward compatibility for Walker integration
    - Delegates to walker.zcli.navigation.handle_zLink()
    - Modern code should use facade directly (zcli.navigation.handle_zLink)
    """
    if not walker:
        raise ValueError(f"handle_zLink {ERROR_MSG_NO_WALKER}")
    
    return walker.zcli.navigation.handle_zLink(zHorizontal=zHorizontal, walker=walker)


def handle_zCrumbs(
    zBlock: str,
    zKey: str,
    walker: Optional[Any] = None
) -> Any:
    """
    Standalone breadcrumbs handler function for Walker compatibility.
    
    Provides backward compatibility with legacy Walker code by maintaining
    the standalone function interface while delegating to the modern facade.
    
    Args
    ----
    zBlock : str
        Block identifier for breadcrumb
    zKey : str
        Key identifier for breadcrumb
    walker : Optional[Any], default=None
        Walker instance (required)
    
    Returns
    -------
    Any
        Breadcrumb operation result
    
    Raises
    ------
    ValueError
        If walker parameter is not provided
    
    Examples
    --------
    Legacy Walker usage::
    
        from zCLI.subsystems.zNavigation import handle_zCrumbs
        handle_zCrumbs("block", "key", walker)
    
    Notes
    -----
    - Backward compatibility for Walker integration
    - Delegates to walker.zcli.navigation.handle_zCrumbs()
    - Modern code should use facade directly (zcli.navigation.handle_zCrumbs)
    """
    if not walker:
        raise ValueError(f"handle_zCrumbs {ERROR_MSG_NO_WALKER}")
    
    return walker.zcli.navigation.handle_zCrumbs(zBlock=zBlock, zKey=zKey, walker=walker)
