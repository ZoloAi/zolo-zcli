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
    
    def __init__(self, logger, *, zcli, config=None, port=None, host=None, serve_path=None, 
                 static_folder=None, template_folder=None, routes_file=None):
        """
        Initialize zServer subsystem (v1.5.8: Independent subsystem with config object support).
        
        Args:
            logger: zCLI logger instance
            zcli: zCLI instance (required for routing, auth, data integration)
            config: HttpServerConfig instance from zConfig (preferred, enables full integration)
            port: HTTP port (deprecated: use config object)
            host: Host address (deprecated: use config object)
            serve_path: Directory to serve files from (deprecated: use config object)
            static_folder: Static files folder (deprecated: use config object)
            template_folder: Jinja2 templates folder (deprecated: use config object)
            routes_file: Optional zServer.*.yaml file (deprecated: use config object)
        
        Note:
            Prefer using config object for full zCLI integration.
            Individual parameters supported for backward compatibility and testing.
        """
        self.logger = logger
        self.zcli = zcli
        
        # Extract configuration from config object (preferred) or individual parameters (backward compat)
        if config:
            # New pattern: config object from zConfig
            self.port = config.port
            self.host = config.host
            self.serve_path = config.serve_path
            self.routes_file = config.routes_file
        else:
            # Backward compatibility: individual parameters
            self.port = port if port is not None else 8080
            self.host = host if host is not None else "127.0.0.1"
            serve_path = serve_path if serve_path is not None else "."
            self.routes_file = routes_file
        
        self.router = None
        self.static_folder = static_folder if static_folder is not None else "static"
        self.template_folder = template_folder if template_folder is not None else "templates"
        
        # Resolve serve_path, handling case where path may not exist yet or cwd deleted
        if config:
            # Config object already has resolved path
            self.serve_path = str(Path(self.serve_path).resolve()) if self.serve_path else str(Path.cwd())
        else:
            # Backward compat: resolve the serve_path parameter
            try:
                self.serve_path = str(Path(serve_path).resolve())
            except (FileNotFoundError, OSError):
                # Path doesn't exist or cwd deleted (common in test cleanup) - use path as-is
                # If relative, it will be relative to wherever we are when server starts
                self.serve_path = str(Path(serve_path))
        
        # Auto-detect zServer routes file if not provided (v1.5.7: Convention over configuration)
        if not routes_file:
            routes_file = self._auto_detect_routes_file()
            if routes_file:
                self.routes_file = routes_file
                self.logger.info(f"[zServer] Auto-detected routes file: {routes_file}")
        
        # Load routes if provided or auto-detected (v1.5.4 Phase 2)
        if routes_file and zcli:
            self._load_routes()
        
        self.server = None
        self.thread = None
        self._running = False
        self.gunicorn_manager = None  # For Production mode
        
        self.logger.info(f"[zServer] Initialized - will serve from: {self.serve_path}")
        self.logger.info(f"[zServer] Static folder: {self.static_folder}/")
        self.logger.info(f"[zServer] Template folder: {self.template_folder}/")
        if self.router:
            self.logger.info(f"[zServer] Declarative routing enabled: {routes_file}")
    
    def _auto_detect_routes_file(self):
        """
        Auto-detect zServer routing file in serve_path (v1.5.7: Convention over configuration).
        
        Scans serve_path for zServer.*.yaml files following zCLI zVaFile conventions.
        Convention: zServer zVaFile should be in the same folder as the application entry point.
        
        Returns:
            str: Path to detected routes file, or None if not found
        """
        import glob
        
        try:
            # Look for zServer.*.yaml files in serve_path
            pattern = os.path.join(self.serve_path, "zServer.*.yaml")
            matches = glob.glob(pattern)
            
            if matches:
                if len(matches) > 1:
                    self.logger.warning(f"[zServer] Multiple routes files found: {matches}")
                    self.logger.warning(f"[zServer] Using first match: {matches[0]}")
                
                # Return relative path if possible
                routes_file = os.path.basename(matches[0])
                return routes_file
            
            self.logger.framework.debug("[zServer] No zServer.*.yaml file found - static serving only")
            return None
            
        except Exception as e:
            self.logger.framework.debug(f"[zServer] Auto-detection failed: {e}")
            return None
    
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
    
    def _get_deployment(self) -> str:
        """
        Get deployment mode from zCLI config.
        
        Returns:
            str: Deployment mode ("Development", "Testing", or "Production")
        """
        if not self.zcli or not hasattr(self.zcli, 'config'):
            return "Development"
        return self.zcli.config.get_environment("deployment", "Development")
    
    def start(self):
        """
        Start HTTP server (deployment-aware).
        
        Behavior based on zSpark.deployment:
        - "Development"/"Testing" → http.server (background thread)
        - "Production" → Gunicorn (subprocess)
        
        Raises:
            RuntimeError: If server is already running
            OSError: If port is already in use or Gunicorn not installed
        
        Example:
            ```python
            # Development mode
            z = zCLI({"deployment": "Development", "http_server": {"port": 8000}})
            server = z.comm.create_http_server()
            server.start()  # Starts http.server
            
            # Production mode
            z = zCLI({"deployment": "Production", "http_server": {"port": 8000}})
            server = z.comm.create_http_server()
            server.start()  # Starts Gunicorn automatically
            ```
        """
        if self._running or (self.gunicorn_manager and self.gunicorn_manager.is_running()):
            self.logger.warning("[zServer] Server is already running")
            return
        
        # Check deployment mode and route to correct server type
        deployment = self._get_deployment().lower()
        
        if deployment == "production":
            self._start_production()
        else:
            self._start_development()
    
    def _start_production(self):
        """
        Start Gunicorn subprocess (Production mode).
        
        Creates a WSGI module and starts Gunicorn to serve it.
        """
        from .zServer_modules.gunicorn_manager import GunicornManager
        
        # Create temporary WSGI module for Gunicorn
        self._create_wsgi_module()
        
        # Start Gunicorn
        self.gunicorn_manager = GunicornManager(
            app_module="_zserver_wsgi_temp:app",
            host=self.host,
            port=self.port,
            workers=4,
            logger=self.logger
        )
        
        try:
            self.gunicorn_manager.start()
            self._running = True
        except Exception as e:
            self.logger.error(f"[zServer] Failed to start Gunicorn: {e}")
            self.gunicorn_manager = None
            raise
    
    def _start_development(self):
        """
        Start http.server thread (Development/Testing mode).
        
        This is the existing http.server logic.
        """
        
        # Save and change to serve directory
        try:
            original_dir = os.getcwd()
        except FileNotFoundError:
            original_dir = self.serve_path  # Fall back if getcwd fails
        
        os.chdir(self.serve_path)
        
        self.logger.info("[zServer] Starting in Development mode (http.server)...")
        
        try:
            # Create handler with logger, router, and folder conventions (v1.5.5)
            handler = partial(
                LoggingHTTPRequestHandler, 
                logger=self.logger, 
                router=self.router,
                static_folder=self.static_folder,
                template_folder=self.template_folder,
                serve_path=self.serve_path
            )
            
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
    
    def _create_wsgi_module(self):
        """
        Create temporary WSGI module for Gunicorn to import.
        
        Generates a self-contained Python file that Gunicorn workers can import
        and use to create the WSGI app with proper routing and configuration.
        """
        import json
        
        # Serialize configuration for the WSGI module
        config = {
            'serve_path': self.serve_path,
            'static_folder': self.static_folder,
            'template_folder': self.template_folder,
            'routes_file': self.routes_file,
        }
        
        wsgi_content = f'''# Auto-generated WSGI module for zServer Production mode
# DO NOT EDIT - Generated by zCLI

import sys
import os

# Configuration from zServer
CONFIG = {json.dumps(config, indent=4)}

# Set working directory to serve_path
serve_path = CONFIG['serve_path']
if os.path.exists(serve_path):
    os.chdir(serve_path)

# Create WSGI app using zServer's WSGI adapter
from zCLI.subsystems.zServer.zServer_modules.wsgi_app import zServerWSGIApp

# Create a minimal zServer-like object with the configuration
class WSGIServerConfig:
    def __init__(self, config):
        self.serve_path = config['serve_path']
        self.static_folder = config['static_folder']
        self.template_folder = config['template_folder']
        self.routes_file = config['routes_file']
        self.router = None
        self.logger = None
        
        # Load routes if routes_file is provided
        if self.routes_file:
            self._load_routes()
    
    def _load_routes(self):
        """Load routes from YAML file."""
        try:
            import yaml
            from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
            from zCLI.utils.logger import ConsoleLogger
            
            # Create minimal logger for WSGI
            self.logger = ConsoleLogger()
            
            # Parse YAML file directly
            with open(self.routes_file, 'r') as f:
                routes_data = yaml.safe_load(f)
            
            # Create router (zcli=None since we don't need auth in this minimal setup)
            self.router = HTTPRouter(routes_data, zcli=None, logger=self.logger)
            
        except Exception as e:
            print(f"[WSGI] Failed to load routes: {{e}}")
            import traceback
            traceback.print_exc()

# Create server config and WSGI app
server_config = WSGIServerConfig(CONFIG)
app = zServerWSGIApp(server_config)
'''
        
        # Write WSGI module
        with open("_zserver_wsgi_temp.py", "w") as f:
            f.write(wsgi_content)
        
        self.logger.debug("[zServer] Created WSGI module: _zserver_wsgi_temp.py")
    
    def wait(self):
        """
        Block until server is interrupted (v1.5.8: Built-in lifecycle management).
        
        Keeps the process alive while the server runs. Signal handlers (SIGINT/SIGTERM)
        registered by zCLI will automatically call shutdown, which stops the server.
        
        This eliminates boilerplate try/except/KeyboardInterrupt blocks in applications.
        
        Example:
            ```python
            # OLD (manual lifecycle)
            z = zCLI(zSpark)
            server = z.comm.create_http_server()
            server.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
            
            # NEW (built-in lifecycle)
            z = zCLI({"zServer": {"enabled": True, "port": 8080}})
            z.server.wait()  # That's it! Signal handlers handle cleanup
            ```
        
        Note:
            - Signal handlers (Ctrl+C, SIGTERM) already registered by zCLI
            - zCLI.shutdown() automatically calls server.stop()
            - This method just keeps the process alive
        """
        import time
        
        if not self._running and not (self.gunicorn_manager and self.gunicorn_manager.is_running()):
            self.logger.warning("[zServer] Server is not running, nothing to wait for")
            return
        
        try:
            while self._running or (self.gunicorn_manager and self.gunicorn_manager.is_running()):
                time.sleep(1)
        except KeyboardInterrupt:
            # Signal handler will call shutdown, which calls stop()
            # Just exit gracefully
            pass
    
    def stop(self):
        """Stop HTTP server (works in all modes)."""
        deployment = self._get_deployment().lower()
        
        if deployment == "production":
            # Stop Gunicorn
            if self.gunicorn_manager:
                self.gunicorn_manager.stop()
                self.gunicorn_manager = None
            
            # Clean up WSGI module
            try:
                if os.path.exists("_zserver_wsgi_temp.py"):
                    os.remove("_zserver_wsgi_temp.py")
                if os.path.exists("_zserver_wsgi_temp.pyc"):
                    os.remove("_zserver_wsgi_temp.pyc")
            except Exception as e:
                self.logger.warning(f"[zServer] Could not remove WSGI temp file: {e}")
            
            self._running = False
            self.logger.info("[zServer] Production server stopped")
        
        else:
            # Stop http.server
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
        """Check if server is running (works in all modes)."""
        if self.gunicorn_manager:
            return self.gunicorn_manager.is_running()
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

