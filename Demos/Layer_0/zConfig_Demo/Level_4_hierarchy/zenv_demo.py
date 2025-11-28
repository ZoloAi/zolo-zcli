#!/usr/bin/env python3
"""
Level 3a: Read Workspace Secrets from .zEnv
============================================

Goal:
    Show how zConfig automatically loads .zEnv files from your workspace.
    No python-dotenv needed - it's built in!

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_demo.py

What This Shows:
    - zConfig looks for .zEnv (or .env) in your workspace
    - Values are loaded automatically on initialization
    - Access via z.config.environment.get_env_var()

Key Point:
    Layer 4 of the hierarchy - workspace-specific secrets that travel
    with your project, not stored in system config files.
"""

from zCLI import zCLI

# Initialize zCLI - automatically loads .zEnv from workspace
z = zCLI({"logger": "PROD"})  # Clean console output

print("\n# Reading from .zEnv (workspace secrets):\n")

# Read values that were auto-loaded from .zEnv
threshold = z.config.environment.get_env_var("APP_THRESHOLD")
region = z.config.environment.get_env_var("APP_REGION")
report_name = z.config.environment.get_env_var("APP_REPORT_NAME")

print(f"APP_THRESHOLD   : {threshold}")
print(f"APP_REGION      : {region}")
print(f"APP_REPORT_NAME : {report_name}")

print("\n# How it works:")
print("  1. zConfig detects workspace root on init")
print("  2. Looks for .zEnv or .env file")
print("  3. Loads variables into environment")
print("  4. Access via get_env_var()")
print("\n# No python-dotenv import needed!")

