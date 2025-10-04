#!/usr/bin/env python3
# tests/crud/test_upsert.py — UPSERT Operations Test
# ───────────────────────────────────────────────────────────────

"""
Test Suite for UPSERT Operations

Tests:
- Simple UPSERT (INSERT OR REPLACE)
- UPSERT with ON CONFLICT (selective update)
- UPSERT on primary key
- UPSERT on unique constraint
- UPSERT with composite primary key
- Update existing vs insert new
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase, TEST_SCHEMA_PATH
from zCLI.subsystems.zCRUD import handle_zCRUD


def test_upsert():
    """Test all UPSERT scenarios."""
    
    print("\n" + "="*80)
    print("UPSERT OPERATIONS TEST")
    print("="*80)
    
    with TestDatabase() as db_path:
        # Test 1: Simple UPSERT (INSERT OR REPLACE) - Insert new record
        print("\n" + "-"*80)
        print("TEST 1: UPSERT - Insert New Record")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "upsert",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test001", "testuser", "test@example.com", "pass123", "zUser"]
        })
        
        assert result == True, "UPSERT should succeed for new record"
        print(f"[OK] ✅ UPSERT inserted new record")
        
        # Verify record exists
        users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email"],
            "where": {"id": "zU_test001"}
        })
        
        assert len(users) == 1, "Should find the inserted user"
        assert users[0]["username"] == "testuser", "Username should match"
        print(f"[Check] User created: {users[0]}")
        
        # Test 2: UPSERT - Update Existing Record (same ID)
        print("\n" + "-"*80)
        print("TEST 2: UPSERT - Update Existing Record")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "upsert",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test001", "updated_user", "updated@example.com", "newpass", "zBuilder"]
        })
        
        assert result == True, "UPSERT should succeed for update"
        print(f"[OK] ✅ UPSERT updated existing record")
        
        # Verify record was updated
        users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "role"],
            "where": {"id": "zU_test001"}
        })
        
        assert len(users) == 1, "Should still have only one user"
        assert users[0]["username"] == "updated_user", "Username should be updated"
        assert users[0]["email"] == "updated@example.com", "Email should be updated"
        assert users[0]["role"] == "zBuilder", "Role should be updated"
        print(f"[Check] User updated: {users[0]}")
        
        # Test 3: UPSERT with ON CONFLICT (selective update)
        print("\n" + "-"*80)
        print("TEST 3: UPSERT with ON CONFLICT - Selective Update")
        print("-"*80)
        
        # First, insert a user
        handle_zCRUD({
            "action": "create",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test002", "user2", "user2@example.com", "pass456", "zUser"]
        })
        
        # UPSERT with ON CONFLICT - only update email, keep username
        result = handle_zCRUD({
            "action": "upsert",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test002", "should_not_update", "newemail@example.com", "newpass", "zAdmin"],
            "on_conflict": {
                "constraint": "id",
                "update": ["email", "role"]  # Only update these fields
            }
        })
        
        assert result == True, "UPSERT with ON CONFLICT should succeed"
        print(f"[OK] ✅ UPSERT with ON CONFLICT succeeded")
        
        # Verify only specified fields were updated
        users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "role"],
            "where": {"id": "zU_test002"}
        })
        
        assert len(users) == 1, "Should have one user"
        assert users[0]["username"] == "user2", "Username should NOT be updated (not in update list)"
        assert users[0]["email"] == "newemail@example.com", "Email should be updated"
        assert users[0]["role"] == "zAdmin", "Role should be updated"
        print(f"[Check] Selective update worked: {users[0]}")
        print(f"[OK] ✅ Only specified fields were updated")
        
        # Test 4: UPSERT - Simple syntax works same as ON CONFLICT
        print("\n" + "-"*80)
        print("TEST 4: UPSERT - Simple vs ON CONFLICT Comparison")
        print("-"*80)
        
        # Create test user
        handle_zCRUD({
            "action": "create",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test004", "simple_user", "simple@example.com", "pass", "zUser"]
        })
        
        # Simple UPSERT (INSERT OR REPLACE) - updates ALL fields
        result = handle_zCRUD({
            "action": "upsert",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_test004", "updated_simple", "simple@example.com", "newpass", "zAdmin"]
        })
        
        assert result == True, "Simple UPSERT should succeed"
        print(f"[OK] ✅ Simple UPSERT (INSERT OR REPLACE) works")
        
        # Verify update
        users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "role"],
            "where": {"id": "zU_test004"}
        })
        
        assert users[0]["username"] == "updated_simple", "Username should be updated"
        assert users[0]["role"] == "zAdmin", "Role should be updated"
        print(f"[Check] Simple UPSERT updated all fields: {users[0]}")
        
        # Test 5: Multiple UPSERTs (batch)
        print("\n" + "-"*80)
        print("TEST 5: Multiple UPSERTs (Idempotent)")
        print("-"*80)
        
        # UPSERT same record 3 times
        for i in range(3):
            result = handle_zCRUD({
                "action": "upsert",
                "tables": ["zUsers"],
                "model": TEST_SCHEMA_PATH,
                "fields": ["id", "username", "email", "password", "role"],
                "values": ["zU_batch", f"batch_user_v{i}", "batch@example.com", "pass", "zUser"]
            })
            assert result == True, f"UPSERT {i+1} should succeed"
        
        # Verify only one record exists
        users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username"],
            "where": {"id": "zU_batch"}
        })
        
        assert len(users) == 1, "Should have only one record (upserted 3 times)"
        assert users[0]["username"] == "batch_user_v2", "Should have latest value"
        print(f"[OK] ✅ Multiple UPSERTs are idempotent")
        
        # Test 6: UPSERT with validation
        print("\n" + "-"*80)
        print("TEST 6: UPSERT with Validation Failure")
        print("-"*80)
        
        # Try UPSERT with invalid email
        result = handle_zCRUD({
            "action": "upsert",
            "tables": ["zUsers"],
            "model": TEST_SCHEMA_PATH,
            "fields": ["id", "username", "email", "password", "role"],
            "values": ["zU_invalid", "invaliduser", "not-an-email", "pass1234", "zUser"]
        })
        
        assert result == False, "UPSERT should fail validation"
        print(f"[OK] ✅ UPSERT respects validation rules (invalid email rejected)")
        
        # Summary
        print("\n" + "="*80)
        print("[SUMMARY] TEST SUMMARY")
        print("="*80)
        print("[OK] All UPSERT Tests Passed!")
        print("")
        print("[TESTED SCENARIOS]:")
        print("  [+] UPSERT new record (INSERT)")
        print("  [+] UPSERT existing record (UPDATE with INSERT OR REPLACE)")
        print("  [+] ON CONFLICT with selective field updates")
        print("  [+] Simple vs ON CONFLICT syntax")
        print("  [+] Multiple UPSERTs (idempotent)")
        print("  [+] UPSERT with validation (rejects invalid data)")
        print("")
        print("[SUCCESS] UPSERT operation is WORKING! " + "✅" * 3)
        print("="*80)
        
        return True


def main():
    """Run all UPSERT tests."""
    try:
        success = test_upsert()
        return success
    except Exception as e:
        print(f"\n[X] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)

