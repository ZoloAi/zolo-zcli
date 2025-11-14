# zCLI/subsystems/zServer/zServer_modules/handler.py

"""
Custom HTTP request handler with logging integration
"""

from http.server import SimpleHTTPRequestHandler
import os


class LoggingHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with zCLI logger integration + routing (v1.5.4 Phase 2)"""
    
    def __init__(self, *args, logger=None, router=None, **kwargs):
        self.zcli_logger = logger
        self.router = router  # HTTPRouter instance (optional)
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
        Handle GET requests with optional routing (v1.5.4 Phase 2).
        
        Flow:
            1. If router exists: Use declarative routing
            2. Otherwise: Fallback to static file serving (current behavior)
        """
        # Check if router exists (declarative routing mode)
        if self.router:
            return self._handle_routed_request()
        
        # Fallback: Static file serving (backward compatible)
        return super().do_GET()
    
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
            # Serve static file
            file_path = self.router.resolve_file_path(route)
            # Update self.path to point to resolved file
            self.path = f"/{os.path.basename(file_path)}"
            return super().do_GET()
        
        elif route_type == "content":
            # Serve inline HTML content (like Flask return "<h1>...</h1>")
            return self._handle_content_route(route)
        
        elif route_type == "template":
            # Serve Jinja2 template (like Flask render_template())
            return self._handle_template_route(route)
        
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
            
            # Get templates directory from serve_path
            import os
            from jinja2 import Environment, FileSystemLoader, TemplateNotFound
            
            serve_path = self.router.zcli.server.serve_path
            templates_dir = os.path.join(serve_path, "templates")
            
            # Create Jinja2 environment
            env = Environment(loader=FileSystemLoader(templates_dir))
            
            # Render template
            template = env.get_template(template_name)
            html_content = template.render(**context)
            
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
    
    def _handle_dynamic_route(self, route: dict):
        """
        Handle dynamic route - render zUI to HTML.
        
        Args:
            route: Route definition with zVaFile and zBlock
        
        Returns:
            None: Sends HTTP response directly
        """
        try:
            # Extract zUI file and block from route
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

