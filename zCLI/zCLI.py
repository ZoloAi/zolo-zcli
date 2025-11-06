# zCLI/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Single source of truth for all subsystems."""

import signal
import sys
import contextvars
from zCLI.utils.zTraceback import ExceptionContext

# Global context variable for current zCLI instance (thread-safe, async-safe)
# Follows Django/Flask/FastAPI pattern for request/application context
_current_zcli: contextvars.ContextVar = contextvars.ContextVar('current_zcli', default=None)


def get_current_zcli():
    """Get the current zCLI instance (thread-safe).
    
    Returns:
        zCLI instance or None if not in a zCLI context.
    
    Usage:
        zcli = get_current_zcli()
        if zcli:
            zcli.display.info("Using current zCLI context")
    """
    return _current_zcli.get()

class zCLI:
    """Core zCLI Engine managing all subsystems 
    Supporting two primary modes: Terminal and zBifrost."""
    
    # Attributes set by subsystems
    logger: any  # Set by zConfig
    session: dict  # Set by zConfig
    zTraceback: any  # Set by zConfig

    def __init__(self, zSpark_obj=None):
        """Initialize zCLI instance -
        with optional zSpark_obj config dict."""

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
            self.logger.info("HTTP server auto-started at %s", self.server.get_url())

        # Initialize session (sets zMode from zSpark_obj or defaults to Terminal)
        self._init_session()
        
        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()
        
        # Note: zAuth database is workspace-relative (@), ensuring each zCLI instance
        # is fully isolated. Auth DB lazy-loads on first save_session() or grant_permission().
        # This preserves the "no global state" principle - the secret sauce of zCLI architecture.

        self.logger.info("zCLI Core initialized - Mode: %s", self.session.get("zMode"))

    def _load_plugins(self):
        """ Load utility plugins (Python modules) from zSpark_obj if provided.
            Uses zUtils, not zLoader."""
        try:
            plugin_paths = self.zspark_obj.get("plugins") or []
            if isinstance(plugin_paths, (list, tuple)):
                self.utils.load_plugins(plugin_paths)
            elif isinstance(plugin_paths, str):
                self.utils.load_plugins([plugin_paths])
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.warning("Failed to load plugins: %s", e)

    def _init_session(self):
        """
        Initialize session with zS_id and zMode.
        Session already has zMode from zConfig - we just set the ID here.
        """
        # Set session ID - always required
        self.session["zS_id"] = self.config.session.generate_id("zS")

        # zMode was already set by zConfig.session.detect_zMode() during session creation
        # It checks zSpark_obj.get("zMode") and defaults to "Terminal"
        # No need to override it here

        self.logger.debug("Session initialized:")
        self.logger.debug("  zS_id: %s", self.session["zS_id"])
        self.logger.debug("  zMode: %s", self.session["zMode"])
        self.logger.debug("  zMachine hostname: %s", self.session["zMachine"].get("hostname"))

    # ───────────────────────────────────────────────────────────────
    # Public API Methods
    # ───────────────────────────────────────────────────────────────

    def run_command(self, command: str):
        """Execute single command string. Returns command result."""
        return self.shell.execute_command(command)

    def run_shell(self):
        """Explicitly run shell mode."""
        return self.shell.run_shell()

    def run(self):
        """Main entry point - determines whether to run in zBifrost mode or Terminal mode."""
        zmode = self.session.get("zMode", "Terminal")
        
        if zmode == "zBifrost":
            self.logger.info("Starting zCLI in zBifrost mode via zWalker...")
            return self.walker.run()

        self.logger.info("Starting zCLI in Terminal mode...")
        return self.run_shell()
    
    # ───────────────────────────────────────────────────────────────
    # Signal Handlers & Graceful Shutdown
    # ───────────────────────────────────────────────────────────────
    
    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            """Handle SIGINT (Ctrl+C) and SIGTERM gracefully"""
            signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
            
            # Prevent multiple shutdown attempts
            if self._shutdown_in_progress:
                self.logger.warning(f"[{signal_name}] Shutdown already in progress...")
                return
            
            self.logger.info(f"[{signal_name}] Received shutdown signal")
            self._shutdown_requested = True
            
            # Call shutdown
            try:
                self.shutdown()
                sys.exit(0)
            except Exception as e:
                self.zTraceback.log_exception(
                    e,
                    message=f"Error during {signal_name} shutdown",
                    context={'signal': signum}
                )
                sys.exit(1)
        
        # Register handlers for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        self.logger.debug("Signal handlers registered (SIGINT, SIGTERM)")
    
    def shutdown(self):
        """
        Gracefully shutdown zCLI and all subsystems
        
        Performs cleanup in reverse initialization order:
        1. Close WebSocket connections (zBifrost)
        2. Stop HTTP server (zServer)
        3. Close database connections (zData)
        4. Flush and close logger
        
        Uses zTraceback for consistent error handling - individual
        component failures do not prevent overall shutdown.
        """
        if self._shutdown_in_progress:
            self.logger.warning("[Shutdown] Shutdown already in progress")
            return
        
        self._shutdown_in_progress = True
        self.logger.info("=" * 70)
        self.logger.info("[Shutdown] Initiating graceful shutdown...")
        self.logger.info("=" * 70)
        
        # Track cleanup success
        cleanup_status = {
            'websocket': False,
            'http_server': False,
            'database': False,
            'logger': False
        }
        
        # 1. Close WebSocket connections (zBifrost)
        with ExceptionContext(
            self.zTraceback,
            operation="WebSocket shutdown",
            default_return=None
        ):
            if self.comm and hasattr(self.comm, 'websocket') and self.comm.websocket:
                if self.comm.websocket._running:
                    self.logger.info("[Shutdown] Closing WebSocket server...")
                    
                    # For async shutdown, we need to handle it properly
                    import asyncio
                    try:
                        # Check if event loop is already running
                        try:
                            loop = asyncio.get_running_loop()
                            # Loop is running - we can't use run_until_complete
                            # Call the internal synchronous cleanup method instead
                            if hasattr(self.comm.websocket, '_sync_shutdown'):
                                self.comm.websocket._sync_shutdown()
                            else:
                                # Fallback: schedule shutdown and continue
                                self.logger.warning("[Shutdown] Async shutdown skipped (loop running)")
                        except RuntimeError:
                            # No running loop - create one and run shutdown
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.comm.websocket.shutdown())
                            loop.close()
                        
                        cleanup_status['websocket'] = True
                    except Exception as e:
                        self.logger.warning(f"[Shutdown] WebSocket cleanup error: {e}")
                else:
                    self.logger.debug("[Shutdown] WebSocket server not running")
                    cleanup_status['websocket'] = True
            else:
                self.logger.debug("[Shutdown] WebSocket server not initialized")
                cleanup_status['websocket'] = True
        
        # 2. Stop HTTP server (zServer)
        with ExceptionContext(
            self.zTraceback,
            operation="HTTP server shutdown",
            default_return=None
        ):
            if self.server:
                if self.server._running:
                    self.logger.info("[Shutdown] Stopping HTTP server...")
                    self.server.stop()
                    cleanup_status['http_server'] = True
                else:
                    self.logger.debug("[Shutdown] HTTP server not running")
                    cleanup_status['http_server'] = True
            else:
                self.logger.debug("[Shutdown] HTTP server not initialized")
                cleanup_status['http_server'] = True
        
        # 3. Close database connections (zData)
        with ExceptionContext(
            self.zTraceback,
            operation="Database connection cleanup",
            default_return=None
        ):
            if hasattr(self, 'data') and self.data:
                if hasattr(self.data, 'handler') and self.data.handler:
                    self.logger.info("[Shutdown] Closing database connections...")
                    if hasattr(self.data.handler, 'close'):
                        self.data.handler.close()
                    cleanup_status['database'] = True
                else:
                    self.logger.debug("[Shutdown] No active database connections")
                    cleanup_status['database'] = True
            else:
                self.logger.debug("[Shutdown] Database subsystem not initialized")
                cleanup_status['database'] = True
        
        # 4. Flush and close logger
        with ExceptionContext(
            self.zTraceback,
            operation="Logger cleanup",
            default_return=None
        ):
            if self.logger:
                self.logger.info("[Shutdown] Flushing logger...")
                # Flush all handlers
                for handler in self.logger.handlers:
                    handler.flush()
                cleanup_status['logger'] = True
        
        # Final status report
        self.logger.info("=" * 70)
        self.logger.info("[Shutdown] Cleanup Status:")
        for component, status in cleanup_status.items():
            status_str = "✓" if status else "✗"
            self.logger.info(f"  {status_str} {component}")
        self.logger.info("=" * 70)
        self.logger.info("[Shutdown] Graceful shutdown complete")
        
        return cleanup_status
    
    def __enter__(self):
        """Context manager entry - register this instance as current."""
        _current_zcli.set(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clear current instance."""
        _current_zcli.set(None)
        return False  # Don't suppress exceptions
