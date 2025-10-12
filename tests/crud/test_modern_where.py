"""
Modern WHERE clause tests for zData.

Tests all advanced WHERE operators across adapters:
- OR conditions
- IN operator
- LIKE patterns
- IS NULL / IS NOT NULL
- Comparison operators (=, !=, >, >=, <, <=)
"""

import pytest
import shutil
from pathlib import Path
from zCLI.zCLI import zCLI


@pytest.fixture(scope="function")
def zcli_with_data():
    """Create zCLI instance with test data."""
    zcli = zCLI()
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Insert test data
    zcli.data.insert("users", ["name", "email", "age", "status"], 
                     ["Alice", "alice@example.com", 30, "active"])
    zcli.data.insert("users", ["name", "email", "age", "status"], 
                     ["Bob", "bob@example.com", 25, "pending"])
    zcli.data.insert("users", ["name", "email", "age", "status"], 
                     ["Charlie", "charlie@example.com", 35, "active"])
    zcli.data.insert("users", ["name", "age", "status"], 
                     ["Dave", 40, "inactive"])  # No email
    
    yield zcli
    
    # Cleanup
    zcli.data.disconnect()
    db_path = Path(__file__).parent.parent / "tests" / "zData_tests" / "sqlite_demo"
    if db_path.exists():
        shutil.rmtree(db_path)


def test_simple_equality(zcli_with_data):
    """Test simple equality WHERE clause."""
    zcli = zcli_with_data
    
    users = zcli.data.select("users", where={"name": "Alice"})
    assert len(users) == 1
    assert users[0]["name"] == "Alice"


def test_or_conditions(zcli_with_data):
    """Test OR conditions."""
    zcli = zcli_with_data
    
    # name = 'Alice' OR name = 'Bob'
    users = zcli.data.select("users", where={
        "$or": [
            {"name": "Alice"},
            {"name": "Bob"}
        ]
    })
    assert len(users) == 2
    
    # age > 30 OR status = 'pending'
    users = zcli.data.select("users", where={
        "$or": [
            {"age": {"$gt": 30}},
            {"status": "pending"}
        ]
    })
    assert len(users) >= 2  # Charlie (35) and Bob (pending)


def test_in_operator(zcli_with_data):
    """Test IN operator."""
    zcli = zcli_with_data
    
    # status IN ('active', 'pending')
    users = zcli.data.select("users", where={"status": ["active", "pending"]})
    assert len(users) == 3
    
    # name IN ('Alice', 'Charlie')
    users = zcli.data.select("users", where={"name": ["Alice", "Charlie"]})
    assert len(users) == 2


def test_like_operator(zcli_with_data):
    """Test LIKE pattern matching."""
    zcli = zcli_with_data
    
    # email LIKE '%alice%'
    users = zcli.data.select("users", where={"email": {"$like": "%alice%"}})
    assert len(users) == 1
    assert "alice" in users[0]["email"].lower()
    
    # name LIKE 'C%' (starts with C)
    users = zcli.data.select("users", where={"name": {"$like": "C%"}})
    assert len(users) == 1
    assert users[0]["name"] == "Charlie"


def test_is_null(zcli_with_data):
    """Test IS NULL operator."""
    zcli = zcli_with_data
    
    # email IS NULL
    users = zcli.data.select("users", where={"email": None})
    assert len(users) == 1
    assert users[0]["name"] == "Dave"


def test_is_not_null(zcli_with_data):
    """Test IS NOT NULL operator."""
    zcli = zcli_with_data
    
    # email IS NOT NULL
    users = zcli.data.select("users", where={"email": {"$notnull": True}})
    assert len(users) == 3  # Alice, Bob, Charlie


def test_comparison_operators(zcli_with_data):
    """Test comparison operators (>, >=, <, <=, !=)."""
    zcli = zcli_with_data
    
    # age > 30
    users = zcli.data.select("users", where={"age": {"$gt": 30}})
    assert len(users) == 2  # Charlie (35), Dave (40)
    
    # age >= 30
    users = zcli.data.select("users", where={"age": {"$gte": 30}})
    assert len(users) == 3  # Alice (30), Charlie (35), Dave (40)
    
    # age < 30
    users = zcli.data.select("users", where={"age": {"$lt": 30}})
    assert len(users) == 1  # Bob (25)
    
    # age <= 30
    users = zcli.data.select("users", where={"age": {"$lte": 30}})
    assert len(users) == 2  # Alice (30), Bob (25)
    
    # status != 'active'
    users = zcli.data.select("users", where={"status": {"$ne": "active"}})
    assert len(users) == 2  # Bob (pending), Dave (inactive)


def test_combined_conditions(zcli_with_data):
    """Test combining multiple WHERE conditions."""
    zcli = zcli_with_data
    
    # age >= 30 AND status = 'active'
    users = zcli.data.select("users", where={
        "age": {"$gte": 30},
        "status": "active"
    })
    assert len(users) == 2  # Alice (30, active), Charlie (35, active)
    
    # (age > 30 OR status = 'pending') AND email IS NOT NULL
    users = zcli.data.select("users", where={
        "$or": [
            {"age": {"$gt": 30}},
            {"status": "pending"}
        ],
        "email": {"$notnull": True}
    })
    assert len(users) == 2  # Bob (pending) and Charlie (35)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

