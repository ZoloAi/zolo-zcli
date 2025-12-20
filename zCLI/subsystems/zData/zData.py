# zCLI/subsystems/zData/zData.py

"""
Unified Data Management System for zCLI.

This module provides the main entry point for all data operations in zCLI, supporting
relational databases (SQLite, PostgreSQL) and file-based data (CSV) through a unified
interface. It handles schema loading, adapter initialization, connection management, and
operation delegation to specialized handlers.

Architecture Overview:
    The zData subsystem uses a 2-tier architecture for simplicity and efficiency:
    
    1. zData Facade (this file):
       - Schema loading and validation
       - Adapter initialization via AdapterFactory
       - Connection lifecycle management (wizard mode vs one-shot mode)
       - Operation routing via DataOperations facade
       - zCLI subsystem integration (zLoader, zOpen, zDisplay, zFunc)
    
    2. Backend Adapters (SQLite, PostgreSQL, CSV):
       - Database-specific implementations
       - CRUD operation execution
       - DDL/DCL/TCL support (database-dependent)
       - Connection handling and query building

Supported Operations:
    CRUD (Create, Read, Update, Delete):
        - insert: Add new records
        - select: Query records with WHERE, JOIN, ORDER BY, LIMIT
        - update: Modify existing records
        - delete: Remove records
        - upsert: Insert or update (conflict resolution)
        - list_tables: List all tables in database
    
    DDL (Data Definition Language):
        - create_table: Create tables from schema
        - drop_table: Remove tables
        - alter_table: Modify table structure
        - table_exists: Check table existence
    
    DCL (Data Control Language - PostgreSQL/MySQL only):
        - grant: Grant privileges to users
        - revoke: Revoke privileges from users
        - list_privileges: List privileges for tables/users
    
    TCL (Transaction Control Language):
        - begin_transaction: Start transaction
        - commit: Commit transaction
        - rollback: Rollback transaction
    
    File Operations (zOpen integration):
        - open_schema: Open schema YAML in editor
        - open_csv: Open CSV data file in editor

Supported Backends:
    - SQLite: Embedded database, file-based, no external dependencies
    - PostgreSQL: Network database, requires psycopg2, project info YAML
    - CSV: File-based, requires pandas, DataFrame caching, multi-table JOINs

Integration Points:
    zSession:
        - wizard_mode: Connection reuse for multi-step workflows
        - schema_cache: Persistent connections across wizard steps
        - zAuth: Authentication context for secure data access
    
    zLoader:
        - Schema loading from zPath (@.zSchema.users, ~.zMachine.schemas/app.yaml)
        - pinned_cache: Cached schemas for faster initialization
    
    zParser:
        - Path resolution (zPath to absolute paths)
        - Data_Path resolution in schema Meta section
    
    zDisplay:
        - Mode-agnostic output (Terminal, Walker, Bifrost)
        - zDeclare for operation announcements
        - AdvancedData integration for table display (Week 6.4 TODO)
    
    zFunc:
        - Hook execution (onBeforeInsert, onAfterInsert, etc.)
        - Custom business logic for data operations
    
    zOpen:
        - File opening (schema YAML, CSV data files)
        - Editor integration

Connection Modes:
    Wizard Mode (wizard_mode=True):
        - Connection reuse: Same adapter instance across multiple operations
        - Schema cache: Stores connection per alias ($users, $products)
        - Lifecycle: Manual disconnect or wizard completion
        - Use case: Multi-step workflows, batch operations
    
    One-Shot Mode (wizard_mode=False):
        - New connection per operation
        - Auto-disconnect after operation completes
        - No persistent state
        - Use case: Single commands, terminal operations

Schema Structure:
    Meta Section (required):
        Data_Type: Backend type (sqlite, postgresql, csv)
        Data_Path: Path to database/CSV directory (~.zMachine.data/app.db)
        Data_Label: Human-readable label for logging
        Schema_Name: Optional schema name for error messages
        zVaFiles: Path to schema YAML file (for open_schema)
    
    Table Sections (one per table):
        field_name:
            type: Data type (TEXT, INTEGER, FLOAT, BOOLEAN, DATE)
            primary_key: Boolean (optional)
            required: Boolean (optional)
            unique: Boolean (optional)
            foreign_key: Foreign key spec (optional)
            default: Default value (optional)
            validators: List of validation rules (optional)

Usage Examples:
    # Example 1: One-shot mode (terminal command)
    zdata = zData(zcli)
    request = {
        "model": "@.zSchema.users",
        "action": "read",
        "options": {"where": "age > 25"}
    }
    result = zdata.handle_request(request)
    
    # Example 2: Wizard mode with connection reuse
    context = {
        "wizard_mode": True,
        "schema_cache": SchemaCache()
    }
    request1 = {
        "model": "@.zSchema.users",
        "action": "insert",
        "options": {"_alias_name": "users", "_schema_cached": schema}
    }
    zdata.handle_request(request1, context)
    # Connection stays open for next request...
    
    # Example 3: Direct adapter access (programmatic)
    zdata.load_schema(schema)
    rows = zdata.select("users", fields=["name", "email"], where={"active": True})
    zdata.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
    zdata.disconnect()

Module Constants:
    This module defines 50+ constants to eliminate magic strings and improve
    maintainability across:
    - Schema keys (Meta, Data_Type, Data_Path, etc.)
    - Request keys (action, model, options, tables)
    - Option keys (_schema_cached, _alias_name, tables)
    - Context keys (wizard_mode, schema_cache)
    - Reserved keys (Meta, db_path)
    - Return values (error, success)
    - Error messages (10+ descriptive errors)
    - Log messages (8+ operation logs)

Type Hints:
    All methods in this module have 100% type hint coverage for improved
    code quality, IDE support, and runtime type checking.

See Also:
    - zCLI/subsystems/zData/zData_modules/shared/backends/: Adapter implementations
    - zCLI/subsystems/zData/zData_modules/shared/data_operations.py: Operation facade
    - zCLI/subsystems/zData/zData_modules/shared/validator.py: Data validation
    - zCLI/subsystems/zData/zData_modules/shared/parsers/: WHERE/value parsers
"""

from zCLI import Any, Dict, List, Optional, os
from zCLI.utils.zExceptions import SchemaNotFoundError, TableNotFoundError
from .zData_modules.shared.backends.adapter_factory import AdapterFactory
from .zData_modules.shared.validator import DataValidator
from .zData_modules.shared.data_operations import DataOperations


# ═══════════════════════════════════════════════════════════════════════════════════════
# MODULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════════════

# Schema keys (Meta section)
META_KEY = "Meta"
META_KEY_DATA_TYPE = "Data_Type"
META_KEY_DATA_PATH = "Data_Path"
META_KEY_DATA_SOURCE = "Data_Source"  # NEW v1.5.12: Environment variable reference (security best practice)
META_KEY_DATA_LABEL = "Data_Label"
META_KEY_SCHEMA_NAME = "Schema_Name"
META_KEY_ZVAFILES = "zVaFiles"
META_KEY_DATA_PARADIGM = "Data_Paradigm"
META_DEFAULT_LABEL = "data"

# Environment variable naming convention (Flask-aligned)
ENV_VAR_PREFIX = "ZDATA_"
ENV_VAR_SUFFIX = "_URL"

# Request keys (handle_request parameters)
REQUEST_KEY_ACTION = "action"
REQUEST_KEY_MODEL = "model"
REQUEST_KEY_OPTIONS = "options"
REQUEST_KEY_TABLES = "tables"

# Option keys (request options)
OPTION_KEY_SCHEMA_CACHED = "_schema_cached"
OPTION_KEY_ALIAS_NAME = "_alias_name"
OPTION_KEY_TABLES = "tables"
OPTION_VALUE_ALL_TABLES = "all"

# Context keys (handle_request context parameter)
CONTEXT_KEY_WIZARD_MODE = "wizard_mode"
CONTEXT_KEY_SCHEMA_CACHE = "schema_cache"

# Reserved schema keys (excluded from table lists)
RESERVED_KEY_META = "Meta"
RESERVED_KEY_DB_PATH = "db_path"

# Return values
RESULT_ERROR = "error"
RESULT_SUCCESS = "success"

# zDisplay color codes
COLOR_ZDATA = "ZDATA"
COLOR_ZCRUD = "ZCRUD"
DISPLAY_STYLE_FULL = "full"

# zDeclare messages
DECLARE_ZDATA_READY = "zData Ready"
DECLARE_ZDATA_REQUEST = "zData Request"

# Error messages
ERROR_NO_ZCLI_INSTANCE = "zData requires a zCLI instance"
ERROR_NO_SESSION_ATTR = "Invalid zCLI instance: missing 'session' attribute"
ERROR_NO_ADAPTER = "No adapter initialized"
ERROR_NO_SCHEMA = "Cannot initialize adapter without schema"
ERROR_FAILED_CONNECT = "Failed to connect to backend"
ERROR_FAILED_INITIALIZE = "Failed to initialize adapter: {error}"
ERROR_NO_HANDLER = "No handler initialized"
ERROR_HANDLER_NO_ADAPTER = "Handler does not have an adapter"
ERROR_NO_SCHEMA_PROVIDED = "No schema provided (model path or cached schema required)"
ERROR_SCHEMA_LOAD_FAILED = "Failed to load schema from: {path}"
ERROR_NO_CACHED_SCHEMA = "No cached schema for first-time connection: ${alias}"
ERROR_NO_ZOPEN = "zOpen not available"
ERROR_NO_SCHEMA_PATH = "No schema path available"
ERROR_NO_TABLES = "No tables available"
ERROR_CSV_NOT_SUPPORTED = "CSV operations not supported for this adapter"
ERROR_MISSING_META_FIELD = "Schema Meta missing required field: '{field}'"
ERROR_DCL_NOT_SUPPORTED = "{adapter} does not support {operation} operations. DCL is only supported by PostgreSQL and MySQL adapters."
ERROR_NO_DATA_CONNECTION = "No database connection info found. Use Data_Source (env var) or Data_Path in schema Meta."

# Security warnings (v1.5.12)
SECURITY_WARNING_DATA_PATH_IN_SCHEMA = "[SECURITY] Data_Path found in schema file. Move credentials to .zEnv using Data_Source pattern!"
SECURITY_INFO_LOADED_FROM_ENV = "[SECURITY] Loaded Data_Path from environment: {env_var}"
SECURITY_INFO_AUTO_CONVENTION = "[SECURITY] Auto-loaded connection from .zEnv using convention: {env_var}"

# Log messages
LOG_ZDATA_READY = "zData Ready"
LOG_LOADING_SCHEMA = "Loading schema from: %s"
LOG_INITIALIZING_ADAPTER = "Initializing %s adapter for: %s (label: %s)"
LOG_CONNECTED_BACKEND = "[OK] Connected to %s backend: %s"
LOG_DISCONNECTED = "Disconnected from backend"
LOG_DISCONNECTED_ONE_SHOT = "Disconnected (one-shot mode)"
LOG_CONNECTION_KEPT_ALIVE = "Connection kept alive (wizard mode)"
LOG_USING_CACHED_SCHEMA = "Using cached schema from alias: $%s"
LOG_REUSING_CONNECTION = "[REUSE] Reusing connection for $%s"
LOG_LOADING_FROM_PINNED = "[LOAD] Loading schema from pinned_cache: $%s"
LOG_CREATED_PERSISTENT = "[CONNECT] Created persistent connection for $%s"
LOG_ERROR_EXECUTING_REQUEST = "Error executing request: %s"

# Log hints
HINT_USE_LOAD_COMMAND = "Hint: Use 'load @data.%s' or provide model path directly"

# Debug log messages (for DDL/DCL/TCL operations)
DEBUG_CREATING_TABLE = "Creating table: %s"
DEBUG_DROPPING_TABLE = "Dropping table: %s"
DEBUG_ALTERING_TABLE = "Altering table: %s"
DEBUG_GRANTING = "Granting %s on %s to %s"
DEBUG_REVOKING = "Revoking %s on %s from %s"
DEBUG_LISTING_PRIVILEGES = "Listing privileges (table=%s, user=%s)"
DEBUG_BEGIN_TRANSACTION = "Beginning transaction"
DEBUG_COMMIT_TRANSACTION = "Committing transaction"
DEBUG_ROLLBACK_TRANSACTION = "Rolling back transaction"

# File operation log messages
LOG_OPENING_SCHEMA = "Opening schema file: %s"
LOG_OPENING_CSV = "Opening CSV file: %s"

# Misc constants
SCHEMA_PATH_SEPARATOR = "."
SCHEMA_NAME_FALLBACK = "unknown"


# ═══════════════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════════════

__all__ = ["zData"]


# ═══════════════════════════════════════════════════════════════════════════════════════
# MAIN ZDATA CLASS
# ═══════════════════════════════════════════════════════════════════════════════════════

class zData:
    """
    Unified Data Management System for zCLI.
    
    This class provides a unified interface for all data operations in zCLI, supporting
    multiple backends (SQLite, PostgreSQL, CSV) through a common API. It handles schema
    loading, adapter initialization, connection management, and operation delegation.
    
    Architecture:
        The zData class acts as a facade that orchestrates:
        - Schema loading (via zLoader)
        - Adapter initialization (via AdapterFactory)
        - Data validation (via DataValidator)
        - Operation routing (via DataOperations)
        - Connection lifecycle (wizard mode vs one-shot mode)
    
    Lifecycle:
        1. Initialization: Create zData instance with zCLI reference
        2. Schema Loading: Load schema from zPath or use cached schema
        3. Adapter Init: Create backend adapter (SQLite/PostgreSQL/CSV)
        4. Connection: Establish database connection
        5. Operations: Execute CRUD/DDL/DCL/TCL operations
        6. Disconnection: Close connection (auto in one-shot, manual in wizard)
    
    Connection Modes:
        Wizard Mode:
            - wizard_mode=True in context
            - Connection reused across multiple operations
            - Schema cache stores connection per alias
            - Manual disconnect or wizard completion
        
        One-Shot Mode:
            - wizard_mode=False (default)
            - New connection per operation
            - Auto-disconnect after operation
    
    Attributes:
        zcli: zCLI core instance (provides access to all subsystems)
        logger: Logger instance for operation logging
        display: zDisplay instance for mode-agnostic output
        loader: zLoader instance for schema loading
        open: zOpen instance for file operations
        schema: Loaded schema dictionary (Meta + table definitions)
        adapter: Backend adapter instance (SQLite/PostgreSQL/CSV)
        validator: DataValidator instance for validation
        operations: DataOperations facade for operation routing
        mycolor: zDisplay color code for zData messages
        _connected: Connection state flag
    
    Usage:
        # One-shot mode
        zdata = zData(zcli)
        request = {"model": "@.zSchema.users", "action": "read"}
        result = zdata.handle_request(request)
        
        # Wizard mode
        context = {"wizard_mode": True, "schema_cache": cache}
        zdata.handle_request(request, context)
    
    Notes:
        - All CRUD/DDL/DCL/TCL methods require schema to be loaded first
        - Connection state is managed automatically based on mode
        - All methods return adapter results or "error" string
        - Type hints are enforced for all public methods
    """

    def __init__(self, zcli: Any) -> None:
        """
        Initialize zData instance with zCLI reference.
        
        This method validates the zCLI instance and stores references to required
        subsystems (logger, display, loader, open). It initializes the zData state
        (schema, adapter, validator, operations) to None, which will be populated
        when a schema is loaded via handle_request() or load_schema().
        
        Args:
            zcli: zCLI core instance with required attributes:
                  - session: Active session dictionary
                  - logger: Logger instance
                  - display: zDisplay instance
                  - loader: zLoader instance
                  - open: zOpen instance
                  - zparser: zParser instance (for path resolution)
        
        Returns:
            None
        
        Raises:
            ValueError: If zcli is None or missing 'session' attribute
        
        Examples:
            # Standard initialization
            zcli = zCLI()
            zdata = zData(zcli)
            
            # Initialization with validation
            if hasattr(zcli, 'session'):
                zdata = zData(zcli)
        
        Notes:
            - This method does NOT load a schema or initialize an adapter
            - Schema loading happens in handle_request() or load_schema()
            - zDeclare announces "zData Ready" to display
        """
        # PHASE 1: Validate zCLI instance
        if zcli is None:
            raise ValueError(ERROR_NO_ZCLI_INSTANCE)

        if not hasattr(zcli, 'session'):
            raise ValueError(ERROR_NO_SESSION_ATTR)

        # PHASE 2: Store zCLI instance and subsystem references
        self.zcli = zcli
        self.logger = zcli.logger
        self.display = zcli.display
        self.loader = zcli.loader
        self.open = zcli.open

        # PHASE 3: Initialize data state (populated on schema load)
        self.schema: Optional[Dict[str, Any]] = None
        self.adapter: Optional[Any] = None
        self.validator: Optional[DataValidator] = None
        self.operations: Optional[DataOperations] = None
        self._connected: bool = False

        # PHASE 4: Display configuration
        self.mycolor = COLOR_ZDATA

        # PHASE 5: Announce readiness
        self.display.zDeclare(DECLARE_ZDATA_READY, color=self.mycolor, indent=0, style=DISPLAY_STYLE_FULL)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════════════════════

    def handle_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Main entry point for all data operations.
        
        This method handles the complete lifecycle of a data operation:
        1. Announces request to display
        2. Initializes schema and adapter (if not already loaded)
        3. Validates connection
        4. Delegates to operation handlers (via DataOperations)
        5. Manages connection lifecycle (wizard mode vs one-shot mode)
        
        The method supports two connection modes:
        - Wizard Mode: Connection stays open across multiple operations
        - One-Shot Mode: Connection auto-closes after operation completes
        
        Args:
            request: Request dictionary with keys:
                     - model: Schema path (e.g., "@.zSchema.users")
                     - action: Operation name ("insert", "read", "update", etc.)
                     - options: Operation options (where, fields, values, etc.)
                     - tables: Target tables (optional, for bulk operations)
            context: Optional context dictionary with keys:
                     - wizard_mode: Boolean (default: False)
                     - schema_cache: SchemaCache instance (for wizard mode)
        
        Returns:
            Operation result from adapter or "error" string on failure:
            - insert/update/delete/upsert: Number of affected rows or True
            - select: List of row dictionaries
            - create_table/drop_table: True/False
            - list_tables: List of table names
            - Error: "error" string
        
        Raises:
            Exception: Propagates exceptions from adapter initialization or operation execution
        
        Examples:
            # Example 1: Simple read operation (one-shot mode)
            request = {
                "model": "@.zSchema.users",
                "action": "read",
                "options": {"where": "age > 25"}
            }
            result = zdata.handle_request(request)
            
            # Example 2: Wizard mode with connection reuse
            context = {"wizard_mode": True, "schema_cache": cache}
            request1 = {"model": "@.zSchema.users", "action": "insert", ...}
            zdata.handle_request(request1, context)
            request2 = {"action": "read", ...}  # Reuses connection
            zdata.handle_request(request2, context)
            
            # Example 3: Cached schema (no model path needed)
            request = {
                "action": "update",
                "options": {
                    "_schema_cached": schema,
                    "_alias_name": "users"
                }
            }
            result = zdata.handle_request(request)
        
        Notes:
            - Wizard mode requires schema_cache in context
            - Connection reuse in wizard mode improves performance
            - One-shot mode auto-disconnects (no cleanup needed)
            - All exceptions are logged with full traceback
        """
        # PHASE 1: Announce request (skip if silent mode for background data fetching)
        silent = request.get("silent", False)
        if not silent:
            self.display.zDeclare(DECLARE_ZDATA_REQUEST, color=COLOR_ZCRUD, indent=1, style=DISPLAY_STYLE_FULL)

        # PHASE 2: Extract wizard mode flag
        wizard_mode = context.get(CONTEXT_KEY_WIZARD_MODE, False) if context else False

        # PHASE 3: Initialize schema and adapter
        if not self._initialize_handler(request, context):
            return RESULT_ERROR

        # PHASE 4: Validate connection
        if not self.is_connected():
            self.logger.error(ERROR_FAILED_CONNECT)
            return RESULT_ERROR

        # PHASE 5: Preprocess request (parse tables option)
        self._preprocess_request(request)

        # PHASE 6: Ensure tables exist (for operations that require tables)
        action = request.get(REQUEST_KEY_ACTION)
        tables = request.get(REQUEST_KEY_TABLES, [])
        if not self.operations.ensure_tables_for_action(action, tables):
            return RESULT_ERROR

        # PHASE 7: Delegate to operation handlers
        try:
            result = self.operations.route_action(action, request)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(LOG_ERROR_EXECUTING_REQUEST, e, exc_info=True)
            result = RESULT_ERROR
        finally:
            # PHASE 8: Manage connection lifecycle
            if not wizard_mode:
                self.disconnect()
                self.logger.debug(LOG_DISCONNECTED_ONE_SHOT)
            else:
                self.logger.debug(LOG_CONNECTION_KEPT_ALIVE)

        return result

    # ═══════════════════════════════════════════════════════════════════════════════════
    # SCHEMA LOADING & ADAPTER INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _initialize_handler(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> bool:
        """
        Initialize schema and adapter with connection reuse support.
        
        This method handles three initialization scenarios:
        1. Wizard mode with connection reuse (check cache first)
        2. One-shot mode with cached schema (from pinned_cache)
        3. Default mode with model path (load schema via zLoader)
        
        Args:
            request: Request dictionary with model/options
            context: Context dictionary with wizard_mode/schema_cache
        
        Returns:
            True if initialization succeeded, False otherwise
        
        Notes:
            - Wizard mode checks schema_cache for existing connection
            - Cached schema bypasses zLoader (faster initialization)
            - Model path triggers full schema load and adapter init
        """
        # PHASE 1: Extract context parameters
        schema_cache = context.get(CONTEXT_KEY_SCHEMA_CACHE) if context else None
        wizard_mode = context.get(CONTEXT_KEY_WIZARD_MODE, False) if context else False

        # PHASE 2: Extract request options
        options = request.get(REQUEST_KEY_OPTIONS, {})
        cached_schema = options.get(OPTION_KEY_SCHEMA_CACHED)
        alias_name = options.get(OPTION_KEY_ALIAS_NAME)

        # PHASE 3: Wizard mode with connection reuse
        if wizard_mode and schema_cache and alias_name:
            return self._init_wizard_handler(schema_cache, alias_name, cached_schema)

        # PHASE 4: One-shot mode with cached schema (from pinned_cache)
        if cached_schema and alias_name:
            self.logger.info(LOG_USING_CACHED_SCHEMA, alias_name)
            self.load_schema(cached_schema)
            return True

        # PHASE 5: Load schema from model path (default)
        return self._init_from_model(request.get(REQUEST_KEY_MODEL))

    def _init_wizard_handler(self, schema_cache: Any, alias_name: str, cached_schema: Optional[Dict[str, Any]]) -> bool:
        """
        Initialize handler for wizard mode with connection reuse.
        
        This method implements the wizard mode connection reuse logic:
        1. Check if connection already exists in schema_cache
        2. If exists, reuse adapter/validator/operations from cache
        3. If not, load schema and store new connection in cache
        
        Args:
            schema_cache: SchemaCache instance (stores connections per alias)
            alias_name: Alias name for connection ($users, $products)
            cached_schema: Optional cached schema dictionary
        
        Returns:
            True if initialization succeeded, False otherwise
        
        Notes:
            - Connection reuse avoids repeated adapter initialization
            - Schema cache is managed by wizard context
            - First use in wizard requires cached_schema
        """
        # PHASE 1: Check if connection already exists (reuse)
        existing_handler = schema_cache.get_connection(alias_name)
        if existing_handler:
            # Reuse existing adapter/validator/operations
            self.adapter = existing_handler.adapter
            self.validator = existing_handler.validator
            self.operations = existing_handler.operations
            self.schema = existing_handler.schema
            self._connected = existing_handler._connected  # pylint: disable=protected-access
            self.logger.info(LOG_REUSING_CONNECTION, alias_name)
            return True

        # PHASE 2: First use in wizard - create and store connection
        if not cached_schema:
            self.logger.error(ERROR_NO_CACHED_SCHEMA.format(alias=alias_name))
            self.logger.error(HINT_USE_LOAD_COMMAND, alias_name)
            return False

        # PHASE 3: Load schema and store new connection
        self.logger.info(LOG_LOADING_FROM_PINNED, alias_name)
        self.load_schema(cached_schema)
        schema_cache.set_connection(alias_name, self)
        self.logger.info(LOG_CREATED_PERSISTENT, alias_name)
        return True

    def _init_from_model(self, model_path: Optional[str]) -> bool:
        """
        Initialize handler by loading schema from model path.
        
        This method loads a schema from a zPath (e.g., @.zSchema.users) using
        zLoader, then initializes the adapter/validator/operations.
        
        Args:
            model_path: zPath to schema file (e.g., "@.zSchema.users")
        
        Returns:
            True if schema loaded and adapter initialized, False otherwise
        
        Raises:
            SchemaNotFoundError: If schema file not found or load failed
        
        Notes:
            - Model path is resolved via zLoader (handles zPath)
            - Schema name extracted from path for error messages
            - Adapter initialization happens in load_schema()
        """
        # PHASE 1: Validate model path
        if not model_path:
            self.logger.error(ERROR_NO_SCHEMA_PROVIDED)
            return False

        # PHASE 2: Load schema via zLoader
        self.logger.info(LOG_LOADING_SCHEMA, model_path)
        schema = self.loader.handle(model_path)

        # PHASE 3: Validate schema load
        if schema == RESULT_ERROR or not schema:
            self.logger.error(ERROR_SCHEMA_LOAD_FAILED.format(path=model_path))
            # Extract schema name from zPath (e.g., '@.zSchema.users' -> 'users')
            schema_name = model_path.split(SCHEMA_PATH_SEPARATOR)[-1] if model_path else SCHEMA_NAME_FALLBACK
            raise SchemaNotFoundError(
                schema_name=schema_name,
                context_type="python",
                zpath=model_path
            )

        # PHASE 4: Load schema and initialize adapter
        self.load_schema(schema)
        return bool(self.adapter)

    def load_schema(self, schema: Dict[str, Any]) -> None:
        """
        Load schema and initialize adapter/validator/operations.
        
        This method performs the complete schema loading and adapter initialization:
        1. Store schema dictionary
        2. Initialize backend adapter (SQLite/PostgreSQL/CSV)
        3. Establish database connection
        4. Initialize validator with schema tables
        5. Initialize operations facade
        
        After this method completes, the zData instance is ready to execute operations.
        
        Args:
            schema: Schema dictionary with Meta section and table definitions
        
        Returns:
            None
        
        Raises:
            ValueError: If Meta section missing required fields
            Exception: If adapter initialization or connection fails
        
        Examples:
            # Load schema and execute operations
            schema = {
                "Meta": {
                    "Data_Type": "sqlite",
                    "Data_Path": "~.zMachine.data/users.db",
                    "Data_Label": "users"
                },
                "users": {
                    "id": {"type": "INTEGER", "primary_key": True},
                    "name": {"type": "TEXT", "required": True}
                }
            }
            zdata.load_schema(schema)
            zdata.insert("users", ["name"], ["Alice"])
            zdata.disconnect()
        
        Notes:
            - This method MUST be called before any CRUD/DDL/DCL/TCL operations
            - Adapter initialization includes connection establishment
            - Validator excludes Meta section from validation
            - Operations facade receives reference to self (for adapter/validator access)
        """
        # PHASE 1: Store schema
        self.schema = schema

        # PHASE 2: Initialize adapter (establishes connection)
        self._initialize_adapter()

        # PHASE 3: Initialize validator with schema tables (exclude Meta)
        schema_tables = {k: v for k, v in schema.items() if k != RESERVED_KEY_META}
        self.validator = DataValidator(schema_tables, logger=self.logger, zcli=self.zcli)

        # PHASE 4: Initialize operations facade (uses self.adapter/validator/schema)
        self.operations = DataOperations(self)

    def _initialize_adapter(self) -> None:
        """
        Initialize backend adapter based on schema Meta section.
        
        This method extracts configuration from the Meta section, resolves paths
        via zParser, creates the appropriate adapter via AdapterFactory, and
        establishes the database connection.
        
        The adapter type (SQLite/PostgreSQL/CSV) is determined by Meta.Data_Type.
        Path resolution handles zPath notation (~.zMachine.*, @.workspace paths).
        
        Returns:
            None
        
        Raises:
            ValueError: If schema is None or Meta missing required fields
            Exception: If adapter creation or connection fails
        
        Notes:
            - This method is called by load_schema()
            - Connection is established automatically (adapter.connect())
            - Logger is set for AdapterFactory before adapter creation
            - self._connected flag is set to True on success
        """
        # PHASE 1: Validate schema
        if not self.schema:
            self.logger.error(ERROR_NO_SCHEMA)
            return

        # PHASE 2: Extract connection config from schema Meta
        meta = self.schema.get(META_KEY, {})

        # PHASE 3: Validate required Meta fields
        if META_KEY_DATA_TYPE not in meta:
            raise ValueError(ERROR_MISSING_META_FIELD.format(field=META_KEY_DATA_TYPE))
        
        # PHASE 3.5: SECURITY - Load Data_Path from environment (v1.5.12)
        # Priority order:
        #   1. Data_Source: Explicit env var reference (e.g., "ZDATA_CONTACTS_URL")
        #   2. Convention: Auto-detect from schema name (e.g., zSchema.contacts → ZDATA_CONTACTS_URL)
        #   3. Data_Path: Direct in schema (DEPRECATED - log security warning)
        data_path = None
        data_path_source = None  # Track where data_path came from for logging
        
        # Option 1: Check for Data_Source (explicit env var reference)
        if META_KEY_DATA_SOURCE in meta:
            env_var_name = meta[META_KEY_DATA_SOURCE]
            data_path_from_env = os.getenv(env_var_name)
            
            if data_path_from_env:
                data_path = data_path_from_env
                data_path_source = "env_explicit"
                self.logger.info(SECURITY_INFO_LOADED_FROM_ENV.format(env_var=env_var_name))
            else:
                self.logger.warning(f"[zData] Environment variable not found: {env_var_name}")
        
        # Option 2: Try auto-convention (if no Data_Source and no Data_Path yet)
        if not data_path and META_KEY_DATA_PATH not in meta:
            # Auto-detect: zSchema.contacts → ZDATA_CONTACTS_URL
            schema_name = meta.get(META_KEY_SCHEMA_NAME, meta.get(META_KEY_ZVAFILES, ""))
            if schema_name:
                # Extract: "zSchema.contacts.yaml" → "contacts"
                schema_key = schema_name.replace("zSchema.", "").replace(".yaml", "").split("/")[-1]
                env_var_name = f"{ENV_VAR_PREFIX}{schema_key.upper()}{ENV_VAR_SUFFIX}"
                data_path_from_env = os.getenv(env_var_name)
                
                if data_path_from_env:
                    data_path = data_path_from_env
                    data_path_source = "env_convention"
                    self.logger.info(SECURITY_INFO_AUTO_CONVENTION.format(env_var=env_var_name))
        
        # Option 3: Fallback to Data_Path in schema (DEPRECATED)
        if not data_path:
            if META_KEY_DATA_PATH in meta:
                data_path = meta[META_KEY_DATA_PATH]
                data_path_source = "schema_file"
                self.logger.warning(SECURITY_WARNING_DATA_PATH_IN_SCHEMA)
            else:
                # No connection info found anywhere
                raise ValueError(ERROR_NO_DATA_CONNECTION)

        # PHASE 4: Extract Meta values
        data_type = meta[META_KEY_DATA_TYPE]
        data_label = meta.get(META_KEY_DATA_LABEL, META_DEFAULT_LABEL)

        # PHASE 5: Resolve special paths via zParser (handles ~.zMachine.* and @ paths)
        data_path = self.zcli.zparser.resolve_data_path(data_path)
        self.logger.info(LOG_INITIALIZING_ADAPTER, data_type, data_path, data_label)

        # PHASE 6: Set logger for factory
        AdapterFactory.set_logger(self.logger)

        # PHASE 7: Create appropriate adapter
        try:
            self.adapter = AdapterFactory.create_adapter(data_type, {
                "path": data_path,
                "label": data_label,
                "meta": meta
            })

            # PHASE 8: Connect
            self.adapter.connect()
            self._connected = True
            self.logger.info(LOG_CONNECTED_BACKEND, data_type, data_path)

        except Exception as e:
            self.logger.error(ERROR_FAILED_INITIALIZE.format(error=e))
            raise

    def _preprocess_request(self, request: Dict[str, Any]) -> None:
        """
        Preprocess request - parse tables option.
        
        This method parses the "tables" option in request.options:
        - "all": Expands to all tables in schema (excluding Meta, db_path)
        - Comma-separated list: Splits into list of table names
        
        The parsed table list is stored in request["tables"] for use by
        operations.ensure_tables_for_action().
        
        Args:
            request: Request dictionary (modified in-place)
        
        Returns:
            None
        
        Examples:
            # Example 1: All tables
            request = {"options": {"tables": "all"}}
            # Result: request["tables"] = ["users", "products", "orders"]
            
            # Example 2: Specific tables
            request = {"options": {"tables": "users, products"}}
            # Result: request["tables"] = ["users", "products"]
        
        Notes:
            - This method modifies request in-place
            - Reserved keys (Meta, db_path) are excluded from "all"
            - Comma-separated strings are split and stripped
        """
        # PHASE 1: Extract tables option
        tables_option = request.get(REQUEST_KEY_OPTIONS, {}).get(OPTION_KEY_TABLES)

        # PHASE 2: Parse tables option
        if tables_option and isinstance(tables_option, str):
            if tables_option.lower() == OPTION_VALUE_ALL_TABLES:
                # Expand "all" to all tables (excluding reserved keys)
                request[REQUEST_KEY_TABLES] = [
                    k for k in self.schema.keys()
                    if k not in (RESERVED_KEY_META, RESERVED_KEY_DB_PATH)
                ]
            else:
                # Split comma-separated list
                request[REQUEST_KEY_TABLES] = [t.strip() for t in tables_option.split(",")]

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CONNECTION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════════════

    def is_connected(self) -> bool:
        """
        Check if adapter is connected to backend.
        
        This method validates connection state by checking:
        1. self._connected flag (set during initialization)
        2. Adapter instance exists
        3. Adapter.is_connected() returns True
        
        Returns:
            True if connected, False otherwise
        
        Examples:
            if zdata.is_connected():
                zdata.insert("users", ["name"], ["Alice"])
            else:
                print("Not connected!")
        
        Notes:
            - This method is called by handle_request() before operations
            - Connection state is managed automatically in wizard/one-shot modes
        """
        return self._connected and self.adapter and self.adapter.is_connected()

    def disconnect(self) -> None:
        """
        Disconnect from backend and close adapter connection.
        
        This method closes the database connection and resets the connection flag.
        It is called automatically in one-shot mode after each operation, or
        manually in wizard mode when operations are complete.
        
        Returns:
            None
        
        Examples:
            # Manual disconnect after operations
            zdata.load_schema(schema)
            zdata.insert("users", ["name"], ["Alice"])
            zdata.disconnect()
        
        Notes:
            - One-shot mode calls this automatically
            - Wizard mode requires manual disconnect
            - Safe to call multiple times (no-op if already disconnected)
        """
        if self.adapter:
            self.adapter.disconnect()
            self._connected = False
            self.logger.info(LOG_DISCONNECTED)

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information from adapter.
        
        This method returns connection metadata from the adapter, typically including:
        - connected: Boolean connection state
        - adapter_type: Backend type (SQLite, PostgreSQL, CSV)
        - path: Database path or CSV directory
        - label: Human-readable label
        
        Returns:
            Dictionary with connection info, or {"connected": False} if not connected
        
        Examples:
            info = zdata.get_connection_info()
            print(f"Connected: {info['connected']}")
            print(f"Adapter: {info.get('adapter_type')}")
        
        Notes:
            - Structure varies by adapter type
            - Always includes "connected" key
        """
        if self.adapter:
            return self.adapter.get_connection_info()
        return {"connected": False}

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CRUD OPERATIONS (Delegated to Adapter)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def insert(self, table: str, fields: List[str], values: List[Any]) -> Any:
        """
        Insert a new record into a table.
        
        This method delegates directly to the adapter's insert() method to add a new
        record to the specified table. The fields and values must match in length and
        order. The adapter handles database-specific INSERT SQL generation.
        
        Args:
            table: Target table name
            fields: List of field names to insert
            values: List of values corresponding to fields
        
        Returns:
            Number of affected rows (typically 1) or adapter-specific result
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Insert a single user
            zdata.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
            
            # Insert with auto-increment ID (omit id field)
            zdata.insert("users", ["name"], ["Bob"])
        
        Notes:
            - Schema loading required before calling this method
            - Fields and values must match in length
            - Adapter handles type conversion and SQL escaping
            - Use handle_request() for validation and hooks
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.insert(table, fields, values)

    def select(self, table: str, fields: Optional[List[str]] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Select records from a table.
        
        This method delegates to the adapter's select() method to query records with
        optional filtering (WHERE), ordering (ORDER BY), limiting (LIMIT), and joining
        (JOIN). The adapter handles database-specific SELECT SQL generation.
        
        Args:
            table: Target table name
            fields: Optional list of field names to select (None = all fields)
            **kwargs: Additional query parameters:
                      - where: WHERE clause (dict or string)
                      - joins: JOIN clauses (list of dicts)
                      - order: ORDER BY clause (string)
                      - limit: LIMIT clause (int)
        
        Returns:
            List of row dictionaries (one dict per row)
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Select all users
            rows = zdata.select("users")
            
            # Select specific fields with WHERE
            rows = zdata.select("users", fields=["name", "email"], where={"age": 25})
            
            # Select with ORDER BY and LIMIT
            rows = zdata.select("users", order="age DESC", limit=10)
        
        Notes:
            - Schema loading required before calling this method
            - WHERE clause can be dict (e.g., {"age": 25}) or string (e.g., "age > 25")
            - Adapter handles auto-join for foreign keys
            - Use handle_request() for complex queries with validation
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.select(table, fields, **kwargs)

    def update(self, table: str, fields: List[str], values: List[Any], where: Any) -> Any:
        """
        Update existing records in a table.
        
        This method delegates to the adapter's update() method to modify records
        matching the WHERE clause. The fields and values must match in length and
        order. The adapter handles database-specific UPDATE SQL generation.
        
        Args:
            table: Target table name
            fields: List of field names to update
            values: List of values corresponding to fields
            where: WHERE clause (dict or string)
        
        Returns:
            Number of affected rows or adapter-specific result
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Update user email
            zdata.update("users", ["email"], ["new@example.com"], where={"id": 1})
            
            # Update multiple fields
            zdata.update("users", ["name", "age"], ["Alice", 30], where={"id": 1})
        
        Notes:
            - Schema loading required before calling this method
            - WHERE clause is required (use empty dict {} to update all rows)
            - Fields and values must match in length
            - Use handle_request() for validation and hooks
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.update(table, fields, values, where)

    def delete(self, table: str, where: Any) -> Any:
        """
        Delete records from a table.
        
        This method delegates to the adapter's delete() method to remove records
        matching the WHERE clause. The adapter handles database-specific DELETE SQL
        generation. This operation is IRREVERSIBLE - use with caution.
        
        Args:
            table: Target table name
            where: WHERE clause (dict or string)
        
        Returns:
            Number of affected rows or adapter-specific result
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Delete specific user
            zdata.delete("users", where={"id": 1})
            
            # Delete users matching criteria
            zdata.delete("users", where={"age": {"<": 18}})
        
        Notes:
            - Schema loading required before calling this method
            - WHERE clause is required (use empty dict {} to delete all rows)
            - Operation is IRREVERSIBLE - backup before deleting
            - Cascade behavior depends on foreign key constraints
            - Use handle_request() for validation and safety checks
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.delete(table, where)

    def upsert(self, table: str, fields: List[str], values: List[Any], conflict_fields: List[str]) -> Any:
        """
        Insert or update a record (UPSERT).
        
        This method delegates to the adapter's upsert() method to insert a new record
        or update an existing one if a conflict occurs on the specified fields. The
        adapter handles database-specific UPSERT SQL generation (INSERT OR REPLACE,
        ON CONFLICT DO UPDATE, or DataFrame merge).
        
        Args:
            table: Target table name
            fields: List of field names to insert/update
            values: List of values corresponding to fields
            conflict_fields: List of fields to check for conflicts (usually primary key)
        
        Returns:
            Number of affected rows or adapter-specific result
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Upsert user by ID (insert if not exists, update if exists)
            zdata.upsert("users", ["id", "name"], [1, "Alice"], conflict_fields=["id"])
            
            # Upsert by email (unique constraint)
            zdata.upsert("users", ["email", "name"], ["alice@example.com", "Alice"], conflict_fields=["email"])
        
        Notes:
            - Schema loading required before calling this method
            - Conflict fields typically include primary key or unique constraints
            - SQLite: Uses INSERT OR REPLACE
            - PostgreSQL: Uses ON CONFLICT DO UPDATE
            - CSV: Uses DataFrame merge
            - Use handle_request() for validation and hooks
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.upsert(table, fields, values, conflict_fields)

    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        This method delegates to the adapter's list_tables() method to retrieve
        all table names from the backend. The result includes all user-created
        tables but excludes system tables (e.g., sqlite_sequence).
        
        Returns:
            List of table names
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            tables = zdata.list_tables()
            print(f"Available tables: {tables}")
        
        Notes:
            - Schema loading required before calling this method
            - System tables are typically excluded
            - CSV adapter returns list of CSV files
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        return self.adapter.list_tables()

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DDL OPERATIONS (Data Definition Language)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def create_table(self, table_name: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create a new table in the database.
        
        This method delegates to the adapter's create_table() method to create a table
        from a schema definition. If schema is not provided, it is extracted from the
        loaded schema dictionary. The adapter handles database-specific CREATE TABLE
        SQL generation.
        
        Args:
            table_name: Name of table to create
            schema: Optional table schema definition (None = use loaded schema)
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
            TableNotFoundError: If schema not provided and table not in loaded schema
        
        Examples:
            # Create table from loaded schema
            zdata.create_table("users")
            
            # Create table with explicit schema
            schema = {
                "id": {"type": "INTEGER", "primary_key": True},
                "name": {"type": "TEXT", "required": True}
            }
            zdata.create_table("users", schema)
        
        Notes:
            - Schema loading required before calling this method
            - Table schema must define field types and constraints
            - Adapter handles database-specific type mapping
            - Use handle_request() for validation and idempotent creation
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        # If schema not provided, get from loaded schema
        if schema is None:
            if not self.schema or table_name not in self.schema:
                # Extract schema name if available (e.g., from Meta section)
                schema_name = self.schema.get(META_KEY, {}).get(META_KEY_SCHEMA_NAME) if self.schema else None
                raise TableNotFoundError(table_name, schema_name=schema_name)
            schema = self.schema[table_name]
        
        self.logger.debug(DEBUG_CREATING_TABLE, table_name)
        return self.adapter.create_table(table_name, schema)

    def drop_table(self, table_name: str) -> Any:
        """
        Drop (delete) a table from the database.
        
        This method delegates to the adapter's drop_table() method to remove a table
        and all its data. This operation is IRREVERSIBLE - use with extreme caution.
        The adapter handles database-specific DROP TABLE SQL generation.
        
        Args:
            table_name: Name of table to drop
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Drop a table (IRREVERSIBLE!)
            zdata.drop_table("old_users")
        
        Notes:
            - Schema loading required before calling this method
            - Operation is IRREVERSIBLE - backup before dropping
            - Cascade behavior depends on foreign key constraints
            - Some adapters support IF EXISTS (no error if table doesn't exist)
            - Use handle_request() for validation and safety checks
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        self.logger.debug(DEBUG_DROPPING_TABLE, table_name)
        return self.adapter.drop_table(table_name)

    def alter_table(self, table_name: str, changes: Dict[str, Any]) -> Any:
        """
        Alter table structure by adding or dropping columns.
        
        This method delegates to the adapter's alter_table() method to modify an
        existing table's structure. The adapter handles database-specific ALTER TABLE
        SQL generation.
        
        Args:
            table_name: Name of table to alter
            changes: Dictionary of changes (e.g., {"add": {"new_field": {...}}, "drop": ["old_field"]})
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Add a new column
            changes = {"add": {"age": {"type": "INTEGER"}}}
            zdata.alter_table("users", changes)
            
            # Drop a column (not supported by all adapters)
            changes = {"drop": ["old_field"]}
            zdata.alter_table("users", changes)
        
        Notes:
            - Schema loading required before calling this method
            - Not all adapters support all ALTER operations (e.g., SQLite limited)
            - Adding columns may require default values
            - Dropping columns may affect dependent objects (views, indexes)
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        self.logger.debug(DEBUG_ALTERING_TABLE, table_name)
        return self.adapter.alter_table(table_name, changes)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        This method delegates to the adapter's table_exists() method to check if a
        table exists. The adapter queries database metadata to determine existence.
        
        Args:
            table_name: Name of table to check
        
        Returns:
            True if table exists, False otherwise
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            if zdata.table_exists("users"):
                print("Users table exists!")
            else:
                zdata.create_table("users")
        
        Notes:
            - Schema loading required before calling this method
            - Check is case-sensitive or case-insensitive depending on adapter
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        return self.adapter.table_exists(table_name)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DCL OPERATIONS (Data Control Language - PostgreSQL/MySQL only)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def grant(self, privileges: str, table_name: str, user: str) -> Any:
        """
        Grant privileges to a user (PostgreSQL/MySQL only).
        
        This method delegates to the adapter's grant() method to grant database
        privileges to a user. This operation is only supported by PostgreSQL and
        MySQL adapters.
        
        Args:
            privileges: Comma-separated list of privileges (e.g., "SELECT, INSERT")
            table_name: Target table name
            user: Username to grant privileges to
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
            NotImplementedError: If adapter does not support DCL operations
        
        Examples:
            # Grant SELECT and INSERT to user
            zdata.grant("SELECT, INSERT", "users", "app_user")
        
        Notes:
            - Schema loading required before calling this method
            - Only supported by PostgreSQL and MySQL adapters
            - Requires appropriate database permissions
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        # Check if adapter supports DCL
        if not hasattr(self.adapter, 'grant'):
            adapter_type = self.adapter.__class__.__name__
            raise NotImplementedError(
                ERROR_DCL_NOT_SUPPORTED.format(adapter=adapter_type, operation="GRANT")
            )
        
        self.logger.debug(DEBUG_GRANTING, privileges, table_name, user)
        return self.adapter.grant(privileges, table_name, user)

    def revoke(self, privileges: str, table_name: str, user: str) -> Any:
        """
        Revoke privileges from a user (PostgreSQL/MySQL only).
        
        This method delegates to the adapter's revoke() method to revoke database
        privileges from a user. This operation is only supported by PostgreSQL and
        MySQL adapters.
        
        Args:
            privileges: Comma-separated list of privileges (e.g., "SELECT, INSERT")
            table_name: Target table name
            user: Username to revoke privileges from
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
            NotImplementedError: If adapter does not support DCL operations
        
        Examples:
            # Revoke INSERT from user
            zdata.revoke("INSERT", "users", "app_user")
        
        Notes:
            - Schema loading required before calling this method
            - Only supported by PostgreSQL and MySQL adapters
            - Requires appropriate database permissions
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        # Check if adapter supports DCL
        if not hasattr(self.adapter, 'revoke'):
            adapter_type = self.adapter.__class__.__name__
            raise NotImplementedError(
                ERROR_DCL_NOT_SUPPORTED.format(adapter=adapter_type, operation="REVOKE")
            )
        
        self.logger.debug(DEBUG_REVOKING, privileges, table_name, user)
        return self.adapter.revoke(privileges, table_name, user)

    def list_privileges(self, table_name: Optional[str] = None, user: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List privileges for tables and users (PostgreSQL/MySQL only).
        
        This method delegates to the adapter's list_privileges() method to query
        database privileges. This operation is only supported by PostgreSQL and
        MySQL adapters.
        
        Args:
            table_name: Optional table name to filter by
            user: Optional username to filter by
        
        Returns:
            List of privilege dictionaries
        
        Raises:
            RuntimeError: If adapter not initialized
            NotImplementedError: If adapter does not support DCL operations
        
        Examples:
            # List all privileges
            privs = zdata.list_privileges()
            
            # List privileges for specific user
            privs = zdata.list_privileges(user="app_user")
        
        Notes:
            - Schema loading required before calling this method
            - Only supported by PostgreSQL and MySQL adapters
            - Requires appropriate database permissions
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        # Check if adapter supports DCL
        if not hasattr(self.adapter, 'list_privileges'):
            adapter_type = self.adapter.__class__.__name__
            raise NotImplementedError(
                ERROR_DCL_NOT_SUPPORTED.format(adapter=adapter_type, operation="privilege listing")
            )
        
        self.logger.debug(DEBUG_LISTING_PRIVILEGES, table_name, user)
        return self.adapter.list_privileges(table_name, user)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # TCL OPERATIONS (Transaction Control Language)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def begin_transaction(self) -> Any:
        """
        Begin a new database transaction.
        
        This method delegates to the adapter's begin_transaction() method to start
        a transaction. Subsequent operations are part of the transaction until
        commit() or rollback() is called.
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Transaction workflow
            zdata.begin_transaction()
            try:
                zdata.insert("users", ["name"], ["Alice"])
                zdata.insert("profiles", ["user_id"], [1])
                zdata.commit()
            except Exception:
                zdata.rollback()
        
        Notes:
            - Schema loading required before calling this method
            - Not all adapters support transactions (e.g., CSV)
            - Transactions are not nested
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        self.logger.debug(DEBUG_BEGIN_TRANSACTION)
        return self.adapter.begin_transaction()

    def commit(self) -> Any:
        """
        Commit the current transaction.
        
        This method delegates to the adapter's commit() method to commit all
        operations since begin_transaction() was called.
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            zdata.begin_transaction()
            zdata.insert("users", ["name"], ["Alice"])
            zdata.commit()
        
        Notes:
            - Schema loading required before calling this method
            - Must be called after begin_transaction()
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        self.logger.debug(DEBUG_COMMIT_TRANSACTION)
        return self.adapter.commit()

    def rollback(self) -> Any:
        """
        Rollback the current transaction.
        
        This method delegates to the adapter's rollback() method to undo all
        operations since begin_transaction() was called.
        
        Returns:
            True on success, False or exception on failure
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            zdata.begin_transaction()
            try:
                zdata.insert("users", ["name"], ["Alice"])
                zdata.insert("profiles", ["user_id"], [1])
                zdata.commit()
            except Exception:
                zdata.rollback()  # Undo both inserts
        
        Notes:
            - Schema loading required before calling this method
            - Must be called after begin_transaction()
            - Use in exception handlers for error recovery
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        self.logger.debug(DEBUG_ROLLBACK_TRANSACTION)
        return self.adapter.rollback()

    # ═══════════════════════════════════════════════════════════════════════════════════
    # MIGRATION OPERATIONS (Declarative Schema Migrations)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def migrate(self, new_schema_path: str, dry_run: bool = False, 
                auto_approve: bool = False, schema_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute declarative schema migration to new schema version.
        
        This method performs a declarative migration by comparing the current schema
        with a new target schema and automatically applying the necessary DDL operations
        (CREATE TABLE, ALTER TABLE, DROP TABLE) to bring the database in line with
        the new schema.
        
        Migration Flow:
        1. Load current schema (from self.schema)
        2. Load new schema from new_schema_path
        3. Compute diff via schema_diff.diff_schemas()
        4. Display preview via zDisplay
        5. Prompt for confirmation (unless dry_run or auto_approve)
        6. Execute DDL operations in transaction
        7. Record migration in _zdata_migrations table
        8. Return success/failure result
        
        Args:
            new_schema_path: Path to new schema YAML file (supports zPath: @., ~.)
            dry_run: If True, preview changes without executing (default False)
            auto_approve: If True, skip confirmation prompt (default False)
            schema_version: Optional version string (e.g., "v1.2.3", git commit)
        
        Returns:
            Dict with keys:
            - success: True if migration succeeded, False otherwise
            - diff: Structured diff from schema_diff.diff_schemas()
            - operations_executed: Count of DDL operations performed
            - error: Error message if failed (only if success=False)
        
        Raises:
            RuntimeError: If adapter not initialized or schema not loaded
            KeyError: If new schema path invalid
            Exception: Any database errors during execution
        
        Examples:
            # Dry-run (preview only)
            result = zdata.migrate("@myapp.users_v2.yaml", dry_run=True)
            
            # Execute migration with confirmation
            result = zdata.migrate("@myapp.users_v2.yaml")
            
            # Execute migration without confirmation (use with caution!)
            result = zdata.migrate("@myapp.users_v2.yaml", auto_approve=True)
            
            # Execute with version tracking
            result = zdata.migrate("@myapp.users_v2.yaml", schema_version="v1.2.3")
        
        Notes:
            - Dry-run mode: Safe for testing, displays preview without executing
            - Auto-approve mode: Use with caution! Skips confirmation prompts
            - Transaction wrapping: All operations are atomic (all-or-nothing)
            - Rollback on failure: Any error triggers automatic rollback
            - History tracking: Successful migrations recorded in _zdata_migrations
            - Idempotency: Re-running same schema is safe (no-op if no changes)
            - Schema must be loaded before calling migrate()
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        if not self.schema:
            raise RuntimeError("No schema loaded. Call load_schema() first.")
        
        # Load new schema from path
        from zCLI.subsystems.zData.zData_modules.shared.migration_history import (
            get_current_schema_hash
        )
        
        # Parse new schema path via zParser
        new_schema = self.zcli.loader.load(new_schema_path)
        
        # Compute schema hash
        schema_hash = get_current_schema_hash(new_schema)
        
        # Build migration request
        request = {
            "old_schema": self.schema,
            "new_schema": new_schema,
            "dry_run": dry_run,
            "auto_approve": auto_approve,
            "schema_version": schema_version or "unknown",
            "schema_hash": schema_hash
        }
        
        # Execute migration via operations facade
        result = self.operations.route_action("migrate", request)
        
        return result

    def get_migration_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve migration execution history.
        
        Returns list of migration records from the _zdata_migrations table,
        ordered by applied_at (most recent first). Useful for displaying
        migration audit trail to users.
        
        Args:
            limit: Maximum number of records to return (default 100)
        
        Returns:
            List of migration record dicts, each with keys:
            - id: Migration ID
            - schema_version: Version string (e.g., "v1.2.3")
            - schema_hash: SHA256 hash of schema
            - applied_at: ISO 8601 timestamp when migration ran
            - duration_ms: Migration execution time in milliseconds
            - tables_added: Count of tables created
            - tables_dropped: Count of tables dropped
            - columns_added: Count of columns added
            - columns_dropped: Count of columns dropped
            - status: "success" or "failed"
            - error_message: Error details if failed
        
        Raises:
            RuntimeError: If adapter not initialized
        
        Examples:
            # Get recent migrations
            history = zdata.get_migration_history(limit=10)
            for record in history:
                print(f"{record['applied_at']}: {record['schema_version']} - {record['status']}")
            
            # Check if any migrations applied
            history = zdata.get_migration_history()
            if history:
                print(f"Last migration: {history[0]['applied_at']}")
            else:
                print("No migrations applied yet")
        
        Notes:
            - Returns empty list if no migrations or table doesn't exist
            - Results ordered by applied_at DESC (newest first)
            - Limit prevents loading huge history (default 100)
            - Shows both successful and failed migrations
        """
        if not self.adapter:
            raise RuntimeError(ERROR_NO_ADAPTER)
        
        from zCLI.subsystems.zData.zData_modules.shared.migration_history import (
            get_migration_history as _get_history
        )
        
        return _get_history(self.adapter, limit=limit)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # FILE OPERATIONS (zOpen Integration)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def open_schema(self, schema_path: Optional[str] = None) -> Any:
        """
        Open schema file in editor via zOpen.
        
        This method delegates to zOpen to open the schema YAML file in the configured
        editor. If schema_path is not provided, it is extracted from the Meta.zVaFiles
        field of the loaded schema.
        
        Args:
            schema_path: Optional path to schema file (None = use Meta.zVaFiles)
        
        Returns:
            Result from zOpen.handle() or "error" on failure
        
        Examples:
            # Open loaded schema in editor
            zdata.open_schema()
            
            # Open specific schema file
            zdata.open_schema("@.zSchema.users.yaml")
        
        Notes:
            - Requires zOpen subsystem
            - Schema loading required if schema_path not provided
            - Editor is configured in zSession or zMachine
        """
        if not self.open:
            self.logger.warning(ERROR_NO_ZOPEN)
            return RESULT_ERROR

        # Use current schema's path if not specified
        if not schema_path and self.schema:
            meta = self.schema.get(META_KEY, {})
            schema_path = meta.get(META_KEY_ZVAFILES)

        if not schema_path:
            self.logger.error(ERROR_NO_SCHEMA_PATH)
            return RESULT_ERROR

        self.logger.info(LOG_OPENING_SCHEMA, schema_path)
        return self.open.handle({"zOpen": {"path": schema_path}})

    def open_csv(self, table_name: Optional[str] = None) -> Any:
        """
        Open CSV data file in editor via zOpen.
        
        This method delegates to zOpen to open a CSV data file in the configured
        editor. This operation is only supported by the CSV adapter. If table_name
        is not provided, the first table is used.
        
        Args:
            table_name: Optional table name (None = first table)
        
        Returns:
            Result from zOpen.handle() or "error" on failure
        
        Examples:
            # Open first table's CSV file
            zdata.open_csv()
            
            # Open specific table's CSV file
            zdata.open_csv("users")
        
        Notes:
            - Requires zOpen subsystem
            - Only supported by CSV adapter
            - Schema loading required before calling this method
            - CSV path is determined by adapter
        """
        if not self.open:
            self.logger.warning(ERROR_NO_ZOPEN)
            return RESULT_ERROR

        if not self.adapter:
            self.logger.error(ERROR_NO_ADAPTER)
            return RESULT_ERROR

        # Get CSV path from adapter
        if hasattr(self.adapter, '_get_csv_path'):
            if not table_name:
                # List available tables
                tables = self.list_tables()
                if not tables:
                    self.logger.error(ERROR_NO_TABLES)
                    return RESULT_ERROR
                table_name = tables[0]  # Default to first table

            csv_path = str(self.adapter._get_csv_path(table_name))  # pylint: disable=protected-access
            self.logger.info(LOG_OPENING_CSV, csv_path)
            return self.open.handle({"zOpen": {"path": csv_path}})

        self.logger.error(ERROR_CSV_NOT_SUPPORTED)
        return RESULT_ERROR
