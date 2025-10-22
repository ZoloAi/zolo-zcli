# zCLI/subsystems/zData/zData_modules/shared/backends/postgresql_adapter.py

"""PostgreSQL backend adapter implementation."""

from zCLI import datetime, yaml
from .sql_adapter import SQLAdapter

# Try to import psycopg2
try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class PostgreSQLAdapter(SQLAdapter):
    """PostgreSQL backend implementation (inherits SQL logic from SQLAdapter)."""

    def __init__(self, config, logger=None):
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgreSQL adapter.\n"
                "Install with: pip install zolo-zcli[postgresql]"
            )

        # Call parent init (sets base_path, data_label, and db_path)
        super().__init__(config, logger)

        # PostgreSQL uses Data_Label as database name (not filename)
        self.database_name = self.data_label

        # Connection parameters from Meta
        meta = config.get("meta", {})
        self.host = meta.get("Data_Host", "localhost")
        self.port = meta.get("Data_Port", 5432)

        # Smart user detection: try specified user, fallback to system user
        specified_user = meta.get("Data_User")
        if specified_user:
            self.user = specified_user
        else:
            # Auto-detect: use system username (works on macOS Homebrew)
            import getpass
            self.user = getpass.getuser()
            if self.logger:
                self.logger.debug("No Data_User specified, using system user: %s", self.user)

        self.password = meta.get("Data_Password")

        # Override db_path to be connection string (not file path)
        self.db_path = f"{self.host}:{self.port}/{self.database_name}"

        if self.logger:
            self.logger.debug("PostgreSQL config - database: %s, host: %s, port: %s, user: %s",
                    self.database_name, self.host, self.port, self.user)

    def connect(self):
        """Establish PostgreSQL connection (creates database if needed)."""
        try:
            # Step 1: Connect to default 'postgres' database to create our database
            if self.logger:
                self.logger.info("Connecting to PostgreSQL server at %s:%s", self.host, self.port)

            conn_params = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "database": "postgres"  # Default database always exists
            }

            if self.password:
                conn_params["password"] = self.password

            temp_conn = psycopg2.connect(**conn_params)
            temp_conn.autocommit = True  # Need autocommit to create database
            temp_cursor = temp_conn.cursor()

            # Step 2: Check if our database exists
            temp_cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database_name,)
            )

            if not temp_cursor.fetchone():
                # Database doesn't exist - create it
                if self.logger:
                    self.logger.info("Creating database: %s", self.database_name)
                # Use sql.Identifier to safely quote database name
                temp_cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.database_name)
                    )
                )
                if self.logger:
                    self.logger.info("[OK] Created database: %s", self.database_name)
            else:
                if self.logger:
                    self.logger.debug("Database already exists: %s", self.database_name)

            temp_cursor.close()
            temp_conn.close()

            # Step 3: Connect to our actual database
            conn_params["database"] = self.database_name
            self.connection = psycopg2.connect(**conn_params)
            self.connection.autocommit = False  # Normal transaction mode

            if self.logger:
                self.logger.info("Connected to PostgreSQL database: %s", self.database_name)

            # Write project info file to Data_path
            self._write_project_info()

            return self.connection

        except Exception as e:  # pylint: disable=broad-except
            if self.logger:
                self.logger.error("PostgreSQL connection failed: %s", e)
            raise

    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            try:
                if self.cursor:
                    self.cursor.close()
                    self.cursor = None
                self.connection.close()
                self.connection = None
                if self.logger:
                    self.logger.info("Disconnected from PostgreSQL: %s", self.database_name)
            except Exception as e:  # pylint: disable=broad-except
                if self.logger:
                    self.logger.error("Error closing PostgreSQL connection: %s", e)

    def get_cursor(self):
        """Get or create a cursor."""
        if not self.cursor and self.connection:
            self.cursor = self.connection.cursor()
        return self.cursor

    def create_table(self, table_name, schema):
        """Create table with PostgreSQL-specific features (SERIAL for PKs)."""
        if self.logger:
            self.logger.info("Creating table: %s", table_name)

        cur = self.get_cursor()
        composite_pk = self._get_composite_pk(schema)
        field_defs, foreign_keys = self._build_field_definitions(schema, composite_pk)

        # Add composite primary key as table-level constraint
        table_constraints = []
        if composite_pk:
            pk_columns = ", ".join(composite_pk)
            table_constraints.append(f"PRIMARY KEY ({pk_columns})")
            if self.logger:
                self.logger.info("Adding composite PRIMARY KEY (%s)", pk_columns)

        # Build and execute DDL
        all_defs = field_defs + table_constraints + foreign_keys
        ddl = f"CREATE TABLE {table_name} ({', '.join(all_defs)});"

        if self.logger:
            self.logger.info("Executing DDL: %s", ddl)
        cur.execute(ddl)
        self.connection.commit()
        if self.logger:
            self.logger.info("Table created: %s", table_name)

        # Create indexes if specified
        if "indexes" in schema:
            self._create_indexes(table_name, schema["indexes"])

        # Update project info file with new table
        self.update_project_info()

    def _get_composite_pk(self, schema):
        """Extract composite primary key from schema."""
        if "primary_key" in schema:
            pk_value = schema["primary_key"]
            if isinstance(pk_value, list) and len(pk_value) > 0:
                if self.logger:
                    self.logger.info("Composite primary key detected: %s", pk_value)
                return pk_value
        return None

    def _build_field_definitions(self, schema, composite_pk):
        """Build field definitions and foreign keys for CREATE TABLE."""
        field_defs = []
        foreign_keys = []

        for field_name, attrs in schema.items():
            if field_name in ["primary_key", "indexes"] or not isinstance(attrs, dict):
                continue

            field_type = self._map_field_type(attrs.get("type", "str"))

            # PostgreSQL: Use SERIAL for integer primary keys (auto-increment)
            if attrs.get("pk") and not composite_pk:
                if attrs.get("type") in ["int", "integer"]:
                    field_type = "SERIAL"
                column = f"{field_name} {field_type}"
                if attrs.get("pk"):
                    column += " PRIMARY KEY"
            else:
                column = f"{field_name} {field_type}"

            # Add constraints (not needed for SERIAL PKs)
            if not (attrs.get("pk") and field_type == "SERIAL"):
                if attrs.get("unique"):
                    column += " UNIQUE"
                if attrs.get("required") is True:
                    column += " NOT NULL"

            field_defs.append(column)

            # Handle foreign keys
            if "fk" in attrs:
                fk_clause = self._build_foreign_key_clause(field_name, attrs)
                if fk_clause:
                    foreign_keys.append(fk_clause)

        return field_defs, foreign_keys

    def table_exists(self, table_name):
        """Check if a table exists in PostgreSQL."""
        cur = self.get_cursor()
        cur.execute(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = %s
            )""",
            (table_name,)
        )
        result = cur.fetchone()
        exists = result[0] if result else False
        if self.logger:
            self.logger.debug("Table '%s' exists: %s", table_name, exists)
        return exists

    def list_tables(self):
        """List all tables in the database."""
        cur = self.get_cursor()
        cur.execute(
            """SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name"""
        )
        tables = [row[0] for row in cur.fetchall()]
        if self.logger:
            self.logger.debug("Found %d tables: %s", len(tables), tables)
        return tables

    # alter_table() - inherited from SQLAdapter (PostgreSQL supports DROP COLUMN)
    # drop_table() - inherited from SQLAdapter with hook override below

    def _after_drop_table(self, table_name):
        """PostgreSQL-specific cleanup - updates .pginfo.yaml tracking file."""
        self.update_project_info()

    # Most CRUD inherited from SQLAdapter

    def upsert(self, table, fields, values, conflict_fields):
        """Insert or update row using PostgreSQL ON CONFLICT syntax."""
        cur = self.get_cursor()

        # Build INSERT clause
        placeholders = self._get_placeholders(len(fields))
        sql_stmt = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"

        # Build ON CONFLICT clause
        if conflict_fields:
            conflict_cols = ", ".join(conflict_fields)
            update_set = ", ".join([f"{f} = EXCLUDED.{f}" for f in fields if f not in conflict_fields])
            if update_set:
                sql_stmt += f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}"
            else:
                sql_stmt += f" ON CONFLICT ({conflict_cols}) DO NOTHING"

        # Add RETURNING clause to get row ID
        sql_stmt += " RETURNING *"

        if self.logger:
            self.logger.debug("Executing UPSERT: %s with values: %s", sql_stmt, values)
        cur.execute(sql_stmt, values)
        self.connection.commit()

        # Get the returned row
        result = cur.fetchone()
        row_id = result[0] if result else None

        if self.logger:
            self.logger.info("Upserted row into %s with ID: %s", table, row_id)
        return row_id

    def map_type(self, abstract_type):
        """Map abstract schema type to PostgreSQL type."""
        if not isinstance(abstract_type, str):
            if self.logger:
                self.logger.debug("Non-string type received (%r); defaulting to TEXT.", abstract_type)
            return "TEXT"

        normalized = abstract_type.strip().rstrip("!?").lower()

        type_map = {
            "str": "TEXT",
            "string": "TEXT",
            "int": "INTEGER",
            "integer": "INTEGER",
            "float": "REAL",
            "real": "REAL",
            "bool": "BOOLEAN",
            "boolean": "BOOLEAN",
            "datetime": "TIMESTAMP",
            "date": "DATE",
            "time": "TIME",
            "json": "JSONB",
            "blob": "BYTEA",
        }

        return type_map.get(normalized, "TEXT")

    def _get_placeholders(self, count):
        """Get parameter placeholders for PostgreSQL (%s, not $1)."""
        return ", ".join(["%s" for _ in range(count)])

    def _get_single_placeholder(self):
        """Get single parameter placeholder for PostgreSQL (%s)."""
        return "%s"

    def _get_last_insert_id(self, cursor):
        """Get last inserted row ID (PostgreSQL uses RETURNING clause instead)."""
        # PostgreSQL doesn't have lastrowid like SQLite
        # We use RETURNING clause in INSERT instead
        if self.logger:
            self.logger.debug("_get_last_insert_id called (PostgreSQL uses RETURNING clause)")

    def insert(self, table, fields, values):
        """Insert row and return ID using RETURNING clause."""
        cur = self.get_cursor()
        placeholders = self._get_placeholders(len(fields))

        # PostgreSQL: Use RETURNING to get inserted ID
        sql_stmt = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders}) RETURNING *"

        if self.logger:
            self.logger.debug("Executing INSERT: %s with values: %s", sql_stmt, values)
        cur.execute(sql_stmt, values)
        self.connection.commit()

        # Get the returned row (first column is typically the ID)
        result = cur.fetchone()
        row_id = result[0] if result else None

        if self.logger:
            self.logger.info("Inserted row into %s with ID: %s", table, row_id)
        return row_id

    def _write_project_info(self):
        """Write PostgreSQL connection info to .pginfo.yaml in Data_path."""
        try:
            # Ensure directory exists
            self._ensure_directory()

            info_file = self.base_path / ".pginfo.yaml"

            # Get PostgreSQL version
            pg_version = "Unknown"
            try:
                cur = self.get_cursor()
                cur.execute("SELECT version();")
                version_string = cur.fetchone()[0]
                # Extract version number (e.g., "PostgreSQL 14.10")
                if "PostgreSQL" in version_string:
                    pg_version = version_string.split()[1]
            except Exception as e:  # pylint: disable=broad-except
                if self.logger:
                    self.logger.debug("Could not get PostgreSQL version: %s", e)

            # Get data directory from server
            data_dir = "Unknown"
            try:
                cur = self.get_cursor()
                cur.execute("SHOW data_directory;")
                data_dir = cur.fetchone()[0]
            except Exception as e:  # pylint: disable=broad-except
                if self.logger:
                    self.logger.debug("Could not get data_directory: %s", e)

            # Gather project information
            info = {
                "project": {
                    "name": self.database_name,
                    "created": datetime.now().isoformat(),
                },
                "connection": {
                    "database": self.database_name,
                    "host": self.host,
                    "port": self.port,
                    "user": self.user,
                    "connection_string": f"postgresql://{self.user}@{self.host}:{self.port}/{self.database_name}"
                },
                "server": {
                    "data_directory": data_dir,
                    "version": pg_version,
                },
                "tables": self.list_tables() if self.is_connected() else [],
                "schema_version": 1,
                "last_updated": datetime.now().isoformat()
            }

            # Write to file
            with open(info_file, 'w', encoding='utf-8') as f:
                yaml.dump(info, f, default_flow_style=False, sort_keys=False)

            if self.logger:
                self.logger.debug("Written PostgreSQL project info to: %s", info_file)

        except Exception as e:  # pylint: disable=broad-except
            if self.logger:
                self.logger.warning("Could not write PostgreSQL project info: %s", e)

    def update_project_info(self):
        """Update tables list in .pginfo.yaml."""
        try:
            info_file = self.base_path / ".pginfo.yaml"

            if not info_file.exists():
                # File doesn't exist, create it
                self._write_project_info()
                return

            # Read existing file
            with open(info_file, 'r', encoding='utf-8') as f:
                info = yaml.safe_load(f)

            # Update tables list and timestamp
            info['tables'] = self.list_tables() if self.is_connected() else []
            info['last_updated'] = datetime.now().isoformat()

            # Write back
            with open(info_file, 'w', encoding='utf-8') as f:
                yaml.dump(info, f, default_flow_style=False, sort_keys=False)

            if self.logger:
                self.logger.debug("Updated PostgreSQL project info: %s", info_file)

        except Exception as e:  # pylint: disable=broad-except
            if self.logger:
                self.logger.warning("Could not update PostgreSQL project info: %s", e)
