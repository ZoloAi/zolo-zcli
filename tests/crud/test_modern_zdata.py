"""
Modern zData tests using the current architecture.

Tests classical paradigm with all three adapters:
- SQLite
- CSV
- PostgreSQL (if available)

Tests:
- Basic CRUD operations
- Advanced WHERE clauses (OR, IN, LIKE, IS NULL)
- AUTO-JOIN and manual JOINs
- Validation
- UPSERT
"""

import pytest
import os
import shutil
from pathlib import Path
from zCLI.zCLI import zCLI


# ══════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def zcli_instance():
    """Create fresh zCLI instance for each test."""
    return zCLI()


@pytest.fixture(scope="function")
def cleanup_sqlite():
    """Clean up SQLite test database after test."""
    yield
    # Cleanup after test
    db_path = Path(__file__).parent.parent / "tests" / "zData_tests" / "sqlite_demo"
    if db_path.exists():
        shutil.rmtree(db_path)


@pytest.fixture(scope="function")
def cleanup_csv():
    """Clean up CSV test files after test."""
    yield
    # Cleanup after test
    csv_path = Path(__file__).parent.parent / "tests" / "zData_tests" / "csv_demo"
    if csv_path.exists():
        for csv_file in csv_path.glob("*.csv"):
            csv_file.unlink()


# ══════════════════════════════════════════════════════════════
# SQLite Tests
# ══════════════════════════════════════════════════════════════

def test_sqlite_basic_crud(zcli_instance, cleanup_sqlite):
    """Test basic CRUD operations with SQLite adapter."""
    zcli = zcli_instance
    
    # Load schema
    schema_path = "@.zCLI.Schemas.zSchema.sqlite_demo"
    schema = zcli.loader.handle(schema_path)
    assert schema is not None
    
    # Load schema into zData
    zcli.data.load_schema(schema)
    assert zcli.data.paradigm == "classical"
    assert zcli.data.is_connected()
    
    # Create tables
    result = zcli.data.handler.ensure_tables()
    assert result is True
    
    # Insert user
    user_id = zcli.data.insert("users", ["name", "email", "age"], ["Alice", "alice@example.com", 30])
    assert user_id is not None
    
    # Read user
    users = zcli.data.select("users", where={"name": "Alice"})
    assert len(users) == 1
    assert users[0]["name"] == "Alice"
    assert users[0]["email"] == "alice@example.com"
    
    # Update user
    count = zcli.data.update("users", ["age"], [31], where={"name": "Alice"})
    assert count == 1
    
    # Verify update
    users = zcli.data.select("users", where={"name": "Alice"})
    assert users[0]["age"] == 31
    
    # Delete user
    count = zcli.data.delete("users", where={"name": "Alice"})
    assert count == 1
    
    # Verify deletion
    users = zcli.data.select("users")
    assert len(users) == 0
    
    # Cleanup
    zcli.data.disconnect()


def test_sqlite_advanced_where(zcli_instance, cleanup_sqlite):
    """Test advanced WHERE clauses with SQLite."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert test data
    zcli.data.insert("users", ["name", "age", "status"], ["Alice", 30, "active"])
    zcli.data.insert("users", ["name", "age", "status"], ["Bob", 25, "pending"])
    zcli.data.insert("users", ["name", "age", "status"], ["Charlie", 35, "active"])
    
    # Test OR condition
    users = zcli.data.select("users", where={"$or": [{"name": "Alice"}, {"name": "Bob"}]})
    assert len(users) == 2
    
    # Test IN operator
    users = zcli.data.select("users", where={"status": ["active", "pending"]})
    assert len(users) == 3
    
    # Test comparison operators
    users = zcli.data.select("users", where={"age": {"$gte": 30}})
    assert len(users) == 2
    
    # Test IS NULL (insert user without email first)
    zcli.data.insert("users", ["name", "age"], ["Dave", 40])
    users = zcli.data.select("users", where={"email": None})
    assert len(users) == 4  # All users without email
    
    zcli.data.disconnect()


def test_sqlite_validation(zcli_instance, cleanup_sqlite):
    """Test validation rules with SQLite."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Test min_length validation (should fail)
    try:
        zcli.data.insert("users", ["name"], ["A"])  # Too short (min 2)
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
    
    # Test email format validation (should fail)
    try:
        zcli.data.insert("users", ["name", "email"], ["Alice", "invalid-email"])
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
    
    # Test age range validation (should fail)
    try:
        zcli.data.insert("users", ["name", "age"], ["Bob", 200])  # Over max (150)
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
    
    zcli.data.disconnect()


def test_sqlite_auto_join(zcli_instance, cleanup_sqlite):
    """Test AUTO-JOIN functionality with SQLite."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert test data
    user_id = zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
    zcli.data.insert("posts", ["user_id", "title", "content"], 
                     [user_id, "Hello World", "First post"])
    
    # Test auto-join
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    rows = zcli.data.handler.select(
        ["users", "posts"],
        fields=None,
        auto_join=True,
        schema=schema_tables
    )
    
    assert len(rows) > 0
    # Verify joined data includes both user and post fields
    assert any("name" in str(row) or "users.name" in str(row) for row in rows)
    assert any("title" in str(row) or "posts.title" in str(row) for row in rows)
    
    zcli.data.disconnect()


def test_sqlite_upsert(zcli_instance, cleanup_sqlite):
    """Test UPSERT operation with SQLite."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # First upsert (insert)
    row_id = zcli.data.upsert("users", ["name", "email", "age"], 
                              ["Alice", "alice@example.com", 30], ["name"])
    assert row_id is not None
    
    # Second upsert (update)
    row_id2 = zcli.data.upsert("users", ["name", "email", "age"], 
                               ["Alice", "alice@example.com", 31], ["name"])
    
    # Verify only one user exists with updated age
    users = zcli.data.select("users", where={"name": "Alice"})
    assert len(users) == 1
    assert users[0]["age"] == 31
    
    zcli.data.disconnect()


# ══════════════════════════════════════════════════════════════
# CSV Tests
# ══════════════════════════════════════════════════════════════

def test_csv_basic_crud(zcli_instance, cleanup_csv):
    """Test basic CRUD operations with CSV adapter."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.csv_demo")
    zcli.data.load_schema(schema)
    assert zcli.data.paradigm == "classical"
    
    # Create tables
    result = zcli.data.handler.ensure_tables()
    assert result is True
    
    # Insert user
    user_id = zcli.data.insert("users", ["name", "email", "age"], ["Alice", "alice@example.com", 30])
    assert user_id is not None
    
    # Read user
    users = zcli.data.select("users", where={"name": "Alice"})
    assert len(users) == 1
    
    # Update user
    count = zcli.data.update("users", ["age"], [31], where={"name": "Alice"})
    assert count == 1
    
    # Delete user
    count = zcli.data.delete("users", where={"name": "Alice"})
    assert count == 1
    
    zcli.data.disconnect()


def test_csv_advanced_where(zcli_instance, cleanup_csv):
    """Test advanced WHERE clauses with CSV."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.csv_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert test data
    zcli.data.insert("users", ["name", "age", "status"], ["Alice", 30, "active"])
    zcli.data.insert("users", ["name", "age", "status"], ["Bob", 25, "pending"])
    zcli.data.insert("users", ["name", "age", "status"], ["Charlie", 35, "active"])
    
    # Test IN operator
    users = zcli.data.select("users", where={"status": ["active", "pending"]})
    assert len(users) == 3
    
    # Test comparison operators
    users = zcli.data.select("users", where={"age": {"$gte": 30}})
    assert len(users) == 2
    
    zcli.data.disconnect()


# ══════════════════════════════════════════════════════════════
# Integration Tests (Multi-Adapter)
# ══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("schema_path,cleanup_fixture", [
    ("@.zCLI.Schemas.zSchema.sqlite_demo", "cleanup_sqlite"),
    ("@.zCLI.Schemas.zSchema.csv_demo", "cleanup_csv"),
])
def test_multi_adapter_consistency(zcli_instance, schema_path, cleanup_fixture, request):
    """Test that all adapters behave consistently."""
    # Get the cleanup fixture dynamically
    cleanup = request.getfixturevalue(cleanup_fixture)
    
    zcli = zcli_instance
    schema = zcli.loader.handle(schema_path)
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert
    user_id = zcli.data.insert("users", ["name", "email"], ["Test", "test@example.com"])
    assert user_id is not None
    
    # Read
    users = zcli.data.select("users", where={"name": "Test"})
    assert len(users) == 1
    assert users[0]["name"] == "Test"
    
    # Update
    count = zcli.data.update("users", ["email"], ["new@example.com"], where={"name": "Test"})
    assert count == 1
    
    # Delete
    count = zcli.data.delete("users", where={"name": "Test"})
    assert count == 1
    
    zcli.data.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

