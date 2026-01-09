#!/usr/bin/env python3
# Demos/validation_demo/demo_validation.py

"""
zDialog Auto-Validation Demo (Week 5.2)

This demo showcases the automatic validation of form data against zSchema rules.
Forms with model: '@.zSchema.demo_users' will auto-validate before submission.

Features Demonstrated:
  ✅ Username pattern validation (3-20 chars, alphanumeric + underscore)
  ✅ Email format validation
  ✅ Age range validation (18-120)
  ✅ Phone format validation
  ✅ Website URL format validation
  ✅ Bio length validation (max 200 chars)
  
Try It:
  1. Run the demo: python3 demo_validation.py
  2. Choose "Add User (Invalid Data - See Errors)"
  3. Enter invalid data (e.g., username "ab", email "not-an-email")
  4. Watch auto-validation catch errors BEFORE submission! 🎯
"""

import sys
from pathlib import Path

# Add zCLI to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zKernel import zKernel

# Initialize zCLI with workspace path
z = zKernel({"zWorkspace": str(Path(__file__).parent)})

# Create the users table from schema
print("\n📋 Creating users table from zSchema.demo_users...")
z.data.load_schema('@.zSchema.demo_users')
z.data.create_table('users')
print("✅ Table created!")

# Start interactive walker
print("\n🚀 Starting validation demo...\n")
z.walker.start('@.zUI.validation_demo')

