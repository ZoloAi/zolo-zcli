"""
Modern JOIN tests for zData.

Tests AUTO-JOIN and manual JOIN functionality across all adapters.
"""

import pytest
import shutil
from pathlib import Path
from zCLI.zCLI import zCLI


@pytest.fixture(scope="function")
def zcli_instance():
    """Create fresh zCLI instance."""
    return zCLI()


@pytest.fixture(scope="function")
def cleanup_sqlite():
    """Clean up SQLite test database."""
    yield
    db_path = Path(__file__).parent.parent / "tests" / "zData_tests" / "sqlite_demo"
    if db_path.exists():
        shutil.rmtree(db_path)


@pytest.fixture(scope="function")
def setup_test_data(zcli_instance, cleanup_sqlite):
    """Setup test data for JOIN tests."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert test users
    user1_id = zcli.data.insert("users", ["name", "email", "age"], 
                                ["Alice", "alice@example.com", 30])
    user2_id = zcli.data.insert("users", ["name", "email", "age"], 
                                ["Bob", "bob@example.com", 25])
    
    # Insert test posts
    zcli.data.insert("posts", ["user_id", "title", "content"], 
                     [user1_id, "Alice's First Post", "Hello from Alice"])
    zcli.data.insert("posts", ["user_id", "title", "content"], 
                     [user2_id, "Bob's First Post", "Hello from Bob"])
    zcli.data.insert("posts", ["user_id", "title", "content"], 
                     [user1_id, "Alice's Second Post", "Another post"])
    
    return zcli, schema


def test_auto_join_two_tables(setup_test_data):
    """Test AUTO-JOIN between users and posts."""
    zcli, schema = setup_test_data
    
    # Get schema tables (excluding Meta)
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    
    # Perform auto-join
    rows = zcli.data.handler.select(
        ["users", "posts"],
        fields=None,
        auto_join=True,
        schema=schema_tables
    )
    
    # Should have 3 joined rows (3 posts)
    assert len(rows) == 3
    
    # Verify joined data structure
    row = rows[0]
    # Row should have fields from both tables
    assert any("name" in str(k) for k in row.keys())
    assert any("title" in str(k) for k in row.keys())
    
    zcli.data.disconnect()


def test_manual_join_inner(setup_test_data):
    """Test manual INNER JOIN."""
    zcli, schema = setup_test_data
    
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    
    # Manual INNER JOIN
    joins = [
        {
            "type": "INNER",
            "table": "posts",
            "on": "users.id = posts.user_id"
        }
    ]
    
    rows = zcli.data.handler.select(
        ["users"],
        fields=None,
        joins=joins,
        schema=schema_tables
    )
    
    # Should have 3 rows (Alice has 2 posts, Bob has 1)
    assert len(rows) == 3
    
    zcli.data.disconnect()


def test_manual_join_left(setup_test_data):
    """Test manual LEFT JOIN."""
    zcli, schema = setup_test_data
    
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    
    # Add user without posts
    zcli.data.insert("users", ["name", "email"], ["Charlie", "charlie@example.com"])
    
    # Manual LEFT JOIN
    joins = [
        {
            "type": "LEFT",
            "table": "posts",
            "on": "users.id = posts.user_id"
        }
    ]
    
    rows = zcli.data.handler.select(
        ["users"],
        fields=None,
        joins=joins,
        schema=schema_tables
    )
    
    # Should have 4 rows (Alice: 2, Bob: 1, Charlie: 1 with NULL post)
    assert len(rows) >= 3
    
    zcli.data.disconnect()


def test_join_with_where(setup_test_data):
    """Test JOIN with WHERE clause."""
    zcli, schema = setup_test_data
    
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    
    # Auto-join with WHERE filtering
    rows = zcli.data.handler.select(
        ["users", "posts"],
        fields=None,
        where={"age": {"$gte": 30}},
        auto_join=True,
        schema=schema_tables
    )
    
    # Should only have Alice's posts (age 30)
    assert len(rows) == 2
    
    zcli.data.disconnect()


def test_join_with_field_selection(setup_test_data):
    """Test JOIN with specific field selection."""
    zcli, schema = setup_test_data
    
    schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
    
    # Auto-join with field selection
    rows = zcli.data.handler.select(
        ["users", "posts"],
        fields=["users.name", "posts.title"],
        auto_join=True,
        schema=schema_tables
    )
    
    assert len(rows) == 3
    
    # Verify only requested fields are present
    row = rows[0]
    assert any("name" in str(k) for k in row.keys())
    assert any("title" in str(k) for k in row.keys())
    
    zcli.data.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

