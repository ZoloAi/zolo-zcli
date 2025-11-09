"""
Server File Parser - Parse zServer.*.yaml routing files (v1.5.4+)

This module parses declarative HTTP routing files for zServer, enabling
Flask blueprint-style route definitions with integrated RBAC.

Philosophy:
    "Routes are data, not code" - zServer follows zCLI's declarative approach

Structure:
    {
        "type": "server",
        "file_path": str,
        "meta": {
            "base_path": "./public",
            "default_route": "index.html",
            "error_pages": {403: "access_denied.html", 404: "404.html"}
        },
        "routes": {
            "/path": {
                "type": "static|dynamic|redirect",
                "file": "page.html",
                "description": "...",
                "_rbac": {require_role: "admin"} or None
            }
        }
    }

Route Types:
    - static: Serve file from base_path
    - dynamic: Execute zFunc handler (future)
    - redirect: HTTP redirect (future)

RBAC Integration:
    Routes can have inline _rbac metadata (same as zUI):
    - require_auth: true
    - require_role: "admin" or ["admin", "moderator"]
    - require_permission: "resource.action"

Examples:
    >>> data = {
    ...     "Meta": {"base_path": "./public"},
    ...     "routes": {
    ...         "/": {"type": "static", "file": "index.html"},
    ...         "/admin": {
    ...             "type": "static",
    ...             "file": "admin.html",
    ...             "_rbac": {"require_role": "admin"}
    ...         }
    ...     }
    ... }
    >>> result = parse_server_file(data, logger)
    >>> result["type"]
    "server"
    >>> result["routes"]["/admin"]["_rbac"]
    {"require_role": "admin"}

Integration:
    - Called by parser_file.py when zServer.*.yaml detected
    - Used by zServer.py to load routing configuration
    - RBAC checked by router.py during request handling

Version: v1.5.4 Phase 2
"""

from typing import Any, Dict, Optional

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

# File type identifier
FILE_TYPE_SERVER = "server"

# Top-level keys
KEY_META = "Meta"
KEY_ROUTES = "routes"

# Meta keys
KEY_BASE_PATH = "base_path"
KEY_DEFAULT_ROUTE = "default_route"
KEY_ERROR_PAGES = "error_pages"

# Route keys
KEY_TYPE = "type"
KEY_FILE = "file"
KEY_HANDLER = "handler"
KEY_TARGET = "target"
KEY_STATUS = "status"
KEY_DESCRIPTION = "description"
KEY_RBAC = "_rbac"

# Route types
ROUTE_TYPE_STATIC = "static"
ROUTE_TYPE_DYNAMIC = "dynamic"
ROUTE_TYPE_REDIRECT = "redirect"

# Default values
DEFAULT_BASE_PATH = "."
DEFAULT_DEFAULT_ROUTE = "index.html"
DEFAULT_ERROR_PAGES = {403: "403.html", 404: "404.html"}

# Log messages
LOG_MSG_PARSING_SERVER = "[vafile_server] Parsing server routing file"
LOG_MSG_FOUND_ROUTES = "[vafile_server] Found %d routes"
LOG_MSG_ROUTE_WITH_RBAC = "[vafile_server] Route '%s' has RBAC: %s"
LOG_MSG_NO_ROUTES = "[vafile_server] No routes defined"


# =============================================================================
# SERVER FILE PARSING
# =============================================================================

def parse_server_file(
    data: Dict[str, Any],
    logger: Any,
    file_path: Optional[str] = None,
    session: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse server routing file with RBAC extraction.
    
    ⚠️ CRITICAL: This function is called by parser_file.py.
    Signature must remain stable.
    
    Args:
        data: Parsed YAML/JSON data from zServer file
        logger: Logger instance for diagnostic output
        file_path: Optional file path for logging
        session: Optional session dict (reserved for future use)
    
    Returns:
        Dict[str, Any]: Parsed server routing structure with format:
            {
                "type": "server",
                "file_path": str or None,
                "meta": {
                    "base_path": str,
                    "default_route": str,
                    "error_pages": {403: str, 404: str}
                },
                "routes": {
                    "/path": {
                        "type": str,
                        "file": str,
                        "description": str,
                        "_rbac": dict or None
                    }
                }
            }
    
    Process Flow:
        1. Extract Meta section (base_path, default_route, error_pages)
        2. Extract routes section with RBAC metadata
        3. Return structured routing data
    
    Examples:
        >>> data = {
        ...     "Meta": {"base_path": "./public"},
        ...     "routes": {
        ...         "/": {"type": "static", "file": "index.html"}
        ...     }
        ... }
        >>> result = parse_server_file(data, logger, "zServer.demo.yaml")
        >>> result["type"]
        "server"
        >>> result["meta"]["base_path"]
        "./public"
    
    Notes:
        - Missing Meta uses defaults
        - Routes without _rbac are public
        - RBAC metadata is preserved for router.py
        - Session parameter reserved for future session-aware parsing
    """
    logger.info(LOG_MSG_PARSING_SERVER)
    
    # Extract Meta with defaults
    meta_raw = data.get(KEY_META, {})
    meta = {
        KEY_BASE_PATH: meta_raw.get(KEY_BASE_PATH, DEFAULT_BASE_PATH),
        KEY_DEFAULT_ROUTE: meta_raw.get(KEY_DEFAULT_ROUTE, DEFAULT_DEFAULT_ROUTE),
        KEY_ERROR_PAGES: meta_raw.get(KEY_ERROR_PAGES, DEFAULT_ERROR_PAGES.copy())
    }
    
    # Extract routes with RBAC
    routes_raw = data.get(KEY_ROUTES, {})
    routes = {}
    
    for route_path, route_data in routes_raw.items():
        if not isinstance(route_data, dict):
            logger.warning(f"[vafile_server] Skipping invalid route: {route_path}")
            continue
        
        # Extract RBAC metadata
        rbac = route_data.get(KEY_RBAC, None)
        
        # Build route entry
        route_entry = {
            KEY_TYPE: route_data.get(KEY_TYPE, ROUTE_TYPE_STATIC),
            KEY_RBAC: rbac
        }
        
        # Add type-specific fields
        if KEY_FILE in route_data:
            route_entry[KEY_FILE] = route_data[KEY_FILE]
        if KEY_HANDLER in route_data:
            route_entry[KEY_HANDLER] = route_data[KEY_HANDLER]
        if KEY_TARGET in route_data:
            route_entry[KEY_TARGET] = route_data[KEY_TARGET]
        if KEY_STATUS in route_data:
            route_entry[KEY_STATUS] = route_data[KEY_STATUS]
        if KEY_DESCRIPTION in route_data:
            route_entry[KEY_DESCRIPTION] = route_data[KEY_DESCRIPTION]
        
        routes[route_path] = route_entry
        
        # Log RBAC routes
        if rbac:
            logger.debug(LOG_MSG_ROUTE_WITH_RBAC, route_path, rbac)
    
    # Log summary
    route_count = len(routes)
    if route_count > 0:
        logger.info(LOG_MSG_FOUND_ROUTES, route_count)
    else:
        logger.warning(LOG_MSG_NO_ROUTES)
    
    return {
        "type": FILE_TYPE_SERVER,
        "file_path": file_path,
        "meta": meta,
        "routes": routes
    }

