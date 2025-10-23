#!/usr/bin/env python3
"""Test script for interactive traceback handling in zCLI v1.5.3.

This script demonstrates the new interactive traceback feature by triggering
various exceptions and launching the Walker UI for error handling.

Usage:
    python3 zTestSuite/test_interactive_traceback.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from zCLI import zCLI


def divide_by_zero():
    """Function that triggers a ZeroDivisionError."""
    return 10 / 0


def invalid_list_access():
    """Function that triggers an IndexError."""
    my_list = [1, 2, 3]
    return my_list[10]


def invalid_dict_access():
    """Function that triggers a KeyError."""
    my_dict = {"name": "test"}
    return my_dict["invalid_key"]


def nested_exception():
    """Function with nested calls that triggers an exception."""
    def level_3():
        return divide_by_zero()
    
    def level_2():
        return level_3()
    
    def level_1():
        return level_2()
    
    return level_1()


def test_basic_interactive_traceback():
    """Test basic interactive traceback with ZeroDivisionError."""
    print("\n" + "="*70)
    print("TEST 1: Basic Interactive Traceback (ZeroDivisionError)")
    print("="*70)
    
    # Initialize zCLI
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    
    try:
        divide_by_zero()
    except Exception as e:
        print(f"\n[CAUGHT] {type(e).__name__}: {e}")
        print("\nLaunching interactive traceback UI...")
        print("(Select options to view details, retry, or stop)\n")
        
        result = zcli.error_handler.interactive_handler(
            e,
            operation=divide_by_zero,
            context={'test': 'basic_traceback', 'function': 'divide_by_zero'}
        )
        
        print(f"\n[RESULT] UI returned: {result}")


def test_retryable_operation():
    """Test interactive traceback with a retryable operation."""
    print("\n" + "="*70)
    print("TEST 2: Retryable Operation (can be 'fixed' with retry)")
    print("="*70)
    
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    
    attempt_count = 0
    
    def risky_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"  [ATTEMPT {attempt_count}] Running risky operation...")
        
        if attempt_count < 3:
            raise ValueError(f"Operation failed on attempt {attempt_count}")
        else:
            print(f"  [SUCCESS] Operation succeeded on attempt {attempt_count}!")
            return "success"
    
    try:
        risky_operation()
    except Exception as e:
        print(f"\n[CAUGHT] {type(e).__name__}: {e}")
        print("\nLaunching interactive traceback UI...")
        print("(Try selecting 'Retry Operation' multiple times)\n")
        
        result = zcli.error_handler.interactive_handler(
            e,
            operation=risky_operation,
            context={'test': 'retryable_operation', 'attempt': attempt_count}
        )
        
        print(f"\n[RESULT] UI returned: {result}")


def test_nested_traceback():
    """Test interactive traceback with nested function calls."""
    print("\n" + "="*70)
    print("TEST 3: Nested Traceback (multi-level function calls)")
    print("="*70)
    
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    
    try:
        nested_exception()
    except Exception as e:
        print(f"\n[CAUGHT] {type(e).__name__}: {e}")
        print("\nLaunching interactive traceback UI...")
        print("(View Details to see the full call stack)\n")
        
        result = zcli.error_handler.interactive_handler(
            e,
            operation=nested_exception,
            context={
                'test': 'nested_traceback', 
                'depth': 3,
                'description': 'Three nested function calls'
            }
        )
        
        print(f"\n[RESULT] UI returned: {result}")


def test_exception_history():
    """Test exception history tracking."""
    print("\n" + "="*70)
    print("TEST 4: Exception History (multiple exceptions)")
    print("="*70)
    
    zcli = zCLI({
        "zWorkspace": str(project_root),
        "zVerbose": False
    })
    
    exceptions = [
        (divide_by_zero, "ZeroDivisionError"),
        (invalid_list_access, "IndexError"),
        (invalid_dict_access, "KeyError")
    ]
    
    for func, error_type in exceptions:
        try:
            func()
        except Exception as e:
            print(f"\n[CAUGHT] {error_type}: {e}")
            # Store in history without launching UI
            zcli.error_handler.last_exception = e
            zcli.error_handler.last_context = {'error_type': error_type}
            zcli.error_handler.exception_history.append({
                'exception': e,
                'operation': func,
                'context': {'error_type': error_type}
            })
    
    print("\nLaunching interactive traceback UI...")
    print("(Select 'Exception History' to view all captured exceptions)\n")
    
    result = zcli.error_handler.interactive_handler(
        exceptions[-1][0].__wrapped__ if hasattr(exceptions[-1][0], '__wrapped__') else Exception("View history"),
        context={'test': 'exception_history', 'count': len(exceptions)}
    )
    
    print(f"\n[RESULT] UI returned: {result}")


def main():
    """Run all interactive traceback tests."""
    print("\n" + "="*70)
    print("zCLI v1.5.3 - Interactive Traceback Test Suite")
    print("="*70)
    print("\nThis test demonstrates the new interactive error handling feature.")
    print("When an exception occurs, you'll see an interactive menu to:")
    print("  - View detailed exception information")
    print("  - Retry the failed operation")
    print("  - View exception history")
    print("\nPress Ctrl+C at any time to exit.\n")
    
    tests = [
        ("Basic Interactive Traceback", test_basic_interactive_traceback),
        ("Retryable Operation", test_retryable_operation),
        ("Nested Traceback", test_nested_traceback),
        ("Exception History", test_exception_history)
    ]
    
    for test_name, test_func in tests:
        try:
            input(f"\nPress Enter to run: {test_name} (or Ctrl+C to skip)...")
            test_func()
        except KeyboardInterrupt:
            print(f"\n\n[SKIPPED] {test_name}")
            continue
        except Exception as e:
            print(f"\n[TEST ERROR] {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Tests interrupted by user")
        sys.exit(0)

