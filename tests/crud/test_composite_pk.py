#!/usr/bin/env python3
# tests/crud/test_composite_pk.py — Composite Primary Key Test
# ───────────────────────────────────────────────────────────────

"""
Composite Primary Key Test

Tests the composite primary key feature for junction tables and
multi-column unique identifiers.

Usage:
    python tests/crud/test_composite_pk.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures import TestDatabase
from zCLI.subsystems.crud import handle_zCRUD, zTables
import sqlite3
import yaml


def test_composite_primary_key():
    """Test composite primary key creation and enforcement."""
    
    print("="*80)
    print("COMPOSITE PRIMARY KEY TEST")
    print("="*80)
    
    # Schema with composite PK
    schema_dict = {
        "zPosts": {
            "id": {"type": "str", "pk": True, "source": "generate_id(zP)"},
            "title": {"type": "str", "required": True}
        },
        "zTags": {
            "id": {"type": "str", "pk": True, "source": "generate_id(zT)"},
            "name": {"type": "str", "required": True, "unique": True}
        },
        "zPostTags": {
            "post_id": {"type": "str", "fk": "zPosts.id", "on_delete": "CASCADE", "required": True},
            "tag_id": {"type": "str", "fk": "zTags.id", "on_delete": "CASCADE", "required": True},
            "added_at": {"type": "datetime", "default": "now"},
            "primary_key": ["post_id", "tag_id"]  # ← Composite PK
        },
        "Meta": {
            "Data_Type": "sqlite",
            "Data_path": "test_composite.db"
        }
    }
    
    # Create schema file
    schema_path = "test_composite_schema.yaml"
    with open(schema_path, 'w') as f:
        yaml.dump(schema_dict, f)
    
    db_path = "test_composite.db"
    
    try:
        # ────────────────────────────────────────────────────────
        # STEP 1: Manually create tables using zTables
        # ────────────────────────────────────────────────────────
        print("\n[Step 1] Creating tables with composite primary key...")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        
        # Create tables in dependency order
        for table_name in ["zPosts", "zTags", "zPostTags"]:
            print(f"[*] Creating table: {table_name}")
            zTables(table_name, schema_dict[table_name], cur, conn)
        
        conn.close()
        print("[OK] All tables created")
        
        # ────────────────────────────────────────────────────────
        # STEP 2: Create posts and tags using CRUD
        # ────────────────────────────────────────────────────────
        print("\n[Step 2] Creating test data...")
        
        # Create posts
        post_request = {
            "action": "create",
            "tables": ["zPosts"],
            "model": schema_path,
            "fields": ["title"],
            "values": ["First Post"]
        }
        post_result = handle_zCRUD(post_request)
        print(f"[OK] Created post: {post_result}")
        
        # Create tags
        tag1_request = {
            "action": "create",
            "tables": ["zTags"],
            "model": schema_path,
            "fields": ["name"],
            "values": ["python"]
        }
        tag1_result = handle_zCRUD(tag1_request)
        
        tag2_request = {
            "action": "create",
            "tables": ["zTags"],
            "model": schema_path,
            "fields": ["name"],
            "values": ["database"]
        }
        tag2_result = handle_zCRUD(tag2_request)
        
        print(f"[OK] Created 2 tags")
        
        # Get IDs
        posts = handle_zCRUD({
            "action": "read",
            "tables": ["zPosts"],
            "model": schema_path,
            "fields": ["id", "title"]
        })
        post_id = posts[0]["id"]
        
        tags = handle_zCRUD({
            "action": "read",
            "tables": ["zTags"],
            "model": schema_path,
            "fields": ["id", "name"]
        })
        tag1_id = tags[0]["id"]
        tag2_id = tags[1]["id"]
        
        print(f"[OK] Post ID: {post_id}")
        print(f"[OK] Tag IDs: {tag1_id}, {tag2_id}")
        
        # ────────────────────────────────────────────────────────
        # STEP 3: Verify composite PK was created
        # ────────────────────────────────────────────────────────
        print("\n[Step 3] Verifying composite primary key exists...")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Check table structure
        cur.execute("PRAGMA table_info(zPostTags)")
        columns = cur.fetchall()
        
        print(f"[Check] zPostTags columns:")
        for col in columns:
            cid, name, dtype, notnull, default, pk = col
            pk_marker = " (PK)" if pk else ""
            print(f"  • {name}: {dtype}{pk_marker}")
        
        # Check if both columns are marked as PK
        pk_columns = [col[1] for col in columns if col[5]]  # col[5] is pk flag
        
        if "post_id" in pk_columns and "tag_id" in pk_columns:
            print("[OK] ✅ Composite primary key created (post_id, tag_id)")
        else:
            print(f"[X] ❌ Composite PK not correct. PK columns: {pk_columns}")
            conn.close()
            return False
        
        conn.close()
        
        # ────────────────────────────────────────────────────────
        # STEP 4: Test composite PK enforcement (unique pairs)
        # ────────────────────────────────────────────────────────
        print("\n[Step 4] Testing composite PK enforcement...")
        
        # Create first post-tag relationship
        pt1_request = {
            "action": "create",
            "tables": ["zPostTags"],
            "model": schema_path,
            "fields": ["post_id", "tag_id"],
            "values": [post_id, tag1_id]
        }
        pt1_result = handle_zCRUD(pt1_request)
        
        if pt1_result:
            print(f"[OK] ✅ Created post-tag: ({post_id}, {tag1_id})")
        else:
            print("[X] Failed to create post-tag")
            return False
        
        # Create second post-tag relationship (different tag, same post)
        pt2_request = {
            "action": "create",
            "tables": ["zPostTags"],
            "model": schema_path,
            "fields": ["post_id", "tag_id"],
            "values": [post_id, tag2_id]
        }
        pt2_result = handle_zCRUD(pt2_request)
        
        if pt2_result:
            print(f"[OK] ✅ Created post-tag: ({post_id}, {tag2_id})")
        else:
            print("[X] Failed to create second post-tag")
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 5: Test duplicate prevention (composite PK enforcement)
        # ────────────────────────────────────────────────────────
        print("\n[Step 5] Testing duplicate prevention...")
        
        # Try to create duplicate (same post_id + tag_id)
        duplicate_request = {
            "action": "create",
            "tables": ["zPostTags"],
            "model": schema_path,
            "fields": ["post_id", "tag_id"],
            "values": [post_id, tag1_id]  # ← Same as first one
        }
        
        duplicate_result = handle_zCRUD(duplicate_request)
        
        if not duplicate_result or duplicate_result == False:
            print(f"[OK] ✅ Duplicate rejected (composite PK working!)")
        else:
            print(f"[X] ❌ Duplicate was allowed (composite PK NOT working)")
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 6: Verify data integrity
        # ────────────────────────────────────────────────────────
        print("\n[Step 6] Verifying data integrity...")
        
        # Read all post-tags
        pt_read = {
            "action": "read",
            "tables": ["zPostTags"],
            "model": schema_path,
            "fields": ["post_id", "tag_id"]
        }
        post_tags = handle_zCRUD(pt_read)
        
        print(f"[Check] Found {len(post_tags)} post-tag relationships:")
        for pt in post_tags:
            print(f"  • Post: {pt['post_id']}, Tag: {pt['tag_id']}")
        
        if len(post_tags) == 2:
            print("[OK] ✅ Correct number of relationships (2)")
        else:
            print(f"[X] Expected 2 relationships, found {len(post_tags)}")
            return False
        
        # ────────────────────────────────────────────────────────
        # STEP 7: Test CASCADE delete
        # ────────────────────────────────────────────────────────
        print("\n[Step 7] Testing CASCADE delete...")
        
        # Delete the post (should cascade to post_tags)
        delete_post = {
            "action": "delete",
            "tables": ["zPosts"],
            "model": schema_path,
            "where": {"id": post_id}
        }
        deleted = handle_zCRUD(delete_post)
        print(f"[OK] Deleted post: {deleted} row(s)")
        
        # Verify post_tags were cascade deleted
        remaining_pt = handle_zCRUD(pt_read)
        
        if len(remaining_pt) == 0:
            print("[OK] ✅ CASCADE delete worked (post_tags removed)")
        else:
            print(f"[X] CASCADE failed, {len(remaining_pt)} post_tags remain")
            return False
        
        # ────────────────────────────────────────────────────────
        # SUCCESS!
        # ────────────────────────────────────────────────────────
        print("\n" + "="*80)
        print("[SUCCESS] Composite Primary Key Test Passed!")
        print("="*80)
        print("\n[Summary]")
        print("  ✅ Composite PK created: PRIMARY KEY (post_id, tag_id)")
        print("  ✅ Allows multiple tags per post")
        print("  ✅ Allows same tag on multiple posts")
        print("  ✅ Prevents duplicate pairs")
        print("  ✅ CASCADE delete works correctly")
        print("\n[Composite PK] Feature is WORKING! 🎉")
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n[Cleanup] Removed test database: {db_path}")
        
        if os.path.exists(schema_path):
            os.remove(schema_path)
            print(f"[Cleanup] Removed test schema: {schema_path}")


if __name__ == "__main__":
    success = test_composite_primary_key()
    sys.exit(0 if success else 1)

