#!/usr/bin/env python3
"""RBAC Automated Test - No user interaction required (v1.5.4 Week 3.3)"""

from pathlib import Path
from zCLI import zCLI

def testzRBAC_enforcement():
    """Test RBAC enforcement without user interaction."""
    
    # Initialize zCLI
    z = zCLI({
        "zWorkspace": str(Path(__file__).parent),
        "zVaFile": "@.zUI.rbac_test",
        "zBlock": "zVaF",
        "zMode": "Terminal"
    })
    
    # Load the UI file
    ui_data = z.loader.handle("@.zUI.rbac_test")
    
    print("\n" + "="*60)
    print("RBAC Automated Test - Checking Parsed Data")
    print("="*60)
    
    # Check if zVaF block exists
    if "zVaF" in ui_data:
        print("\n✅ zVaF block loaded successfully")
        zblock = ui_data["zVaF"]
        
        # Check specific keys for zRBAC metadata
        test_cases = [
            ("^Login", None, "Should have no RBAC (public)"),
            ("^Public Info", None, "Should have no RBAC (public override)"),
            ("^View Dashboard", {"require_auth": True}, "Should require auth"),
            ("^Edit Settings", {"require_role": "user"}, "Should require 'user' role"),
            ("^Moderator Panel", {"require_role": ["admin", "moderator"]}, "Should require admin/moderator"),
            ("^Delete Data", {"require_role": "admin", "require_permission": "data.delete"}, "Should require admin + permission"),
        ]
        
        for key, expectedzRBAC, description in test_cases:
            if key in zblock:
                value = zblock[key]
                actualzRBAC = value.get("zRBAC") if isinstance(value, dict) else None
                
                if expectedzRBAC is None:
                    if actualzRBAC is None or (isinstance(actualzRBAC, dict) and actualzRBAC.get("require_role") is None):
                        print(f"\n✅ {key}: {description}")
                        print(f"   RBAC: {actualzRBAC}")
                    else:
                        print(f"\n❌ {key}: Expected no RBAC, got {actualzRBAC}")
                else:
                    if actualzRBAC:
                        matches = all(actualzRBAC.get(k) == v for k, v in expectedzRBAC.items())
                        if matches:
                            print(f"\n✅ {key}: {description}")
                            print(f"   RBAC: {actualzRBAC}")
                        else:
                            print(f"\n❌ {key}: RBAC mismatch")
                            print(f"   Expected: {expectedzRBAC}")
                            print(f"   Got: {actualzRBAC}")
                    else:
                        print(f"\n❌ {key}: Expected RBAC {expectedzRBAC}, got None")
            else:
                print(f"\n❌ {key}: Key not found in zblock")
        
        # Now test actual access control
        print("\n" + "="*60)
        print("Testing Access Control Logic")
        print("="*60)
        
        # Test 1: Anonymous user (not authenticated)
        z.session["zAuth"] = {}
        print("\n--- Test 1: Anonymous User ---")
        
        # Should deny access to ^View Dashboard
        if z.wizard._checkzRBAC_access("^View Dashboard", zblock.get("^View Dashboard")) == "access_denied":
            print("✅ ^View Dashboard: Correctly denied (requires auth)")
        else:
            print("❌ ^View Dashboard: Should have been denied!")
        
        # Test 2: User with 'user' role
        z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "user",
            "API_Key": "mock_token"
        }
        print("\n--- Test 2: User Role ---")
        
        # Should grant access to ^Edit Settings
        if z.wizard._checkzRBAC_access("^Edit Settings", zblock.get("^Edit Settings")) == "access_granted":
            print("✅ ^Edit Settings: Correctly granted (has 'user' role)")
        else:
            print("❌ ^Edit Settings: Should have been granted!")
        
        # Should deny access to ^Moderator Panel
        if z.wizard._checkzRBAC_access("^Moderator Panel", zblock.get("^Moderator Panel")) == "access_denied":
            print("✅ ^Moderator Panel: Correctly denied (needs admin/moderator)")
        else:
            print("❌ ^Moderator Panel: Should have been denied!")
        
        # Test 3: User with 'admin' role (no permissions)
        z.session["zAuth"] = {
            "id": "admin456",
            "username": "adminuser",
            "role": "admin",
            "API_Key": "mock_token"
        }
        print("\n--- Test 3: Admin Role (No Permissions) ---")
        
        # Should grant access to ^Moderator Panel
        if z.wizard._checkzRBAC_access("^Moderator Panel", zblock.get("^Moderator Panel")) == "access_granted":
            print("✅ ^Moderator Panel: Correctly granted (has 'admin' role)")
        else:
            print("❌ ^Moderator Panel: Should have been granted!")
        
        # Should deny access to ^Delete Data (needs permission)
        if z.wizard._checkzRBAC_access("^Delete Data", zblock.get("^Delete Data")) == "access_denied":
            print("✅ ^Delete Data: Correctly denied (needs data.delete permission)")
        else:
            print("❌ ^Delete Data: Should have been denied!")
        
        print("\n" + "="*60)
        print("RBAC Test Complete!")
        print("="*60 + "\n")
    else:
        print("\n❌ Failed to load zVaF block")

if __name__ == "__main__":
    testzRBAC_enforcement()

