#!/usr/bin/env python3
"""RBAC Test - Anonymous user (v1.5.4 Week 3.3)"""

from pathlib import Path
from zCLI import zCLI

# Test as anonymous user (not logged in)
z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.rbac_test",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

print("\n" + "="*60)
print("RBAC Test - Anonymous User (Not Logged In)")
print("="*60)
print("\nExpected behavior:")
print("  ✓ Login - accessible")
print("  ✓ Public Info - accessible")
print("  ✗ View Dashboard - ACCESS DENIED (needs auth)")
print("  ✗ Edit Settings - ACCESS DENIED (needs user role)")
print("  ✗ Moderator Panel - ACCESS DENIED (needs admin/moderator)")
print("  ✗ Delete Data - ACCESS DENIED (needs admin + permission)")
print("  ✗ Admin Only - ACCESS DENIED (needs admin + permission)")
print("\n" + "="*60 + "\n")

z.walker.run()

