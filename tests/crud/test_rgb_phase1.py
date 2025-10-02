#!/usr/bin/env python3
# Test RGB Phase 1 Implementation

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from zCLI.subsystems.crud.crud_handler import zTables
import sqlite3
import tempfile

def test_rgb_columns_auto_added():
    """Test that RGB columns are automatically added to tables."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Define a simple test schema
        test_schema = {
            "id": {"type": "TEXT", "primary_key": True},
            "name": {"type": "TEXT", "not_null": True}
        }
        
        # Create table using zTables
        zTables("test_table", test_schema, cur, conn)
        
        # Check if RGB columns were added
        cur.execute("PRAGMA table_info(test_table)")
        columns = [row[1] for row in cur.fetchall()]
        
        expected_columns = ["id", "name", "weak_force_r", "weak_force_g", "weak_force_b"]
        
        print("Columns found:", columns)
        
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"
        
        print("✅ RGB columns automatically added to test table")
        
        # Test RGB default values
        cur.execute("INSERT INTO test_table (id, name) VALUES (?, ?)", ("test1", "Test User"))
        cur.execute("SELECT weak_force_r, weak_force_g, weak_force_b FROM test_table WHERE id = ?", ("test1",))
        r, g, b = cur.fetchone()
        
        print(f"RGB values: R={r}, G={g}, B={b}")
        
        assert r == 255, f"Expected R=255, got {r}"
        assert g == 0, f"Expected G=0, got {g}"
        assert b == 255, f"Expected B=255, got {b}"
        
        print("✅ RGB default values correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    print("🧪 Testing RGB Phase 1 - Column Auto-Addition")
    print("=" * 50)
    
    success = test_rgb_columns_auto_added()
    
    if success:
        print("\n🎉 Phase 1.1 test passed!")
        print("✅ RGB columns are automatically added to all tables")
    else:
        print("\n❌ Phase 1.1 test failed!")
        print("Check the implementation and try again")

def test_migration_table_creation():
    """Test that zMigrations table is created."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "cursor": cur,
            "conn": conn,
            "ready": True
        }
        
        # Initialize migrator and ensure migration table
        from zCLI.subsystems.zMigrate import ZMigrate
        migrator = ZMigrate()
        migrator._ensure_migrations_table(zData)
        
        # Check if zMigrations table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zMigrations'")
        result = cur.fetchone()
        
        assert result is not None, "zMigrations table was not created"
        
        # Check table structure
        cur.execute("PRAGMA table_info(zMigrations)")
        columns = [row[1] for row in cur.fetchall()]
        
        expected_columns = ["id", "migration_type", "target_table", "rgb_impact_r", "rgb_impact_g", "rgb_impact_b"]
        
        print("zMigrations columns found:", columns)
        
        for col in expected_columns:
            assert col in columns, f"Missing column in zMigrations: {col}"
        
        print("✅ zMigrations table created with correct structure")
        return True
        
    except Exception as e:
        print(f"❌ Migration table test failed: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_rgb_updates():
    """Test RGB update functions."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "cursor": cur,
            "conn": conn,
            "ready": True
        }
        
        # Create test table with RGB columns
        test_schema = {
            "id": {"type": "TEXT", "primary_key": True},
            "name": {"type": "TEXT", "not_null": True}
        }
        zTables("test_table", test_schema, cur, conn)
        
        # Insert test data
        cur.execute("INSERT INTO test_table (id, name) VALUES (?, ?)", ("test1", "Test User"))
        conn.commit()
        
        # Test RGB update on access
        from zCLI.subsystems.zMigrate import ZMigrate
        migrator = ZMigrate()
        
        # Update RGB on access
        migrator._update_rgb_on_access("test_table", "test1", zData)
        
        # Check RGB values after access
        cur.execute("SELECT weak_force_r, weak_force_g, weak_force_b FROM test_table WHERE id = ?", ("test1",))
        r, g, b = cur.fetchone()
        
        print(f"RGB after access: R={r}, G={g}, B={b}")
        
        assert r == 255, f"Expected R=255 after access, got {r}"
        assert g == 5, f"Expected G=5 after access, got {g}"
        assert b == 255, f"Expected B=255 after access, got {b}"
        
        print("✅ RGB update on access working correctly")
        
        # Test RGB update on migration success
        migrator._update_rgb_on_migration("test_table", "add_column", True, zData)
        
        cur.execute("SELECT weak_force_b FROM test_table WHERE id = ?", ("test1",))
        b_after_migration = cur.fetchone()[0]
        
        print(f"B after migration success: {b_after_migration}")
        
        # B should be capped at 255, so still 255
        assert b_after_migration == 255, f"Expected B=255 after migration success, got {b_after_migration}"
        
        print("✅ RGB update on migration success working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ RGB update test failed: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    print("🧪 Testing RGB Phase 1 - Column Auto-Addition")
    print("=" * 50)
    
    success1 = test_rgb_columns_auto_added()
    print("\n" + "=" * 50)
    print("🧪 Testing RGB Phase 1 - Migration Table Creation")
    print("=" * 50)
    
    success2 = test_migration_table_creation()
    print("\n" + "=" * 50)
    print("🧪 Testing RGB Phase 1 - RGB Updates")
    print("=" * 50)
    
    success3 = test_rgb_updates()
    
    if success1 and success2 and success3:
        print("\n🎉 Phase 1.3 tests passed!")
        print("✅ RGB columns, zMigrations table, and RGB updates working correctly")
        print("🌈 Quantum weak nuclear force system operational!")
    else:
        print("\n❌ Phase 1.3 tests failed!")
        print("Check the implementation and try again")
