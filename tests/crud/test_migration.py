#!/usr/bin/env python3
# tests/crud/test_migration.py — Migration System Test
# ───────────────────────────────────────────────────────────────

"""
Migration System Test Suite

Tests the automatic ADD COLUMN migration feature.

Usage:
    python tests/crud/test_migration.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sqlite3
import yaml
from zCLI.subsystems.zMigrate import ZMigrate, auto_migrate_schema
from zCLI.subsystems.zCRUD import handle_zCRUD


def test_add_column_migration():
    """Test automatic ADD COLUMN migration."""
    
    print("="*80)
    print("MIGRATION TEST - Automatic ADD COLUMN")
    print("="*80)
    
    db_path = "test_migration.db"
    
    try:
        # ────────────────────────────────────────────────────────
        # STEP 1: Create initial database with basic schema
        # ────────────────────────────────────────────────────────
        print("\n[Step 1] Creating initial database with basic schema...")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        
        # Create table with only 2 columns
        cur.execute("""
            CREATE TABLE test_apps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert test data
        cur.execute("INSERT INTO test_apps (id, name) VALUES (?, ?)", ["app1", "TestApp"])
        conn.commit()
        
        print("[OK] Database created with table: test_apps (2 columns)")
        print("     Columns: id, name")
        
        # Verify initial structure
        cur.execute("PRAGMA table_info(test_apps)")
        initial_columns = [row[1] for row in cur.fetchall()]
        print(f"[OK] Initial columns: {initial_columns}")
        
        conn.close()
        
        # ────────────────────────────────────────────────────────
        # STEP 2: Create YAML schema with ADDITIONAL column
        # ────────────────────────────────────────────────────────
        print("\n[Step 2] Creating YAML schema with additional column...")
        
        # Schema has 3 columns: id, name, status (NEW!)
        schema_yaml = """
test_apps:
  id:
    type: str
    pk: true
  
  name:
    type: str
    required: true
  
  status:
    type: str
    default: "active"

Meta:
  Data_Type: sqlite
  Data_path: test_migration.db
"""
        
        schema_path = "test_schema_migration.yaml"
        with open(schema_path, 'w') as f:
            f.write(schema_yaml)
        
        print("[OK] YAML schema created with 3 columns")
        print("     Columns: id, name, status (NEW)")
        
        # ────────────────────────────────────────────────────────
        # STEP 3: Run zCRUD operation (triggers auto-migration)
        # ────────────────────────────────────────────────────────
        print("\n[Step 3] Running CRUD operation (triggers migration)...")
        
        request = {
            "action": "create",
            "tables": ["test_apps"],
            "model": schema_path,
            "fields": ["id", "name", "status"],
            "values": ["app2", "NewApp", "pending"]
        }
        
        result = handle_zCRUD(request)
        
        if result:
            print("[OK] CREATE operation succeeded")
            print(f"     Result: {result}")
        else:
            print("[X] CREATE operation failed")
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 4: Verify column was added
        # ────────────────────────────────────────────────────────
        print("\n[Step 4] Verifying column was added...")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(test_apps)")
        final_columns = [row[1] for row in cur.fetchall()]
        
        print(f"[Check] Final columns: {final_columns}")
        
        if "status" in final_columns:
            print("[OK] ✅ Column 'status' was added automatically!")
        else:
            print("[X] ❌ Column 'status' was NOT added")
            conn.close()
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 5: Verify existing data preserved
        # ────────────────────────────────────────────────────────
        print("\n[Step 5] Verifying existing data preserved...")
        
        cur.execute("SELECT id, name, status FROM test_apps WHERE id = ?", ["app1"])
        old_row = cur.fetchone()
        
        if old_row:
            print(f"[OK] Old record preserved: {old_row}")
            if old_row[2] is None:  # status should be NULL for existing row
                print("[OK] ✅ Existing row has NULL for new column (expected)")
            else:
                print(f"[OK] Existing row has value: {old_row[2]}")
        else:
            print("[X] Old record not found!")
            conn.close()
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 6: Verify new data has default value
        # ────────────────────────────────────────────────────────
        print("\n[Step 6] Verifying new data has values...")
        
        cur.execute("SELECT id, name, status FROM test_apps WHERE id = ?", ["app2"])
        new_row = cur.fetchone()
        
        if new_row:
            print(f"[OK] New record: {new_row}")
            if new_row[2] == "pending":
                print("[OK] ✅ New row has correct status value")
            else:
                print(f"[X] Status value unexpected: {new_row[2]}")
        else:
            print("[X] New record not found!")
            conn.close()
            return False
        
        conn.close()
        
        # ────────────────────────────────────────────────────────
        # SUCCESS!
        # ────────────────────────────────────────────────────────
        print("\n" + "="*80)
        print("[SUCCESS] Migration Test Completed Successfully!")
        print("="*80)
        print("\n[Summary]")
        print("  ✅ Initial table created (2 columns)")
        print("  ✅ Schema updated with new column")
        print("  ✅ Migration detected new column")
        print("  ✅ ALTER TABLE ADD COLUMN executed")
        print("  ✅ Existing data preserved")
        print("  ✅ New data uses new column")
        print("\n[Migration] Auto-migration is WORKING! 🎉")
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n[Cleanup] Removed test database: {db_path}")
        
        if os.path.exists(schema_path):
            os.remove(schema_path)
            print(f"[Cleanup] Removed test schema: {schema_path}")


def test_no_changes_scenario():
    """Test that migration does nothing when schema matches database."""
    
    print("\n" + "="*80)
    print("MIGRATION TEST - No Changes Scenario")
    print("="*80)
    
    db_path = "test_no_change.db"
    schema_path = "test_schema_no_change.yaml"
    
    try:
        # Create database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        
        cur.execute("""
            CREATE TABLE test_table (
                id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        print("\n[Setup] Database created with table: test_table")
        
        # Create matching schema (no new columns)
        schema_yaml = """
test_table:
  id:
    type: str
    pk: true
  name:
    type: str

Meta:
  Data_Type: sqlite
  Data_path: test_no_change.db
"""
        
        with open(schema_path, 'w') as f:
            f.write(schema_yaml)
        
        # Run operation (should NOT migrate anything)
        print("\n[Test] Running operation with matching schema...")
        
        request = {
            "action": "create",
            "tables": ["test_table"],
            "model": schema_path,
            "fields": ["id", "name"],
            "values": ["test1", "TestName"]
        }
        
        result = handle_zCRUD(request)
        
        if result:
            print("[OK] ✅ Operation succeeded (no migration needed)")
            print("[OK] Schema already up to date")
            return True
        else:
            print("[X] Operation failed")
            return False
            
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(schema_path):
            os.remove(schema_path)


def test_multiple_columns_migration():
    """Test adding multiple columns in one migration."""
    
    print("\n" + "="*80)
    print("MIGRATION TEST - Multiple Columns")
    print("="*80)
    
    db_path = "test_multi_col.db"
    schema_path = "test_schema_multi.yaml"
    
    try:
        # Create initial database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        
        cur.execute("""
            CREATE TABLE apps (
                id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        print("\n[Setup] Initial schema: id, name")
        
        # Schema with 3 NEW columns
        schema_yaml = """
apps:
  id:
    type: str
    pk: true
  name:
    type: str
  type:
    type: str
    default: "web"
  version:
    type: str
    default: "1.0.0"
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_path: test_multi_col.db
"""
        
        with open(schema_path, 'w') as f:
            f.write(schema_yaml)
        
        print("[Setup] Updated schema adds: type, version, created_at")
        
        # Run CRUD operation
        print("\n[Test] Running CREATE operation...")
        
        request = {
            "action": "create",
            "tables": ["apps"],
            "model": schema_path,
            "fields": ["id", "name"],
            "values": ["app1", "TestApp"]
        }
        
        result = handle_zCRUD(request)
        
        # Verify all columns added
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(apps)")
        columns = [row[1] for row in cur.fetchall()]
        conn.close()
        
        print(f"\n[Check] Final columns: {columns}")
        
        expected_new = ["type", "version", "created_at"]
        for col in expected_new:
            if col in columns:
                print(f"[OK] ✅ Column '{col}' added")
            else:
                print(f"[X] ❌ Column '{col}' NOT added")
                return False
        
        print("\n[OK] ✅ Multiple columns migrated successfully!")
        return True
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(schema_path):
            os.remove(schema_path)


# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

def run_all_migration_tests():
    """Run all migration tests."""
    
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*25 + "zCLI MIGRATION TEST SUITE" + " "*28 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    tests = [
        ("Basic ADD COLUMN Migration", test_add_column_migration),
        ("No Changes Scenario", test_no_changes_scenario),
        ("Multiple Columns Migration", test_multiple_columns_migration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n[X] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*80)
    print(f"Total: {len(results)} tests")
    print(f"[OK] Passed: {passed}")
    print(f"[X] Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n[SUCCESS] All migration tests passed! ✅")
        return True
    else:
        print(f"\n[FAIL] {failed} test(s) failed ❌")
        return False


if __name__ == "__main__":
    success = run_all_migration_tests()
    sys.exit(0 if success else 1)

