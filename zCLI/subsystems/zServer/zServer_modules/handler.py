# zCLI/subsystems/zServer/zServer_modules/handler.py

"""
Custom HTTP request handler with logging integration
"""

from http.server import SimpleHTTPRequestHandler
import os


class LoggingHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with zCLI logger integration + routing (v1.5.5: Flask conventions)"""
    
    def __init__(self, *args, logger=None, router=None, static_folder="static", template_folder="templates", ui_folder="UI", serve_path=".", **kwargs):
        self.zcli_logger = logger
        self.router = router  # HTTPRouter instance (optional)
        self.static_folder = static_folder  # Flask convention: static files folder
        self.template_folder = template_folder  # Flask convention: templates folder
        self.ui_folder = ui_folder  # zUI zVaF files folder
        self.serve_path = serve_path  # Base directory for serving files
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use zCLI logger instead of stderr"""
        if self.zcli_logger:
            self.zcli_logger.info(f"[zServer] {self.address_string()} - {format % args}")
        else:
            # Fallback to default behavior if no logger
            super().log_message(format, *args)
    
    def end_headers(self):
        """Add CORS headers for local development"""
        # Allow local development access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.end_headers()
    
    def list_directory(self, path):
        """Disable directory listing for security"""
        self.send_error(403, "Directory listing is disabled")
        return None
    
    def do_GET(self):
        """
        Handle GET requests with Flask-like conventions (v1.5.5).
        
        Flow:
            1. Check for favicon.ico and serve default if not found
            2. Check for /static/* and auto-serve from static_folder
            3. Check for /UI/* and auto-serve from ui_folder (zVaF files)
            4. If router exists: Use declarative routing
            5. Otherwise: Fallback to static file serving (current behavior)
        """
        # Handle favicon.ico with default zolo favicon
        if self.path == '/favicon.ico':
            return self._serve_default_favicon()
        
        # Auto-serve /static/* from static_folder (Flask convention)
        if self.path.startswith('/static/'):
            return self._serve_static_file()
        
        # Auto-serve /UI/* from ui_folder (zUI zVaF files) - case-sensitive to match folder
        ui_prefix = f'/{self.ui_folder}/'
        if self.path.startswith(ui_prefix) or self.path.lower().startswith(ui_prefix.lower()):
            return self._serve_ui_file()
        
        # Check if router exists (declarative routing mode)
        if self.router:
            return self._handle_routed_request()
        
        # Fallback: Static file serving (backward compatible)
        return super().do_GET()
    
    def do_POST(self):
        """
        Handle POST requests for forms and APIs (v1.5.7 Phase 1.2).
        
        Flow:
            1. If router exists: Use declarative routing
            2. Otherwise: Return 405 Method Not Allowed
        """
        # Check if router exists (declarative routing mode)
        if self.router:
            return self._handle_routed_request()
        
        # No router - POST not supported
        return self.send_error(405, "POST not supported without routing")
    
    def _serve_default_favicon(self):
        """Serve default zolo favicon from zServer static folder"""
        import os
        
        # Path to default favicon in zServer static folder
        zserver_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        favicon_path = os.path.join(zserver_dir, 'static', 'favicon.ico')
        
        if not os.path.exists(favicon_path):
            # No default favicon, return 404
            return self.send_error(404, "Favicon not found")
        
        try:
            with open(favicon_path, 'rb') as f:
                favicon_data = f.read()
            
            self.send_response(200)
            self.send_header("Content-type", "image/x-icon")
            self.send_header("Content-length", len(favicon_data))
            self.send_header("Cache-Control", "public, max-age=86400")  # Cache for 1 day
            self.end_headers()
            self.wfile.write(favicon_data)
            
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Error serving favicon: {e}")
            return self.send_error(500, f"Error serving favicon: {str(e)}")
    
    def _serve_static_file(self):
        """
        Auto-serve files from /static/* (Flask convention).
        
        Maps /static/js/hello.js → {serve_path}/static/js/hello.js
        """
        import os
        import mimetypes
        from urllib.parse import unquote
        
        # Remove /static/ prefix to get relative path
        relative_path = self.path[8:]  # Remove '/static/'
        
        # Decode URL encoding (e.g., %20 → space)
        relative_path = unquote(relative_path)
        
        # Build absolute path: {serve_path}/{static_folder}/{relative_path}
        file_path = os.path.join(os.getcwd(), self.static_folder, relative_path)
        
        # Security: Prevent directory traversal
        file_path = os.path.abspath(file_path)
        static_root = os.path.abspath(os.path.join(os.getcwd(), self.static_folder))
        
        if not file_path.startswith(static_root):
            return self.send_error(403, "Access denied")
        
        # Check if file exists
        if not os.path.exists(file_path):
            return self.send_error(404, f"File not found: {self.path}")
        
        # Check if it's a directory (not allowed)
        if os.path.isdir(file_path):
            return self.send_error(403, "Directory listing is disabled")
        
        # Serve the file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-length", len(content))
            self.send_header("Cache-Control", "public, max-age=3600")  # Cache for 1 hour
            self.end_headers()
            self.wfile.write(content)
            
            if self.zcli_logger:
                self.zcli_logger.debug(f"[Handler] Served static file: {self.path}")
            
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Error serving static file: {e}")
            return self.send_error(500, f"Error serving file: {str(e)}")
    
    def _serve_ui_file(self):
        """
        Auto-serve zVaF files from /UI/* (zUI convention).
        
        Maps /UI/zUI.index.yaml → {serve_path}/UI/zUI.index.yaml
        """
        import os
        import mimetypes
        from urllib.parse import unquote
        
        # Remove /UI/ prefix to get relative path (case-insensitive match)
        ui_prefix = f'/{self.ui_folder}/'
        ui_prefix_len = len(ui_prefix)
        
        # Handle both exact case and lowercase URLs
        if self.path.startswith(ui_prefix):
            relative_path = self.path[ui_prefix_len:]
        else:
            # Case-insensitive fallback
            relative_path = self.path[ui_prefix_len:]
        
        # Decode URL encoding (e.g., %20 → space)
        relative_path = unquote(relative_path)
        
        # Build absolute path: {serve_path}/{ui_folder}/{relative_path}
        file_path = os.path.join(os.getcwd(), self.ui_folder, relative_path)
        
        # Security: Prevent directory traversal
        file_path = os.path.abspath(file_path)
        ui_root = os.path.abspath(os.path.join(os.getcwd(), self.ui_folder))
        
        if not file_path.startswith(ui_root):
            return self.send_error(403, "Access denied")
        
        # Check if file exists
        if not os.path.exists(file_path):
            return self.send_error(404, f"UI file not found: {self.path}")
        
        # Check if it's a directory (not allowed)
        if os.path.isdir(file_path):
            return self.send_error(403, "Directory listing is disabled")
        
        # Serve the YAML file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Force YAML content type
            content_type = 'application/x-yaml'
            
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-length", len(content.encode('utf-8')))
            self.send_header("Cache-Control", "no-cache")  # Don't cache UI files during development
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
            if self.zcli_logger:
                self.zcli_logger.debug(f"[Handler] Served UI file: {self.path}")
            
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Error serving UI file: {e}")
            return self.send_error(500, f"Error serving UI file: {str(e)}")
    
    def _handle_routed_request(self):
        """Handle request using HTTPRouter with RBAC enforcement"""
        # Match route
        route = self.router.match_route(self.path)
        if not route:
            # No route found - 404
            return self.send_error(404, "Route not found")
        
        # Check RBAC
        has_access, error_page = self.router.check_access(route)
        if not has_access:
            # Access denied - serve error page
            if error_page:
                # Try to serve error page
                self.path = f"/{error_page}"
                return super().do_GET()
            else:
                # Fallback to HTTP 403
                return self.send_error(403, "Access Denied")
        
        # Access granted - serve based on route type
        route_type = route.get("type", "static")
        
        if route_type == "static":
            # Serve static file directly
            file_path = self.router.resolve_file_path(route)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return self.send_error(404, f"File not found: {file_path}")
            
            # Check if it's a directory (not allowed for static routes)
            if os.path.isdir(file_path):
                return self.send_error(403, "Directory listing is disabled")
            
            # Serve the file directly
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                import mimetypes
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content)
                
            except Exception as e:
                if hasattr(self, 'zcli_logger') and self.zcli_logger:
                    self.zcli_logger.error(f"[Handler] Error serving static file: {e}")
                return self.send_error(500, f"Error serving file: {str(e)}")
        
        elif route_type == "content":
            # Serve inline HTML content (like Flask return "<h1>...</h1>")
            return self._handle_content_route(route)
        
        elif route_type == "template":
            # Serve Jinja2 template (like Flask render_template())
            return self._handle_template_route(route)
        
        elif route_type == "zWalker":
            # zWalker: Execute zVaF blocks via zWalker (server-side rendering)
            return self._handle_zwalker_route(route)
        
        elif route_type == "form":
            # Handle declarative web form (zDialog pattern - v1.5.7)
            return self._handle_form_route(route)
        
        elif route_type == "json":
            # Handle declarative JSON response (v1.5.7)
            return self._handle_json_route(route)
        
        elif route_type == "dynamic":
            # Serve dynamically generated HTML from zUI
            return self._handle_dynamic_route(route)
        
        # Unknown route type
        return self.send_error(501, f"Route type '{route_type}' not supported")
    
    def _handle_content_route(self, route: dict):
        """
        Handle content route - serve inline HTML string (like Flask return "<h1>...</h1>").
        
        Args:
            route: Route definition with "content" field
        
        Returns:
            None: Sends HTTP response directly
        """
        try:
            # Extract HTML content from route
            html_content = route.get("content", "")
            
            if not html_content:
                return self.send_error(500, "Content route missing 'content' field")
            
            # Send HTML response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(html_content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            # Log error and send 500
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Content route error: {e}")
            return self.send_error(500, f"Content serving failed: {str(e)}")
    
    def _handle_template_route(self, route: dict):
        """
        Handle template route - render Jinja2 template (like Flask render_template()).
        
        Now zWalker-aware: If route has zVaFile, it will be converted to URL and injected
        into template context for client-side loading (mixed mode support).
        
        Args:
            route: Route definition with "template" field and optional "context" dict
        
        Returns:
            None: Sends HTTP response directly
        """
        try:
            template_name = route.get("template", "")
            if not template_name:
                return self.send_error(500, "Template route missing 'template' field")
            
            # Get context data (variables to pass to template)
            context = route.get("context", {})
            
            # Get zcli instance from router
            if not hasattr(self.router, 'zcli'):
                return self.send_error(500, "zCLI instance not available")
            
            # Auto-inject zSession values (zVaFile, zVaFolder, zBlock) into context
            # so templates can render them without manual Jinja plumbing
            zcli = self.router.zcli
            if hasattr(zcli, 'session') and zcli.session:
                # Only inject if not already present in route context
                if "zVaFile" not in context:
                    context["zVaFile"] = zcli.session.get("zVaFile")
                if "zVaFolder" not in context:
                    context["zVaFolder"] = zcli.session.get("zVaFolder")
                if "zBlock" not in context:
                    context["zBlock"] = zcli.session.get("zBlock")
                
                # Debug: log what we got from zSession
                if self.zcli_logger:
                    self.zcli_logger.info(f"[Handler] Auto-injected from zSession: zVaFile={context.get('zVaFile')}, zVaFolder={context.get('zVaFolder')}, zBlock={context.get('zBlock')}")
            
            # zUI support: Convert zVaFile to URL if present (mixed mode)
            zVaFile = route.get("zVaFile")
            if zVaFile:
                ui_file_path = self._convert_zpath_to_url(zVaFile)
                context["zVaFile"] = ui_file_path
                if self.zcli_logger:
                    self.zcli_logger.debug(f"[Handler] Template with zVaFile: {ui_file_path}")
            
            # Get templates directory from serve_path (Flask convention)
            import os
            from jinja2 import Environment, FileSystemLoader, TemplateNotFound
            
            templates_dir = os.path.join(self.serve_path, self.template_folder)
            
            # Create Jinja2 environment
            env = Environment(loader=FileSystemLoader(templates_dir))
            
            # Render template
            template = env.get_template(template_name)
            html_content = template.render(**context)
            
            # Auto-inject zUI config script before </head> (if zSession values present)
            # This makes zBifrost/zSession integration automatic for HTML authors
            zui_config_values = {
                "zVaFile": context.get("zVaFile"),
                "zVaFolder": context.get("zVaFolder"),
                "zBlock": context.get("zBlock")
            }
            # Only inject if at least one value is present (not all None)
            if any(v is not None for v in zui_config_values.values()):
                import json
                zui_config_json = json.dumps(zui_config_values, indent=4)
                zui_config_script = f'\n<!-- zUI Config (auto-injected from zSession) -->\n<script id="zui-config" type="application/json">\n{zui_config_json}\n</script>\n</head>'
                html_content = html_content.replace('</head>', zui_config_script, 1)
                if self.zcli_logger:
                    self.zcli_logger.info(f"[Handler] Auto-injected <script id='zui-config'> into HTML head")
            else:
                if self.zcli_logger:
                    self.zcli_logger.debug(f"[Handler] Skipped zui-config injection (all values None)")
            
            # Send HTML response
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-length", len(html_content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except TemplateNotFound as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Template not found: {e}")
            return self.send_error(404, f"Template not found: {template_name}")
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Template rendering error: {e}")
            return self.send_error(500, f"Template rendering failed: {str(e)}")
    
    def _handle_zwalker_route(self, route: dict):
        """
        Handle zWalker route - Execute zVaF blocks server-side using zVaF.html template.
        
        Supports hierarchical fallbacks: route → session
        - zVaFolder: route value OR session default
        - zVaFile: route value OR session default
        - zBlock: route value OR session default
        
        Args:
            route: Route definition with optional "context" dict
        
        Returns:
            None: Sends HTTP response directly
        """
        try:
            # Import needed modules
            import os
            from jinja2 import Environment, FileSystemLoader, TemplateNotFound
            
            # Get zcli instance for session access
            zcli = self.router.zcli if hasattr(self.router, 'zcli') else None
            
            # zWalker routes always use zVaF.html (full declarative mode)
            template_name = "zVaF.html"
            
            # Get context data (variables to pass to template)
            context = route.get("context", {})
            
            # Apply hierarchical fallbacks: route → session
            # Route-level values override session defaults
            if zcli:
                zVaFolder = route.get("zVaFolder") or zcli.session.get("zVaFolder")
                zVaFile = route.get("zVaFile") or zcli.session.get("zVaFile")
                zBlock = route.get("zBlock") or zcli.session.get("zBlock")
                
                if hasattr(self, 'zcli_logger') and self.zcli_logger:
                    self.zcli_logger.debug(f"[Handler] zWalker resolved - Folder: {zVaFolder}, File: {zVaFile}, Block: {zBlock}")
            else:
                # No session available - use route values only
                zVaFolder = route.get("zVaFolder")
                zVaFile = route.get("zVaFile")
                zBlock = route.get("zBlock")
            
            # Store resolved values in context for template/future use
            if zVaFolder:
                context["zVaFolder"] = zVaFolder
            if zVaFile:
                context["zVaFile"] = zVaFile
            if zBlock:
                context["zBlock"] = zBlock
            
            # Get templates directory from serve_path
            templates_dir = os.path.join(self.serve_path, self.template_folder)
            
            # Create Jinja2 environment
            env = Environment(loader=FileSystemLoader(templates_dir))
            
            # Render template with context (Jinja2 support)
            template = env.get_template(template_name)
            html_content = template.render(**context)
            
            # Auto-inject zUI config script before </head> (same as template routes)
            zui_config_values = {
                "zVaFile": context.get("zVaFile"),
                "zVaFolder": context.get("zVaFolder"),
                "zBlock": context.get("zBlock")
            }
            if any(v is not None for v in zui_config_values.values()):
                import json
                zui_config_json = json.dumps(zui_config_values, indent=4)
                zui_config_script = f'\n<!-- zUI Config (auto-injected from zSession) -->\n<script id="zui-config" type="application/json">\n{zui_config_json}\n</script>\n</head>'
                html_content = html_content.replace('</head>', zui_config_script, 1)
                if self.zcli_logger:
                    self.zcli_logger.info(f"[Handler] zWalker route - Auto-injected zui-config: {zui_config_values}")
            
            # Send HTML response
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-length", len(html_content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
            if self.zcli_logger:
                self.zcli_logger.debug(f"[Handler] Served zWalker route: {self.path}")
            
        except TemplateNotFound as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Template not found: {e}")
            return self.send_error(404, f"Template not found: {template_name}")
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] zWalker rendering error: {e}")
            return self.send_error(500, f"zWalker rendering failed: {str(e)}")
    
    def _convert_zpath_to_url(self, zpath: str) -> str:
        """
        Convert zCLI zPath to URL path for client-side fetching.
        
        Args:
            zpath: zCLI path, can be:
                - Absolute: "@.UI.zUI.index.zVaF" (workspace/UI/zUI.index.yaml)
                - Relative: "zUI.index.zVaF" (assumes UI folder)
        
        Returns:
            str: URL path like "/ui/zUI.index.yaml"
        
        Note:
            The UI folder prefix is stripped since /ui/* already maps to UI/ folder.
            Dots in filenames are preserved (zUI.index.yaml).
        """
        original_path = zpath
        
        # Remove @ prefix (absolute path marker)
        if zpath.startswith("@."):
            zpath = zpath[2:]
        elif zpath.startswith("@"):
            zpath = zpath[1:]
        
        # Remove .zVaF suffix if present
        if zpath.endswith(".zVaF"):
            zpath = zpath[:-5]
        
        # Strip UI folder prefix if present (since /ui/* already maps to UI/)
        # Handles: "UI.zUI.index" or "UI/zUI.index"
        if zpath.startswith("UI."):
            zpath = zpath[3:]  # Remove "UI."
        elif zpath.startswith("UI/"):
            zpath = zpath[3:]  # Remove "UI/"
        
        # Add .yaml extension if not present
        if not zpath.endswith(".yaml"):
            zpath += ".yaml"
        
        # Build URL path (dots are preserved as part of filename)
        # Use actual ui_folder name for URL (case-sensitive)
        url_path = f"/{self.ui_folder}/{zpath}"
        
        # Log conversion for debugging
        if hasattr(self, 'zcli_logger') and self.zcli_logger:
            self.zcli_logger.debug(f"[Handler] zPath conversion: {original_path} → {url_path}")
        
        return url_path
    
    def _handle_dynamic_route(self, route: dict):
        """
        Handle dynamic route - render zUI to HTML.
        
        Args:
            route: Route definition with zVaFile and zBlock
        
        Returns:
            None: Sends HTTP response directly
        """
        try:
            # Extract zVaF file and block from route
            zVaFile = route.get("zVaFile", "")
            zBlock = route.get("zBlock", "zVaF")
            
            if not zVaFile:
                return self.send_error(500, "Dynamic route missing zVaFile")
            
            # Get zcli instance from router
            if not hasattr(self.router, 'zcli'):
                return self.send_error(500, "zCLI instance not available")
            
            # Import and create page renderer with routes for dual-mode navigation
            from .page_renderer import PageRenderer
            routes = self.router.routes.get('routes', {}) if hasattr(self.router, 'routes') else {}
            renderer = PageRenderer(self.router.zcli, routes=routes)
            
            # Render zUI to HTML
            html_content = renderer.render_page(zVaFile, zBlock)
            
            # Send HTML response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(html_content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            # Log error and send 500
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Dynamic route error: {e}")
            return self.send_error(500, f"Dynamic rendering failed: {str(e)}")
    
    def _handle_form_route(self, route: dict):
        """
        Handle form route - declarative web form processing (zDialog pattern).
        
        Args:
            route: Route definition with model, fields, onSubmit, etc.
        
        Returns:
            None: Sends HTTP response (redirect or error)
        """
        try:
            # Only accept POST for forms
            if self.command != 'POST':
                return self.send_error(405, "Form routes only accept POST")
            
            # Get zcli instance from router
            if not hasattr(self.router, 'zcli'):
                return self.send_error(500, "zCLI instance not available")
            
            # Read POST body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            # Parse form data
            from .form_utils import parse_form_data, process_form_submission
            
            form_data = parse_form_data(body, content_type, self.zcli_logger)
            
            # Process form submission
            success, redirect_url, error_message = process_form_submission(
                route, form_data, self.router.zcli, self.zcli_logger
            )
            
            if success and redirect_url:
                # Redirect to success page
                self.send_response(303)  # See Other (POST-redirect-GET pattern)
                self.send_header("Location", redirect_url)
                self.end_headers()
            elif not success and redirect_url:
                # Redirect to error page with error message in query param
                error_url = f"{redirect_url}?error={error_message}" if error_message else redirect_url
                self.send_response(303)
                self.send_header("Location", error_url)
                self.end_headers()
            elif success:
                # No redirect specified - send success message
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                response_html = "<h1>Form submitted successfully</h1>"
                self.send_header("Content-length", len(response_html.encode('utf-8')))
                self.end_headers()
                self.wfile.write(response_html.encode('utf-8'))
            else:
                # No redirect specified - send error message
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                response_html = f"<h1>Form submission failed</h1><p>{error_message}</p>"
                self.send_header("Content-length", len(response_html.encode('utf-8')))
                self.end_headers()
                self.wfile.write(response_html.encode('utf-8'))
            
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] Form route error: {e}")
            return self.send_error(500, f"Form processing failed: {str(e)}")
    
    def _handle_json_route(self, route: dict):
        """
        Handle JSON route - declarative JSON response.
        
        Args:
            route: Route definition with data field
        
        Returns:
            None: Sends HTTP JSON response
        """
        try:
            # Get zcli instance from router
            if not hasattr(self.router, 'zcli'):
                return self.send_error(500, "zCLI instance not available")
            
            # Extract query parameters for placeholder resolution
            from .form_utils import extract_query_params
            query_params = extract_query_params(self.path)
            
            # Render JSON response
            from .json_utils import render_json_response
            
            body, status_code, headers = render_json_response(
                route, self.router.zcli, self.zcli_logger, query_params
            )
            
            # Send response
            self.send_response(status_code)
            for header_name, header_value in headers.items():
                self.send_header(header_name, header_value)
            self.end_headers()
            self.wfile.write(body)
            
        except Exception as e:
            if hasattr(self, 'zcli_logger') and self.zcli_logger:
                self.zcli_logger.error(f"[Handler] JSON route error: {e}")
            return self.send_error(500, f"JSON rendering failed: {str(e)}")

