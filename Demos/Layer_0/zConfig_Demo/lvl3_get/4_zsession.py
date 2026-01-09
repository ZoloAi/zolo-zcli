#!/usr/bin/env python3
"""Level 3: Get - Session State (Runtime Configuration)

Learn to read runtime session values created during zCLI initialization.
Session is ephemeral - it exists only in memory during your program's runtime.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl3_get/4_zsession.py

Key Discovery:
  - Access runtime session with z.session
  - Session stores runtime state (zSpark, zMode, zLogger, zTraceback, etc.)
  - Session is ephemeral (memory only, not persisted)
  - zSpark dictionary is stored in session for reference
  - Copy-paste any accessor line you need
"""

from zKernel import zKernel


def run_demo():
    print("\n" + "="*60)
    print("  YOUR SESSION STATE (RUNTIME)")
    print("="*60)

    # Consistent zSpark pattern
    zSpark = {
        "deployment": "Production",
        "title": "session-demo",
        "logger": "INFO",
        "logger_path": "./logs",
        "zTraceback": True,
    }
    z = zKernel(zSpark)

    # Get session dictionary (copy this pattern)
    session = z.session

    print("\n# SESSION IDENTITY:")
    print(f"  zS_id             : {session.get('zS_id')}")
    print(f"  title             : {session.get('title')}")

    print("\n# RUNTIME CONFIGURATION:")
    print(f"  zMode             : {session.get('zMode')}")
    print(f"  zSpace            : {session.get('zSpace')}")
    print(f"  zLogger           : {session.get('zLogger')}")
    print(f"  logger_path       : {session.get('logger_path')}")
    print(f"  zTraceback        : {session.get('zTraceback')}")

    print("\n# ZSPARK (AS PROVIDED):")
    zspark_stored = session.get('zSpark')
    if zspark_stored:
        for key, value in zspark_stored.items():
            print(f"  {key:18s}: {value}")
    else:
        print("  (No zSpark provided)")

    print("\n# ENVIRONMENT:")
    print(f"  virtual_env       : {session.get('virtual_env')}")
    print(f"  system_env        : {type(session.get('system_env')).__name__} (full env vars)")

    print("\n# CUSTOM VARIABLES (zVars):")
    zvars = session.get('zVars')
    if zvars:
        print(f"  zVars             : {zvars}")
    else:
        print("  zVars             : {} (empty)")

    print("\n# What you discovered:")
    print("  ✓ Session holds runtime state created during initialization")
    print("  ✓ Session is ephemeral (memory only, not persisted)")
    print("  ✓ zSpark values are stored in session for reference")
    print("  ✓ Session includes runtime identity (zS_id, title)")
    print("  ✓ Session tracks logger, deployment, and traceback settings")
    print("  ✓ Session provides access to system environment variables")
    print("  ✓ Copy-paste any accessor line you need")

    print("\n# Usage pattern:")
    print("  session = z.session              # Get session dictionary")
    print("  value = session.get('zMode')     # Get single value")


if __name__ == "__main__":
    run_demo()


