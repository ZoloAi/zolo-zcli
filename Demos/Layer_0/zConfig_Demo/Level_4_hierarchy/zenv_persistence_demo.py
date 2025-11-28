#!/usr/bin/env python3
"""
Level 3b: Read Persistent Environment Config
=============================================

Goal:
    Show how zConfig stores persistent environment settings in system config files.
    These values survive across projects and restarts.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_persistence_demo.py

What This Shows:
    - Layer 3: Environment Config (deployment context + custom fields)
    - Values persist system-wide (not workspace-specific like .zEnv)
    - Custom fields are built into the template - use them!

Key Point:
    This config lives in ~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml
    and is available to ALL your projects.
"""

from zCLI import zCLI

z = zCLI({"logger": "PROD"})  # Clean output

print("\n# Layer 3: Environment Config (persistent, deployment context)")
print("# Location: ~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml\n")

# Environment config - deployment context
deployment = z.config.get_environment("deployment")
role = z.config.get_environment("role")

print(f"deployment : {deployment}")
print(f"role       : {role}")

print("\n# Layer 3: Custom Fields (YOUR persistent values)")
print("# These are built into the template - use them for your app!\n")

# Custom fields - built into the default template
custom_1 = z.config.get_environment("custom_field_1")
custom_2 = z.config.get_environment("custom_field_2")
custom_3 = z.config.get_environment("custom_field_3")

print(f"custom_field_1 : {custom_1}")
print(f"custom_field_2 : {custom_2}")
print(f"custom_field_3 : {custom_3}")

print("\n# Why use persistent environment config?")
print("  ✓ Survives across ALL projects (not workspace-specific)")
print("  ✓ Edit once, use everywhere")
print("  ✓ Perfect for deployment settings, roles, defaults")
print("  ✓ Custom fields ready for YOUR app's persistent data")

print("\n# Custom fields are perfect for:")
print("  - Application defaults")
print("  - User preferences")
print("  - Feature flags")
print("  - API endpoints")
print("  - Any persistent data your app needs")

print("\n# To edit these values:")
print("  - Via zShell: 'config environment deployment Production'")
print("  - Via code: z.config.persistence.persist_environment('deployment', 'Production')")
print("  - Manually: Edit ~/Library/.../zConfig.environment.yaml")

