#!/usr/bin/env python3
# Test RGB Phase 2 - ALTER TABLE Integration

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from zCLI.subsystems.crud.crud_handler import zTables, handle_zData
import sqlite3
import tempfile
import yaml

def create_test_schema():
    """Create a test schema for ALTER TABLE operations."""
    return {
        "test_users": {
            "id": {"type": "TEXT", "primary_key": True},
            "username": {"type": "TEXT", "not_null": True},
            "email": {"type": "TEXT", "not_null": True},
            "age": {"type": "INTEGER"}
        },
        "Meta": {
            "Data_Type": "sqlite",
            "Data_path": "test.db"
        }
    }

def test_alter_table_integration():
    """Test ALTER TABLE operations with RGB tracking."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test schema
        schema = create_test_schema()
        schema["Meta"]["Data_path"] = db_path
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "path": db_path,
            "ready": True
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        zData["cursor"] = cur
        zData["conn"] = conn
        
        # Create initial table
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Insert test data
        cur.execute("INSERT INTO test_users (id, username, email, age) VALUES (?, ?, ?, ?)", 
                   ("user1", "alice", "alice@example.com", 25))
        conn.commit()
        
        print("✅ Initial table created with test data")
        
        # Test 1: DROP COLUMN operation
        print("\n🧪 Testing DROP COLUMN with RGB tracking...")
        
        drop_request = {
            "action": "alter_table",
            "table": "test_users",
            "operation": "drop_column",
            "column": "age"
        }
        
        # Use handle_zData to process the ALTER TABLE request
        zCRUD_Preped = {
            "zRequest": drop_request,
            "zForm": schema,
            "walker": None
        }
        
        result = handle_zData(zCRUD_Preped)
        
        if result:
            print("✅ DROP COLUMN operation successful")
            
            # Verify column was dropped
            cur.execute("PRAGMA table_info(test_users)")
            columns = [row[1] for row in cur.fetchall()]
            
            assert "age" not in columns, "Column 'age' should have been dropped"
            assert "weak_force_r" in columns, "RGB columns should still exist"
            
            print("✅ Column 'age' successfully dropped")
            
            # Check if migration was logged
            cur.execute("SELECT COUNT(*) FROM zMigrations WHERE migration_type = 'drop_column'")
            migration_count = cur.fetchone()[0]
            
            assert migration_count > 0, "Migration should have been logged"
            print("✅ Migration logged to zMigrations table")
            
            # Check RGB values after ALTER operation
            cur.execute("SELECT weak_force_r, weak_force_g, weak_force_b FROM test_users WHERE id = 'user1'")
            r, g, b = cur.fetchone()
            
            print(f"RGB after DROP COLUMN: R={r}, G={g}, B={b}")
            
            # B should be higher (migration success), R might be lower (structural change)
            assert b >= 255, f"B should be high after successful migration, got {b}"
            
            print("✅ RGB values updated after ALTER operation")
            
        else:
            print("❌ DROP COLUMN operation failed")
            return False
        
        # Test 2: RENAME COLUMN operation
        print("\n🧪 Testing RENAME COLUMN with RGB tracking...")
        
        rename_request = {
            "action": "alter_table",
            "table": "test_users",
            "operation": "rename_column",
            "old_name": "username",
            "new_name": "user_name"
        }
        
        zCRUD_Preped = {
            "zRequest": rename_request,
            "zForm": schema,
            "walker": None
        }
        
        result = handle_zData(zCRUD_Preped)
        
        if result:
            print("✅ RENAME COLUMN operation successful")
            
            # Verify column was renamed
            cur.execute("PRAGMA table_info(test_users)")
            columns = [row[1] for row in cur.fetchall()]
            
            assert "user_name" in columns, "Column should have been renamed to 'user_name'"
            assert "username" not in columns, "Old column 'username' should not exist"
            
            print("✅ Column successfully renamed")
            
            # Check migration was logged
            cur.execute("SELECT COUNT(*) FROM zMigrations WHERE migration_type = 'rename_column'")
            migration_count = cur.fetchone()[0]
            
            assert migration_count > 0, "Rename migration should have been logged"
            print("✅ Rename migration logged")
            
        else:
            print("❌ RENAME COLUMN operation failed")
            return False
        
        # Test 3: RENAME TABLE operation
        print("\n🧪 Testing RENAME TABLE with RGB tracking...")
        
        rename_table_request = {
            "action": "alter_table",
            "table": "test_users",
            "operation": "rename_table",
            "new_table_name": "renamed_users"
        }
        
        zCRUD_Preped = {
            "zRequest": rename_table_request,
            "zForm": schema,
            "walker": None
        }
        
        result = handle_zData(zCRUD_Preped)
        
        if result:
            print("✅ RENAME TABLE operation successful")
            
            # Verify table was renamed
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='renamed_users'")
            table_exists = cur.fetchone()
            
            assert table_exists is not None, "Table should have been renamed to 'renamed_users'"
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_users'")
            old_table_exists = cur.fetchone()
            
            assert old_table_exists is None, "Old table 'test_users' should not exist"
            
            print("✅ Table successfully renamed")
            
            # Check migration was logged
            cur.execute("SELECT COUNT(*) FROM zMigrations WHERE migration_type = 'rename_table'")
            migration_count = cur.fetchone()[0]
            
            assert migration_count > 0, "Rename table migration should have been logged"
            print("✅ Rename table migration logged")
            
        else:
            print("❌ RENAME TABLE operation failed")
            return False
        
        # Test 4: Verify all migrations are logged with RGB impact
        print("\n🧪 Testing migration history with RGB impact...")
        
        cur.execute("""
            SELECT migration_type, target_table, rgb_impact_r, rgb_impact_g, rgb_impact_b, criticality_level
            FROM zMigrations 
            ORDER BY applied_at
        """)
        
        migrations = cur.fetchall()
        
        assert len(migrations) >= 3, f"Expected at least 3 migrations, got {len(migrations)}"
        
        for migration_type, table, r_impact, g_impact, b_impact, criticality in migrations:
            print(f"Migration: {migration_type} on {table} - RGB impact: R={r_impact}, G={g_impact}, B={b_impact}, Criticality={criticality}")
            
            # Verify RGB impact values are reasonable
            assert isinstance(r_impact, (int, type(None))), "R impact should be integer"
            assert isinstance(g_impact, (int, type(None))), "G impact should be integer"
            assert isinstance(b_impact, (int, type(None))), "B impact should be integer"
            assert isinstance(criticality, (int, type(None))), "Criticality should be integer"
        
        print("✅ All migrations logged with RGB impact tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ ALTER TABLE integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    print("🧪 Testing RGB Phase 2 - ALTER TABLE Integration")
    print("=" * 60)
    
    success = test_alter_table_integration()
    
    if success:
        print("\n🎉 Phase 2 tests passed!")
        print("✅ ALTER TABLE operations integrated with RGB tracking")
        print("🌈 Full ALTER TABLE support operational!")
        print("📊 Migration history with RGB impact tracking working!")
    else:
        print("\n❌ Phase 2 tests failed!")
        print("Check the implementation and try again")
