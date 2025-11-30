#!/usr/bin/env python3
"""
Test Virtual Environment Detection
===================================

This test verifies that zCLI correctly detects:
1. Whether we're running in a virtual environment
2. The path to the virtual environment (if active)

Run:
    # Outside venv
    python3 Tests/test_venv_detection.py
    
    # Inside venv
    python3 -m venv test_venv
    source test_venv/bin/activate  # On Unix
    # test_venv\Scripts\activate  # On Windows
    python3 Tests/test_venv_detection.py
    deactivate
"""

from zCLI import zCLI
import sys


def test_venv_detection():
    """Test that zCLI correctly detects virtual environment status."""
    
    print("\n" + "="*60)
    print("  VIRTUAL ENVIRONMENT DETECTION TEST")
    print("="*60)
    
    # Initialize zCLI
    z = zCLI({"deployment": "Production", "logger": "INFO"})
    
    # Get session data
    session = z.session
    venv_path = session.get('virtual_env')
    
    # Also check the environment module directly
    is_in_venv = z.config.environment.is_in_venv()
    venv_from_env = z.config.environment.get_venv_path()
    
    print("\n# Python sys module checks:")
    print(f"  sys.prefix          : {sys.prefix}")
    print(f"  sys.base_prefix     : {sys.base_prefix}")
    print(f"  hasattr real_prefix : {hasattr(sys, 'real_prefix')}")
    print(f"  prefix != base      : {sys.prefix != sys.base_prefix}")
    
    print("\n# zCLI Environment detection:")
    print(f"  is_in_venv()        : {is_in_venv}")
    print(f"  get_venv_path()     : {venv_from_env}")
    
    print("\n# zSession values:")
    print(f"  virtual_env         : {venv_path}")
    
    # Determine expected result
    expected_in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    print("\n# Test Results:")
    print(f"  Expected in venv    : {expected_in_venv}")
    print(f"  zCLI says in venv   : {is_in_venv}")
    
    if expected_in_venv == is_in_venv:
        print("  Status              : ✓ PASS - Detection matches Python's sys module")
    else:
        print("  Status              : ✗ FAIL - Detection mismatch!")
        return False
    
    # Check consistency between methods
    if venv_path == venv_from_env:
        print("  Consistency         : ✓ PASS - Session and Environment match")
    else:
        print("  Consistency         : ✗ FAIL - Session and Environment mismatch!")
        return False
    
    # Check path logic
    if is_in_venv and venv_path is None:
        print("  Path logic          : ✗ FAIL - In venv but path is None!")
        return False
    elif not is_in_venv and venv_path is not None:
        print("  Path logic          : ✗ FAIL - Not in venv but path exists!")
        return False
    else:
        print("  Path logic          : ✓ PASS - Path presence matches venv status")
    
    print("\n" + "="*60)
    if is_in_venv:
        print("  Running IN virtual environment")
        print(f"  Path: {venv_path}")
    else:
        print("  Running in SYSTEM environment (no venv)")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_venv_detection()
    sys.exit(0 if success else 1)

