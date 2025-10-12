"""
Modern validation tests for zData.

Tests schema-based validation rules across all adapters.
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
def setup_schema(zcli_instance, cleanup_sqlite):
    """Setup schema and tables."""
    zcli = zcli_instance
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    return zcli


def test_required_field_validation(setup_schema):
    """Test required field validation."""
    zcli = setup_schema
    
    # Try to insert without required field (name)
    with pytest.raises(Exception):
        zcli.data.insert("users", ["email"], ["test@example.com"])
    
    zcli.data.disconnect()


def test_min_length_validation(setup_schema):
    """Test min_length validation rule."""
    zcli = setup_schema
    
    # Name must be at least 2 characters
    with pytest.raises(Exception):
        zcli.data.insert("users", ["name"], ["A"])
    
    # Valid name should work
    user_id = zcli.data.insert("users", ["name"], ["Alice"])
    assert user_id is not None
    
    zcli.data.disconnect()


def test_max_length_validation(setup_schema):
    """Test max_length validation rule."""
    zcli = setup_schema
    
    # Name cannot exceed 100 characters
    long_name = "A" * 101
    with pytest.raises(Exception):
        zcli.data.insert("users", ["name"], [long_name])
    
    # Valid length should work
    valid_name = "A" * 100
    user_id = zcli.data.insert("users", ["name"], [valid_name])
    assert user_id is not None
    
    zcli.data.disconnect()


def test_email_format_validation(setup_schema):
    """Test email format validation."""
    zcli = setup_schema
    
    # Invalid email format
    with pytest.raises(Exception):
        zcli.data.insert("users", ["name", "email"], ["Alice", "not-an-email"])
    
    # Valid email should work
    user_id = zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
    assert user_id is not None
    
    zcli.data.disconnect()


def test_min_max_value_validation(setup_schema):
    """Test min/max value validation for numbers."""
    zcli = setup_schema
    
    # Age must be between 0 and 150
    with pytest.raises(Exception):
        zcli.data.insert("users", ["name", "age"], ["Alice", -5])
    
    with pytest.raises(Exception):
        zcli.data.insert("users", ["name", "age"], ["Bob", 200])
    
    # Valid age should work
    user_id = zcli.data.insert("users", ["name", "age"], ["Alice", 30])
    assert user_id is not None
    
    zcli.data.disconnect()


def test_update_validation(setup_schema):
    """Test validation on UPDATE operations."""
    zcli = setup_schema
    
    # Insert valid user
    user_id = zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
    
    # Try to update with invalid data
    with pytest.raises(Exception):
        zcli.data.update("users", ["name"], ["A"], where={"id": user_id})  # Too short
    
    # Valid update should work
    count = zcli.data.update("users", ["name"], ["Alicia"], where={"id": user_id})
    assert count == 1
    
    zcli.data.disconnect()


def test_posts_validation(setup_schema):
    """Test validation rules on posts table."""
    zcli = setup_schema
    
    # Insert user first
    user_id = zcli.data.insert("users", ["name"], ["Alice"])
    
    # Test title min_length (must be at least 5 characters)
    with pytest.raises(Exception):
        zcli.data.insert("posts", ["user_id", "title"], [user_id, "Hi"])
    
    # Test title max_length (cannot exceed 200 characters)
    long_title = "A" * 201
    with pytest.raises(Exception):
        zcli.data.insert("posts", ["user_id", "title"], [user_id, long_title])
    
    # Valid post should work
    post_id = zcli.data.insert("posts", ["user_id", "title"], [user_id, "Hello World"])
    assert post_id is not None
    
    zcli.data.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

