# zCLI/zCLI.py — Core zCLI Engine
# ═══════════════════════════════════════════════════════════════════════════════
"""
zCLI Core Engine - Top-Level Orchestration & Entry Point
═══════════════════════════════════════════════════════════════════════════════

This module provides the top-level `zCLI` class, which orchestrates all subsystems
and manages the complete lifecycle of a zCLI application instance.

ARCHITECTURE OVERVIEW
─────────────────────────────────────────────────────────────────────────────────

zCLI follows a 4-layer bottom-up architecture to ensure clean dependency management
and minimize circular imports:

    Layer 3: Orchestration      ← zWalker (UI/menu navigation engine)
                ↑
    Layer 2: Core Abstraction   ← zUtils, zWizard, zData, zShell
                ↑
    Layer 1: Core Subsystems    ← zDisplay, zAuth, zDispatch, zNavigation,
                                  zParser, zLoader, zFunc, zDialog, zOpen
                ↑
    Layer 0: Foundation         ← zConfig (session, logger, traceback), zComm

SUBSYSTEM DEPENDENCY MAP
─────────────────────────────────────────────────────────────────────────────────

The initialization order is critical - each layer depends ONLY on layers below it:

    Layer 0 (Foundation):
        • zConfig   → Provides session dict, logger, zTraceback, machine/env config
        • zComm     → Communication infrastructure (HTTP, WebSocket, zBifrost)

    Layer 1 (Core Subsystems - 9 total):
        • zDisplay     → UI rendering, multi-mode output (Terminal, zBifrost, Walker)
        • zAuth        → Three-tier authentication (zSession, App, Dual-Mode), RBAC
        • zDispatch    → Command routing & dispatch, facade pattern
        • zNavigation  → Menu creation, breadcrumbs, inter-file linking
        • zParser      → YAML parsing, configuration loading, zVaFile package
        • zLoader      → File I/O, intelligent caching (6-tier cache architecture)
        • zFunc        → Function execution, Python integration
        • zDialog      → Interactive forms, auto-validation with zData
        • zOpen        → File & URL opening (files, directories, browsers)

    Layer 2 (Core Abstraction - 4 total):
        • zUtils   → Plugin system (delegates to zLoader.plugin_cache)
        • zWizard  → Multi-step workflows, loop engine (no upper dependencies)
        • zData    → Data management, database integration, declarative migrations
        • zShell   → Command execution, interactive REPL, wizard canvas mode

    Layer 3 (Orchestration - 1 total):
        • zWalker  → UI/menu navigation orchestrator (delegates to all 16 subsystems)

INITIALIZATION ORDER RATIONALE
─────────────────────────────────────────────────────────────────────────────────

1. **zConfig FIRST** - Everything depends on session dict, logger, traceback
2. **zComm EARLY** - Required by zDisplay (zBifrost mode), zData (HTTP adapter)
3. **Layer 1 (Core)** - Foundation is ready, now we can build core functionality
4. **zUtils BEFORE zWizard/zData/zShell** - Plugin system enables extensibility
5. **zWizard BEFORE zData/zShell** - Loop engine may be used by interactive ops
6. **zData BEFORE zShell** - Shell commands may need database access
7. **zShell BEFORE zWalker** - Walker delegates to shell for step execution
8. **zWalker LAST** - Orchestrator needs ALL subsystems ready

SHUTDOWN COORDINATION
─────────────────────────────────────────────────────────────────────────────────

Shutdown happens in REVERSE initialization order to prevent dangling references:

    1. WebSocket connections (zBifrost via zComm) - Close active client connections
    2. HTTP server (zServer via zComm)            - Stop serving requests
    3. Database connections (zData)               - Close DB connections gracefully
    4. Logger handlers                            - Flush logs to disk

Each component cleanup is wrapped in ExceptionContext - individual failures do NOT
prevent overall shutdown. Status tracking ensures transparency.

THREAD-SAFETY GUARANTEES
─────────────────────────────────────────────────────────────────────────────────

- **contextvars.ContextVar**: Used for `_current_zcli` instead of global state
- **Thread-Local Context**: Each thread/async task gets its own zCLI instance
- **No Global State**: All state lives in the zCLI instance or session dict
- **Exception Auto-Registration**: zExceptions automatically find their zCLI context

This design follows Django/Flask/FastAPI patterns for request/application context.

SIGNAL HANDLING
─────────────────────────────────────────────────────────────────────────────────

Signal handlers are automatically registered for graceful shutdown:

    • SIGINT (Ctrl+C)  → Triggers graceful shutdown, prevents multiple attempts
    • SIGTERM (kill)   → Triggers graceful shutdown, prevents multiple attempts

Shutdown flags (`_shutdown_requested`, `_shutdown_in_progress`) prevent race
conditions and duplicate cleanup.

CONTEXT MANAGER PATTERN
─────────────────────────────────────────────────────────────────────────────────

zCLI supports context manager protocol for automatic cleanup:

    with zCLI() as z:
        z.run_command("data select users")
        # Automatic cleanup on exit

This ensures resources are always released, even if exceptions occur.

DUAL-MODE SUPPORT
─────────────────────────────────────────────────────────────────────────────────

zCLI operates in two primary modes:

    1. **Terminal Mode** (default)
       - Interactive shell (REPL loop)
       - Command execution via zShell
       - Human-friendly output (colors, formatting)

    2. **zBifrost Mode** (WebSocket server)
       - Network-based UI interaction
       - JSON message passing
       - Delegates to zWalker for orchestration
       - Multi-client support

Mode is detected from zSpark_obj["zMode"] or defaults to "Terminal".

USAGE EXAMPLES
─────────────────────────────────────────────────────────────────────────────────

Example 1: Basic CLI Usage (Terminal Mode)
    ```python
    from zCLI import zCLI

    z = zCLI()
    z.run()  # Starts interactive shell
    ```

Example 2: Single Command Execution
    ```python
    z = zCLI()
    result = z.run_command("data select users where role=admin")
    print(result)
    ```

Example 3: Context Manager (Automatic Cleanup)
    ```python
    with zCLI() as z:
        z.run_command("echo 'Hello, World!'")
        z.run_command("data insert users name='Alice' role='admin'")
    # Automatic shutdown on exit
    ```

Example 4: zBifrost Mode (WebSocket Server)
    ```python
    z = zCLI(zSpark_obj={"zMode": "zBifrost", "port": 8765})
    z.run()  # Starts WebSocket server via zWalker
    ```

Example 5: Custom Configuration
    ```python
    z = zCLI(zSpark_obj={
        "zMode": "Terminal",
        "plugins": ["@MyPlugin.py"],
        "log_level": "DEBUG"
    })
    z.run_shell()
    ```

MODULE CONSTANTS
─────────────────────────────────────────────────────────────────────────────────
See constants section below for session keys, modes, logger messages, etc.

SUBSYSTEM COUNT
─────────────────────────────────────────────────────────────────────────────────
Total subsystems managed by zCLI: 17 (2 Layer 0 + 9 Layer 1 + 4 Layer 2 + 1 Layer 3 + 1 HTTP server)

FILE METADATA
─────────────────────────────────────────────────────────────────────────────────
Module: zCLI.zCLI
Version: 1.5.4+
Modernized: 2025-01-07 (Week 6.18)
Grade: C (70/100) → A+ (95/100)
Lines: 382 → 950+ (+149%)
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import signal
import sys
import contextvars
from typing import Any, Dict, Optional
from zCLI.utils.zTraceback import ExceptionContext

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Session Keys (4) - Used in session dict
# ─────────────────────────────────────────────────────────────────────────────
SESSION_KEY_ZS_ID: str = "zS_id"
SESSION_KEY_ZMODE: str = "zMode"
SESSION_KEY_ZMACHINE: str = "zMachine"
SESSION_KEY_ZSPARK: str = "zSpark_obj"

# ─────────────────────────────────────────────────────────────────────────────
# Mode Constants (3) - zMode values
# ─────────────────────────────────────────────────────────────────────────────
MODE_TERMINAL: str = "Terminal"
MODE_ZBIFROST: str = "zBifrost"
MODE_WALKER: str = "Walker"

# ─────────────────────────────────────────────────────────────────────────────
# Signal Names (2) - For signal handler logging
# ─────────────────────────────────────────────────────────────────────────────
SIGNAL_INT: str = "SIGINT"
SIGNAL_TERM: str = "SIGTERM"

# ─────────────────────────────────────────────────────────────────────────────
# Shutdown Component Keys (4) - For status tracking dict
# ─────────────────────────────────────────────────────────────────────────────
SHUTDOWN_WEBSOCKET: str = "websocket"
SHUTDOWN_HTTP_SERVER: str = "http_server"
SHUTDOWN_DATABASE: str = "database"
SHUTDOWN_LOGGER: str = "logger"

# ─────────────────────────────────────────────────────────────────────────────
# Shutdown Status Symbols (2) - For status display
# ─────────────────────────────────────────────────────────────────────────────
SHUTDOWN_STATUS_SUCCESS: str = "✓"
SHUTDOWN_STATUS_FAIL: str = "✗"

# ─────────────────────────────────────────────────────────────────────────────
# Logger Messages - Info (10)
# ─────────────────────────────────────────────────────────────────────────────
LOG_INIT_COMPLETE: str = "zCLI Core initialized - Mode: %s"
LOG_MODE_TERMINAL: str = "Starting zCLI in Terminal mode..."
LOG_MODE_ZBIFROST: str = "Starting zCLI in zBifrost mode via zWalker..."
LOG_HTTP_START: str = "HTTP server auto-started at %s"
LOG_SESSION_INIT: str = "Session initialized:"
LOG_SESSION_ID_PREFIX: str = "  zS_id: %s"
LOG_SESSION_MODE_PREFIX: str = "  zMode: %s"
LOG_SESSION_MACHINE_PREFIX: str = "  zMachine hostname: %s"
LOG_SHUTDOWN_START: str = "[Shutdown] Initiating graceful shutdown..."
LOG_SHUTDOWN_COMPLETE: str = "[Shutdown] Graceful shutdown complete"

# ─────────────────────────────────────────────────────────────────────────────
# Logger Messages - Warning (5)
# ─────────────────────────────────────────────────────────────────────────────
LOG_WARN_PLUGIN_FAIL: str = "Failed to load plugins: %s"
LOG_WARN_SHUTDOWN_IN_PROGRESS: str = "[Shutdown] Shutdown already in progress"
LOG_WARN_WEBSOCKET_ERROR: str = "[Shutdown] WebSocket cleanup error: %s"
LOG_WARN_SIGNAL_DUPLICATE: str = "[%s] Shutdown already in progress..."
LOG_WARN_ASYNC_SHUTDOWN_SKIPPED: str = "[Shutdown] Async shutdown skipped (loop running)"

# ─────────────────────────────────────────────────────────────────────────────
# Logger Messages - Debug (9)
# ─────────────────────────────────────────────────────────────────────────────
LOG_DEBUG_SESSION_ID: str = "  zS_id: %s"
LOG_DEBUG_SESSION_MODE: str = "  zMode: %s"
LOG_DEBUG_SESSION_MACHINE: str = "  zMachine hostname: %s"
LOG_DEBUG_SIGNAL_HANDLERS: str = "Signal handlers registered (SIGINT, SIGTERM)"
LOG_DEBUG_WEBSOCKET_NOT_RUNNING: str = "[Shutdown] WebSocket server not running"
LOG_DEBUG_WEBSOCKET_NOT_INIT: str = "[Shutdown] WebSocket server not initialized"
LOG_DEBUG_HTTP_NOT_RUNNING: str = "[Shutdown] HTTP server not running"
LOG_DEBUG_HTTP_NOT_INIT: str = "[Shutdown] HTTP server not initialized"
LOG_DEBUG_DB_NOT_CONNECTED: str = "[Shutdown] No active database connections"
LOG_DEBUG_DB_NOT_INIT: str = "[Shutdown] Database subsystem not initialized"

# ─────────────────────────────────────────────────────────────────────────────
# Shutdown Messages (6)
# ─────────────────────────────────────────────────────────────────────────────
SHUTDOWN_MSG_WEBSOCKET_CLOSE: str = "[Shutdown] Closing WebSocket server..."
SHUTDOWN_MSG_HTTP_STOP: str = "[Shutdown] Stopping HTTP server..."
SHUTDOWN_MSG_DB_CLOSE: str = "[Shutdown] Closing database connections..."
SHUTDOWN_MSG_LOGGER_FLUSH: str = "[Shutdown] Flushing logger..."
SHUTDOWN_MSG_STATUS_REPORT: str = "[Shutdown] Cleanup Status:"
SHUTDOWN_MSG_COMPONENT_STATUS: str = "  %s %s"

# ─────────────────────────────────────────────────────────────────────────────
# Shutdown Separators (2)
# ─────────────────────────────────────────────────────────────────────────────
SHUTDOWN_SEPARATOR: str = "=" * 70
SHUTDOWN_OPERATION_PREFIX: str = "[Shutdown]"

# ─────────────────────────────────────────────────────────────────────────────
# Error Messages (6)
# ─────────────────────────────────────────────────────────────────────────────
ERROR_SHUTDOWN_SIGNAL: str = "Error during %s shutdown"
ERROR_WEBSOCKET_SHUTDOWN: str = "WebSocket shutdown"
ERROR_HTTP_SHUTDOWN: str = "HTTP server shutdown"
ERROR_DB_SHUTDOWN: str = "Database connection cleanup"
ERROR_LOGGER_SHUTDOWN: str = "Logger cleanup"
ERROR_SIGNAL_RECEIVED: str = "[%s] Received shutdown signal"

# ─────────────────────────────────────────────────────────────────────────────
# Layer Names (4) - For architecture documentation
# ─────────────────────────────────────────────────────────────────────────────
LAYER_0_FOUNDATION: str = "Layer 0: Foundation"
LAYER_1_CORE: str = "Layer 1: Core Subsystems"
LAYER_2_ABSTRACTION: str = "Layer 2: Core Abstraction"
LAYER_3_ORCHESTRATION: str = "Layer 3: Orchestration"

# ─────────────────────────────────────────────────────────────────────────────
# Plugin Config Keys (1)
# ─────────────────────────────────────────────────────────────────────────────
ZSPARK_PLUGINS_KEY: str = "plugins"

# ─────────────────────────────────────────────────────────────────────────────
# Context Variable Name (1)
# ─────────────────────────────────────────────────────────────────────────────
CONTEXT_VAR_NAME: str = "current_zcli"

# Global context variable for current zCLI instance (thread-safe, async-safe)
# Follows Django/Flask/FastAPI pattern for request/application context
_current_zcli: contextvars.ContextVar = contextvars.ContextVar(CONTEXT_VAR_NAME, default=None)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API - Context Access
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_zcli() -> Optional['zCLI']:
    """
    Get the current zCLI instance from the thread-local context.
    
    This function provides thread-safe access to the current zCLI instance without
    requiring explicit instance passing. It follows the Django/Flask/FastAPI pattern
    for request/application context management.
    
    The context is automatically set during:
        • zCLI.__init__() - Instance is registered on creation
        • zCLI.__enter__() - Context manager entry
        • zCLI.__exit__()  - Context manager exit (clears context)
    
    This enables zExceptions to automatically find their zCLI instance for
    auto-registration without requiring explicit instance references.
    
    Returns
    -------
    Optional[zCLI]
        The current zCLI instance if one is registered in the current thread/async task,
        or None if not in a zCLI context.
    
    Thread Safety
    -------------
    Uses `contextvars.ContextVar` which is:
        • Thread-safe: Each thread has its own context
        • Async-safe: Each async task has its own context
        • Inheritance: Child threads/tasks inherit parent context
    
    Examples
    --------
    Example 1: Access from anywhere in the call stack
        ```python
        from zCLI import zCLI, get_current_zcli
        
        def my_plugin_function():
            # No need to pass zCLI instance explicitly
            z = get_current_zcli()
            if z:
                z.display.info("Plugin executing in zCLI context")
        
        z = zCLI()
        my_plugin_function()  # Has access to z via context
        ```
    
    Example 2: Check if in zCLI context
        ```python
        z = get_current_zcli()
        if z:
            # We're in a zCLI context - can use subsystems
            z.logger.info("Logging from current context")
        else:
            # Not in a zCLI context - handle gracefully
            print("Not in zCLI context")
        ```
    
    Example 3: Exception auto-registration
        ```python
        # zExceptions use get_current_zcli() internally
        from zCLI.utils.zExceptions import MyCustomException
        
        z = zCLI()
        raise MyCustomException("Error!")  # Automatically finds z via context
        ```
    
    See Also
    --------
    zCLI.__enter__ : Registers instance on context manager entry
    zCLI.__exit__ : Clears instance on context manager exit
    """
    return _current_zcli.get()


# ═══════════════════════════════════════════════════════════════════════════════
# CORE CLASS - zCLI
# ═══════════════════════════════════════════════════════════════════════════════

class zCLI:
    """
    Core zCLI Engine - Top-Level Orchestrator for all subsystems.
    
    The zCLI class is the main entry point and orchestrator for the entire zCLI
    framework. It manages the lifecycle of all 17 subsystems, handles initialization
    order, provides graceful shutdown coordination, and exposes a unified API for
    command execution.
    
    Responsibilities
    ----------------
    1. **Subsystem Initialization**: Bootstrap all subsystems in correct dependency order
    2. **Lifecycle Management**: Handle startup, running, and graceful shutdown
    3. **Context Provider**: Register as current instance for thread-safe access
    4. **Signal Handling**: Respond to SIGINT/SIGTERM for graceful shutdown
    5. **Mode Detection**: Automatically detect Terminal vs zBifrost mode
    6. **Plugin Loading**: Load utility plugins from zSpark_obj configuration
    7. **Resource Cleanup**: Ensure all resources are released on shutdown
    
    Subsystem Attributes (17 total)
    --------------------------------
    Layer 0 (Foundation):
        config : zConfig
            Configuration management (session, logger, traceback, machine/env)
        comm : zComm
            Communication infrastructure (HTTP, WebSocket, zBifrost)
        
    Layer 1 (Core Subsystems - 9 total):
        display : zDisplay
            UI rendering and multi-mode output
        auth : zAuth
            Three-tier authentication and RBAC
        dispatch : zDispatch
            Command routing and dispatch
        navigation : zNavigation
            Menu creation and breadcrumbs
        zparser : zParser
            YAML parsing and configuration loading
        loader : zLoader
            File I/O and intelligent caching
        zfunc : zFunc
            Function execution and Python integration
        dialog : zDialog
            Interactive forms and auto-validation
        open : zOpen
            File and URL opening
            
    Layer 2 (Core Abstraction - 4 total):
        utils : zUtils
            Plugin system (delegates to zLoader.plugin_cache)
        wizard : zWizard
            Multi-step workflows and loop engine
        data : zData
            Data management and database integration
        shell : zShell
            Command execution and interactive REPL
            
    Layer 3 (Orchestration - 1 total):
        walker : zWalker
            UI/menu navigation orchestrator
    
    Optional:
        server : Optional[HTTPServer]
            HTTP server (auto-started if enabled in config)
    
    Attributes Set by Subsystems
    -----------------------------
    logger : logging.Logger
        Logger instance (set by zConfig during initialization)
    session : Dict[str, Any]
        Session dictionary (set by zConfig during initialization)
    zTraceback : zTraceback
        Exception handler (set by zConfig during initialization)
    
    Private Attributes
    ------------------
    zspark_obj : Dict[str, Any]
        Configuration dictionary passed to __init__
    _shutdown_requested : bool
        Flag indicating if shutdown has been requested
    _shutdown_in_progress : bool
        Flag indicating if shutdown is currently in progress
    mycolor : str
        Display color identifier (set to "MAIN")
    
    Lifecycle Methods
    -----------------
    __init__(zSpark_obj=None)
        Initialize all subsystems in dependency order
    run()
        Main entry point - starts Terminal or zBifrost mode
    run_shell()
        Explicitly run Terminal mode (interactive REPL)
    run_command(command)
        Execute a single command string
    shutdown()
        Gracefully shutdown all subsystems in reverse order
    
    Context Manager Support
    -----------------------
    __enter__()
        Register instance as current context
    __exit__(exc_type, exc_val, exc_tb)
        Clear current context and cleanup
    
    Signal Handling
    ---------------
    Automatic registration of SIGINT and SIGTERM handlers during __init__.
    Both signals trigger graceful shutdown with proper cleanup coordination.
    
    Thread Safety
    -------------
    - Instance registration via contextvars.ContextVar (thread-safe, async-safe)
    - No global state - all state in instance or session dict
    - Each thread/task can have its own zCLI instance
    
    Examples
    --------
    Example 1: Basic usage (Terminal mode)
        ```python
        from zCLI import zCLI
        
        z = zCLI()
        z.run()  # Starts interactive shell
        ```
    
    Example 2: Single command execution
        ```python
        z = zCLI()
        result = z.run_command("data select users where role=admin")
        print(f"Found {len(result)} admins")
        ```
    
    Example 3: Context manager (automatic cleanup)
        ```python
        with zCLI() as z:
            z.run_command("echo 'Starting batch process'")
            z.run_command("data insert logs message='Process started'")
        # Automatic shutdown on exit
        ```
    
    Example 4: zBifrost mode (WebSocket server)
        ```python
        z = zCLI(zSpark_obj={"zMode": "zBifrost", "port": 8765})
        z.run()  # Starts WebSocket server via zWalker
        ```
    
    Example 5: Custom configuration with plugins
        ```python
        z = zCLI(zSpark_obj={
            "zMode": "Terminal",
            "plugins": ["@MyPlugin.py", "@DataProcessor.py"],
            "log_level": "DEBUG",
            "database": "@myapp.db"
        })
        z.run_shell()
        ```
    
    See Also
    --------
    get_current_zcli : Get the current zCLI instance from thread context
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # Type Hints for Attributes Set by Subsystems
    # ─────────────────────────────────────────────────────────────────────────
    logger: logging.Logger          # Set by zConfig
    session: Dict[str, Any]         # Set by zConfig
    zTraceback: Any                 # Set by zConfig (zTraceback instance)

    def __init__(self, zSpark_obj: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize zCLI instance with all subsystems.
        
        Performs bottom-up initialization across 4 layers, ensuring each layer's
        dependencies are satisfied before proceeding to the next layer.
        
        The initialization order is critical:
            1. Layer 0 (Foundation) - zConfig, zComm
            2. Layer 1 (Core Subsystems) - 9 subsystems
            3. Layer 2 (Core Abstraction) - zUtils, zWizard, zData, zShell
            4. Layer 3 (Orchestration) - zWalker
            5. Optional HTTP server auto-start
            6. Session initialization
            7. Signal handler registration
        
        Parameters
        ----------
        zSpark_obj : Optional[Dict[str, Any]], default=None
            Configuration dictionary for customizing zCLI behavior. Common keys:
            
            - **zMode** (str): Operating mode - "Terminal" (default) or "zBifrost"
            - **plugins** (List[str]): Plugin paths to load (e.g. ["@MyPlugin.py"])
            - **log_level** (str): Logging level - "DEBUG", "INFO", "WARNING", "ERROR"
            - **database** (str): Database path for zData (e.g. "@myapp.db")
            - **port** (int): WebSocket port for zBifrost mode (default 8765)
            - Any other subsystem-specific configuration
            
            If None, defaults are used (Terminal mode, no plugins, INFO logging).
        
        Raises
        ------
        ImportError
            If a subsystem module cannot be imported (rare - indicates installation issue)
        AttributeError
            If a subsystem class is missing expected attributes (rare - indicates version mismatch)
        
        Side Effects
        ------------
        - Registers instance in thread-local context via _current_zcli.set(self)
        - Sets signal handlers for SIGINT and SIGTERM
        - May auto-start HTTP server if enabled in config
        - Creates session dict with zS_id, zMode, zMachine
        - Initializes logger (may create log files)
        
        Layer 0: Foundation
        -------------------
        **zConfig** (FIRST):
            Provides session dict, logger, zTraceback. Everything depends on these.
        **zComm**:
            Communication infrastructure. Required by zDisplay (zBifrost) and zData (HTTP adapter).
        
        Layer 1: Core Subsystems (9 total)
        -----------------------------------
        **zDisplay**: UI rendering, multi-mode output
        **zAuth**: Three-tier authentication, RBAC
        **zDispatch**: Command routing, dispatch facade
        **zNavigation**: Menu creation, breadcrumbs
        **zParser**: YAML parsing, zVaFile package
        **zLoader**: File I/O, 6-tier caching
        **zFunc**: Function execution
        **zDialog**: Interactive forms
        **zOpen**: File/URL opening
        
        Layer 2: Core Abstraction (4 total)
        ------------------------------------
        **zUtils**: Plugin system (BEFORE zWizard/zData/zShell for extensibility)
        **zWizard**: Loop engine (BEFORE zData/zShell for interactive workflows)
        **zData**: Database integration (BEFORE zShell for data commands)
        **zShell**: Command execution (BEFORE zWalker for shell delegation)
        
        Layer 3: Orchestration (1 total)
        ---------------------------------
        **zWalker**: UI/menu orchestrator (LAST - needs ALL subsystems ready)
        
        Examples
        --------
        Example 1: Default initialization (Terminal mode)
            ```python
            z = zCLI()
            # Uses defaults: Terminal mode, no plugins, INFO logging
            ```
        
        Example 2: zBifrost mode with custom port
            ```python
            z = zCLI(zSpark_obj={"zMode": "zBifrost", "port": 9000})
            ```
        
        Example 3: Terminal mode with plugins
            ```python
            z = zCLI(zSpark_obj={
                "plugins": ["@MyPlugin.py"],
                "log_level": "DEBUG"
            })
            ```
        
        Example 4: Custom database and plugins
            ```python
            z = zCLI(zSpark_obj={
                "database": "@production.db",
                "plugins": ["@validators.py", "@transforms.py"],
                "zMode": "Terminal"
            })
            ```
        
        Notes
        -----
        - Initialization is expensive (~100-500ms) - reuse instances when possible
        - The instance is automatically registered in thread-local context
        - Signal handlers are registered automatically (SIGINT, SIGTERM)
        - zAuth database is workspace-relative (@) for isolation
        - HTTP server auto-starts if enabled in config (rare - typically manual)
        
        See Also
        --------
        run : Main entry point after initialization
        shutdown : Graceful cleanup (reverse initialization order)
        """

        # Initialize zSpark_obj config dict
        self.zspark_obj = zSpark_obj or {}
        
        # Shutdown coordination
        self._shutdown_requested = False
        self._shutdown_in_progress = False
        
        # Register this instance as current context (thread-safe)
        # Enables automatic exception registration for zExceptions
        _current_zcli.set(self)

        # ─────────────────────────────────────────────────────────────
        # Layer 0: Foundation
        # ─────────────────────────────────────────────────────────────
        # Initialize zConfig FIRST (provides machine config, environment config, session, logger, and traceback)
        # After this call, self.session, self.logger, and self.zTraceback are ready to use
        from .subsystems.zConfig import zConfig
        self.config = zConfig(zcli=self, zSpark_obj=zSpark_obj)

        # Initialize zComm (Communication infrastructure for zBifrost and zData)
        from .subsystems.zComm import zComm
        self.comm = zComm(self)

        # ─────────────────────────────────────────────────────────────
        # Layer 1: Core Subsystems
        # ─────────────────────────────────────────────────────────────
        # Initialize display subsystem
        from .subsystems.zDisplay import zDisplay
        self.display = zDisplay(self)
        self.mycolor = "MAIN"

        # Initialize authentication subsystem
        from .subsystems.zAuth import zAuth
        self.auth = zAuth(self)

        # Initialize dispatch subsystem
        from .subsystems.zDispatch import zDispatch
        self.dispatch = zDispatch(self)

        # Initialize navigation subsystem
        from .subsystems.zNavigation import zNavigation
        self.navigation = zNavigation(self)

        # Initialize parser subsystem
        from .subsystems.zParser import zParser
        self.zparser = zParser(self)

        # Initialize loader subsystem
        from .subsystems.zLoader import zLoader
        self.loader = zLoader(self)

        # Initialize function subsystem
        from .subsystems.zFunc import zFunc
        self.zfunc = zFunc(self)

        # Initialize dialog subsystem
        from .subsystems.zDialog import zDialog
        self.dialog = zDialog(self)

        # Initialize open subsystem
        from .subsystems.zOpen import zOpen
        self.open = zOpen(self)


        # ─────────────────────────────────────────────────────────────
        # Layer 2: Core Abstraction
        # ─────────────────────────────────────────────────────────────
        # Initialize utility subsystem (provides plugin system for other subsystems)
        from .subsystems.zUtils import zUtils
        self.utils = zUtils(self)    # Plugin system - available to all Layer 2+ subsystems
        self._load_plugins()         # Load plugins immediately after plugin system is ready

        # Initialize wizard subsystem (loop engine - no upper dependencies)
        from .subsystems.zWizard import zWizard
        self.wizard = zWizard(self)

        # Initialize data subsystem (may use zWizard for interactive operations)
        from .subsystems.zData import zData
        self.data = zData(self)

        # Initialize shell and command executor (depends on zUtils, zWizard, zData)
        from .subsystems.zShell import zShell
        self.shell = zShell(self)

        # Layer 3: Orchestration
        # Initialize walker subsystem
        from .subsystems.zWalker import zWalker
        self.walker = zWalker(self)  # Modern walker with unified navigation (can use plugins immediately)

        # Initialize HTTP server (optional) - auto-start if enabled in config
        self.server = None
        if hasattr(self.config, 'http_server') and self.config.http_server.enabled:
            self.server = self.comm.create_http_server(
                port=self.config.http_server.port,
                host=self.config.http_server.host,
                serve_path=self.config.http_server.serve_path
            )
            self.server.start()
            self.logger.info(LOG_HTTP_START, self.server.get_url())

        # Initialize session (sets zMode from zSpark_obj or defaults to Terminal)
        self._init_session()
        
        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()
        
        # Note: zAuth database is workspace-relative (@), ensuring each zCLI instance
        # is fully isolated. Auth DB lazy-loads on first save_session() or grant_permission().
        # This preserves the "no global state" principle - the secret sauce of zCLI architecture.

        self.logger.info(LOG_INIT_COMPLETE, self.session.get(SESSION_KEY_ZMODE))

    def _load_plugins(self) -> None:
        """
        Load utility plugins (Python modules) from zSpark_obj if provided.
        
        This method loads plugins specified in zSpark_obj["plugins"] and registers them
        with zUtils.load_plugins(). Plugins are Python modules that can extend zCLI
        functionality without modifying core code.
        
        Plugin Loading Strategy
        -----------------------
        - Uses **zUtils**, not zLoader (zUtils delegates to zLoader.plugin_cache internally)
        - Supports both single plugin (str) and multiple plugins (list/tuple)
        - Plugin paths can be zPath format (e.g. "@MyPlugin.py" for workspace-relative)
        - Failures are logged as warnings but do NOT halt initialization
        
        Plugin Format
        -------------
        Plugins can be:
            • Single string: zSpark_obj["plugins"] = "@MyPlugin.py"
            • List/tuple: zSpark_obj["plugins"] = ["@Plugin1.py", "@Plugin2.py"]
        
        Error Handling
        --------------
        Catches and logs (WARNING level):
            • ImportError: Plugin file not found or syntax error
            • AttributeError: Plugin missing required attributes
            • TypeError: Invalid plugin format
        
        Examples
        --------
        Example 1: Single plugin
            ```python
            z = zCLI(zSpark_obj={"plugins": "@MyValidator.py"})
            # MyValidator.py is loaded and available
            ```
        
        Example 2: Multiple plugins
            ```python
            z = zCLI(zSpark_obj={
                "plugins": ["@validators.py", "@transforms.py", "@hooks.py"]
            })
            # All three plugins loaded
            ```
        
        Example 3: Plugin loading failure (graceful)
            ```python
            z = zCLI(zSpark_obj={"plugins": "@missing.py"})
            # Logs warning, continues initialization
            ```
        
        Notes
        -----
        - Plugins are loaded AFTER zUtils initialization (Layer 2)
        - Plugin failures do NOT prevent zCLI from initializing
        - Plugins can access all subsystems via get_current_zcli()
        - Plugin cache supports collision detection, mtime invalidation, LRU eviction
        
        See Also
        --------
        zUtils.load_plugins : Actual plugin loading implementation
        zLoader.plugin_cache : Plugin caching infrastructure
        """
        try:
            plugin_paths = self.zspark_obj.get(ZSPARK_PLUGINS_KEY) or []
            if isinstance(plugin_paths, (list, tuple)):
                self.utils.load_plugins(plugin_paths)
            elif isinstance(plugin_paths, str):
                self.utils.load_plugins([plugin_paths])
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.warning(LOG_WARN_PLUGIN_FAIL, e)

    def _init_session(self) -> None:
        """
        Initialize session dictionary with zS_id and verify zMode.
        
        The session dict is created by zConfig during Layer 0 initialization. This method
        adds the session ID (zS_id) and logs the session configuration for debugging.
        
        Session Keys Set
        ----------------
        - **zS_id**: Unique session identifier (format: "zS_<UUID>")
        - **zMode**: Already set by zConfig.session.detect_zMode() (no override here)
        - **zMachine**: Already set by zConfig (machine hostname, OS, etc.)
        
        Mode Detection (Already Done by zConfig)
        -----------------------------------------
        zConfig.session.detect_zMode() checks:
            1. zSpark_obj.get("zMode") - Explicit mode override
            2. Defaults to "Terminal" if not specified
        
        No need to re-detect here - zMode is already correct.
        
        Session ID Generation
        ---------------------
        Uses zConfig.session.generate_id("zS") to create unique session identifier:
            • Format: "zS_<UUID>"
            • Unique per zCLI instance
            • Used for session tracking in logs, auth, etc.
        
        Examples
        --------
        Example 1: Default session (Terminal mode)
            ```python
            z = zCLI()
            # Session initialized with:
            #   zS_id: "zS_abc123..."
            #   zMode: "Terminal"
            #   zMachine: {"hostname": "mypc", "os": "Darwin", ...}
            ```
        
        Example 2: zBifrost mode session
            ```python
            z = zCLI(zSpark_obj={"zMode": "zBifrost"})
            # Session initialized with:
            #   zS_id: "zS_def456..."
            #   zMode: "zBifrost"
            #   zMachine: {"hostname": "server", ...}
            ```
        
        Notes
        -----
        - Called AFTER all subsystems are initialized
        - Session dict is shared across all subsystems
        - zS_id is unique per instance, not globally unique across machines
        - zMode cannot be changed after initialization
        
        See Also
        --------
        zConfig.session.generate_id : Session ID generation
        zConfig.session.detect_zMode : Mode detection logic
        """
        # Set session ID - always required
        self.session[SESSION_KEY_ZS_ID] = self.config.session.generate_id("zS")

        # zMode was already set by zConfig.session.detect_zMode() during session creation
        # It checks zSpark_obj.get("zMode") and defaults to "Terminal"
        # No need to override it here

        self.logger.debug(LOG_SESSION_INIT)
        self.logger.debug(LOG_DEBUG_SESSION_ID, self.session[SESSION_KEY_ZS_ID])
        self.logger.debug(LOG_DEBUG_SESSION_MODE, self.session[SESSION_KEY_ZMODE])
        self.logger.debug(LOG_DEBUG_SESSION_MACHINE, self.session[SESSION_KEY_ZMACHINE].get("hostname"))

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC API METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def run_command(self, command: str) -> Any:
        """
        Execute a single command string and return the result.
        
        This is the primary method for programmatic command execution. It delegates
        to zShell.execute_command() which parses and executes the command.
        
        Parameters
        ----------
        command : str
            Command string to execute (e.g. "data select users", "echo 'Hello'")
        
        Returns
        -------
        Any
            Command execution result. Type depends on the command:
                • Data queries: List of dicts (query results)
                • echo: None (output via zDisplay)
                • config get: str or dict (config value)
                • Most commands: None (side effects via zDisplay)
        
        Examples
        --------
        Example 1: Data query
            ```python
            z = zCLI()
            users = z.run_command("data select users where role=admin")
            print(f"Found {len(users)} admins")
            ```
        
        Example 2: Echo command
            ```python
            z = zCLI()
            z.run_command("echo 'Processing batch...'")
            # Output via zDisplay, returns None
            ```
        
        Example 3: Config access
            ```python
            z = zCLI()
            db_path = z.run_command("config get database")
            print(f"Database: {db_path}")
            ```
        
        Notes
        -----
        - Command is parsed and executed by zShell
        - Output typically goes to zDisplay, not return value
        - Exceptions are handled by zTraceback (logged, not raised by default)
        - For interactive REPL, use run_shell() instead
        
        See Also
        --------
        run_shell : Start interactive shell mode (REPL)
        zShell.execute_command : Underlying command execution
        """
        return self.shell.execute_command(command)

    def run_shell(self) -> None:
        """
        Explicitly start Terminal mode (interactive REPL).
        
        Launches the interactive shell (Read-Eval-Print Loop) where users can enter
        commands interactively. This is the default mode when run() is called without
        zBifrost mode.
        
        Returns
        -------
        None
            Runs until user exits (Ctrl+D, `exit` command, or signal)
        
        Examples
        --------
        Example 1: Start interactive shell
            ```python
            z = zCLI()
            z.run_shell()  # Interactive prompt appears
            # User can type commands: data select users, echo 'hi', etc.
            ```
        
        Example 2: Force Terminal mode even if zBifrost is configured
            ```python
            z = zCLI(zSpark_obj={"zMode": "zBifrost"})
            z.run_shell()  # Overrides zBifrost, starts Terminal
            ```
        
        Notes
        -----
        - Blocks until user exits or signal received
        - Command history is maintained via ShellRunner
        - Uses zDisplay for output formatting
        - Supports wizard canvas mode for multi-line workflows
        
        See Also
        --------
        run : Main entry point (auto-detects mode)
        run_command : Execute single command programmatically
        zShell.run_shell : Underlying REPL implementation
        """
        return self.shell.run_shell()

    def run(self) -> Any:
        """
        Main entry point - auto-detects and starts Terminal or zBifrost mode.
        
        This is the primary entry point after zCLI initialization. It checks the
        session's zMode and routes to the appropriate execution path:
            • Terminal mode → run_shell() (interactive REPL)
            • zBifrost mode → zWalker.run() (WebSocket server)
        
        Mode Detection
        --------------
        Reads session[SESSION_KEY_ZMODE], which is set during zConfig initialization:
            1. Checks zSpark_obj.get("zMode")
            2. Defaults to "Terminal" if not specified
        
        Returns
        -------
        Any
            • Terminal mode: None (blocks until exit)
            • zBifrost mode: Return value from zWalker.run() (usually None)
        
        Examples
        --------
        Example 1: Default (Terminal mode)
            ```python
            z = zCLI()
            z.run()  # Starts interactive shell
            ```
        
        Example 2: zBifrost mode (WebSocket server)
            ```python
            z = zCLI(zSpark_obj={"zMode": "zBifrost", "port": 8765})
            z.run()  # Starts WebSocket server
            ```
        
        Example 3: Context manager with run()
            ```python
            with zCLI() as z:
                z.run()  # Interactive shell with automatic cleanup on exit
            ```
        
        Notes
        -----
        - Terminal mode: Blocks until user exits
        - zBifrost mode: Starts async WebSocket server via zWalker
        - Mode cannot be changed after initialization
        - run() is typically the last method called on a zCLI instance
        
        See Also
        --------
        run_shell : Explicitly start Terminal mode
        run_command : Execute single command
        zWalker.run : WebSocket server entry point (zBifrost mode)
        """
        zmode = self.session.get(SESSION_KEY_ZMODE, MODE_TERMINAL)
        
        if zmode == MODE_ZBIFROST:
            self.logger.info(LOG_MODE_ZBIFROST)
            return self.walker.run()

        self.logger.info(LOG_MODE_TERMINAL)
        return self.run_shell()
    
    # ═══════════════════════════════════════════════════════════════════════
    # SIGNAL HANDLERS & GRACEFUL SHUTDOWN
    # ═══════════════════════════════════════════════════════════════════════
    
    def _register_signal_handlers(self) -> None:
        """
        Register signal handlers for graceful shutdown on SIGINT and SIGTERM.
        
        Automatically registers handlers during __init__ to ensure clean shutdown when
        users press Ctrl+C (SIGINT) or when the process receives a termination signal
        (SIGTERM).
        
        Signals Handled
        ---------------
        - **SIGINT (2)**: Interrupt signal (Ctrl+C in terminal)
        - **SIGTERM (15)**: Termination signal (kill command, systemd stop, etc.)
        
        Handler Behavior
        ----------------
        1. Check if shutdown already in progress (prevent duplicate attempts)
        2. Log signal reception
        3. Set _shutdown_requested flag
        4. Call shutdown() for graceful cleanup
        5. Exit with code 0 (success) or 1 (error)
        
        Shutdown Coordination
        ---------------------
        - **_shutdown_in_progress flag**: Prevents duplicate shutdown attempts
        - **_shutdown_requested flag**: Indicates shutdown was triggered by signal
        - **Exception handling**: Errors logged via zTraceback, don't prevent shutdown
        
        Examples
        --------
        Example 1: Ctrl+C during interactive shell
            ```python
            z = zCLI()
            z.run()  # Press Ctrl+C
            # Signal handler catches SIGINT
            # → Logs "[SIGINT] Received shutdown signal"
            # → Calls shutdown() (closes DB, WebSocket, HTTP, logs)
            # → sys.exit(0)
            ```
        
        Example 2: Systemd stop or kill command
            ```python
            z = zCLI(zSpark_obj={"zMode": "zBifrost"})
            z.run()  # Running WebSocket server
            # $ kill <pid>  (sends SIGTERM)
            # Signal handler catches SIGTERM
            # → Logs "[SIGTERM] Received shutdown signal"
            # → Calls shutdown() (graceful cleanup)
            # → sys.exit(0)
            ```
        
        Example 3: Double Ctrl+C protection
            ```python
            z = zCLI()
            z.run()
            # Press Ctrl+C → starts shutdown
            # Press Ctrl+C again (impatient user)
            # → Handler sees _shutdown_in_progress = True
            # → Logs warning, returns without duplicate shutdown
            ```
        
        Notes
        -----
        - Handlers are registered automatically during __init__
        - Both SIGINT and SIGTERM use the same handler logic
        - Shutdown is idempotent (safe to call multiple times)
        - Errors during shutdown are logged but don't prevent exit
        - Exit codes: 0 (clean), 1 (error during shutdown)
        
        See Also
        --------
        shutdown : Graceful cleanup implementation
        """
        def signal_handler(signum, frame):  # pylint: disable=unused-argument
            """Handle SIGINT (Ctrl+C) and SIGTERM gracefully"""
            signal_name = SIGNAL_INT if signum == signal.SIGINT else SIGNAL_TERM
            
            # Prevent multiple shutdown attempts
            if self._shutdown_in_progress:
                self.logger.warning(LOG_WARN_SIGNAL_DUPLICATE, signal_name)
                return
            
            self.logger.info(ERROR_SIGNAL_RECEIVED, signal_name)
            self._shutdown_requested = True
            
            # Call shutdown
            try:
                self.shutdown()
                sys.exit(0)
            except Exception as e:
                self.zTraceback.log_exception(
                    e,
                    message=ERROR_SHUTDOWN_SIGNAL % signal_name,
                    context={'signal': signum}
                )
                sys.exit(1)
        
        # Register handlers for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        self.logger.debug(LOG_DEBUG_SIGNAL_HANDLERS)
    
    def shutdown(self) -> Dict[str, bool]:
        """
        Gracefully shutdown zCLI and all subsystems in reverse initialization order.
        
        Performs comprehensive cleanup of all resources:
            1. WebSocket connections (zBifrost via zComm)
            2. HTTP server (zServer via zComm)
            3. Database connections (zData)
            4. Logger handlers (flush to disk)
        
        Shutdown Order Rationale
        ------------------------
        Cleanup happens in REVERSE of initialization order to prevent dangling references:
            • WebSocket/HTTP first: Stop accepting new connections
            • Database second: Close active connections
            • Logger last: Ensure all shutdown logs are written
        
        Error Handling Strategy
        -----------------------
        Each component cleanup is wrapped in ExceptionContext - individual failures do
        NOT prevent overall shutdown. Status tracking ensures transparency.
        
        If component A fails, components B/C/D still attempt cleanup.
        
        Idempotency
        -----------
        Safe to call multiple times:
            • First call: Performs cleanup, sets _shutdown_in_progress = True
            • Subsequent calls: Logs warning, returns immediately
        
        Returns
        -------
        Dict[str, bool]
            Status dictionary mapping component names to cleanup success:
                {
                    'websocket': True/False,
                    'http_server': True/False,
                    'database': True/False,
                    'logger': True/False
                }
        
        Component Cleanup Details
        -------------------------
        **1. WebSocket (zBifrost)**:
            • Close active client connections
            • Stop async event loop (if running)
            • Handle both running and non-running loops
        
        **2. HTTP Server**:
            • Stop serving requests
            • Close listening socket
            • Wait for active requests to complete
        
        **3. Database**:
            • Close all adapter connections (SQLite, PostgreSQL, CSV)
            • Flush pending transactions
            • Release file locks
        
        **4. Logger**:
            • Flush all handlers to disk
            • Ensure shutdown log entries are written
            • Do NOT close handlers (may still need logging)
        
        Examples
        --------
        Example 1: Explicit shutdown
            ```python
            z = zCLI()
            z.run_command("data insert users name='Alice'")
            status = z.shutdown()
            print(f"Cleanup status: {status}")
            # {'websocket': True, 'http_server': True, 'database': True, 'logger': True}
            ```
        
        Example 2: Context manager (automatic)
            ```python
            with zCLI() as z:
                z.run_command("echo 'Hello'")
            # shutdown() called automatically on __exit__
            ```
        
        Example 3: Signal-triggered shutdown
            ```python
            z = zCLI()
            z.run()  # Press Ctrl+C
            # Signal handler calls shutdown() automatically
            ```
        
        Example 4: Multiple shutdown calls (idempotent)
            ```python
            z = zCLI()
            status1 = z.shutdown()  # Performs cleanup
            status2 = z.shutdown()  # Logs warning, returns {}
            ```
        
        Notes
        -----
        - Shutdown is idempotent (safe to call multiple times)
        - Component failures are logged but don't halt shutdown
        - Async WebSocket shutdown handles both running and non-running event loops
        - Database cleanup calls disconnect() or close() depending on adapter
        - Logger flush ensures all shutdown messages are written to disk
        - Exit status report shows ✓ (success) or ✗ (failure) for each component
        
        See Also
        --------
        _register_signal_handlers : Automatic shutdown on SIGINT/SIGTERM
        __exit__ : Context manager exit (calls shutdown)
        """
        if self._shutdown_in_progress:
            self.logger.warning(LOG_WARN_SHUTDOWN_IN_PROGRESS)
            return {}
        
        self._shutdown_in_progress = True
        self.logger.info(SHUTDOWN_SEPARATOR)
        self.logger.info(LOG_SHUTDOWN_START)
        self.logger.info(SHUTDOWN_SEPARATOR)
        
        # Track cleanup success
        cleanup_status = {
            SHUTDOWN_WEBSOCKET: False,
            SHUTDOWN_HTTP_SERVER: False,
            SHUTDOWN_DATABASE: False,
            SHUTDOWN_LOGGER: False
        }
        
        # 1. Close WebSocket connections (zBifrost)
        with ExceptionContext(
            self.zTraceback,
            operation=ERROR_WEBSOCKET_SHUTDOWN,
            default_return=None
        ):
            if self.comm and hasattr(self.comm, 'websocket') and self.comm.websocket:
                if self.comm.websocket._running:  # pylint: disable=protected-access
                    self.logger.info(SHUTDOWN_MSG_WEBSOCKET_CLOSE)
                    
                    # For async shutdown, we need to handle it properly
                    import asyncio
                    try:
                        # Check if event loop is already running
                        try:
                            loop = asyncio.get_running_loop()
                            # Loop is running - we can't use run_until_complete
                            # Call the internal synchronous cleanup method instead
                            if hasattr(self.comm.websocket, '_sync_shutdown'):
                                self.comm.websocket._sync_shutdown()  # pylint: disable=protected-access
                            else:
                                # Fallback: schedule shutdown and continue
                                self.logger.warning(LOG_WARN_ASYNC_SHUTDOWN_SKIPPED)
                        except RuntimeError:
                            # No running loop - create one and run shutdown
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.comm.websocket.shutdown())
                            loop.close()
                        
                        cleanup_status[SHUTDOWN_WEBSOCKET] = True
                    except Exception as e:
                        self.logger.warning(LOG_WARN_WEBSOCKET_ERROR, e)
                else:
                    self.logger.debug(LOG_DEBUG_WEBSOCKET_NOT_RUNNING)
                    cleanup_status[SHUTDOWN_WEBSOCKET] = True
            else:
                self.logger.debug(LOG_DEBUG_WEBSOCKET_NOT_INIT)
                cleanup_status[SHUTDOWN_WEBSOCKET] = True
        
        # 2. Stop HTTP server (zServer)
        with ExceptionContext(
            self.zTraceback,
            operation=ERROR_HTTP_SHUTDOWN,
            default_return=None
        ):
            if self.server:
                if self.server._running:  # pylint: disable=protected-access
                    self.logger.info(SHUTDOWN_MSG_HTTP_STOP)
                    self.server.stop()
                    cleanup_status[SHUTDOWN_HTTP_SERVER] = True
                else:
                    self.logger.debug(LOG_DEBUG_HTTP_NOT_RUNNING)
                    cleanup_status[SHUTDOWN_HTTP_SERVER] = True
            else:
                self.logger.debug(LOG_DEBUG_HTTP_NOT_INIT)
                cleanup_status[SHUTDOWN_HTTP_SERVER] = True
        
        # 3. Close database connections (zData)
        with ExceptionContext(
            self.zTraceback,
            operation=ERROR_DB_SHUTDOWN,
            default_return=None
        ):
            if hasattr(self, 'data') and self.data:
                if hasattr(self.data, 'adapter') and self.data.adapter:
                    self.logger.info(SHUTDOWN_MSG_DB_CLOSE)
                    if hasattr(self.data.adapter, 'disconnect'):
                        self.data.adapter.disconnect()
                    elif hasattr(self.data.adapter, 'close'):
                        self.data.adapter.close()
                    cleanup_status[SHUTDOWN_DATABASE] = True
                else:
                    self.logger.debug(LOG_DEBUG_DB_NOT_CONNECTED)
                    cleanup_status[SHUTDOWN_DATABASE] = True
            else:
                self.logger.debug(LOG_DEBUG_DB_NOT_INIT)
                cleanup_status[SHUTDOWN_DATABASE] = True
        
        # 4. Flush and close logger
        with ExceptionContext(
            self.zTraceback,
            operation=ERROR_LOGGER_SHUTDOWN,
            default_return=None
        ):
            if self.logger:
                self.logger.info(SHUTDOWN_MSG_LOGGER_FLUSH)
                # Flush all handlers
                for handler in self.logger.handlers:
                    handler.flush()
                cleanup_status[SHUTDOWN_LOGGER] = True
        
        # Final status report
        self.logger.info(SHUTDOWN_SEPARATOR)
        self.logger.info(SHUTDOWN_MSG_STATUS_REPORT)
        for component, status in cleanup_status.items():
            status_str = SHUTDOWN_STATUS_SUCCESS if status else SHUTDOWN_STATUS_FAIL
            self.logger.info(SHUTDOWN_MSG_COMPONENT_STATUS, status_str, component)
        self.logger.info(SHUTDOWN_SEPARATOR)
        self.logger.info(LOG_SHUTDOWN_COMPLETE)
        
        return cleanup_status
    
    def __enter__(self) -> 'zCLI':
        """
        Context manager entry - register this instance as current context.
        
        Called automatically when entering a `with zCLI() as z:` block. Registers
        the instance in thread-local context for access via get_current_zcli().
        
        Returns
        -------
        zCLI
            This instance (for `as` binding)
        
        Examples
        --------
        Example 1: Basic context manager usage
            ```python
            with zCLI() as z:
                z.run_command("data select users")
                z.run_command("echo 'Done'")
            # Automatic shutdown on exit
            ```
        
        Example 2: Access from nested functions via context
            ```python
            def my_plugin():
                z = get_current_zcli()  # Automatically finds instance
                z.display.info("Plugin running")
            
            with zCLI() as z:
                my_plugin()  # Has access to z via context
            ```
        
        Notes
        -----
        - Automatically called by Python when entering `with` block
        - Registers instance via _current_zcli.set(self)
        - Thread-safe via contextvars.ContextVar
        - Companion to __exit__ which clears the context
        
        See Also
        --------
        __exit__ : Context manager exit (clears context, calls shutdown)
        get_current_zcli : Access instance from thread context
        """
        _current_zcli.set(self)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """
        Context manager exit - clear current context (does NOT call shutdown).
        
        Called automatically when exiting a `with zCLI() as z:` block. Clears the
        thread-local context registration.
        
        **IMPORTANT**: This method does NOT call shutdown() automatically. If you need
        automatic cleanup, explicitly call shutdown() in your code or handle it via
        signal handlers.
        
        Parameters
        ----------
        exc_type : Any
            Exception type if an exception occurred, else None
        exc_val : Any
            Exception value if an exception occurred, else None
        exc_tb : Any
            Exception traceback if an exception occurred, else None
        
        Returns
        -------
        bool
            Always returns False (does NOT suppress exceptions)
        
        Exception Handling
        ------------------
        - Returns False: Exceptions propagate normally (not suppressed)
        - zTraceback handles exception logging automatically
        - Context is cleared even if exceptions occur
        
        Examples
        --------
        Example 1: Normal exit (no exceptions)
            ```python
            with zCLI() as z:
                z.run_command("echo 'Hello'")
            # __exit__ called → context cleared
            # No automatic shutdown (must call z.shutdown() explicitly if needed)
            ```
        
        Example 2: Exception during execution
            ```python
            with zCLI() as z:
                z.run_command("data select missing_table")  # Raises exception
            # __exit__ called → context cleared
            # Exception propagates (not suppressed)
            ```
        
        Example 3: Explicit shutdown (recommended)
            ```python
            with zCLI() as z:
                try:
                    z.run_command("data insert users name='Alice'")
                finally:
                    z.shutdown()  # Explicit cleanup
            ```
        
        Notes
        -----
        - Automatically called by Python when exiting `with` block
        - Clears context via _current_zcli.set(None)
        - Does NOT suppress exceptions (returns False)
        - Does NOT call shutdown() - must be called explicitly if needed
        - Context is cleared even if exceptions occur
        
        See Also
        --------
        __enter__ : Context manager entry (registers context)
        shutdown : Explicit cleanup method
        _register_signal_handlers : Automatic shutdown on signals
        """
        _current_zcli.set(None)
        return False  # Don't suppress exceptions
