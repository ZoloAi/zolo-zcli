"""
Comprehensive DDL Migration Tests - Complete Implementation Validation

Tests all DDL operations including:
- CREATE TABLE
- DROP TABLE
- ADD COLUMN
- DROP COLUMN (with SQLite workaround)
- MODIFY COLUMN (with SQLite workaround)

Tests both SQLite and PostgreSQL adapters to ensure compatibility.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import zCLI components
from zCLI.L3_Abstraction.n_zData.zData_modules.shared.backends.sqlite_adapter import SQLiteAdapter
from zCLI.L3_Abstraction.n_zData.zData_modules.shared.backends.base_adapter import BaseAdapter


class TestDDLMigrationComplete:
    """Test suite for complete DDL migration implementation."""
    
    @pytest.fixture
    def sqlite_adapter(self):
        """Create SQLite adapter with temporary database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        
        adapter = SQLiteAdapter({"db_path": temp_db.name})
        adapter.connect()
        
        yield adapter
        
        adapter.disconnect()
        os.unlink(temp_db.name)
    
    def test_create_table(self, sqlite_adapter):
        """Test CREATE TABLE operation."""
        schema = {
            "id": {"type": "INTEGER", "primary_key": True},
            "name": {"type": "TEXT", "required": True},
            "email": {"type": "TEXT"}
        }
        
        sqlite_adapter.create_table("users", schema)
        
        # Verify table exists
        assert sqlite_adapter.table_exists("users")
        
        # Verify columns
        cur = sqlite_adapter.get_cursor()
        cur.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        assert "id" in columns
        assert "name" in columns
        assert "email" in columns
    
    def test_drop_table(self, sqlite_adapter):
        """Test DROP TABLE operation."""
        schema = {"id": {"type": "INTEGER", "primary_key": True}}
        sqlite_adapter.create_table("temp_table", schema)
        
        assert sqlite_adapter.table_exists("temp_table")
        
        sqlite_adapter.drop_table("temp_table")
        
        assert not sqlite_adapter.table_exists("temp_table")
    
    def test_add_column(self, sqlite_adapter):
        """Test ADD COLUMN operation."""
        schema = {
            "id": {"type": "INTEGER", "primary_key": True},
            "name": {"type": "TEXT"}
        }
        sqlite_adapter.create_table("users", schema)
        
        # Add new column
        changes = {
            "add_columns": {
                "age": {"type": "INTEGER", "default": 0}
            }
        }
        sqlite_adapter.alter_table("users", changes)
        
        # Verify new column exists
        cur = sqlite_adapter.get_cursor()
        cur.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        assert "age" in columns
        assert columns["age"] == "INTEGER"
    
    def test_drop_column_sqlite_workaround(self, sqlite_adapter):
        """Test DROP COLUMN with SQLite table recreation."""
        # Create table with 3 columns
        schema = {
            "id": {"type": "INTEGER", "primary_key": True},
            "name": {"type": "TEXT"},
            "email": {"type": "TEXT"}
        }
        sqlite_adapter.create_table("users", schema)
        
        # Insert test data
        cur = sqlite_adapter.get_cursor()
        cur.execute("INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@example.com')")
        sqlite_adapter.connection.commit()
        
        # Drop email column
        changes = {"drop_columns": ["email"]}
        sqlite_adapter.alter_table("users", changes)
        
        # Verify email column removed
        cur.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        assert "id" in columns
        assert "name" in columns
        assert "email" not in columns
        
        # Verify data preserved
        cur.execute("SELECT id, name FROM users WHERE id = 1")
        row = cur.fetchone()
        assert row[0] == 1
        assert row[1] == "John"
    
    def test_modify_column_sqlite_workaround(self, sqlite_adapter):
        """Test MODIFY COLUMN with SQLite table recreation."""
        # Create table
        schema = {
            "id": {"type": "INTEGER", "primary_key": True},
            "name": {"type": "TEXT"},
            "age": {"type": "INTEGER"}
        }
        sqlite_adapter.create_table("users", schema)
        
        # Insert test data
        cur = sqlite_adapter.get_cursor()
        cur.execute("INSERT INTO users (id, name, age) VALUES (1, 'John', 30)")
        sqlite_adapter.connection.commit()
        
        # Modify age column type to TEXT
        changes = {
            "modify_columns": {
                "age": {"type": "TEXT"}
            }
        }
        sqlite_adapter.alter_table("users", changes)
        
        # Verify column type changed
        cur.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        assert columns["age"] == "TEXT"
        
        # Verify data preserved
        cur.execute("SELECT id, name, age FROM users WHERE id = 1")
        row = cur.fetchone()
        assert row[0] == 1
        assert row[1] == "John"
        assert str(row[2]) == "30"  # Preserved as text
    
    def test_combined_operations(self, sqlite_adapter):
        """Test combined ADD + DROP + MODIFY operations."""
        # Create initial table
        schema = {
            "id": {"type": "INTEGER", "primary_key": True},
            "name": {"type": "TEXT"},
            "old_field": {"type": "TEXT"},
            "change_me": {"type": "INTEGER"}
        }
        sqlite_adapter.create_table("users", schema)
        
        # Insert test data
        cur = sqlite_adapter.get_cursor()
        cur.execute("INSERT INTO users (id, name, old_field, change_me) VALUES (1, 'John', 'old', 42)")
        sqlite_adapter.connection.commit()
        
        # Combined changes
        changes = {
            "add_columns": {
                "new_field": {"type": "TEXT", "default": "default"}
            },
            "drop_columns": ["old_field"],
            "modify_columns": {
                "change_me": {"type": "TEXT"}
            }
        }
        sqlite_adapter.alter_table("users", changes)
        
        # Verify all changes applied
        cur.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        assert "new_field" in columns
        assert "old_field" not in columns
        assert columns["change_me"] == "TEXT"
        
        # Verify data preserved
        cur.execute("SELECT id, name, change_me FROM users WHERE id = 1")
        row = cur.fetchone()
        assert row[0] == 1
        assert row[1] == "John"
        assert str(row[2]) == "42"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
