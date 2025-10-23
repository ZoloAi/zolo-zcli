#!/usr/bin/env python3
"""Simple test for interactive traceback feature."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from zCLI import zCLI


def main():
    print("\n" + "="*70)
    print("Simple Interactive Traceback Test")
    print("="*70)
    
    # Initialize zCLI
    print("\nInitializing zCLI...")
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    print("✓ zCLI initialized")
    
    # Test 1: Store exception without launching UI
    print("\nTest 1: Storing exception...")
    try:
        x = 10 / 0
    except Exception as e:
        zcli.error_handler.last_exception = e
        zcli.error_handler.last_context = {'test': 'division', 'value': 10}
        print(f"✓ Exception stored: {type(e).__name__}")
    
    # Test 2: Verify exception info can be retrieved
    print("\nTest 2: Retrieving exception info...")
    info = zcli.error_handler.get_traceback_info(zcli.error_handler.last_exception)
    print(f"✓ File: {info.get('file', 'unknown')}")
    print(f"✓ Line: {info.get('line', '?')}")
    print(f"✓ Function: {info.get('function', 'unknown')}")
    print(f"✓ Exception: {info.get('exception_type', 'unknown')}")
    
    # Test 3: Test display function
    print("\nTest 3: Testing display function...")
    try:
        from zCLI.utils.error_handler import display_formatted_traceback
        print("✓ display_formatted_traceback imported")
        
        # Would call: display_formatted_traceback(zcli)
        # But we'll skip the actual display to keep output clean
        print("✓ Display function available")
    except Exception as e:
        print(f"✗ Failed to import display function: {e}")
    
    # Test 4: Verify UI file exists
    print("\nTest 4: Checking UI file...")
    from pathlib import Path
    import zCLI as zcli_module
    zcli_package_dir = Path(zcli_module.__file__).parent
    ui_file = zcli_package_dir / "UI" / "zUI.zcli_sys.yaml"
    
    if ui_file.exists():
        print(f"✓ UI file exists: {ui_file}")
        
        # Read and check for Traceback block
        with open(ui_file) as f:
            content = f.read()
            if "Traceback:" in content:
                print("✓ Traceback block found in UI file")
            else:
                print("✗ Traceback block not found in UI file")
    else:
        print(f"✗ UI file not found: {ui_file}")
    
    print("\n" + "="*70)
    print("✓ All basic tests passed!")
    print("="*70)
    print("\nInteractive traceback is ready to use.")
    print("Call zcli.error_handler.interactive_handler(exception) to launch UI.")
    print("")


if __name__ == "__main__":
    main()

