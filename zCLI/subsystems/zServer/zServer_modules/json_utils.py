"""
JSON Utilities - Declarative JSON responses for APIs

This module provides JSON rendering from declarative route definitions,
enabling API endpoints without Python handler functions.

Philosophy:
    "APIs are data, not code" - Define JSON responses in YAML

Architecture:
    - Parse YAML data definitions
    - Support dynamic values (from zConfig, zSession, etc.)
    - Support placeholders ({query.param}, {session.user_id})
    - Render JSON responses directly

Integration:
    Used by handler.py and wsgi_app.py to process type: json routes

Examples:
    >>> # In routes.yaml
    >>> /api/health:
    >>>   type: json
    >>>   data:
    >>>     status: ok
    >>>     version: "1.0"
    >>>     timestamp: "{timestamp}"

Version: v1.5.7 Phase 1.2
"""

import json
from typing import Any, Dict
from datetime import datetime

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

# JSON route keys
KEY_DATA = "data"
KEY_STATUS = "status"

# Default status
DEFAULT_STATUS = 200

# Content type
CONTENT_TYPE_JSON = "application/json"

# Log messages
LOG_MSG_RENDER_JSON = "[JSONUtils] Rendering JSON response"
LOG_MSG_PLACEHOLDER_RESOLVE = "[JSONUtils] Resolving placeholder: %s"


# =============================================================================
# JSON RENDERING FUNCTIONS
# =============================================================================

def render_json_response(
    route: Dict[str, Any],
    zcli: Any,
    logger: Any,
    query_params: Dict[str, str] = None
) -> tuple[bytes, int, Dict[str, str]]:
    """
    Render JSON response from declarative route definition.
    
    Args:
        route: JSON route definition from routes.yaml
        zcli: zCLI instance (for accessing config, session, etc.)
        logger: Logger instance
        query_params: Query parameters from URL (optional)
    
    Returns:
        tuple[bytes, int, Dict]: (body, status_code, headers)
    
    Examples:
        >>> route = {
        ...     "data": {"status": "ok", "version": "1.0"},
        ...     "status": 200
        ... }
        >>> body, status, headers = render_json_response(route, zcli, logger)
        >>> body
        b'{"status": "ok", "version": "1.0"}'
    """
    logger.debug(LOG_MSG_RENDER_JSON)
    
    # Get data definition
    data = route.get(KEY_DATA, {})
    
    # Resolve placeholders
    if query_params is None:
        query_params = {}
    
    resolved_data = _resolve_placeholders(data, zcli, query_params, logger)
    
    # Get status code
    status_code = route.get(KEY_STATUS, DEFAULT_STATUS)
    
    # Create JSON response
    json_body = json.dumps(resolved_data, indent=2)
    body_bytes = json_body.encode('utf-8')
    
    # Headers
    headers = {
        'Content-Type': CONTENT_TYPE_JSON,
        'Content-Length': str(len(body_bytes))
    }
    
    return body_bytes, status_code, headers


def _make_json_safe(obj: Any, max_depth: int = 10, _depth: int = 0) -> Any:
    """
    Recursively convert objects to JSON-safe types.
    
    Handles:
        - Dicts and lists (recursive)
        - Complex objects → string representation
        - Circular references (max depth limit)
    
    Args:
        obj: Object to make JSON-safe
        max_depth: Maximum recursion depth
        _depth: Current depth (internal)
    
    Returns:
        JSON-safe representation of obj
    """
    # Depth limit to prevent infinite recursion
    if _depth > max_depth:
        return "<max_depth_exceeded>"
    
    # Already JSON-safe primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    
    # Dict - recursively process values
    if isinstance(obj, dict):
        return {
            str(k): _make_json_safe(v, max_depth, _depth + 1)
            for k, v in obj.items()
        }
    
    # List/tuple - recursively process items
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(item, max_depth, _depth + 1) for item in obj]
    
    # Everything else - convert to string representation
    try:
        # Try to get a nice string representation
        return str(obj)
    except Exception:
        return f"<{type(obj).__name__}>"


def _resolve_placeholders(
    data: Any,
    zcli: Any,
    query_params: Dict[str, str],
    logger: Any
) -> Any:
    """
    Resolve placeholders in data structure.
    
    Supports:
        - {query.param} - Query parameters
        - {session} - Entire session dictionary
        - {session.key} - Individual session values
        - {config.key} - Config values
        - {timestamp} - Current timestamp
        - {date} - Current date
    
    Args:
        data: Data structure (dict, list, str, etc.)
        zcli: zCLI instance
        query_params: Query parameters
        logger: Logger instance
    
    Returns:
        Any: Data with placeholders resolved
    
    Examples:
        >>> data = {"query": "{query.q}", "timestamp": "{timestamp}"}
        >>> resolved = _resolve_placeholders(data, zcli, {"q": "test"}, logger)
        >>> resolved
        {"query": "test", "timestamp": "2024-12-06T..."}
    """
    # Handle dict
    if isinstance(data, dict):
        return {
            key: _resolve_placeholders(value, zcli, query_params, logger)
            for key, value in data.items()
        }
    
    # Handle list
    elif isinstance(data, list):
        return [
            _resolve_placeholders(item, zcli, query_params, logger)
            for item in data
        ]
    
    # Handle string (potential placeholder)
    elif isinstance(data, str):
        if data.startswith('{') and data.endswith('}'):
            placeholder = data[1:-1]  # Remove { }
            logger.debug(LOG_MSG_PLACEHOLDER_RESOLVE, placeholder)
            
            # Query parameters
            if placeholder.startswith('query.'):
                param_name = placeholder[6:]  # Remove 'query.'
                return query_params.get(param_name, '')
            
            # Session values
            elif placeholder == 'session':
                # Return entire session dictionary (safely serialize)
                if hasattr(zcli, 'session'):
                    return _make_json_safe(dict(zcli.session))
                return {}
            elif placeholder.startswith('session.'):
                session_key = placeholder[8:]  # Remove 'session.'
                value = zcli.session.get(session_key, '')
                # If session value is dict/list, return as-is (don't stringify)
                return value
            
            # Config values
            elif placeholder.startswith('config.'):
                config_key = placeholder[7:]  # Remove 'config.'
                return getattr(zcli.config, config_key, '')
            
            # Special values
            elif placeholder == 'timestamp':
                return datetime.now().isoformat()
            
            elif placeholder == 'date':
                return datetime.now().strftime('%Y-%m-%d')
            
            # Unknown placeholder - return as-is
            else:
                logger.warning(f"[JSONUtils] Unknown placeholder: {placeholder}")
                return data
        
        # Not a placeholder - return as-is
        return data
    
    # Other types - return as-is
    else:
        return data

