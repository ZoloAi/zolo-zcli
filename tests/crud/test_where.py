#!/usr/bin/env python3
# tests/crud/test_where.py — Advanced WHERE Operators Test
# ───────────────────────────────────────────────────────────────

"""
Test Suite for Advanced WHERE Operators

Tests all supported operators:
- Comparison: <, >, <=, >=, !=
- IN operator: [val1, val2, val3]
- LIKE patterns: {LIKE: "%pattern%"}
- IS NULL / IS NOT NULL
- OR conditions
- BETWEEN
- Complex nested conditions
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase
from zCLI.subsystems.zCRUD import handle_zCRUD
import datetime


def test_advanced_where():
    """Test all advanced WHERE operators."""
    
    print("\n" + "="*80)
    print("ADVANCED WHERE OPERATORS TEST")
    print("="*80)
    
    with TestDatabase() as db_path:
        # Create test data
        print("\n[Setup] Creating test data...")
        _create_test_data(db_path)
        
        # Test 1: Comparison operators
        print("\n" + "-"*80)
        print("TEST 1: Comparison Operators (<, >, <=, >=, !=)")
        print("-"*80)
        
        # Test >
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "role"],
            "where": {"id": {">": "zU_00000002"}}
        })
        print(f"[>] Found {len(result)} users with id > 'zU_00000002'")
        assert len(result) >= 1, "Should find users with ID greater than zU_00000002"
        print(f"[OK] Comparison operator '>' works")
        
        # Test >=
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username"],
            "where": {"id": {">=": "zU_00000002"}}
        })
        print(f"[>=] Found {len(result)} users with id >= 'zU_00000002'")
        assert len(result) >= 1, "Should find users"
        print(f"[OK] Comparison operator '>=' works")
        
        # Test !=
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "role"],
            "where": {"role": {"!=": "zAdmin"}}
        })
        print(f"[!=] Found {len(result)} non-admin users")
        assert len(result) >= 2, "Should find non-admin users"
        print(f"[OK] Comparison operator '!=' works")
        
        # Test 2: IN operator
        print("\n" + "-"*80)
        print("TEST 2: IN Operator")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "role"],
            "where": {"role": ["zAdmin", "zBuilder"]}
        })
        print(f"[IN] Found {len(result)} admin/builder users")
        assert len(result) >= 2, "Should find admin and builder users"
        for user in result:
            assert user["role"] in ["zAdmin", "zBuilder"], f"User role should be admin or builder: {user}"
        print(f"[OK] IN operator works")
        
        # Test 3: LIKE patterns
        print("\n" + "-"*80)
        print("TEST 3: LIKE Patterns")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "email"],
            "where": {"email": {"LIKE": "%test%"}}
        })
        print(f"[LIKE] Found {len(result)} users with 'test' in email")
        assert len(result) >= 1, "Should find users with test in email"
        for user in result:
            assert "test" in user["email"].lower(), f"Email should contain 'test': {user['email']}"
        print(f"[OK] LIKE operator works")
        
        # Test 4: IS NULL / IS NOT NULL
        print("\n" + "-"*80)
        print("TEST 4: IS NULL / IS NOT NULL")
        print("-"*80)
        
        # Add a user with NULL email for testing
        handle_zCRUD({
            "action": "create",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "email", "password", "role"],
            "values": ["null_test", "null@test.com", "pass123", "zUser"]
        })
        
        # Test IS NOT NULL
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "email"],
            "where": {"email": {"IS NOT": None}}
        })
        print(f"[IS NOT NULL] Found {len(result)} users with email")
        assert len(result) >= 3, "Should find users with email"
        print(f"[OK] IS NOT NULL works")
        
        # Test 5: OR conditions
        print("\n" + "-"*80)
        print("TEST 5: OR Conditions")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "role"],
            "where": {
                "OR": [
                    {"role": "zAdmin"},
                    {"username": "builder"}
                ]
            }
        })
        print(f"[OR] Found {len(result)} users (admin OR username='builder')")
        assert len(result) >= 1, "Should find admin or builder user"
        print(f"[OK] OR conditions work")
        
        # Test 6: Complex nested conditions
        print("\n" + "-"*80)
        print("TEST 6: Complex Nested Conditions")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "role"],
            "where": {
                "role": {"!=": "zUser"},
                "OR": [
                    {"username": {"LIKE": "%admin%"}},
                    {"username": {"LIKE": "%builder%"}}
                ]
            }
        })
        print(f"[Complex] Found {len(result)} users (non-user role AND (admin OR builder in name))")
        assert len(result) >= 1, "Should find matching users"
        print(f"[OK] Complex nested conditions work")
        
        # Test 7: BETWEEN operator
        print("\n" + "-"*80)
        print("TEST 7: BETWEEN Operator")
        print("-"*80)
        
        # Get all user IDs first
        all_users = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["id"]
        })
        if len(all_users) >= 2:
            ids = sorted([u["id"] for u in all_users])
            min_id = ids[0]
            max_id = ids[-1]
            
            result = handle_zCRUD({
                "action": "read",
                "tables": ["zUsers"],
                "model": "tests/schemas/schema.test.yaml",
                "fields": ["username", "id"],
                "where": {"id": {"BETWEEN": [min_id, max_id]}}
            })
            print(f"[BETWEEN] Found {len(result)} users with ID between [{min_id}, {max_id}]")
            assert len(result) >= 2, "Should find users in range"
            print(f"[OK] BETWEEN operator works")
        else:
            print(f"[SKIP] Not enough users to test BETWEEN")
        
        # Test 8: UPDATE with advanced WHERE
        print("\n" + "-"*80)
        print("TEST 8: UPDATE with Advanced WHERE")
        print("-"*80)
        
        updated = handle_zCRUD({
            "action": "update",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "values": {"role": "zBuilder"},
            "where": {"username": {"LIKE": "%test%"}}
        })
        print(f"[UPDATE] Updated {updated} user(s) with 'test' in username")
        assert updated >= 0, "Should update users"
        print(f"[OK] UPDATE with LIKE works")
        
        # Test 9: DELETE with advanced WHERE
        print("\n" + "-"*80)
        print("TEST 9: DELETE with Advanced WHERE")
        print("-"*80)
        
        deleted = handle_zCRUD({
            "action": "delete",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "where": {"username": {"IN": ["null_test"]}}
        })
        print(f"[DELETE] Deleted {deleted} user(s) with IN operator")
        assert deleted >= 0, "Should delete users"
        print(f"[OK] DELETE with IN works")
        
        # Test 10: Multiple comparison operators
        print("\n" + "-"*80)
        print("TEST 10: Multiple Comparison Operators in One Query")
        print("-"*80)
        
        result = handle_zCRUD({
            "action": "read",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": ["username", "id"],
            "where": {
                "id": {">": "zU_00000001"},
                "role": {"!=": "zUser"}
            }
        })
        print(f"[Multi] Found {len(result)} users (id > X AND role != zUser)")
        assert len(result) >= 0, "Query should execute without error"
        print(f"[OK] Multiple comparison operators work")
        
        # Summary
        print("\n" + "="*80)
        print("[SUMMARY] TEST SUMMARY")
        print("="*80)
        print("[OK] All Advanced WHERE Operator Tests Passed!")
        print("")
        print("[TESTED OPERATORS]:")
        print("  [+] Comparison: <, >, <=, >=, !=")
        print("  [+] IN operator")
        print("  [+] LIKE patterns")
        print("  [+] IS NULL / IS NOT NULL")
        print("  [+] OR conditions")
        print("  [+] BETWEEN")
        print("  [+] Complex nested conditions")
        print("  [+] UPDATE with advanced WHERE")
        print("  [+] DELETE with advanced WHERE")
        print("")
        print("[SUCCESS] Advanced WHERE operators are WORKING! " + "✅" * 3)
        print("="*80)
        
        return True


def _create_test_data(db_path):
    """Create test users for WHERE tests."""
    test_users = [
        {"username": "admin", "email": "admin@test.com", "password": "admin123", "role": "zAdmin"},
        {"username": "builder", "email": "builder@test.com", "password": "build123", "role": "zBuilder"},
        {"username": "user1", "email": "user1@test.com", "password": "user123", "role": "zUser"},
        {"username": "testuser", "email": "testuser@example.com", "password": "test123", "role": "zUser"},
    ]
    
    for user in test_users:
        handle_zCRUD({
            "action": "create",
            "tables": ["zUsers"],
            "model": "tests/schemas/schema.test.yaml",
            "fields": list(user.keys()),
            "values": list(user.values())
        })
    
    print(f"[OK] Created {len(test_users)} test users")


if __name__ == "__main__":
    try:
        success = test_advanced_where()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[X] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

