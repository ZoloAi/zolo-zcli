#!/usr/bin/env python3
# tests/crud/test_zApps_crud.py — zApps CRUD Operations Test Suite
# ───────────────────────────────────────────────────────────────

"""
zApps CRUD Operations Test Suite

Tests CREATE, READ, UPDATE, DELETE operations with zApps table.
Uses test fixtures for isolated, repeatable testing.

Usage:
    python tests/crud/test_zApps_crud.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase, count_rows, TEST_SCHEMA_PATH
from zCLI.subsystems.zCRUD import handle_zCRUD
import yaml


def run_zApps_crud_tests():
    """Run zApps CRUD tests with isolated test database."""
    
    print("=" * 80)
    print("zCRUD DELETE & UPDATE TEST - zApps Use Case")
    print("Using test fixtures (isolated test database)")
    print("=" * 80)
    
    # Load test schema
    with open(TEST_SCHEMA_PATH, 'r') as f:
        test_schema = yaml.safe_load(f)
    
    # Use test database with automatic setup/cleanup
    with TestDatabase() as db_path:
        print(f"\n[Setup] Using test database: {db_path}")
        print(f"[Setup] Using schema: {TEST_SCHEMA_PATH}")
        
        # TEST 1: CREATE
        print("\n" + "─" * 80)
        print("TEST 1: CREATE - Setting up test zApps")
        print("─" * 80)
        
        # Create request with model path
        create_request = {
            "action": "create",
            "tables": ["zApps"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["name", "type"],
            "values": ["TestApp_Delete", "web"]
        }
        
        print("\n[Request]")
        print(f"  Action: {create_request['action']}")
        print(f"  Table: {create_request['tables'][0]}")
        print(f"  Fields: {create_request['fields']}")
        print(f"  Values: {create_request['values']}")
        
        try:
            result = handle_zCRUD(create_request)
            print(f"[OK] Result: {result} row(s) created")
            assert result == 1, "Should create 1 row"
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # Create second test app
        create_request_2 = {
            "action": "create",
            "tables": ["zApps"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["name", "type"],
            "values": ["TestApp_Update", "desktop"]
        }
        
        print("\n[*] Creating second test app...")
        try:
            result = handle_zCRUD(create_request_2)
            print(f"[OK] Result: {result} row(s) created")
            assert count_rows('zApps') == 2, "Should have 2 apps"
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # TEST 2: READ
        print("\n" + "─" * 80)
        print("TEST 2: READ - List all zApps")
        print("─" * 80)
        
        read_request = {
            "action": "read",
            "tables": ["zApps"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "name", "type", "version"]
        }
        
        try:
            results = handle_zCRUD(read_request)
            print(f"\n[OK] Found {len(results)} app(s):")
            for row in results:
                print(f"  • {row}")
            assert len(results) == 2, "Should find 2 apps"
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # TEST 3: UPDATE
        print("\n" + "─" * 80)
        print("TEST 3: UPDATE - Modify TestApp_Update")
        print("─" * 80)
        
        update_request = {
            "action": "update",
            "tables": ["zApps"],
            "model": TEST_SCHEMA_PATH,
            "values": {
                "type": "mobile",
                "version": "2.0.0"
            },
            "where": {
                "name": "TestApp_Update"
            }
        }
        
        try:
            result = handle_zCRUD(update_request)
            print(f"[OK] Result: {result} row(s) updated")
            
            # Verify update
            print("\n[*] Verifying update...")
            verify_read = {
                "action": "read",
                "tables": ["zApps"],
                "model": TEST_SCHEMA_PATH,
                "fields": ["name", "type", "version"],
                "where": {"name": "TestApp_Update"}
            }
            
            results = handle_zCRUD(verify_read)
            if results and results[0]['version'] == '2.0.0':
                print(f"[OK] Updated record: {results[0]}")
            else:
                print("[X] Verification failed")
                return False
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # TEST 4: DELETE
        print("\n" + "─" * 80)
        print("TEST 4: DELETE - Remove TestApp_Delete")
        print("─" * 80)
        
        delete_request = {
            "action": "delete",
            "tables": ["zApps"],
            "model": TEST_SCHEMA_PATH,
            "where": {
                "name": "TestApp_Delete"
            }
        }
        
        try:
            result = handle_zCRUD(delete_request)
            print(f"[OK] Result: {result} row(s) deleted")
            assert count_rows('zApps') == 1, "Should have 1 app remaining"
            
            # Verify deletion
            print("\n[*] Verifying deletion...")
            verify_delete = {
                "action": "read",
                "tables": ["zApps"],
                "model": TEST_SCHEMA_PATH,
                "fields": ["name"],
                "where": {"name": "TestApp_Delete"}
            }
            
            results = handle_zCRUD(verify_delete)
            if not results:
                print("[OK] Record successfully deleted (not found)")
            else:
                print(f"[X] Record still exists: {results}")
                return False
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # TEST 5: DELETE by ID
        print("\n" + "─" * 80)
        print("TEST 5: DELETE - Using ID filter (UI pattern)")
        print("─" * 80)
        
        try:
            # Get ID of remaining app
            get_id_request = {
                "action": "read",
                "tables": ["zApps"],
                "model": TEST_SCHEMA_PATH,
                "fields": ["id", "name"],
                "where": {"name": "TestApp_Update"}
            }
            
            results = handle_zCRUD(get_id_request)
            if results:
                app_id = results[0]["id"]
                print(f"[*] Found app ID: {app_id}")
                
                # Delete using ID
                delete_by_id_request = {
                    "action": "delete",
                    "tables": ["zApps"],
                    "model": TEST_SCHEMA_PATH,
                    "where": {"id": app_id}
                }
                
                result = handle_zCRUD(delete_by_id_request)
                print(f"[OK] Result: {result} row(s) deleted")
                assert count_rows('zApps') == 0, "Should have 0 apps remaining"
            else:
                print("[X] Could not find TestApp_Update")
                return False
        except Exception as e:
            print(f"[X] Error: {e}")
            return False
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("[SUMMARY] TEST SUMMARY")
        print("=" * 80)
        print("""
[OK] TESTED OPERATIONS:
  1. CREATE  - Added test records
  2. READ    - Retrieved and verified data
  3. UPDATE  - Modified fields with WHERE clause
  4. DELETE  - Removed records by name and by ID
  
[KEY] KEY FINDINGS:
  • Direct zCRUD format works without zFunc wrapper
  • UPDATE supports multiple fields and WHERE clause
  • DELETE supports flexible WHERE conditions
  • All operations use test database (isolated)
  • Automatic cleanup after tests
  
[FORMAT] DIRECT zCRUD FORMAT:
  CREATE/UPDATE/DELETE use same structure as UI onSubmit blocks
  
[SUCCESS] All zApps CRUD tests completed successfully!
""")
        print("=" * 80)
        
        return True


if __name__ == "__main__":
    success = run_zApps_crud_tests()
    sys.exit(0 if success else 1)

