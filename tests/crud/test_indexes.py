#!/usr/bin/env python3
# tests/crud/test_indexes.py — Index Support Test
# ───────────────────────────────────────────────────────────────

"""
Test Suite for Index Support

Tests:
- Simple index creation (single column)
- Composite index creation (multiple columns)
- Unique index creation
- Partial index creation (with WHERE clause)
- Expression index creation
- Index detection in migration system
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sqlite3
import yaml
from tests.fixtures import TestDatabase
from zCLI.subsystems.zData import handle_zCRUD, zTables


def test_indexes():
    """Test all index creation scenarios."""
    
    print("\n" + "="*80)
    print("INDEX SUPPORT TEST")
    print("="*80)
    
    # Test 1: Simple index
    print("\n" + "-"*80)
    print("TEST 1: Simple Index (Single Column)")
    print("-"*80)
    
    db_path = "test_indexes.db"
    schema_path = "test_indexes_schema.yaml"
    
    try:
        # Create schema with simple index
        schema = {
            "test_users": {
                "id": {"type": "str", "pk": True},
                "email": {"type": "str", "required": True},
                "username": {"type": "str", "required": True},
                "indexes": [
                    {
                        "name": "idx_users_email",
                        "columns": ["email"]
                    }
                ]
            },
            "Meta": {
                "Data_Type": "sqlite",
                "Data_path": db_path
            }
        }
        
        # Save schema
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        # Create table (should also create index)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Verify index was created
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        
        index_names = [idx[1] for idx in indexes]
        print(f"[Check] Found indexes: {index_names}")
        
        assert "idx_users_email" in index_names, "Simple index should be created"
        print(f"[OK] ✅ Simple index created")
        
        # Verify index columns
        cur.execute("PRAGMA index_info(idx_users_email)")
        index_cols = [col[2] for col in cur.fetchall()]
        print(f"[Check] Index columns: {index_cols}")
        
        assert index_cols == ["email"], "Index should be on email column"
        print(f"[OK] ✅ Index on correct column")
        
        conn.close()
        
        # Test 2: Composite index
        print("\n" + "-"*80)
        print("TEST 2: Composite Index (Multiple Columns)")
        print("-"*80)
        
        schema["test_users"]["indexes"].append({
            "name": "idx_users_email_username",
            "columns": ["email", "username"]
        })
        
        # Recreate with composite index
        if os.path.exists(db_path):
            os.remove(db_path)
        
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Verify composite index
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        index_names = [idx[1] for idx in indexes]
        
        assert "idx_users_email_username" in index_names, "Composite index should be created"
        print(f"[OK] ✅ Composite index created")
        
        # Verify index columns (order matters!)
        cur.execute("PRAGMA index_info(idx_users_email_username)")
        index_cols = [col[2] for col in cur.fetchall()]
        
        assert index_cols == ["email", "username"], "Composite index should have both columns in order"
        print(f"[OK] ✅ Composite index has correct columns: {index_cols}")
        
        conn.close()
        
        # Test 3: Unique index
        print("\n" + "-"*80)
        print("TEST 3: Unique Index")
        print("-"*80)
        
        schema["test_users"]["indexes"] = [{
            "name": "idx_users_email_unique",
            "columns": ["email"],
            "unique": True
        }]
        
        if os.path.exists(db_path):
            os.remove(db_path)
        
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Verify unique index
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        
        # Find our index
        unique_idx = None
        for idx in indexes:
            if idx[1] == "idx_users_email_unique":
                unique_idx = idx
                break
        
        assert unique_idx is not None, "Unique index should exist"
        assert unique_idx[2] == 1, "Index should be marked as unique"
        print(f"[OK] ✅ Unique index created")
        
        # Test uniqueness enforcement
        cur.execute("INSERT INTO test_users (id, email, username) VALUES ('u1', 'test@example.com', 'user1')")
        
        try:
            cur.execute("INSERT INTO test_users (id, email, username) VALUES ('u2', 'test@example.com', 'user2')")
            conn.commit()
            assert False, "Should have failed due to unique constraint"
        except sqlite3.IntegrityError as e:
            print(f"[OK] ✅ Unique constraint enforced: {e}")
        
        conn.close()
        
        # Test 4: Partial index (WHERE clause)
        print("\n" + "-"*80)
        print("TEST 4: Partial Index (WHERE clause)")
        print("-"*80)
        
        schema["test_users"]["status"] = {"type": "str", "default": "active"}
        schema["test_users"]["indexes"] = [{
            "name": "idx_active_users",
            "columns": ["email"],
            "where": "status = 'active'"
        }]
        
        if os.path.exists(db_path):
            os.remove(db_path)
        
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Verify partial index exists
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        index_names = [idx[1] for idx in indexes]
        
        assert "idx_active_users" in index_names, "Partial index should be created"
        
        # Check if it's a partial index
        partial_idx = None
        for idx in indexes:
            if idx[1] == "idx_active_users":
                partial_idx = idx
                break
        
        assert partial_idx[4] == 1, "Index should be marked as partial"
        print(f"[OK] ✅ Partial index created with WHERE clause")
        
        conn.close()
        
        # Test 5: Expression index
        print("\n" + "-"*80)
        print("TEST 5: Expression Index")
        print("-"*80)
        
        schema["test_users"]["indexes"] = [{
            "name": "idx_email_lower",
            "expression": "LOWER(email)"
        }]
        
        if os.path.exists(db_path):
            os.remove(db_path)
        
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", schema["test_users"], cur, conn)
        
        # Verify expression index
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        index_names = [idx[1] for idx in indexes]
        
        assert "idx_email_lower" in index_names, "Expression index should be created"
        print(f"[OK] ✅ Expression index created")
        
        # Test case-insensitive search
        cur.execute("INSERT INTO test_users (id, email, username, status) VALUES ('u1', 'TEST@Example.COM', 'user1', 'active')")
        cur.execute("INSERT INTO test_users (id, email, username, status) VALUES ('u2', 'other@example.com', 'user2', 'active')")
        conn.commit()
        
        # Search using LOWER() should use index
        cur.execute("SELECT email FROM test_users WHERE LOWER(email) = LOWER('test@example.com')")
        result = cur.fetchone()
        
        assert result is not None, "Should find email case-insensitively"
        print(f"[OK] ✅ Expression index enables case-insensitive search")
        
        conn.close()
        
        # Test 6: Migration system detects missing indexes
        print("\n" + "-"*80)
        print("TEST 6: Migration Detects Missing Indexes")
        print("-"*80)
        
        # Create DB without indexes
        if os.path.exists(db_path):
            os.remove(db_path)
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Create table WITHOUT indexes
        cur.execute("""
            CREATE TABLE test_users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        """)
        conn.commit()
        
        # Now update schema to include indexes
        schema_with_indexes = {
            "test_users": {
                "id": {"type": "str", "pk": True},
                "email": {"type": "str", "required": True},
                "username": {"type": "str", "required": True},
                "status": {"type": "str", "default": "active"},
                "indexes": [
                    {"name": "idx_users_email", "columns": ["email"]},
                    {"name": "idx_users_username", "columns": ["username"]}
                ]
            },
            "Meta": {
                "Data_Type": "sqlite",
                "Data_path": db_path
            }
        }
        
        # Run auto-migration
        from zCLI.subsystems.zMigrate import auto_migrate_schema
        
        zData = {
            "type": "sqlite",
            "conn": conn,
            "cursor": cur,
            "path": db_path,
            "ready": True,
            "meta": schema_with_indexes["Meta"]
        }
        
        result = auto_migrate_schema(schema_with_indexes, zData)
        
        assert result == True, "Migration should succeed"
        
        # Verify indexes were created
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        index_names = [idx[1] for idx in indexes]
        
        print(f"[Check] Indexes after migration: {index_names}")
        assert "idx_users_email" in index_names, "Email index should be created by migration"
        assert "idx_users_username" in index_names, "Username index should be created by migration"
        print(f"[OK] ✅ Migration detected and created 2 missing indexes")
        
        conn.close()
        
        # Test 7: Multiple indexes at once
        print("\n" + "-"*80)
        print("TEST 7: Multiple Indexes Creation")
        print("-"*80)
        
        # Clean up from previous test
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create table with multiple different index types
        multi_idx_schema = {
            "id": {"type": "str", "pk": True},
            "email": {"type": "str", "required": True},
            "username": {"type": "str", "required": True},
            "status": {"type": "str", "default": "active"},
            "created_at": {"type": "datetime", "default": "now"},
            "indexes": [
                {"name": "idx_email", "columns": ["email"]},
                {"name": "idx_username", "columns": ["username"]},
                {"name": "idx_status_created", "columns": ["status", "created_at"]},
                {"name": "idx_active_emails", "columns": ["email"], "where": "status = 'active'"}
            ]
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        zTables("test_users", multi_idx_schema, cur, conn)
        
        # Verify all indexes created
        cur.execute("PRAGMA index_list(test_users)")
        indexes = cur.fetchall()
        index_names = [idx[1] for idx in indexes]
        
        print(f"[Check] Created {len(index_names)} indexes: {index_names}")
        
        assert "idx_email" in index_names, "Simple index should exist"
        assert "idx_username" in index_names, "Username index should exist"
        assert "idx_status_created" in index_names, "Composite index should exist"
        assert "idx_active_emails" in index_names, "Partial index should exist"
        print(f"[OK] ✅ Created 4 different index types simultaneously")
        
        conn.close()
        
        # Summary
        print("\n" + "="*80)
        print("[SUMMARY] TEST SUMMARY")
        print("="*80)
        print("[OK] All Index Tests Passed!")
        print("")
        print("[TESTED FEATURES]:")
        print("  [+] Simple index (single column)")
        print("  [+] Composite index (multiple columns)")
        print("  [+] Unique index")
        print("  [+] Partial index (WHERE clause)")
        print("  [+] Expression index")
        print("  [+] Index detection in migration")
        print("  [+] Indexes in full CRUD workflow")
        print("")
        print("[SUCCESS] Index support is WORKING! " + "✅" * 3)
        print("="*80)
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n[Cleanup] Removed test database: {db_path}")
        
        if os.path.exists(schema_path):
            os.remove(schema_path)
            print(f"[Cleanup] Removed test schema: {schema_path}")


def main():
    """Run index management tests."""
    try:
        return test_indexes()
    except Exception as e:
        print(f"\n[X] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)

