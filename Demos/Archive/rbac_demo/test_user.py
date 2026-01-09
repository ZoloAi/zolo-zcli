#!/usr/bin/env python3
"""RBAC Test - User role (v1.5.4 Week 3.3)"""

from pathlib import Path
from zKernel import zKernel

z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.rbac_test",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

# Simulate logged in user with "user" role
z.session["zAuth"] = {
    "id": "user123",
    "username": "test_user",
    "role": "user",
    "API_Key": "token_abc"
}

print("\n" + "="*60)
print("RBAC Test - User Role")
print("="*60)
print("\nCurrent user: test_user (role: user)")
print("\nExpected behavior:")
print("  ✓ Login - accessible")
print("  ✓ Public Info - accessible")
print("  ✓ View Dashboard - accessible (authenticated)")
print("  ✓ Edit Settings - accessible (user role)")
print("  ✗ Moderator Panel - ACCESS DENIED (needs admin/moderator)")
print("  ✗ Delete Data - ACCESS DENIED (needs admin + permission)")
print("  ✗ Admin Only - ACCESS DENIED (needs admin + permission)")
print("\n" + "="*60 + "\n")

z.walker.run()

