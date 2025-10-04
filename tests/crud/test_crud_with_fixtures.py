#!/usr/bin/env python3
# tests/crud/test_crud_with_fixtures.py — Example CRUD Test with Fixtures
# ───────────────────────────────────────────────────────────────

"""
Example CRUD Test Using Test Fixtures

Demonstrates how to write self-contained CRUD tests that:
1. Create their own test database
2. Run operations
3. Verify results
4. Clean up automatically

This is a template for migrating existing tests.

Usage:
    python tests/crud/test_crud_with_fixtures.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase, count_rows, clear_table
from zCLI.subsystems.zCRUD import handle_zCRUD


def test_create_read_update_delete():
    """Test complete CRUD cycle with fixtures."""
    
    print("\n" + "=" * 70)
    print("[TEST] CRUD Operations with Test Fixtures")
    print("=" * 70)
    
    # Use context manager for automatic setup/teardown
    with TestDatabase() as db_path:
        print(f"\n[Setup] Test database: {db_path}")
        
        # ─────────────────────────────────────────────────────────
        # TEST 1: CREATE
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 70)
        print("TEST 1: CREATE - Add test app")
        print("─" * 70)
        
        create_request = {
            "model": "test.schemas.schema.test.zApps",
            "action": "create",
            "tables": ["zApps"],
            "fields": ["id", "name", "type", "version"],
            "values": ["zA_fixture_test", "FixtureTestApp", "web", "1.0.0"]
        }
        
        try:
            result = handle_zCRUD(create_request)
            if result:
                print(f"[PASS] CREATE: Added {result} row(s)")
                assert count_rows('zApps') == 1, "Should have 1 app"
            else:
                print(f"[FAIL] CREATE: No rows added")
                return False
        except Exception as e:
            print(f"[FAIL] CREATE error: {e}")
            return False
        
        # ─────────────────────────────────────────────────────────
        # TEST 2: READ
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 70)
        print("TEST 2: READ - Retrieve app")
        print("─" * 70)
        
        read_request = {
            "model": "test.schemas.schema.test.zApps",
            "action": "read",
            "tables": ["zApps"],
            "fields": ["id", "name", "type", "version"],
            "where": {"name": "FixtureTestApp"}
        }
        
        try:
            results = handle_zCRUD(read_request)
            if results and len(results) > 0:
                print(f"[PASS] READ: Found {len(results)} row(s)")
                print(f"       Data: {results[0]}")
                assert results[0]['name'] == 'FixtureTestApp', "Name should match"
            else:
                print(f"[FAIL] READ: No results found")
                return False
        except Exception as e:
            print(f"[FAIL] READ error: {e}")
            return False
        
        # ─────────────────────────────────────────────────────────
        # TEST 3: UPDATE
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 70)
        print("TEST 3: UPDATE - Modify app")
        print("─" * 70)
        
        update_request = {
            "model": "test.schemas.schema.test.zApps",
            "action": "update",
            "tables": ["zApps"],
            "values": {"version": "2.0.0", "type": "desktop"},
            "where": {"name": "FixtureTestApp"}
        }
        
        try:
            result = handle_zCRUD(update_request)
            if result:
                print(f"[PASS] UPDATE: Modified {result} row(s)")
                
                # Verify update
                verify = handle_zCRUD(read_request)
                if verify and verify[0]['version'] == '2.0.0':
                    print(f"       Verified: version updated to 2.0.0")
                else:
                    print(f"[FAIL] UPDATE: Version not updated")
                    return False
            else:
                print(f"[FAIL] UPDATE: No rows modified")
                return False
        except Exception as e:
            print(f"[FAIL] UPDATE error: {e}")
            return False
        
        # ─────────────────────────────────────────────────────────
        # TEST 4: DELETE
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 70)
        print("TEST 4: DELETE - Remove app")
        print("─" * 70)
        
        delete_request = {
            "model": "test.schemas.schema.test.zApps",
            "action": "delete",
            "tables": ["zApps"],
            "where": {"name": "FixtureTestApp"}
        }
        
        try:
            result = handle_zCRUD(delete_request)
            if result:
                print(f"[PASS] DELETE: Removed {result} row(s)")
                assert count_rows('zApps') == 0, "Should have 0 apps after delete"
            else:
                print(f"[FAIL] DELETE: No rows removed")
                return False
        except Exception as e:
            print(f"[FAIL] DELETE error: {e}")
            return False
        
        print("\n" + "=" * 70)
        print("[SUCCESS] All CRUD operations passed!")
        print("=" * 70)
        
        return True
    
    # Database automatically cleaned up when exiting context


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("[EXAMPLE] CRUD Test with Fixtures Template")
    print("=" * 70)
    print("\nThis demonstrates the pattern for self-contained tests:")
    print("  1. Create test database from schema.test.yaml")
    print("  2. Run test operations")
    print("  3. Verify results")
    print("  4. Automatic cleanup")
    print("=" * 70)
    
    success = test_create_read_update_delete()
    
    sys.exit(0 if success else 1)

