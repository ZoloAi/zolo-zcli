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
        
        elif route_type == "dynamic":
            # Serve dynamically generated HTML from zUI
            return self._handle_dynamic_route(route)
        
        # Unknown route type
        return self.send_error(501, f"Route type '{route_type}' not supported")
    
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
            
            # Import and create page renderer
            from .page_renderer import PageRenderer
            renderer = PageRenderer(self.router.zcli)
            
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

