# zCLI/subsystems/zComm/zComm_modules/bifrost/bridge_modules/bridge_connection.py
"""
Connection Info Manager - Manages server metadata sent to WebSocket clients.

Provides connection information, feature lists, model discovery, and schema
introspection for clients connecting to the zBifrost WebSocket server.

Architecture:
    - Aggregates server metadata from multiple sources (cache, session, zData)
    - Gracefully handles missing dependencies (walker, zcli, zData)
    - Provides model discovery via zData introspection
    - Returns structured connection info on client connect

Integration:
    - Used by zBifrost during client authentication
    - Relies on CacheManager for cache stats
    - Integrates with zData for model discovery
    - Accesses session via zCLI instance (dependency injection pattern)
"""

from zCLI import Optional, Dict, List, Any
from zCLI.version import __version__

# ═══════════════════════════════════════════════════════════
# Module-Level Constants
# ═══════════════════════════════════════════════════════════

# Log Prefix
LOG_PREFIX = "[ConnectionInfo]"

# Connection Info Dict Keys
KEY_SERVER_VERSION = "server_version"
KEY_FEATURES = "features"
KEY_CACHE_STATS = "cache_stats"
KEY_AVAILABLE_MODELS = "available_models"
KEY_SESSION = "session"

# Session Dict Keys
KEY_SESSION_WORKSPACE = "workspace"
KEY_SESSION_MODE = "mode"

# Default Mode
DEFAULT_MODE = "Terminal"

# Feature List
FEATURE_SCHEMA_CACHE = "schema_cache"
FEATURE_QUERY_CACHE = "query_cache"
FEATURE_CONNECTION_INFO = "connection_info"
FEATURE_REALTIME_SYNC = "realtime_sync"

FEATURES = [
    FEATURE_SCHEMA_CACHE,
    FEATURE_QUERY_CACHE,
    FEATURE_CONNECTION_INFO,
    FEATURE_REALTIME_SYNC
]

# Model Dict Keys
KEY_MODEL_NAME = "name"
KEY_MODEL_TYPE = "type"
KEY_MODEL_OPERATIONS = "operations"
KEY_MODEL_SCHEMA = "schema"
KEY_MODEL_FIELDS = "fields"
KEY_MODEL_CACHEABLE = "cacheable"

# Model Types
MODEL_TYPE_TABLE = "table"
MODEL_TYPE_SCHEMA = "schema"

# CRUD Operations
OPERATION_CREATE = "create"
OPERATION_READ = "read"
OPERATION_UPDATE = "update"
OPERATION_DELETE = "delete"

CRUD_OPERATIONS = [
    OPERATION_CREATE,
    OPERATION_READ,
    OPERATION_UPDATE,
    OPERATION_DELETE
]

# Log Messages
LOG_MODEL_DISCOVERY_ERROR = f"{LOG_PREFIX} Could not discover models: {{error}}"
LOG_SESSION_INFO_ERROR = f"{LOG_PREFIX} Could not get session info: {{error}}"
LOG_MODEL_DISCOVERY_GENERAL_ERROR = f"{LOG_PREFIX} Model discovery error: {{error}}"
LOG_INTROSPECT_FAILED = f"{LOG_PREFIX} Failed to introspect {{model_name}}: {{error}}"

# Error Messages
ERROR_LOGGER_REQUIRED = "logger parameter is required and cannot be None"
ERROR_MODEL_NAME_REQUIRED = "model_name must be a non-empty string"


class ConnectionInfoManager:
    """
    Manages connection metadata sent to WebSocket clients on connect.
    
    Aggregates server information from multiple sources including version info,
    feature lists, cache statistics, available data models, and session metadata.
    Provides model discovery and introspection via zData integration.
    
    Lifecycle:
        1. Initialize with logger and optional dependencies (cache, zcli, walker)
        2. Call get_connection_info() during client authentication
        3. Call introspect_model() for detailed schema information
    
    Args:
        logger: Logger instance (required)
        cache_manager: CacheManager instance for cache stats
        zcli: zCLI instance for session access
        walker: Walker instance for zData access
    
    Raises:
        ValueError: If logger is None
    """

    def __init__(
        self,
        logger: Any,
        cache_manager: Any,
        zcli: Optional[Any] = None,
        walker: Optional[Any] = None
    ) -> None:
        """
        Initialize connection info manager with validation.
        
        Args:
            logger: Logger instance (required, cannot be None)
            cache_manager: CacheManager instance for cache statistics
            zcli: Optional zCLI instance for session metadata
            walker: Optional Walker instance for zData model discovery
        
        Raises:
            ValueError: If logger is None
        """
        # Input validation
        if logger is None:
            raise ValueError(ERROR_LOGGER_REQUIRED)

        self.logger = logger
        self.cache = cache_manager
        self.zcli = zcli
        self.walker = walker

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection metadata to send to client on connect.
        
        Aggregates server version, feature list, cache stats, available models,
        and session information. Gracefully handles missing dependencies.
        
        Returns:
            Connection info dict with keys:
                - server_version (str): Current zCLI version
                - features (list): Enabled feature names
                - cache_stats (dict): Cache hit/miss statistics
                - available_models (list, optional): Discovered data models
                - session (dict, optional): Workspace and mode info
        
        Raises:
            AttributeError: If cache_manager missing get_all_stats method
        """
        info = {
            KEY_SERVER_VERSION: __version__,
            KEY_FEATURES: FEATURES,
            KEY_CACHE_STATS: self.cache.get_all_stats()
        }

        # Add available models if zData is available
        if self.walker and hasattr(self.walker, 'data'):
            try:
                info[KEY_AVAILABLE_MODELS] = self._discover_models()
            except Exception as e:  # Broad catch intentional: model discovery is optional
                self.logger.debug(LOG_MODEL_DISCOVERY_ERROR.format(error=e))

        # Add session data if available
        if self.zcli and hasattr(self.zcli, 'session'):
            try:
                info[KEY_SESSION] = {
                    KEY_SESSION_WORKSPACE: getattr(self.zcli.session, 'workspace', None),
                    KEY_SESSION_MODE: getattr(self.zcli, 'mode', DEFAULT_MODE)
                }
            except Exception as e:  # Broad catch intentional: session info is optional
                self.logger.debug(LOG_SESSION_INFO_ERROR.format(error=e))

        return info

    def _discover_models(self) -> List[Dict[str, Any]]:
        """
        Discover available data models via zData introspection.
        
        Attempts multiple discovery methods:
        1. list_tables() - for database-backed models
        2. get_all_schemas() - for schema-defined models
        
        Returns:
            List of model info dicts, each containing:
                - name (str): Model/table name
                - type (str): 'table' or 'schema'
                - operations (list): Available CRUD operations
                - fields (list, optional): Field names for schema models
        
        Raises:
            AttributeError: If walker.data missing discovery methods
        """
        models = []

        try:
            # Try to get available models from zData
            if self.walker and hasattr(self.walker, 'data'):
                # Check if we can list tables
                if hasattr(self.walker.data, 'list_tables'):
                    tables = self.walker.data.list_tables()
                    for table in tables:
                        models.append({
                            KEY_MODEL_NAME: table,
                            KEY_MODEL_TYPE: MODEL_TYPE_TABLE,
                            KEY_MODEL_OPERATIONS: CRUD_OPERATIONS
                        })

                # Check if we can get schema info
                elif hasattr(self.walker.data, 'get_all_schemas'):
                    schemas = self.walker.data.get_all_schemas()
                    for schema_name, schema_data in schemas.items():
                        models.append({
                            KEY_MODEL_NAME: schema_name,
                            KEY_MODEL_TYPE: MODEL_TYPE_SCHEMA,
                            KEY_MODEL_FIELDS: list(
                                schema_data.get(KEY_MODEL_FIELDS, {}).keys()
                            ) if isinstance(schema_data, dict) else [],
                            KEY_MODEL_OPERATIONS: CRUD_OPERATIONS
                        })

        except (AttributeError, TypeError, KeyError) as e:
            self.logger.debug(LOG_MODEL_DISCOVERY_GENERAL_ERROR.format(error=e))

        return models

    def introspect_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed schema information for a specific model.
        
        Args:
            model_name: Model name to introspect (required, non-empty)
            
        Returns:
            Model metadata dict with keys:
                - name (str): Model name
                - schema (dict): Full schema definition
                - operations (list): Available CRUD operations
                - cacheable (bool): Whether model supports caching
            Returns None if model not found or introspection fails.
        
        Raises:
            ValueError: If model_name is None or empty string
            AttributeError: If walker.data missing get_schema method
        """
        # Input validation
        if not model_name or not isinstance(model_name, str):
            raise ValueError(ERROR_MODEL_NAME_REQUIRED)

        try:
            if self.walker and hasattr(self.walker, 'data'):
                schema = self.walker.data.get_schema(model_name)
                if schema:
                    return {
                        KEY_MODEL_NAME: model_name,
                        KEY_MODEL_SCHEMA: schema,
                        KEY_MODEL_OPERATIONS: CRUD_OPERATIONS,
                        KEY_MODEL_CACHEABLE: True
                    }
        except (AttributeError, TypeError, KeyError) as e:
            self.logger.warning(LOG_INTROSPECT_FAILED.format(model_name=model_name, error=e))

        return None
