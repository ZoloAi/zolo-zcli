#!/usr/bin/env python3
# tests/crud/test_csv_adapter.py — CSV Adapter Test Suite
# ───────────────────────────────────────────────────────────────

"""
CSV Adapter Test Suite

Tests all CRUD operations with CSV backend using pandas.

Usage:
    python tests/crud/test_csv_adapter.py
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zCLI.subsystems.zData import zData


def test_csv_adapter():
    """Test CSV adapter with all CRUD operations."""
    
    print("\n" + "="*80)
    print("CSV ADAPTER TEST SUITE")
    print("="*80)
    
    # Create temp directory for CSV files
    temp_dir = tempfile.mkdtemp()
    print(f"\n📁 Test directory: {temp_dir}")
    
    try:
        # Test schema with CSV backend
        schema = {
            'Meta': {
                'Data_Type': 'csv',
                'Data_path': temp_dir
            },
            'users': {
                'id': {'type': 'int', 'pk': True},
                'name': {'type': 'str', 'required': True},
                'email': {'type': 'str'},
                'age': {'type': 'int'}
            },
            'products': {
                'id': {'type': 'int', 'pk': True},
                'name': {'type': 'str'},
                'price': {'type': 'float'},
                'stock': {'type': 'int'}
            }
        }
        
        # ═══════════════════════════════════════════════════════════
        # TEST 1: Initialization
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 1: CSV Adapter Initialization")
        print("-"*80)
        
        zdata = zData(schema=schema)
        assert zdata.is_connected(), "Should be connected"
        print("✅ CSV adapter initialized")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 2: Table Creation
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 2: Table Creation")
        print("-"*80)
        
        result = zdata.ensure_tables()
        assert result, "Tables should be created"
        
        # Verify CSV files exist
        users_csv = Path(temp_dir) / "users.csv"
        products_csv = Path(temp_dir) / "products.csv"
        assert users_csv.exists(), "users.csv should exist"
        assert products_csv.exists(), "products.csv should exist"
        print("✅ Tables created (CSV files)")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 3: INSERT Operations
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 3: INSERT Operations")
        print("-"*80)
        
        id1 = zdata.insert('users', ['name', 'email', 'age'], ['Alice', 'alice@example.com', 30])
        id2 = zdata.insert('users', ['name', 'email', 'age'], ['Bob', 'bob@example.com', 25])
        id3 = zdata.insert('users', ['name', 'email', 'age'], ['Charlie', 'charlie@example.com', 35])
        
        assert id1 > 0, "Should return row ID"
        assert id2 > id1, "IDs should increment"
        assert id3 > id2, "IDs should increment"
        print(f"✅ Inserted 3 rows (IDs: {id1}, {id2}, {id3})")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 4: SELECT Operations
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 4: SELECT Operations")
        print("-"*80)
        
        rows = zdata.select('users')
        assert len(rows) == 3, f"Should have 3 rows, got {len(rows)}"
        print(f"✅ SELECT: Found {len(rows)} rows")
        
        # SELECT with specific fields
        rows = zdata.select('users', fields=['name', 'email'])
        assert len(rows) == 3, "Should still have 3 rows"
        assert 'name' in rows[0], "Should have name field"
        assert 'email' in rows[0], "Should have email field"
        print("✅ SELECT with field selection works")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 5: WHERE Clause Filtering
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 5: WHERE Clause Filtering")
        print("-"*80)
        
        # Simple equality
        rows = zdata.select('users', where={'name': 'Alice'})
        assert len(rows) == 1, "Should find 1 row"
        assert rows[0]['name'] == 'Alice', "Should be Alice"
        print("✅ WHERE with equality")
        
        # Greater than
        rows = zdata.select('users', where={'age': {'$gt': 28}})
        assert len(rows) == 2, f"Should find 2 rows, got {len(rows)}"
        print("✅ WHERE with $gt operator")
        
        # Less than
        rows = zdata.select('users', where={'age': {'$lt': 30}})
        assert len(rows) == 1, "Should find 1 row (Bob)"
        print("✅ WHERE with $lt operator")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 6: UPDATE Operations
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 6: UPDATE Operations")
        print("-"*80)
        
        count = zdata.update('users', ['email'], ['alice.updated@example.com'], where={'name': 'Alice'})
        assert count == 1, f"Should update 1 row, updated {count}"
        
        # Verify update
        rows = zdata.select('users', where={'name': 'Alice'})
        assert rows[0]['email'] == 'alice.updated@example.com', "Email should be updated"
        print("✅ UPDATE operation successful")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 7: DELETE Operations
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 7: DELETE Operations")
        print("-"*80)
        
        count = zdata.delete('users', where={'name': 'Bob'})
        assert count == 1, f"Should delete 1 row, deleted {count}"
        
        # Verify deletion
        rows = zdata.select('users')
        assert len(rows) == 2, f"Should have 2 rows left, got {len(rows)}"
        assert all(row['name'] != 'Bob' for row in rows), "Bob should be deleted"
        print("✅ DELETE operation successful")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 8: UPSERT Operations
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 8: UPSERT Operations")
        print("-"*80)
        
        # Upsert existing (update)
        id_update = zdata.upsert('users', ['name', 'email', 'age'], 
                                 ['Alice', 'alice.upsert@example.com', 31], ['name'])
        assert id_update > 0, "Should return ID"
        
        rows = zdata.select('users', where={'name': 'Alice'})
        assert rows[0]['email'] == 'alice.upsert@example.com', "Email should be updated"
        assert rows[0]['age'] == 31, "Age should be updated"
        print("✅ UPSERT (update existing) successful")
        
        # Upsert new (insert)
        id_insert = zdata.upsert('users', ['name', 'email', 'age'], 
                                 ['Diana', 'diana@example.com', 28], ['name'])
        assert id_insert > 0, "Should return ID"
        
        rows = zdata.select('users')
        assert len(rows) == 3, f"Should have 3 rows, got {len(rows)}"
        assert any(row['name'] == 'Diana' for row in rows), "Diana should be inserted"
        print("✅ UPSERT (insert new) successful")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 9: ORDER BY
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 9: ORDER BY Operations")
        print("-"*80)
        
        # Order by age ascending
        rows = zdata.select('users', order={'age': 'ASC'})
        ages = [row['age'] for row in rows]
        assert ages == sorted(ages), "Should be sorted ascending"
        print("✅ ORDER BY ASC works")
        
        # Order by age descending
        rows = zdata.select('users', order={'age': 'DESC'})
        ages = [row['age'] for row in rows]
        assert ages == sorted(ages, reverse=True), "Should be sorted descending"
        print("✅ ORDER BY DESC works")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 10: LIMIT
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 10: LIMIT Operations")
        print("-"*80)
        
        rows = zdata.select('users', limit=2)
        assert len(rows) == 2, f"Should return 2 rows, got {len(rows)}"
        print("✅ LIMIT works")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 11: RGB Columns
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 11: RGB Weak Nuclear Force Columns")
        print("-"*80)
        
        rows = zdata.select('users')
        for row in rows:
            assert 'weak_force_r' in row, "Should have weak_force_r column"
            assert 'weak_force_g' in row, "Should have weak_force_g column"
            assert 'weak_force_b' in row, "Should have weak_force_b column"
        print("✅ RGB columns present in all rows")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 12: Multiple Tables
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 12: Multiple Tables")
        print("-"*80)
        
        zdata.insert('products', ['name', 'price', 'stock'], ['Widget', 19.99, 100])
        zdata.insert('products', ['name', 'price', 'stock'], ['Gadget', 29.99, 50])
        
        rows = zdata.select('products')
        assert len(rows) == 2, f"Should have 2 products, got {len(rows)}"
        print("✅ Multiple tables work independently")
        
        # ═══════════════════════════════════════════════════════════
        # TEST 13: List Tables
        # ═══════════════════════════════════════════════════════════
        print("\n" + "-"*80)
        print("TEST 13: List Tables")
        print("-"*80)
        
        tables = zdata.list_tables()
        assert 'users' in tables, "Should list users table"
        assert 'products' in tables, "Should list products table"
        assert len(tables) == 2, f"Should have 2 tables, got {len(tables)}"
        print(f"✅ List tables: {tables}")
        
        # ═══════════════════════════════════════════════════════════
        # Cleanup
        # ═══════════════════════════════════════════════════════════
        zdata.disconnect()
        print("\n✅ Disconnected from CSV backend")
        
        print("\n" + "="*80)
        print("CSV ADAPTER TEST RESULTS")
        print("="*80)
        print("✅ All 13 tests passed!")
        print("🎉 CSV adapter fully functional!")
        print("="*80)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temp directory: {temp_dir}")


def main():
    """Main entry point for test runner."""
    success = test_csv_adapter()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
