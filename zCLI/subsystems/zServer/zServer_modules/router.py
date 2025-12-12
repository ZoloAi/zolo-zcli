"""
HTTP Router - Declarative routing with RBAC integration (v1.5.4 Phase 2)

This module provides HTTP request routing based on zServer.*.yaml definitions,
with integrated role-based access control (RBAC) using zAuth.

Philosophy:
    "Routes are data, not code" - Flask blueprint style for zCLI

Architecture:
    - Match incoming paths to route definitions
    - Enforce RBAC before serving content
    - Serve error pages on access denial
    - Support exact match, wildcard, and default routes

Route Matching Priority:
    1. Exact match ("/about" → "/about")
    2. Wildcard match ("/*" → any path)
    3. Default route (Meta.default_route)

RBAC Integration:
    Uses zcli.auth.has_role() and zcli.auth.is_authenticated()
    to enforce route-level access control defined in _rbac metadata.

Examples:
    >>> router = HTTPRouter(routes_data, zcli, logger)
    >>> route = router.match_route("/admin")
    >>> has_access, error_page = router.check_access(route)
    >>> if has_access:
    ...     file_path = router.resolve_file_path(route)

Version: v1.5.4 Phase 2
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

# Route keys (must match vafile_server.py)
KEY_META = "meta"
KEY_ROUTES = "routes"
KEY_BASE_PATH = "base_path"
KEY_DEFAULT_ROUTE = "default_route"
KEY_ERROR_PAGES = "error_pages"
KEY_TYPE = "type"
KEY_FILE = "file"
KEY_RBAC = "_rbac"

# RBAC keys
RBAC_KEY_REQUIRE_AUTH = "require_auth"
RBAC_KEY_REQUIRE_ROLE = "require_role"
RBAC_KEY_REQUIRE_PERMISSION = "require_permission"

# Route types
ROUTE_TYPE_STATIC = "static"
ROUTE_TYPE_CONTENT = "content"  # Inline HTML content (like Flask return "<h1>...</h1>")
ROUTE_TYPE_TEMPLATE = "template"  # Jinja2 template rendering (v1.5.4 Phase 2)
ROUTE_TYPE_ZWALKER = "zWalker"  # Execute zVaF blocks via zWalker (server-side rendering)
ROUTE_TYPE_FORM = "form"  # Declarative web forms (zDialog pattern for web - v1.5.7 Phase 1.2)
ROUTE_TYPE_JSON = "json"  # Declarative JSON responses (v1.5.7 Phase 1.2)
ROUTE_TYPE_DYNAMIC = "dynamic"
ROUTE_TYPE_REDIRECT = "redirect"

# HTTP error codes
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404

# Wildcard pattern
WILDCARD_PATTERN = "/*"

# Default error pages
DEFAULT_ERROR_403 = "403.html"
DEFAULT_ERROR_404 = "404.html"

# Log messages
LOG_MSG_ROUTER_INIT = "[HTTPRouter] Initialized with %d routes"
LOG_MSG_ROUTE_MATCHED = "[HTTPRouter] Matched route: %s → %s"
LOG_MSG_NO_MATCH = "[HTTPRouter] No route match for: %s"
LOG_MSG_RBAC_CHECK = "[HTTPRouter] RBAC check for %s: %s"
LOG_MSG_ACCESS_GRANTED = "[HTTPRouter] Access granted: %s"
LOG_MSG_ACCESS_DENIED = "[HTTPRouter] Access denied: %s (reason: %s)"
LOG_MSG_RESOLVE_PATH = "[HTTPRouter] Resolved path: %s → %s"


# =============================================================================
# HTTP ROUTER CLASS
# =============================================================================

class HTTPRouter:
    """
    HTTP request router with RBAC enforcement.
    
    Matches incoming HTTP requests to route definitions from zServer.*.yaml
    and enforces role-based access control before serving content.
    
    Attributes:
        routes: Full routes data structure from parser
        zcli: zCLI instance (for auth access)
        logger: Logger instance
        meta: Metadata (base_path, default_route, error_pages)
        route_map: Map of path → route definition
    
    Methods:
        match_route(path): Find route definition for request path
        check_access(route): Check RBAC and return (has_access, error_page)
        resolve_file_path(route): Get absolute file path for route
    """
    
    def __init__(
        self,
        routes: Dict[str, Any],
        zcli: Any,
        logger: Any
    ):
        """
        Initialize HTTP router.
        
        Args:
            routes: Parsed routes data from parse_server_file()
            zcli: zCLI instance (required for auth access)
            logger: Logger instance
        """
        self.routes = routes
        self.zcli = zcli
        self.logger = logger
        
        # Extract metadata
        self.meta = routes.get(KEY_META, {})
        self.route_map = routes.get(KEY_ROUTES, {})
        
        route_count = len(self.route_map)
        self.logger.info(LOG_MSG_ROUTER_INIT, route_count)
    
    def match_route(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Match request path to route definition.
        
        Matching Priority:
            1. Exact match
            2. Wildcard match (/*)
            3. Default route (from Meta)
        
        Args:
            path: HTTP request path (e.g., "/about")
        
        Returns:
            Optional[Dict[str, Any]]: Route definition or None
        
        Examples:
            >>> router = HTTPRouter(routes, zcli, logger)
            >>> route = router.match_route("/admin")
            >>> route["file"]
            "admin.html"
            >>> route["_rbac"]
            {"require_role": "admin"}
        """
        # 1. Exact match
        if path in self.route_map:
            route = self.route_map[path]
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, route.get(KEY_FILE, "N/A"))
            return route
        
        # 2. Wildcard match
        if WILDCARD_PATTERN in self.route_map:
            route = self.route_map[WILDCARD_PATTERN]
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, "wildcard")
            return route
        
        # 3. Default route
        default_route = self.meta.get(KEY_DEFAULT_ROUTE)
        if default_route:
            route = {KEY_TYPE: ROUTE_TYPE_STATIC, KEY_FILE: default_route}
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, default_route)
            return route
        
        # No match
        self.logger.warning(LOG_MSG_NO_MATCH, path)
        return None
    
    def check_access(self, route: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check RBAC for route.
        
        Enforces access control based on _rbac metadata in route definition.
        Uses zcli.auth to check authentication and roles.
        
        Args:
            route: Route definition from match_route()
        
        Returns:
            Tuple[bool, Optional[str]]: (has_access, error_page_path)
                - has_access: True if access granted, False if denied
                - error_page_path: Path to error page (403.html) if denied, None if granted
        
        Examples:
            >>> router = HTTPRouter(routes, zcli, logger)
            >>> route = router.match_route("/admin")
            >>> has_access, error_page = router.check_access(route)
            >>> if not has_access:
            ...     # Serve error_page instead
        """
        rbac = route.get(KEY_RBAC)
        
        # No RBAC = public access
        if not rbac:
            self.logger.debug(LOG_MSG_ACCESS_GRANTED, "public route")
            return True, None
        
        # Check authentication requirement
        require_auth = rbac.get(RBAC_KEY_REQUIRE_AUTH, False)
        if require_auth:
            if not self.zcli.auth.is_authenticated():
                error_page = self.meta.get(KEY_ERROR_PAGES, {}).get(HTTP_403_FORBIDDEN, DEFAULT_ERROR_403)
                self.logger.info(LOG_MSG_ACCESS_DENIED, "authentication", "not authenticated")
                return False, error_page
        
        # Check role requirement
        require_role = rbac.get(RBAC_KEY_REQUIRE_ROLE)
        if require_role:
            if not self.zcli.auth.has_role(require_role):
                error_page = self.meta.get(KEY_ERROR_PAGES, {}).get(HTTP_403_FORBIDDEN, DEFAULT_ERROR_403)
                self.logger.info(LOG_MSG_ACCESS_DENIED, "role", f"required: {require_role}")
                return False, error_page
        
        # Check permission requirement
        require_permission = rbac.get(RBAC_KEY_REQUIRE_PERMISSION)
        if require_permission:
            if not self.zcli.auth.has_permission(require_permission):
                error_page = self.meta.get(KEY_ERROR_PAGES, {}).get(HTTP_403_FORBIDDEN, DEFAULT_ERROR_403)
                self.logger.info(LOG_MSG_ACCESS_DENIED, "permission", f"required: {require_permission}")
                return False, error_page
        
        # All checks passed
        self.logger.debug(LOG_MSG_ACCESS_GRANTED, "RBAC checks passed")
        return True, None
    
    def resolve_file_path(self, route: Dict[str, Any]) -> str:
        """
        Resolve absolute file path from route definition.
        
        Combines Meta.base_path with route.file to get full path.
        
        Args:
            route: Route definition from match_route()
        
        Returns:
            str: Absolute file path
        
        Examples:
            >>> router = HTTPRouter(routes, zcli, logger)
            >>> route = {"file": "about.html"}
            >>> router.resolve_file_path(route)
            "/path/to/public/about.html"
        """
        base_path = self.meta.get(KEY_BASE_PATH, ".")
        file_name = route.get(KEY_FILE, "")
        
        resolved = os.path.join(base_path, file_name)
        self.logger.debug(LOG_MSG_RESOLVE_PATH, file_name, resolved)
        
        return resolved

