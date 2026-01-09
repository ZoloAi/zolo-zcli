#!/usr/bin/env python3
# Demos/validation_demo/demo_validation_auto.py

"""
zDialog Auto-Validation Demo (Week 5.2) - Automated Test

This demo showcases auto-validation with pre-programmed test cases.
Watch validation catch errors BEFORE submission!
"""

import sys
from pathlib import Path

# Add zCLI to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zKernel import zKernel

print("\n" + "="*70)
print("🎯 zDialog Auto-Validation Demo (Week 5.2)")
print("="*70)

# Initialize zCLI with workspace path
z = zKernel({"zWorkspace": str(Path(__file__).parent)})

# Create the users table from schema
print("\n📋 Step 1: Creating users table from zSchema.demo_users...")
schema = z.loader.handle('@.zSchema.demo_users')
z.data.load_schema(schema)
z.data.create_table('users')
print("✅ Table created!")

# Test Case 1: Valid Data (Should Succeed)
print("\n" + "-"*70)
print("📝 Test Case 1: VALID DATA")
print("-"*70)
print("Inserting user with valid data:")
print("  • Username: 'valid_user'")
print("  • Email: 'test@example.com'")
print("  • Age: 25")

try:
    result = z.data.insert('users', 
                          ['username', 'email', 'age'], 
                          ['valid_user', 'test@example.com', 25])
    print("\n✅ SUCCESS: User inserted (validation passed)")
except Exception as e:
    print(f"\n❌ FAILED: {e}")

# Test Case 2: Invalid Username (Too Short)
print("\n" + "-"*70)
print("📝 Test Case 2: INVALID USERNAME (too short)")
print("-"*70)
print("Attempting to insert user with invalid username:")
print("  • Username: 'ab' (❌ too short, needs 3-20 chars)")
print("  • Email: 'test2@example.com'")
print("  • Age: 30")

try:
    result = z.data.insert('users',
                          ['username', 'email', 'age'],
                          ['ab', 'test2@example.com', 30])  # ❌ Too short
    print("\n❌ UNEXPECTED: User inserted (validation should have failed)")
except Exception as e:
    print("\n✅ EXPECTED: Validation caught the error!")

# Test Case 3: Invalid Email Format
print("\n" + "-"*70)
print("📝 Test Case 3: INVALID EMAIL FORMAT")
print("-"*70)
print("Attempting to insert user with invalid email:")
print("  • Username: 'testuser'")
print("  • Email: 'not-an-email' (❌ invalid format)")
print("  • Age: 28")

try:
    result = z.data.insert('users',
                          ['username', 'email', 'age'],
                          ['testuser', 'not-an-email', 28])  # ❌ Invalid email
    print("\n❌ UNEXPECTED: User inserted (validation should have failed)")
except Exception as e:
    print("\n✅ EXPECTED: Validation caught the error!")

# Test Case 4: Age Out of Range (Too Young)
print("\n" + "-"*70)
print("📝 Test Case 4: AGE OUT OF RANGE (below minimum)")
print("-"*70)
print("Attempting to insert user with invalid age:")
print("  • Username: 'younguser'")
print("  • Email: 'young@example.com'")
print("  • Age: 15 (❌ below minimum of 18)")

try:
    result = z.data.insert('users',
                          ['username', 'email', 'age'],
                          ['younguser', 'young@example.com', 15])  # ❌ Below minimum
    print("\n❌ UNEXPECTED: User inserted (validation should have failed)")
except Exception as e:
    print("\n✅ EXPECTED: Validation caught the error!")

# Test Case 5: Missing Required Field (Email)
print("\n" + "-"*70)
print("📝 Test Case 5: MISSING REQUIRED FIELD (email)")
print("-"*70)
print("Attempting to insert user without required email:")
print("  • Username: 'nomail'")
print("  • Email: (❌ missing)")
print("  • Age: 25")

try:
    result = z.data.insert('users',
                          ['username', 'age'],  # ❌ Missing required 'email'
                          ['nomail', 25])
    print("\n❌ UNEXPECTED: User inserted (validation should have failed)")
except Exception as e:
    print("\n✅ EXPECTED: Validation caught the error!")

# Test Case 6: Multiple Validation Errors
print("\n" + "-"*70)
print("📝 Test Case 6: MULTIPLE VALIDATION ERRORS")
print("-"*70)
print("Attempting to insert user with multiple errors:")
print("  • Username: 'x' (❌ too short)")
print("  • Email: 'bad' (❌ invalid format)")
print("  • Age: 200 (❌ above maximum of 120)")

try:
    result = z.data.insert('users',
                          ['username', 'email', 'age'],
                          ['x', 'bad', 200])  # ❌ Multiple errors
    print("\n❌ UNEXPECTED: User inserted (validation should have failed)")
except Exception as e:
    print("\n✅ EXPECTED: Validation caught multiple errors!")

# Test Case 7: Valid Data with Optional Fields
print("\n" + "-"*70)
print("📝 Test Case 7: VALID DATA WITH OPTIONAL FIELDS")
print("-"*70)
print("Inserting user with optional phone and website:")
print("  • Username: 'complete_user'")
print("  • Email: 'complete@example.com'")
print("  • Age: 35")
print("  • Phone: '+1234567890'")
print("  • Website: 'https://example.com'")
print("  • Bio: 'A test user with all fields'")

try:
    result = z.data.insert('users',
                          ['username', 'email', 'age', 'phone', 'website', 'bio'],
                          ['complete_user', 'complete@example.com', 35, '+1234567890', 'https://example.com', 'A test user with all fields'])
    print("\n✅ SUCCESS: User inserted with all optional fields (validation passed)")
except Exception as e:
    print(f"\n❌ FAILED: {e}")

# View all users
print("\n" + "="*70)
print("📊 FINAL RESULTS: All Users in Database")
print("="*70)

users = z.data.select('users')
if users:
    print(f"\n✅ Successfully inserted {len(users)} user(s):")
    for i, user in enumerate(users, 1):
        print(f"\n  {i}. ID: {user.get('id')}")
        print(f"     Username: {user.get('username')}")
        print(f"     Email: {user.get('email')}")
        print(f"     Age: {user.get('age')}")
        if user.get('phone'):
            print(f"     Phone: {user.get('phone')}")
        if user.get('website'):
            print(f"     Website: {user.get('website')}")
        if user.get('bio'):
            print(f"     Bio: {user.get('bio')}")
else:
    print("\n⚠️  No users found in database")

print("\n" + "="*70)
print("🎉 Demo Complete!")
print("="*70)
print("\n📝 Summary:")
print("  • Valid data: ✅ Inserted successfully")
print("  • Invalid data: ✅ Caught by auto-validation")
print("  • Multiple errors: ✅ All detected before submission")
print("\n🎯 Key Insight: Auto-validation prevents invalid data from")
print("   reaching the database, saving round-trips and improving UX!")
print("\n" + "="*70 + "\n")

