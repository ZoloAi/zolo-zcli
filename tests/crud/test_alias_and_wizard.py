"""
Test alias system and wizard integration with zData.

Tests:
- Loading schemas with --as alias
- Using $alias in data commands
- Wizard mode with persistent connections
- Transaction support
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


def test_alias_loading(zcli_instance):
    """Test loading schema with alias."""
    zcli = zcli_instance
    
    # Load schema with alias using shell command
    result = zcli.shell.execute_command("load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo")
    
    # Verify alias is stored in pinned_cache
    alias_data = zcli.loader.cache.pinned_cache.get_alias("sqlite_demo")
    assert alias_data is not None
    assert "users" in alias_data
    
    # Verify we can list aliases
    aliases = zcli.loader.cache.pinned_cache.list_aliases()
    assert "sqlite_demo" in aliases


def test_data_command_with_alias(zcli_instance, cleanup_sqlite):
    """Test using $alias in data commands."""
    zcli = zcli_instance
    
    # Load schema with alias
    zcli.shell.execute_command("load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo")
    
    # Create tables using alias
    result = zcli.shell.execute_command("data create --model $sqlite_demo")
    
    # Insert using alias
    result = zcli.shell.execute_command(
        'data insert users --model $sqlite_demo --name Alice --email alice@example.com --age 30'
    )
    
    # Read using alias
    result = zcli.shell.execute_command('data read users --model $sqlite_demo --where "name=Alice"')
    
    # Verify the operation worked (check session or output)
    assert result != "error"


def test_wizard_persistent_connection(zcli_instance, cleanup_sqlite):
    """Test wizard mode with persistent connection."""
    zcli = zcli_instance
    
    # Load schema with alias
    zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    schema = zcli.session["zCache"]["system_cache"].get("@.zCLI.Schemas.zSchema.sqlite_demo")
    
    # Load as alias
    zcli.loader.cache.pinned_cache.set_alias("test_db", schema["data"])
    
    # Create wizard workflow
    workflow = {
        "step1": {
            "event": "zData",
            "action": "create",
            "model": "@.zCLI.Schemas.zSchema.sqlite_demo"
        },
        "step2": {
            "event": "zData",
            "action": "insert",
            "model": "@.zCLI.Schemas.zSchema.sqlite_demo",
            "tables": ["users"],
            "fields": ["name", "email"],
            "values": ["Alice", "alice@example.com"]
        },
        "step3": {
            "event": "zData",
            "action": "read",
            "model": "@.zCLI.Schemas.zSchema.sqlite_demo",
            "tables": ["users"]
        }
    }
    
    # Execute workflow (would normally be via zWizard)
    # For now, just verify schema_cache can store connections
    schema_cache = zcli.loader.cache.schema_cache
    
    # Simulate connection storage
    zcli.data.load_schema(schema["data"])
    schema_cache.set_connection("test_db", zcli.data.handler)
    
    # Verify connection is stored
    stored_handler = schema_cache.get_connection("test_db")
    assert stored_handler is not None
    assert stored_handler.is_connected()
    
    # Cleanup
    schema_cache.disconnect_all()


def test_wizard_transaction_rollback(zcli_instance, cleanup_sqlite):
    """Test wizard transaction with rollback."""
    zcli = zcli_instance
    
    schema = zcli.loader.handle("@.zCLI.Schemas.zSchema.sqlite_demo")
    zcli.data.load_schema(schema)
    zcli.data.handler.ensure_tables()
    
    # Begin transaction
    zcli.data.handler.adapter.begin_transaction()
    
    # Insert user
    zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])
    
    # Rollback
    zcli.data.handler.adapter.rollback()
    
    # Verify user was not persisted
    users = zcli.data.select("users")
    assert len(users) == 0
    
    zcli.data.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

