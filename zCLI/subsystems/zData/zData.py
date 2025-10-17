# zCLI/subsystems/zData/zData.py

"""Unified data management with dual-paradigm support (classical/quantum)."""

from .zData_modules.paradigms.classical import ClassicalData
from .zData_modules.paradigms.quantum import QuantumData

class zData:
    """Unified data management dispatcher routing to classical or quantum handlers."""

    def __init__(self, zcli):
        """Initialize zData instance."""

        # Validate zCLI instance
        if zcli is None:
            raise ValueError("zData requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Modern architecture: zCLI instance provides all dependencies
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.loader = zcli.loader
        self.zparser = zcli.zparser  # Path resolution
        self.zfunc = zcli.zfunc      # Function hooks & transforms
        self.open = zcli.open        # File/schema opening

        # Data state
        self.schema = None
        self.paradigm = None  # 'classical' or 'quantum'
        self.handler = None   # ClassicalData or QuantumData instance
        self.mycolor = "ZDATA"
        
        self.display.handle({
            "event": "sysmsg",
            "label": "zData Ready",
            "color": self.mycolor,
            "indent": 0
        })


    def handle_request(self, request, context=None):
        """Main entry point for data operations."""
        self.display.handle({
            "event": "sysmsg",
            "style": "full",
            "label": "zData Request",
            "color": "ZCRUD",
            "indent": 1
        })

        # Initialize schema and handler
        wizard_mode = context.get("wizard_mode", False) if context else False
        if not self._initialize_handler(request, context):
            return "error"

        # Validate connection
        if not self.is_connected():
            self.logger.error("Failed to connect to backend")
            return "error"

        # Delegate to handler
        try:
            result = self.handler.handle_request(request)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Error executing request: %s", e, exc_info=True)
            result = "error"
        finally:
            if not wizard_mode:
                self.disconnect()
                self.logger.debug("Disconnected (one-shot mode)")
            else:
                self.logger.debug("Connection kept alive (wizard mode)")

        return result

    def _initialize_handler(self, request, context):
        """Initialize schema handler with connection reuse support."""
        schema_cache = context.get("schema_cache") if context else None
        wizard_mode = context.get("wizard_mode", False) if context else False

        options = request.get("options", {})
        cached_schema = options.get("_schema_cached")
        alias_name = options.get("_alias_name")

        # Wizard mode with connection reuse
        if wizard_mode and schema_cache and alias_name:
            return self._init_wizard_handler(schema_cache, alias_name, cached_schema)

        # One-shot mode with cached schema
        if cached_schema:
            self.logger.info("Using cached schema from alias: $%s", alias_name)
            self.load_schema(cached_schema)
            return True

        # Load schema from model path
        return self._init_from_model(request.get("model"))

    def _init_wizard_handler(self, schema_cache, alias_name, cached_schema):
        """Initialize handler for wizard mode with connection reuse."""
        existing_handler = schema_cache.get_connection(alias_name)
        if existing_handler:
            self.handler = existing_handler
            self.schema = existing_handler.schema
            self.paradigm = self._detect_paradigm(self.schema)
            self.logger.info("Reusing connection for $%s", alias_name)
            return True

        # First use in wizard - create and store connection
        if not cached_schema:
            self.logger.error("No cached schema in wizard mode for alias: $%s", alias_name)
            return False

        self.logger.info("Using cached schema from alias: $%s", alias_name)
        self.load_schema(cached_schema)
        schema_cache.set_connection(alias_name, self.handler)
        self.logger.info("🔗 Created persistent connection for $%s", alias_name)
        return True

    def _init_from_model(self, model_path):
        """Initialize handler by loading schema from model path."""
        if not model_path:
            self.logger.error("No schema provided (model path or cached schema required)")
            return False

        self.logger.info("Loading schema from: %s", model_path)
        schema = self.loader.handle(model_path)
        if schema == "error" or not schema:
            self.logger.error("Failed to load schema from: %s", model_path)
            return False

        self.load_schema(schema)
        return bool(self.handler)

    def load_schema(self, schema):
        """Load schema and initialize appropriate handler (classical or quantum)."""
        self.schema = schema

        # Detect paradigm from schema
        self.paradigm = self._detect_paradigm(schema)
        self.logger.info("Detected data paradigm: %s", self.paradigm)

        # Initialize appropriate handler based on detected paradigm
        # NOTE: Creating the handler instance automatically:
        #   1. Calls the handler's __init__ method
        #   2. Initializes the backend adapter (SQLite, CSV, PostgreSQL, etc.)
        #   3. Establishes database connection
        #   4. Sets up schema/tables as needed
        # After this block, self.handler is connected and ready for operations
        if self.paradigm == "classical":
            # Classical: Conventional relational database pattern
            self.handler = ClassicalData(self.zcli, schema)
        elif self.paradigm == "quantum":
            # Quantum: Abstracted data structures (zMemoryCell/zQuark pattern)
            self.handler = QuantumData(self.zcli, schema)
        else:
            raise ValueError(f"Unknown data paradigm: {self.paradigm}")

    def _detect_paradigm(self, schema):
        """Detect data paradigm from schema metadata."""
        meta = schema.get("Meta", {})

        # Get paradigm from Meta, default to classical
        paradigm = meta.get("Data_Paradigm", "classical").lower()

        if paradigm in ["classical", "quantum"]:
            return paradigm

        self.logger.warning(
            "Unknown Data_Paradigm '%s', defaulting to classical", 
            paradigm
        )
        return "classical"

    def get_connection_info(self):
        """Get connection information."""
        if self.handler:
            return self.handler.get_connection_info()
        return {"connected": False}

    def is_connected(self):
        """Check if handler is connected."""
        return self.handler and self.handler.is_connected()

    def disconnect(self):
        """Disconnect from backend."""
        if self.handler:
            self.handler.disconnect()
            self.logger.info("Disconnected from backend")

    # ═══════════════════════════════════════════════════════════
    # CRUD Operations (Delegated to Handler)
    # ═══════════════════════════════════════════════════════════

    def insert(self, table, fields, values):
        """Insert a row."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.insert(table, fields, values)

    def select(self, table, fields=None, **kwargs):
        """Select rows."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.select(table, fields, 
                                   kwargs.get("where"), 
                                   kwargs.get("joins"), 
                                   kwargs.get("order"), 
                                   kwargs.get("limit"))

    def update(self, table, fields, values, where):
        """Update rows."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.update(table, fields, values, where)

    def delete(self, table, where):
        """Delete rows."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.delete(table, where)

    def upsert(self, table, fields, values, conflict_fields):
        """Upsert (insert or update) a row."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.upsert(table, fields, values, conflict_fields)

    def list_tables(self):
        """List all tables."""
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.list_tables()

    # ═══════════════════════════════════════════════════════════
    # File Operations (zOpen Integration)
    # ═══════════════════════════════════════════════════════════

    def open_schema(self, schema_path=None):
        """Open schema file in editor via zOpen."""
        if not self.open:
            self.logger.warning("zOpen not available")
            return "error"

        # Use current schema's path if not specified
        if not schema_path and self.schema:
            meta = self.schema.get("Meta", {})
            schema_path = meta.get("zVaFiles")

        if not schema_path:
            self.logger.error("No schema path available")
            return "error"

        self.logger.info("Opening schema file: %s", schema_path)
        return self.open.handle({"zOpen": {"path": schema_path}})

    def open_csv(self, table_name=None):
        """Open CSV data file in editor via zOpen."""
        if not self.open:
            self.logger.warning("zOpen not available")
            return "error"

        if not self.handler:
            self.logger.error("No handler initialized")
            return "error"

        # Get CSV path from adapter
        if hasattr(self.handler, 'adapter') and hasattr(self.handler.adapter, '_get_csv_path'):
            if not table_name:
                # List available tables
                tables = self.handler.list_tables()
                if not tables:
                    self.logger.error("No tables available")
                    return "error"
                table_name = tables[0]  # Default to first table

            csv_path = str(self.handler.adapter._get_csv_path(table_name))
            self.logger.info("Opening CSV file: %s", csv_path)
            return self.open.handle({"zOpen": {"path": csv_path}})

        self.logger.error("CSV operations not supported for this adapter")
        return "error"
