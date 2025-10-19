# zTestSuite/zData_Test.py
"""Comprehensive test suite for zData subsystem.

Tests cover:
- Initialization and schema loading
- DML operations (INSERT, SELECT, UPDATE, DELETE, UPSERT)
- DDL operations (CREATE, DROP, ALTER, table_exists)
- TCL operations (BEGIN, COMMIT, ROLLBACK)
- DCL operations (GRANT, REVOKE - PostgreSQL only)
- Multi-backend support (SQLite, CSV, PostgreSQL)
- Connection management
- Error handling
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import yaml
import tempfile
from pathlib import Path


class TestzDataInitialization(unittest.TestCase):
    """Test zData initialization and basic setup."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        with patch('builtins.print'):
            self.zcli = zCLI()

    def test_zdata_initialization(self):
        """Test zData initializes correctly."""
        self.assertIsNotNone(self.zcli.data)
        self.assertEqual(self.zcli.data.mycolor, "ZDATA")
        self.assertIsNone(self.zcli.data.schema)
        self.assertIsNone(self.zcli.data.handler)

    def test_zdata_has_required_dependencies(self):
        """Test zData has all required dependencies."""
        self.assertIsNotNone(self.zcli.data.zcli)
        self.assertIsNotNone(self.zcli.data.logger)
        self.assertIsNotNone(self.zcli.data.display)
        self.assertIsNotNone(self.zcli.data.loader)
        self.assertIsNotNone(self.zcli.data.open)

    def test_zdata_has_all_sql_methods(self):
        """Test zData exposes all SQL operation methods."""
        # DML
        self.assertTrue(hasattr(self.zcli.data, 'insert'))
        self.assertTrue(hasattr(self.zcli.data, 'select'))
        self.assertTrue(hasattr(self.zcli.data, 'update'))
        self.assertTrue(hasattr(self.zcli.data, 'delete'))
        self.assertTrue(hasattr(self.zcli.data, 'upsert'))
        self.assertTrue(hasattr(self.zcli.data, 'list_tables'))
        
        # DDL
        self.assertTrue(hasattr(self.zcli.data, 'create_table'))
        self.assertTrue(hasattr(self.zcli.data, 'drop_table'))
        self.assertTrue(hasattr(self.zcli.data, 'alter_table'))
        self.assertTrue(hasattr(self.zcli.data, 'table_exists'))
        
        # DCL
        self.assertTrue(hasattr(self.zcli.data, 'grant'))
        self.assertTrue(hasattr(self.zcli.data, 'revoke'))
        self.assertTrue(hasattr(self.zcli.data, 'list_privileges'))
        
        # TCL
        self.assertTrue(hasattr(self.zcli.data, 'begin_transaction'))
        self.assertTrue(hasattr(self.zcli.data, 'commit'))
        self.assertTrue(hasattr(self.zcli.data, 'rollback'))


class TestzDataSQLiteAdapter(unittest.TestCase):
    """Test zData with SQLite backend."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="zdata_test_")
        self.test_dir = Path(self.temp_dir)
        
        # Initialize zCLI with test workspace
        with patch('builtins.print'):
            self.zcli = zCLI({
                "zWorkspace": str(self.test_dir)
            })
        
        # Load SQLite schema using zLoader (proper zPath resolution)
        self.schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        
        # Override the Data_Path in the schema to use temp directory
        if "Meta" in self.schema:
            self.schema["Meta"]["Data_Path"] = str(self.test_dir)
        
        self.zcli.data.load_schema(self.schema)
        
        # Store the schema path for wizard transactions
        # Update the file cache so wizard uses the modified schema
        self.schema_path = "@.zTestSuite.demos.zSchema.sqlite_demo"
        # The file cache stores loaded schemas - update it with our modified version
        if hasattr(self.zcli.loader.cache, 'file_cache'):
            self.zcli.loader.cache.file_cache.cache[self.schema_path] = self.schema
        
        # Drop existing tables (if any) and create fresh tables
        for table_name in ["users", "posts", "products"]:
            if table_name in self.schema:
                try:
                    self.zcli.data.drop_table(table_name)
                except Exception:
                    pass  # Table doesn't exist yet
                self.zcli.data.create_table(table_name)

    def tearDown(self):
        """Clean up after each test."""
        if self.zcli.data.is_connected():
            self.zcli.data.disconnect()
        
        # Remove entire temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sqlite_schema_loading(self):
        """Test SQLite schema loads correctly."""
        self.assertIsNotNone(self.zcli.data.schema)
        self.assertEqual(self.zcli.data.paradigm, "classical")
        self.assertIsNotNone(self.zcli.data.handler)
        self.assertTrue(self.zcli.data.is_connected())

    def test_sqlite_list_tables(self):
        """Test listing tables in SQLite database."""
        tables = self.zcli.data.list_tables()
        self.assertIsInstance(tables, list)
        self.assertIn("users", tables)
        self.assertIn("posts", tables)
        self.assertIn("products", tables)

    def test_sqlite_table_exists(self):
        """Test checking if tables exist."""
        self.assertTrue(self.zcli.data.table_exists("users"))
        self.assertTrue(self.zcli.data.table_exists("posts"))
        self.assertFalse(self.zcli.data.table_exists("nonexistent"))

    def test_sqlite_insert_and_select(self):
        """Test INSERT and SELECT operations."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email", "age"], ["Alice", "alice@example.com", 30])
        
        # Select data
        results = self.zcli.data.select("users")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Verify data
        user = results[0]
        self.assertEqual(user["name"], "Alice")
        self.assertEqual(user["email"], "alice@example.com")
        self.assertEqual(user["age"], 30)

    def test_sqlite_update(self):
        """Test UPDATE operation."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email"], ["Bob", "bob@example.com"])
        
        # Update data
        self.zcli.data.update("users", ["email"], ["bob.new@example.com"], where="name = 'Bob'")
        
        # Verify update
        results = self.zcli.data.select("users", where="name = 'Bob'")
        self.assertEqual(results[0]["email"], "bob.new@example.com")

    def test_sqlite_delete(self):
        """Test DELETE operation."""
        # Insert data
        self.zcli.data.insert("users", ["name"], ["Charlie"])
        
        # Verify insert
        results = self.zcli.data.select("users", where="name = 'Charlie'")
        self.assertEqual(len(results), 1)
        
        # Delete data
        self.zcli.data.delete("users", where="name = 'Charlie'")
        
        # Verify deletion
        results = self.zcli.data.select("users", where="name = 'Charlie'")
        self.assertEqual(len(results), 0)

    def test_sqlite_upsert(self):
        """Test UPSERT operation."""
        # Insert initial data with explicit id
        self.zcli.data.insert("users", ["id", "name", "email"], [1, "Dave", "dave@example.com"])
        
        # Upsert (should update based on id)
        self.zcli.data.upsert("users", ["id", "name", "email"], [1, "Dave", "dave.new@example.com"], conflict_fields=["id"])
        
        # Verify upsert
        results = self.zcli.data.select("users", where="name = 'Dave'")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["email"], "dave.new@example.com")

    def test_sqlite_transactions(self):
        """Test transaction operations via zWizard (proper pattern)."""
        # NOTE: This test demonstrates the CORRECT pattern for transactions:
        # Transactions should be managed by zWizard using schema_cache, not by direct zData calls.
        # The schema_cache automatically manages connection reuse across workflow steps.
        
        # NOTE: Wizard loads schemas fresh from disk, so it will use the original zMachine path
        # This is acceptable for testing wizard transaction behavior
        # We're testing that transactions work, not path resolution
        
        # Clear wizard's schema_cache to ensure clean state
        if hasattr(self.zcli, 'wizard') and hasattr(self.zcli.wizard, 'schema_cache'):
            self.zcli.wizard.schema_cache.clear()
        
        # Create a zWizard workflow with transaction
        # Using schema path directly - zWizard's schema_cache will handle connection reuse
        workflow = {
            "_transaction": True,
            "step1": {
                "zData": {
                    "model": self.schema_path,
                    "action": "insert",
                    "tables": ["users"],
                    "options": {
                        "name": "TransactionUser1",
                        "age": 40
                    }
                }
            },
            "step2": {
                "zData": {
                    "model": self.schema_path,
                    "action": "insert",
                    "tables": ["users"],
                    "options": {
                        "name": "TransactionUser2",
                        "age": 45
                    }
                }
            }
        }
        
        # Execute workflow with transaction
        result = self.zcli.wizard.handle(workflow)
        
        # Verify both inserts succeeded
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # Both should return True (successful inserts)
        self.assertTrue(result[0], "First insert should succeed")
        self.assertTrue(result[1], "Second insert should succeed")
        
        # Load the wizard's schema (from original path) to verify the data
        wizard_schema = self.zcli.loader.handle(self.schema_path)
        self.zcli.data.load_schema(wizard_schema)
        
        # Verify data was committed
        users = self.zcli.data.select("users")
        user_names = [user["name"] for user in users]
        self.assertIn("TransactionUser1", user_names, f"TransactionUser1 not found. Users: {user_names}")
        self.assertIn("TransactionUser2", user_names, f"TransactionUser2 not found. Users: {user_names}")
        
        # Clean up wizard's database
        self.zcli.data.delete("users", where="name LIKE 'TransactionUser%'")

    def test_sqlite_select_with_filters(self):
        """Test SELECT with WHERE, ORDER, LIMIT."""
        # Insert test data
        self.zcli.data.insert("users", ["name", "age"], ["Alice", 30])
        self.zcli.data.insert("users", ["name", "age"], ["Bob", 25])
        self.zcli.data.insert("users", ["name", "age"], ["Charlie", 35])
        
        # Test WHERE
        results = self.zcli.data.select("users", where="age > 26")
        self.assertEqual(len(results), 2)
        
        # Test ORDER
        results = self.zcli.data.select("users", order="age ASC")
        self.assertEqual(results[0]["name"], "Bob")  # Youngest first
        
        # Test LIMIT
        results = self.zcli.data.select("users", limit=2)
        self.assertEqual(len(results), 2)

    def test_sqlite_create_and_drop_table(self):
        """Test CREATE TABLE and DROP TABLE operations."""
        # Create new table
        self.zcli.data.create_table("test_table", {
            "id": {"type": "int", "pk": True},
            "name": {"type": "str", "required": True}
        })
        
        # Verify table exists
        self.assertTrue(self.zcli.data.table_exists("test_table"))
        
        # Drop table
        self.zcli.data.drop_table("test_table")
        
        # Verify table dropped
        self.assertFalse(self.zcli.data.table_exists("test_table"))

    def test_sqlite_alter_table_add_column(self):
        """Test ALTER TABLE ADD COLUMN."""
        # Add column
        self.zcli.data.alter_table("users", {
            "add_columns": {
                "phone": {"type": "str"}
            }
        })
        
        # Insert data with new column
        self.zcli.data.insert("users", ["name", "phone"], ["Grace", "555-1234"])
        
        # Verify new column
        results = self.zcli.data.select("users", where="name = 'Grace'")
        self.assertIsNotNone(results[0])

    def test_sqlite_dcl_not_supported(self):
        """Test DCL operations raise NotImplementedError for SQLite."""
        with self.assertRaises(NotImplementedError):
            self.zcli.data.grant("SELECT", "users", "test_user")
        
        with self.assertRaises(NotImplementedError):
            self.zcli.data.revoke("SELECT", "users", "test_user")
        
        with self.assertRaises(NotImplementedError):
            self.zcli.data.list_privileges()


class TestzDataPostgreSQLAdapter(unittest.TestCase):
    """Test zData with PostgreSQL backend."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        with patch('builtins.print'):
            self.zcli = zCLI()
        
        # Check if psycopg2 is available
        try:
            import psycopg2
            self.psycopg2_available = True
        except ImportError:
            self.psycopg2_available = False
            self.skipTest("psycopg2 not available - skipping PostgreSQL tests")
        
        # Set up test directory using zPath format (@.tests.zData_tests)
        workspace_root = Path(self.zcli.session.get("zWorkspace", Path.cwd()))
        self.test_dir = workspace_root / "tests" / "zData_tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Load PostgreSQL schema using zLoader (proper zPath resolution)
        try:
            self.schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.postgresql_demo")
            self.zcli.data.load_schema(self.schema)
            
            # Drop existing tables (if any) and create fresh tables
            for table_name in ["users", "posts", "products"]:
                if table_name in self.schema:
                    try:
                        self.zcli.data.drop_table(table_name)
                    except Exception:
                        pass  # Table doesn't exist yet
                    self.zcli.data.create_table(table_name)
        except Exception as e:
            self.skipTest(f"PostgreSQL server not available: {e}")

    def tearDown(self):
        """Clean up after each test."""
        if self.zcli.data.is_connected():
            # Drop test tables
            try:
                for table in ["users", "posts", "products"]:
                    if self.zcli.data.table_exists(table):
                        self.zcli.data.drop_table(table)
            except:
                pass
            self.zcli.data.disconnect()

    def test_postgresql_schema_loading(self):
        """Test PostgreSQL schema loads correctly."""
        self.assertIsNotNone(self.zcli.data.schema)
        self.assertEqual(self.zcli.data.paradigm, "classical")
        self.assertIsNotNone(self.zcli.data.handler)
        self.assertTrue(self.zcli.data.is_connected())

    def test_postgresql_list_tables(self):
        """Test listing tables in PostgreSQL database."""
        tables = self.zcli.data.list_tables()
        self.assertIsInstance(tables, list)
        # Tables may or may not exist depending on server state
        self.assertIn("users", tables)

    def test_postgresql_insert_and_select(self):
        """Test INSERT and SELECT operations."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email", "age"], ["Alice", "alice@example.com", 30])
        
        # Select data
        results = self.zcli.data.select("users")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_postgresql_update(self):
        """Test UPDATE operation."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email"], ["Bob", "bob@example.com"])
        
        # Update data
        rows_updated = self.zcli.data.update("users", ["email"], ["bob.new@example.com"], where="name = 'Bob'")
        self.assertGreater(rows_updated, 0)

    def test_postgresql_delete(self):
        """Test DELETE operation."""
        # Insert data
        self.zcli.data.insert("users", ["name"], ["Charlie"])
        
        # Delete data
        rows_deleted = self.zcli.data.delete("users", where="name = 'Charlie'")
        self.assertGreater(rows_deleted, 0)

    def test_postgresql_transactions(self):
        """Test transaction support."""
        # Begin transaction
        self.zcli.data.begin_transaction()
        
        # Insert data
        self.zcli.data.insert("users", ["name"], ["TransactionTest"])
        
        # Rollback
        self.zcli.data.rollback()
        
        # Verify rollback worked
        results = self.zcli.data.select("users", where="name = 'TransactionTest'")
        self.assertEqual(len(results), 0)
        
        # Test commit
        self.zcli.data.begin_transaction()
        self.zcli.data.insert("users", ["name"], ["CommitTest"])
        self.zcli.data.commit()
        
        # Verify commit worked
        results = self.zcli.data.select("users", where="name = 'CommitTest'")
        self.assertGreater(len(results), 0)

    def test_postgresql_dcl_grant_revoke(self):
        """Test DCL operations (GRANT/REVOKE)."""
        # Note: This test may fail if test user doesn't have GRANT privileges
        try:
            # Grant privilege
            result = self.zcli.data.grant("SELECT", "users", "public")
            self.assertTrue(result)
            
            # Revoke privilege
            result = self.zcli.data.revoke("SELECT", "users", "public")
            self.assertTrue(result)
        except Exception as e:
            # DCL operations may fail due to permissions
            self.skipTest(f"DCL operations require superuser privileges: {e}")

    def test_postgresql_list_privileges(self):
        """Test listing privileges."""
        try:
            # List privileges
            privileges = self.zcli.data.list_privileges(table_name="users")
            self.assertIsInstance(privileges, list)
        except Exception as e:
            self.skipTest(f"Privilege listing requires appropriate permissions: {e}")


class TestzDataCSVAdapter(unittest.TestCase):
    """Test zData with CSV backend."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="zdata_csv_test_")
        self.test_dir = Path(self.temp_dir)
        
        # Initialize zCLI with test workspace
        with patch('builtins.print'):
            self.zcli = zCLI({
                "zWorkspace": str(self.test_dir)
            })
        
        # Load CSV schema using zLoader (proper zPath resolution)
        self.schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.csv_demo")
        
        # Override the Data_Path in the schema to use temp directory
        if "Meta" in self.schema:
            self.schema["Meta"]["Data_Path"] = str(self.test_dir)
        
        self.zcli.data.load_schema(self.schema)
        
        # Drop existing tables (if any) and create fresh tables
        for table_name in ["users", "posts", "products"]:
            if table_name in self.schema:
                try:
                    self.zcli.data.drop_table(table_name)
                except Exception:
                    pass  # Table doesn't exist yet
                self.zcli.data.create_table(table_name)

    def tearDown(self):
        """Clean up after each test."""
        if self.zcli.data.is_connected():
            self.zcli.data.disconnect()
        
        # Remove entire temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_csv_schema_loading(self):
        """Test CSV schema loads correctly."""
        self.assertIsNotNone(self.zcli.data.schema)
        self.assertEqual(self.zcli.data.paradigm, "classical")
        self.assertIsNotNone(self.zcli.data.handler)

    def test_csv_insert_and_select(self):
        """Test INSERT and SELECT operations with CSV."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
        
        # Select data
        results = self.zcli.data.select("users")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_csv_update(self):
        """Test UPDATE operation with CSV."""
        # Insert data
        self.zcli.data.insert("users", ["name", "email"], ["Bob", "bob@example.com"])
        
        # Update data
        self.zcli.data.update("users", ["email"], ["bob.new@example.com"], where="name = 'Bob'")
        
        # Verify update
        results = self.zcli.data.select("users", where="name = 'Bob'")
        self.assertGreater(len(results), 0)

    def test_csv_delete(self):
        """Test DELETE operation with CSV."""
        # Insert data
        self.zcli.data.insert("users", ["name"], ["Charlie"])
        
        # Delete data
        self.zcli.data.delete("users", where="name = 'Charlie'")
        
        # Verify deletion
        results = self.zcli.data.select("users", where="name = 'Charlie'")
        self.assertEqual(len(results), 0)

    def test_csv_list_tables(self):
        """Test listing tables in CSV database."""
        tables = self.zcli.data.list_tables()
        self.assertIsInstance(tables, list)

    def test_csv_empty_table(self):
        """Test operations on empty CSV table."""
        # Select from empty table
        results = self.zcli.data.select("users")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_csv_multiple_inserts(self):
        """Test multiple insert operations."""
        # Insert multiple rows
        for i in range(5):
            self.zcli.data.insert("users", ["name", "email"], [f"User{i}", f"user{i}@example.com"])
        
        # Verify all rows inserted
        results = self.zcli.data.select("users")
        self.assertEqual(len(results), 5)

    def test_csv_select_with_limit(self):
        """Test SELECT with LIMIT."""
        # Insert multiple rows
        for i in range(10):
            self.zcli.data.insert("users", ["name"], [f"User{i}"])
        
        # Select with limit
        results = self.zcli.data.select("users", limit=5)
        self.assertLessEqual(len(results), 5)

    def test_csv_update_nonexistent(self):
        """Test UPDATE on non-existent row."""
        # Update non-existent row
        rows_updated = self.zcli.data.update("users", ["name"], ["NewName"], where="name = 'NonExistent'")
        self.assertEqual(rows_updated, 0)

    def test_csv_delete_all(self):
        """Test DELETE all rows."""
        # Insert data
        self.zcli.data.insert("users", ["name"], ["Alice"])
        self.zcli.data.insert("users", ["name"], ["Bob"])
        
        # Delete all (no WHERE clause)
        self.zcli.data.delete("users", where=None)
        
        # Verify all deleted
        results = self.zcli.data.select("users")
        self.assertEqual(len(results), 0)


class TestzDataErrorHandling(unittest.TestCase):
    """Test zData error handling."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        with patch('builtins.print'):
            self.zcli = zCLI()

    def test_no_handler_error(self):
        """Test operations fail without handler."""
        with self.assertRaises(RuntimeError) as context:
            self.zcli.data.insert("users", ["name"], ["Alice"])
        self.assertIn("No handler initialized", str(context.exception))

    def test_invalid_schema_detection(self):
        """Test invalid paradigm defaults to classical."""
        # Schema with invalid paradigm but valid required fields
        invalid_schema = {
            "Meta": {
                "Data_Paradigm": "invalid_paradigm",
                "Data_Type": "sqlite",
                "Data_Path": "~.zMachine.tests/zData_tests",
                "Data_Label": "test_invalid"
            },
            "users": {"name": {"type": "str"}}
        }
        
        self.zcli.data.load_schema(invalid_schema)
        self.assertEqual(self.zcli.data.paradigm, "classical")

    def test_table_not_found_error(self):
        """Test error when table not in schema."""
        # Load schema using zLoader (proper zPath resolution)
        schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        self.zcli.data.load_schema(schema)
        
        with self.assertRaises(ValueError):
            self.zcli.data.create_table("nonexistent_table")


class TestzDataPluginIntegration(unittest.TestCase):
    """Test zData integration with plugins."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="zdata_plugin_test_")
        self.test_dir = Path(self.temp_dir)
        
        # Initialize zCLI with test workspace
        with patch('builtins.print'):
            self.zcli = zCLI({
                "zWorkspace": str(self.test_dir)
            })
        
        # Load id_generator plugin explicitly using PluginCache
        # This ensures the plugin is available for zParser plugin invocations
        try:
            # Resolve the plugin file path
            file_path = self.zcli.zparser.resolve_symbol_path("@", ["@", "zTestSuite", "demos", "id_generator"])
            if not file_path.endswith('.py'):
                file_path = f"{file_path}.py"
            
            # Load the plugin directly into PluginCache (used by zParser)
            plugin_name = "id_generator"
            module = self.zcli.loader.cache.plugin_cache.load_and_cache(file_path, plugin_name)
            self.zcli.logger.debug(f"Plugin {plugin_name} loaded from {file_path}")
        except Exception as e:
            self.zcli.logger.warning(f"Failed to load id_generator plugin: {e}")
        
        # Load SQLite schema
        self.schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        
        # Override the Data_Path in the schema to use temp directory
        if "Meta" in self.schema:
            self.schema["Meta"]["Data_Path"] = str(self.test_dir)
        
        self.zcli.data.load_schema(self.schema)
        
        # Create fresh users table
        try:
            self.zcli.data.drop_table("users")
        except Exception:
            pass
        self.zcli.data.create_table("users")

    def tearDown(self):
        """Clean up after each test."""
        if self.zcli.data.is_connected():
            self.zcli.data.disconnect()
        
        # Remove entire temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plugin_uuid_generation(self):
        """Test using plugin to generate UUID for insert."""
        # Generate UUID using plugin
        user_id = self.zcli.zparser.resolve_plugin_invocation("&id_generator.generate_uuid()")
        
        # Verify it's a valid UUID format
        self.assertIsInstance(user_id, str)
        self.assertEqual(len(user_id), 36)  # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        self.assertIn("-", user_id)
        
        # Use in insert
        self.zcli.data.insert("users", ["name", "email"], ["Alice", user_id])
        
        # Verify insert
        results = self.zcli.data.select("users", where=f"email = '{user_id}'")
        self.assertEqual(len(results), 1)

    def test_plugin_prefixed_id(self):
        """Test using plugin to generate prefixed IDs."""
        # Generate prefixed ID
        user_id = self.zcli.zparser.resolve_plugin_invocation("&id_generator.prefixed_id('USER')")
        
        # Verify format
        self.assertIsInstance(user_id, str)
        self.assertTrue(user_id.startswith("USER_"))
        
        # Use in insert
        self.zcli.data.insert("users", ["name", "email"], ["Bob", user_id])
        
        # Verify
        results = self.zcli.data.select("users", where="name = 'Bob'")
        self.assertEqual(results[0]["email"], user_id)

    def test_plugin_timestamp_generation(self):
        """Test using plugin to generate timestamps."""
        # Generate ISO timestamp
        iso_time = self.zcli.zparser.resolve_plugin_invocation("&id_generator.get_timestamp('iso')")
        self.assertIsInstance(iso_time, str)
        self.assertIn("T", iso_time)  # ISO format has T separator
        
        # Generate unix timestamp
        unix_time = self.zcli.zparser.resolve_plugin_invocation("&id_generator.get_timestamp('unix')")
        self.assertIsInstance(unix_time, int)
        self.assertGreater(unix_time, 1000000000)  # Reasonable unix timestamp

    def test_plugin_short_uuid(self):
        """Test using plugin to generate short UUIDs."""
        # Generate short UUID
        short_id = self.zcli.zparser.resolve_plugin_invocation("&id_generator.short_uuid()")
        
        # Verify format
        self.assertIsInstance(short_id, str)
        self.assertEqual(len(short_id), 8)
        
        # Use in insert
        self.zcli.data.insert("users", ["name", "email"], ["Charlie", short_id])
        
        # Verify
        results = self.zcli.data.select("users", where="name = 'Charlie'")
        self.assertEqual(results[0]["email"], short_id)

    def test_plugin_composite_id(self):
        """Test using plugin to generate composite IDs."""
        # Generate composite ID
        order_id = self.zcli.zparser.resolve_plugin_invocation("&id_generator.composite_id('ORD')")
        
        # Verify format
        self.assertIsInstance(order_id, str)
        self.assertTrue(order_id.startswith("ORD_"))
        self.assertEqual(order_id.count("_"), 2)  # prefix_date_random

    def test_plugin_multiple_inserts_unique_ids(self):
        """Test that plugin generates unique IDs for multiple inserts."""
        ids = []
        
        # Generate multiple IDs
        for i in range(5):
            user_id = self.zcli.zparser.resolve_plugin_invocation("&id_generator.generate_uuid()")
            ids.append(user_id)
            self.zcli.data.insert("users", ["name", "email"], [f"User{i}", user_id])
        
        # Verify all IDs are unique
        self.assertEqual(len(ids), len(set(ids)))
        
        # Verify all inserts succeeded
        results = self.zcli.data.select("users")
        self.assertEqual(len(results), 5)


class TestzDataConnectionManagement(unittest.TestCase):
    """Test zData connection management."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI import zCLI
        
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="zdata_conn_test_")
        self.test_dir = Path(self.temp_dir)
        
        # Initialize zCLI with test workspace
        with patch('builtins.print'):
            self.zcli = zCLI({
                "zWorkspace": str(self.test_dir)
            })

    def tearDown(self):
        """Clean up after each test."""
        if self.zcli.data.is_connected():
            self.zcli.data.disconnect()
        
        # Remove entire temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_connection_status(self):
        """Test connection status checking."""
        self.assertFalse(self.zcli.data.is_connected())
        
        # Load schema using zLoader (proper zPath resolution)
        schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        if "Meta" in schema:
            schema["Meta"]["Data_Path"] = str(self.test_dir)
        self.zcli.data.load_schema(schema)
        
        self.assertTrue(self.zcli.data.is_connected())

    def test_disconnect(self):
        """Test disconnecting from database."""
        # Load schema using zLoader (proper zPath resolution)
        schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        if "Meta" in schema:
            schema["Meta"]["Data_Path"] = str(self.test_dir)
        self.zcli.data.load_schema(schema)
        
        self.assertTrue(self.zcli.data.is_connected())
        
        # Disconnect
        self.zcli.data.disconnect()
        self.assertFalse(self.zcli.data.is_connected())

    def test_get_connection_info(self):
        """Test getting connection information."""
        # Without connection
        info = self.zcli.data.get_connection_info()
        self.assertFalse(info["connected"])
        
        # With connection - load schema using zLoader (proper zPath resolution)
        schema = self.zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
        if "Meta" in schema:
            schema["Meta"]["Data_Path"] = str(self.test_dir)
        self.zcli.data.load_schema(schema)
        
        info = self.zcli.data.get_connection_info()
        self.assertIsInstance(info, dict)


def run_tests(verbose=False):
    """Run all zData tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzDataInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzDataSQLiteAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestzDataCSVAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestzDataErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestzDataPluginIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestzDataConnectionManagement))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

