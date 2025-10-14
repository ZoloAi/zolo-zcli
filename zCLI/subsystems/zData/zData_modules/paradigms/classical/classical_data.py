"""Classical data management handler."""

from logger import Logger
from ...shared.backends.adapter_factory import AdapterFactory
from ...shared.validator import DataValidator
from ...shared.data_operations import DataOperations

# Logger instance
logger = Logger.get_logger(__name__)

class ClassicalData:
    """Classical data handler - manages connections and delegates operations."""

    def __init__(self, zcli, schema):
        """Initialize ClassicalData handler."""
        self.zcli = zcli
        self.schema = schema
        self.logger = zcli.logger
        self.adapter = None
        self._connected = False

        # Initialize validator with schema (excluding Meta section)
        schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
        self.validator = DataValidator(schema_tables)

        # Initialize adapter
        self._initialize_adapter()

        # Initialize shared operations (uses this handler's adapter/validator)
        self.operations = DataOperations(self)

    def _initialize_adapter(self):
        """Initialize backend adapter based on schema Meta."""
        if not self.schema:
            self.logger.error("Cannot initialize adapter without schema")
            return

        # Extract connection config from schema
        meta = self.schema.get("Meta", {})

        # Validate required Meta fields
        if "Data_Type" not in meta:
            raise ValueError("Schema Meta missing required field: 'Data_Type'")
        if "Data_path" not in meta:
            raise ValueError("Schema Meta missing required field: 'Data_path'")

        data_type = meta["Data_Type"]
        data_path = meta["Data_path"]
        data_label = meta.get("Data_Label", "data")

        # Resolve special paths via zParser (handles ~.zMachine.* and @ paths)
        data_path = self.zcli.zparser.resolve_data_path(data_path)
        self.logger.info("Initializing %s adapter for: %s (label: %s)", data_type, data_path, data_label)

        # Create appropriate adapter
        try:
            self.adapter = AdapterFactory.create_adapter(data_type, {
                "path": data_path,
                "label": data_label,
                "meta": meta
            })

            # Connect
            self.adapter.connect()
            self._connected = True
            self.logger.info("[OK] Connected to %s backend: %s", data_type, data_path)

        except Exception as e:
            self.logger.error("Failed to initialize adapter: %s", e)
            raise

    def handle_request(self, request):
        """Handle classical data operation request."""
        action = request.get("action")
        self.logger.info("🎬 Classical data action: %s", action)

        # Preprocess and ensure tables
        self._preprocess_request(request)
        tables = request.get("tables", [])
        if not self.operations.ensure_tables_for_action(action, tables):
            return "error"

        # Delegate to operations
        return self.operations.route_action(action, request)

    def _preprocess_request(self, request):
        """Preprocess request - parse tables from options."""
        tables_option = request.get("options", {}).get("tables")
        if tables_option and isinstance(tables_option, str):
            if tables_option.lower() == "all":
                request["tables"] = [k for k in self.schema.keys() if k not in ("Meta", "db_path")]
            else:
                request["tables"] = [t.strip() for t in tables_option.split(",")]

    # ═══════════════════════════════════════════════════════════
    # Connection Management
    # ═══════════════════════════════════════════════════════════

    def is_connected(self):
        """Check if adapter is connected."""
        return self._connected and self.adapter and self.adapter.is_connected()

    def disconnect(self):
        """Disconnect from backend."""
        if self.adapter:
            self.adapter.disconnect()
            self._connected = False
            logger.info("Disconnected from backend")

    def get_connection_info(self):
        """Get connection information."""
        if self.adapter:
            return self.adapter.get_connection_info()
        return {"connected": False}
