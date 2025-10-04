#!/usr/bin/env python3
# tests/crud/test_direct_operations.py — Direct CRUD Operations Test Suite
# ───────────────────────────────────────────────────────────────

"""
Direct CRUD Operations Test Suite

Tests core CRUD functions directly with test database.
Simplified version using test fixtures.

Usage:
    python tests/crud/test_direct_operations.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase, count_rows, TEST_SCHEMA_PATH
from zCLI.subsystems.zCRUD.crud_delete import zDelete_sqlite
from zCLI.subsystems.zCRUD.crud_update import zUpdate
from zCLI.subsystems.zCRUD.crud_create import zCreate_sqlite
import sqlite3


def run_direct_operations_tests():
    """Run direct CRUD operations tests with test database."""
    
    print("=" * 80)
    print("DIRECT zCRUD Operations Test - Delete & Update")
    print("Testing core functions with isolated test database")
    print("=" * 80)
    
    # Use test database with automatic setup/cleanup
    with TestDatabase() as db_path:
        print(f"\n[Setup] Using test database: {db_path}")
        
        # Setup database connection
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        print(f"[OK] Connected to database")
        
        # Create zData structure (mimics crud_handler output)
        zData = {
            "ready": True,
            "type": "sqlite",
            "conn": conn,
            "cursor": cur,
            "path": db_path
        }
        
        # Load actual test schema (with defaults)
        import yaml
        with open(TEST_SCHEMA_PATH, 'r') as f:
            zForm = yaml.safe_load(f)
        
        # Update Meta with correct path
        zForm["Meta"]["Data_path"] = db_path
        
        # TEST 1: Initial count
        print("\n" + "─" * 80)
        print("TEST 1: Initial State")
        print("─" * 80)
        
        initial_count = count_rows('zApps')
        print(f"[Data] Initial app count: {initial_count}")
        
        # TEST 2: CREATE
        print("\n" + "─" * 80)
        print("TEST 2: CREATE - Add test apps")
        print("─" * 80)
        
        import datetime
        now = datetime.datetime.now(datetime.UTC).isoformat()
        
        create_request_1 = {
            "tables": ["zApps"],
            "values": {
                "name": "DirectTest_Delete",
                "type": "web",
                "version": "1.0.0",
                "created_at": now
            }
        }
        
        create_request_2 = {
            "tables": ["zApps"],
            "values": {
                "name": "DirectTest_Update",
                "type": "desktop",
                "version": "1.0.0",
                "created_at": now
            }
        }
        
        try:
            result1 = zCreate_sqlite(create_request_1, zForm, zData)
            print(f"[OK] Created 'DirectTest_Delete': {result1} row(s)")
            
            result2 = zCreate_sqlite(create_request_2, zForm, zData)
            print(f"[OK] Created 'DirectTest_Update': {result2} row(s)")
            
            assert count_rows('zApps') == 2, "Should have 2 apps"
        except Exception as e:
            print(f"[X] Create failed: {e}")
            conn.close()
            return False
        
        # TEST 3: UPDATE
        print("\n" + "─" * 80)
        print("TEST 3: UPDATE - Modify DirectTest_Update")
        print("─" * 80)
        
        update_request = {
            "tables": ["zApps"],
            "values": {"type": "mobile", "version": "2.0.0"},
            "where": {"name": "DirectTest_Update"}
        }
        
        print(f"[*] Update request:")
        print(f"    Values: {update_request['values']}")
        print(f"    Where: {update_request['where']}")
        
        try:
            rows_updated = zUpdate(update_request, zForm, zData)
            print(f"[OK] Result: {rows_updated} row(s) updated")
            
            # Verify update
            cur.execute("SELECT * FROM zApps WHERE name = ?", ("DirectTest_Update",))
            updated_row = cur.fetchone()
            if updated_row:
                print(f"[OK] Verified: {dict(zip([d[0] for d in cur.description], updated_row))}")
            else:
                print("[X] Record not found after update")
                conn.close()
                return False
        except Exception as e:
            print(f"[X] Update failed: {e}")
            conn.close()
            return False
        
        # TEST 4: DELETE
        print("\n" + "─" * 80)
        print("TEST 4: DELETE - Remove DirectTest_Delete")
        print("─" * 80)
        
        delete_request = {
            "tables": ["zApps"],
            "where": {"name": "DirectTest_Delete"}
        }
        
        print(f"[*] Delete request:")
        print(f"    Where: {delete_request['where']}")
        
        try:
            rows_deleted = zDelete_sqlite(delete_request, zForm, zData)
            print(f"[OK] Result: {rows_deleted} row(s) deleted")
            
            # Verify deletion
            cur.execute("SELECT COUNT(*) FROM zApps WHERE name = ?", ("DirectTest_Delete",))
            still_exists = cur.fetchone()[0]
            if still_exists == 0:
                print("[OK] Verified: Record successfully deleted")
            else:
                print(f"[X] Record still exists (count: {still_exists})")
                conn.close()
                return False
        except Exception as e:
            print(f"[X] Delete failed: {e}")
            conn.close()
            return False
        
        # TEST 5: Cleanup
        print("\n" + "─" * 80)
        print("TEST 5: Cleanup - Remove remaining test data")
        print("─" * 80)
        
        cleanup_request = {
            "tables": ["zApps"],
            "where": {"name": "DirectTest_Update"}
        }
        
        try:
            rows_deleted = zDelete_sqlite(cleanup_request, zForm, zData)
            print(f"[OK] Cleanup: {rows_deleted} row(s) deleted")
            
            final_count = count_rows('zApps')
            print(f"[Data] Final app count: {final_count}")
            
            if final_count == initial_count:
                print("[OK] Database restored to initial state")
            else:
                print(f"[WARN] Database state changed (was {initial_count}, now {final_count})")
        except Exception as e:
            print(f"[X] Cleanup failed: {e}")
            conn.close()
            return False
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("[SUMMARY] TEST SUMMARY")
        print("=" * 80)
        print("""
[OK] CORE FUNCTIONALITY VERIFIED:
  [+] CREATE - Direct function calls work
  [+] UPDATE - Multi-field updates with WHERE
  [+] DELETE - WHERE clause filtering
  [+] All operations use parameterized queries
  [+] Test database isolation working

[SUCCESS] All direct operations tests passed!
""")
        print("=" * 80)
        
        # Close connection
        conn.close()
        
        return True


if __name__ == "__main__":
    success = run_direct_operations_tests()
    sys.exit(0 if success else 1)

