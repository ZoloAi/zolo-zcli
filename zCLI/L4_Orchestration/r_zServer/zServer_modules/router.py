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
        logger: Any,
        serve_path: str = '.'
    ):
        """
        Initialize HTTP router.
        
        Args:
            routes: Parsed routes data from parse_server_file()
            zcli: zCLI instance (required for auth access)
            logger: Logger instance
            serve_path: Base path for serving files (for resolving zVaFile paths)
        """
        self.routes = routes
        self.zcli = zcli
        self.logger = logger
        self.serve_path = serve_path
        
        # Extract metadata
        self.meta = routes.get(KEY_META, {})
        self.route_map = routes.get(KEY_ROUTES, {})
        
        # Auto-discovered routes from zWalker files
        self.auto_discovered_routes = {}
        
        # Discover zBlock routes from walker routes with auto_discover_blocks
        self._discover_walker_blocks()
        
        route_count = len(self.route_map) + len(self.auto_discovered_routes)
        self.logger.info(f"[HTTPRouter] Initialized with {len(self.route_map)} explicit + {len(self.auto_discovered_routes)} auto-discovered = {route_count} total routes")
    
    def _discover_walker_blocks(self):
        """
        Auto-discover zBlock routes from zWalker routes with auto_discover_blocks=true.
        
        For each walker route with auto_discover_blocks enabled:
        1. Parse the referenced zVaFile (e.g., zUI.zVaF.yaml)
        2. Extract all top-level keys (excluding 'meta') from that file
        3. Scan the entire zVaFolder directory for ALL zUI.*.yaml files
        4. For each file, extract the first top-level block (excluding 'meta')
        5. Create virtual routes: /{zBlock} → walker(zBlock={zBlock})
        
        This allows direct navigation to /zAbout, /zRegister, /zLogin, etc. without
        requiring explicit route definitions for each block, matching Terminal mode behavior.
        """
        self.logger.info(f"[Router] Starting auto-discovery - checking {len(self.route_map)} routes")
        
        if not self.route_map:
            self.logger.info("[Router] No routes to check for auto-discovery")
            return
        
        for route_path, route_config in self.route_map.items():
            self.logger.info(f"[Router] Checking route: {route_path}, type={route_config.get(KEY_TYPE)}, auto_discover={route_config.get('auto_discover_blocks')}")
            # Only process zWalker routes with auto_discover_blocks
            if route_config.get(KEY_TYPE) != ROUTE_TYPE_ZWALKER:
                continue
            
            if not route_config.get('auto_discover_blocks', False):
                continue
            
            # Get zVaFile path for parsing (with session fallback)
            zVaFolder = route_config.get('zVaFolder')
            zVaFile = route_config.get('zVaFile')
            
            # Fall back to session defaults if not specified in route
            if not zVaFolder and self.zcli and self.zcli.session:
                zVaFolder = self.zcli.session.get('zVaFolder', '')
            if not zVaFile and self.zcli and self.zcli.session:
                zVaFile = self.zcli.session.get('zVaFile', '')
            
            if not zVaFile:
                self.logger.warning(f"[Router] Cannot auto-discover blocks for {route_path}: no zVaFile in route or session")
                continue
            
            self.logger.info(f"[Router] Auto-discovering blocks for {route_path} from {zVaFolder}/{zVaFile}")
            
            # Resolve zPath notation (@.UI → UI/)
            if zVaFolder and zVaFolder.startswith('@.'):
                zVaFolder_resolved = zVaFolder[2:]  # Strip @. prefix
            elif not zVaFolder:
                zVaFolder_resolved = ''  # Default to empty (root level)
            else:
                zVaFolder_resolved = zVaFolder
            
            # Build directory path
            directory_path = os.path.join(self.serve_path, zVaFolder_resolved)
            
            # First: Parse the main zVaFile and extract blocks
            vafile_path = os.path.join(directory_path, f"{zVaFile}.yaml")
            
            try:
                import yaml
                import glob
                
                # Parse main zVaFile
                with open(vafile_path, 'r') as f:
                    vafile_data = yaml.safe_load(f)
                
                if isinstance(vafile_data, dict):
                    # Extract all top-level keys except 'meta'
                    zBlocks = [key for key in vafile_data.keys() if key != 'meta']
                    
                    self.logger.info(f"[Router] Auto-discovered {len(zBlocks)} zBlocks from {zVaFile}: {zBlocks}")
                    
                    # Create virtual routes for each zBlock in main file
                    for zBlock in zBlocks:
                        virtual_path = f"/{zBlock}"
                        
                        # Skip if explicit route already exists
                        if virtual_path in self.route_map:
                            self.logger.debug(f"[Router] Skipping {virtual_path} - explicit route exists")
                            continue
                        
                        # Create virtual route (copy parent route config but override zBlock and zVaFile)
                        virtual_route = route_config.copy()
                        virtual_route['zBlock'] = zBlock
                        virtual_route['zVaFile'] = zVaFile
                        virtual_route['_auto_discovered'] = True  # Mark as virtual
                        
                        self.auto_discovered_routes[virtual_path] = virtual_route
                        self.logger.debug(f"[Router] Created virtual route: {virtual_path} → {zVaFile}.{zBlock}")
                
                # Second: Scan entire directory for ALL zUI.*.yaml files
                self.logger.info(f"[Router] Scanning directory {directory_path} for additional zUI.*.yaml files")
                pattern = os.path.join(directory_path, "zUI.*.yaml")
                all_files = glob.glob(pattern)
                
                for file_path in all_files:
                    file_name = os.path.basename(file_path)
                    file_base = file_name.replace('.yaml', '')  # e.g., "zUI.zAbout" → "zUI.zAbout"
                    
                    # Skip the main file we already processed
                    if file_base == zVaFile:
                        continue
                    
                    try:
                        with open(file_path, 'r') as f:
                            file_data = yaml.safe_load(f)
                        
                        if not isinstance(file_data, dict):
                            continue
                        
                        # Extract first top-level block (excluding 'meta')
                        blocks = [key for key in file_data.keys() if key != 'meta']
                        
                        if not blocks:
                            self.logger.debug(f"[Router] No blocks found in {file_name}")
                            continue
                        
                        # Use the first block as the route
                        first_block = blocks[0]
                        
                        # Strip navigation modifiers (^, ~) from URL path
                        # Modifiers are for block behavior, not URL paths
                        # Example: ^zLogin block → /zLogin route (clean URL)
                        clean_block_name = first_block.lstrip("^~")
                        virtual_path = f"/{clean_block_name}"
                        
                        # Skip if explicit route or already discovered
                        if virtual_path in self.route_map or virtual_path in self.auto_discovered_routes:
                            self.logger.debug(f"[Router] Skipping {virtual_path} - already exists")
                            continue
                        
                        # Create virtual route pointing to this specific file
                        virtual_route = route_config.copy()
                        virtual_route['zBlock'] = first_block
                        virtual_route['zVaFile'] = file_base  # e.g., "zUI.zAbout"
                        virtual_route['_auto_discovered'] = True
                        
                        self.auto_discovered_routes[virtual_path] = virtual_route
                        # Log shows: clean URL path → file.block (with modifiers preserved)
                        self.logger.info(f"[Router] Auto-discovered route: {virtual_path} → {file_base}.{first_block}")
                    
                    except Exception as e:
                        self.logger.warning(f"[Router] Error parsing {file_name}: {e}")
                
                total_discovered = len(self.auto_discovered_routes)
                self.logger.info(f"[Router] Auto-discovery complete: {total_discovered} total virtual routes")
            
            except FileNotFoundError:
                self.logger.warning(f"[Router] zVaFile not found: {vafile_path}")
            except Exception as e:
                self.logger.error(f"[Router] Error discovering blocks from {vafile_path}: {e}")
                import traceback
                self.logger.error(f"[Router] Traceback: {traceback.format_exc()}")
    
    def match_route(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Match request path to route definition.
        
        Matching Priority:
            1. Exact match (explicit routes)
            2. Parametrized match (/:param patterns)
            3. Auto-discovered zBlock routes (from zWalker)
            4. Wildcard match (/*)
            5. Default route (from Meta)
        
        Args:
            path: HTTP request path (e.g., "/about" or "/users/123/avatar")
        
        Returns:
            Optional[Dict[str, Any]]: Route definition or None
        
        Examples:
            >>> router = HTTPRouter(routes, zcli, logger)
            >>> route = router.match_route("/admin")
            >>> route["file"]
            "admin.html"
            >>> route = router.match_route("/users/123/avatar")
            >>> route["type"]
            "zFunc"
        """
        # 1. Exact match (explicit routes)
        if path in self.route_map:
            route = self.route_map[path]
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, route.get(KEY_FILE, "N/A"))
            return route
        
        # 2. Parametrized match (/:param patterns)
        route, params = self._match_parametrized_route(path)
        if route:
            # Store extracted parameters for handler access
            route['_route_params'] = params
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, f"parametrized: {route.get('handler', 'N/A')}")
            return route
        
        # 3. Auto-discovered zBlock routes (from zWalker with auto_discover_blocks)
        if path in self.auto_discovered_routes:
            route = self.auto_discovered_routes[path]
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, f"auto-discovered zBlock: {route.get('zBlock')}")
            return route
        
        # 4. Wildcard match
        if WILDCARD_PATTERN in self.route_map:
            route = self.route_map[WILDCARD_PATTERN]
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, "wildcard")
            return route
        
        # 5. Default route
        default_route = self.meta.get(KEY_DEFAULT_ROUTE)
        if default_route:
            route = {KEY_TYPE: ROUTE_TYPE_STATIC, KEY_FILE: default_route}
            self.logger.debug(LOG_MSG_ROUTE_MATCHED, path, default_route)
            return route
        
        # No match
        self.logger.warning(LOG_MSG_NO_MATCH, path)
        return None
    
    def _match_parametrized_route(self, path: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
        """
        Match request path against parametrized route patterns (e.g., /users/:user_id/avatar).
        
        Args:
            path: HTTP request path (e.g., "/users/123/avatar")
        
        Returns:
            Tuple of (route_definition, extracted_parameters)
        
        Examples:
            >>> route, params = self._match_parametrized_route("/users/123/avatar")
            >>> params
            {"user_id": "123"}
        """
        path_segments = [s for s in path.split('/') if s]  # Split and remove empty strings
        
        for route_pattern, route in self.route_map.items():
            # Skip if not a parametrized route
            if ':' not in route_pattern:
                continue
            
            pattern_segments = [s for s in route_pattern.split('/') if s]
            
            # Must have same number of segments
            if len(path_segments) != len(pattern_segments):
                continue
            
            # Try to match each segment
            params = {}
            match = True
            
            for path_seg, pattern_seg in zip(path_segments, pattern_segments):
                if pattern_seg.startswith(':'):
                    # Parameter segment - extract value
                    param_name = pattern_seg[1:]  # Remove ':' prefix
                    params[param_name] = path_seg
                elif path_seg != pattern_seg:
                    # Static segment - must match exactly
                    match = False
                    break
            
            if match:
                return route, params
        
        return None, {}
    
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

