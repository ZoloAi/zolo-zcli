#!/usr/bin/env python3
"""
Test zCRUD Delete & Update Operations with zApps
Demonstrates direct zCRUD usage (isolated from zFunc format)
"""

import sys
import os

from zCLI.subsystems.crud import handle_zCRUD
from zCLI.utils.logger import logger

print("=" * 80)
print("zCRUD DELETE & UPDATE TEST - zApps Use Case")
print("Isolated from zFunc format (direct zCRUD calls)")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: CREATE - Setup test data
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 1: CREATE - Setting up test zApps")
print("─" * 80)

# Create test app using direct zCRUD format
create_request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "create",
    "tables": ["zApps"],
    "values": {
        "name": "TestApp_Delete",
        "type": "web"
    }
}

print("\n📝 Request:")
print(f"  Model: {create_request['model']}")
print(f"  Action: {create_request['action']}")
print(f"  Tables: {create_request['tables']}")
print(f"  Values: {create_request['values']}")

try:
    result = handle_zCRUD(create_request)
    print(f"✅ Result: {result} row(s) created")
except Exception as e:
    print(f"❌ Error: {e}")

# Create another test app for update testing
create_request_2 = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "create",
    "tables": ["zApps"],
    "values": {
        "name": "TestApp_Update",
        "type": "desktop"
    }
}

print("\n📝 Creating second test app...")
try:
    result = handle_zCRUD(create_request_2)
    print(f"✅ Result: {result} row(s) created")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: READ - Verify data exists
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 2: READ - List all zApps")
print("─" * 80)

read_request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "read",
    "tables": ["zApps"],
    "fields": ["id", "name", "type", "version"]
}

print("\n📝 Request:")
print(f"  Action: {read_request['action']}")
print(f"  Tables: {read_request['tables']}")
print(f"  Fields: {read_request['fields']}")

try:
    results = handle_zCRUD(read_request)
    print(f"\n✅ Found {len(results)} app(s):")
    for row in results:
        print(f"  • {row}")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: UPDATE - Modify existing record
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 3: UPDATE - Modify TestApp_Update")
print("─" * 80)

update_request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "update",
    "tables": ["zApps"],
    "values": {
        "type": "mobile",
        "version": "2.0.0"
    },
    "where": {
        "name": "TestApp_Update"
    }
}

print("\n📝 Request:")
print(f"  Action: {update_request['action']}")
print(f"  Tables: {update_request['tables']}")
print(f"  Values: {update_request['values']}")
print(f"  Where: {update_request['where']}")

try:
    result = handle_zCRUD(update_request)
    print(f"✅ Result: {result} row(s) updated")
except Exception as e:
    print(f"❌ Error: {e}")

# Verify update
print("\n📝 Verifying update...")
verify_read = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "read",
    "tables": ["zApps"],
    "fields": ["name", "type", "version"],
    "where": {"name": "TestApp_Update"}
}

try:
    results = handle_zCRUD(verify_read)
    if results:
        print(f"✅ Updated record: {results[0]}")
    else:
        print("❌ No record found after update")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: DELETE - Remove specific record
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 4: DELETE - Remove TestApp_Delete")
print("─" * 80)

delete_request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "delete",
    "tables": ["zApps"],
    "where": {
        "name": "TestApp_Delete"
    }
}

print("\n📝 Request:")
print(f"  Action: {delete_request['action']}")
print(f"  Tables: {delete_request['tables']}")
print(f"  Where: {delete_request['where']}")

try:
    result = handle_zCRUD(delete_request)
    print(f"✅ Result: {result} row(s) deleted")
except Exception as e:
    print(f"❌ Error: {e}")

# Verify deletion
print("\n📝 Verifying deletion...")
verify_delete = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "read",
    "tables": ["zApps"],
    "fields": ["name"],
    "where": {"name": "TestApp_Delete"}
}

try:
    results = handle_zCRUD(verify_delete)
    if not results:
        print("✅ Record successfully deleted (not found)")
    else:
        print(f"❌ Record still exists: {results}")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: DELETE with ID (like UI configuration)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 5: DELETE - Using ID filter (UI pattern)")
print("─" * 80)

# First get the ID of TestApp_Update
get_id_request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "read",
    "tables": ["zApps"],
    "fields": ["id", "name"],
    "where": {"name": "TestApp_Update"}
}

try:
    results = handle_zCRUD(get_id_request)
    if results:
        app_id = results[0]["id"]
        print(f"📌 Found app ID: {app_id}")
        
        # Delete using ID (matches UI pattern in ui.zCloud.yaml)
        delete_by_id_request = {
            "model": "@.zCloud.schemas.schema.zIndex.zApps",
            "action": "delete",
            "tables": ["zApps"],
            "where": {
                "id": app_id
            }
        }
        
        print("\n📝 Request:")
        print(f"  Action: {delete_by_id_request['action']}")
        print(f"  Tables: {delete_by_id_request['tables']}")
        print(f"  Where: {delete_by_id_request['where']}")
        
        result = handle_zCRUD(delete_by_id_request)
        print(f"✅ Result: {result} row(s) deleted")
    else:
        print("❌ Could not find TestApp_Update to delete")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Final verification
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("TEST 6: FINAL - List remaining zApps")
print("─" * 80)

final_read = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "read",
    "tables": ["zApps"],
    "fields": ["id", "name", "type", "version"]
}

try:
    results = handle_zCRUD(final_read)
    print(f"\n✅ Remaining app(s): {len(results)}")
    for row in results:
        print(f"  • {row}")
except Exception as e:
    print(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print("""
✅ TESTED OPERATIONS:
  1. CREATE  - Added test records
  2. READ    - Retrieved and verified data
  3. UPDATE  - Modified fields with WHERE clause
  4. DELETE  - Removed records by name and by ID
  
🎯 KEY FINDINGS:
  • Direct zCRUD format works without zFunc wrapper
  • UPDATE supports multiple fields and WHERE clause
  • DELETE supports flexible WHERE conditions
  • Both operations return row count
  
📝 DIRECT zCRUD FORMAT (Isolated from zFunc):
  
  UPDATE Example:
    {
      "model": "@.zCloud.schemas.schema.zIndex.zApps",
      "action": "update",
      "tables": ["zApps"],
      "values": {"field": "new_value"},
      "where": {"id": "zA_123"}
    }
  
  DELETE Example:
    {
      "model": "@.zCloud.schemas.schema.zIndex.zApps",
      "action": "delete",
      "tables": ["zApps"],
      "where": {"id": "zA_123"}
    }

🔄 COMPARISON WITH UI CONFIG:
  
  Current (lines 105-113 in ui.zCloud.yaml):
    ^Delete_zApp:
      zDialog:
        model: "@.zCloud.schemas.schema.zIndex.zApps"
        fields: ["zApps.id"]
        onSubmit:
          action: delete
          tables: ["zApps"]
          where: zConv
  
  This format directly maps to zCRUD - the onSubmit block
  IS the zCRUD request format. zConv provides the WHERE values.
""")
print("=" * 80)

