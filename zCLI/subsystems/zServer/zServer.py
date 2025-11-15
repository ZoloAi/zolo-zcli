# zCLI/subsystems/zServer/zServer.py

"""
zServer - Lightweight HTTP Static File Server

Serves static files using Python's built-in http.server.
Designed to work standalone or alongside zBifrost WebSocket server.
"""

from http.server import HTTPServer
import threading
import os
from pathlib import Path
from functools import partial

from .zServer_modules.handler import LoggingHTTPRequestHandler


class zServer:
    """
    Lightweight HTTP static file server
    
    Features:
    - Serves static files (HTML, CSS, JS)
    - Runs in background thread
    - Integrates with zCLI logger
    - CORS enabled for local development
    - Directory listing disabled for security
    """
    
    def __init__(self, logger, *, zcli=None, port=8080, host="127.0.0.1", serve_path=".", routes_file=None):
        """
        Initialize zServer (v1.5.4 Phase 2: Added declarative routing)
        
        Args:
            logger: zCLI logger instance
            zcli: zCLI instance (optional, required for routing with RBAC)
            port: HTTP port (default: 8080)
            host: Host address (default: 127.0.0.1)
            serve_path: Directory to serve files from (default: current directory)
            routes_file: Optional zServer.*.yaml file for declarative routing
        """
        self.logger = logger
        self.zcli = zcli
        self.port = port
        self.host = host
        self.routes_file = routes_file
        self.router = None
        
        # Resolve serve_path, handling case where path may not exist yet or cwd deleted
        try:
            self.serve_path = str(Path(serve_path).resolve())
        except (FileNotFoundError, OSError):
            # Path doesn't exist or cwd deleted (common in test cleanup) - use path as-is
            # If relative, it will be relative to wherever we are when server starts
            self.serve_path = str(Path(serve_path))
        
        # Load routes if provided (v1.5.4 Phase 2)
        if routes_file and zcli:
            self._load_routes()
        
        self.server = None
        self.thread = None
        self._running = False
        
        self.logger.info(f"[zServer] Initialized - will serve from: {self.serve_path}")
        if self.router:
            self.logger.info(f"[zServer] Declarative routing enabled: {routes_file}")
    
    def _load_routes(self):
        """
        Load routing configuration from zServer.*.yaml file (v1.5.4 Phase 2).
        
        Uses zParser to load and parse routing file directly (bypassing zLoader's
        zPath decoder to avoid dot interpretation in filenames like zServer.routes.yaml).
        """
        try:
            # Load file directly using zParser (bypass zLoader's zPath decoder)
            # This avoids interpreting dots in "zServer.routes.yaml" as path separators
            from ..zParser.parser_modules import parse_file_content
            from ..zLoader.loader_modules import load_file_raw
            
            # Read raw file content
            raw_content = load_file_raw(self.routes_file, self.logger)
            
            # Parse content (zParser will detect zServer in path and parse as server file)
            routes_data = parse_file_content(
                raw_content,
                self.logger,
                file_extension=".yaml",
                file_path=self.routes_file
            )
            
            if routes_data and routes_data.get("type") == "server":
                # Import router (lazy import to avoid circular dependency)
                from .zServer_modules.router import HTTPRouter
                self.router = HTTPRouter(routes_data, self.zcli, self.logger)
                self.logger.info(f"[zServer] Loaded routes from: {self.routes_file}")
            else:
                self.logger.warning(f"[zServer] Invalid routes file: {self.routes_file}")
        except Exception as e:
            self.logger.error(f"[zServer] Failed to load routes: {e}")
            # Continue without router (fallback to static serving)
    
    def start(self):
        """
        Start HTTP server in background thread
        
        Raises:
            RuntimeError: If server is already running
            OSError: If port is already in use
        """
        if self._running:
            self.logger.warning("[zServer] Server is already running")
            return
        
        # Save and change to serve directory
        try:
            original_dir = os.getcwd()
        except FileNotFoundError:
            original_dir = self.serve_path  # Fall back if getcwd fails
        
        os.chdir(self.serve_path)
        
        try:
            # Create handler with logger and router (v1.5.4 Phase 2)
            handler = partial(LoggingHTTPRequestHandler, logger=self.logger, router=self.router)
            
            # Create HTTP server
            self.server = HTTPServer((self.host, self.port), handler)
            self._running = True
            
            # Start server in background thread
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            
            self.logger.info(f"[zServer] HTTP server started at http://{self.host}:{self.port}")
            self.logger.info(f"[zServer] Serving files from: {self.serve_path}")
            
        except OSError as e:
            self._running = False
            os.chdir(original_dir)
            if e.errno == 48:  # Address already in use
                error_msg = f"[zServer] Port {self.port} already in use"
                self.logger.error(error_msg)
                raise OSError(error_msg) from e
            raise
        except Exception as e:
            self._running = False
            os.chdir(original_dir)
            self.logger.error(f"[zServer] Failed to start: {e}")
            raise
        finally:
            # Return to original directory if server failed to start
            if not self._running:
                os.chdir(original_dir)
    
    def _run_server(self):
        """Run server (called in background thread)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"[zServer] Server error: {e}")
        finally:
            self._running = False
    
    def stop(self):
        """Stop HTTP server"""
        if not self._running:
            self.logger.warning("[zServer] Server is not running")
            return
        
        if self.server:
            self.logger.info("[zServer] Stopping HTTP server...")
            
            # Mark as not running first to prevent new requests
            self._running = False
            
            # Shutdown must be called from a different thread to avoid deadlock
            import threading
            shutdown_thread = threading.Thread(target=self.server.shutdown)
            shutdown_thread.daemon = True
            shutdown_thread.start()
            shutdown_thread.join(timeout=2)
            
            # Close the server socket
            self.server.server_close()
            
            # Wait for server thread to finish
            if self.thread:
                self.thread.join(timeout=2)
            
            self.logger.info("[zServer] HTTP server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self._running
    
    def get_url(self):
        """Get server URL"""
        return f"http://{self.host}:{self.port}"
    
    def health_check(self):
        """
        Get health status of HTTP server
        
        Returns:
            dict: Server health status with keys:
                - running (bool): Whether server is running
                - host (str): Server host address
                - port (int): Server port
                - url (str|None): Server URL (None if not running)
                - serve_path (str): Directory being served
        """
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "url": self.get_url() if self._running else None,
            "serve_path": self.serve_path
        }

