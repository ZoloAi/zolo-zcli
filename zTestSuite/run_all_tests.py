#!/usr/bin/env python3
# zTestSuite/run_all_tests.py

"""
Centralized Test Runner for zCLI
Runs all test suites and provides summary per subsystem.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all test modules
try:
    from zTestSuite import zConfig_Test
    ZCONFIG_AVAILABLE = True
except ImportError:
    ZCONFIG_AVAILABLE = False

try:
    from zTestSuite import zComm_Test
    ZCOMM_AVAILABLE = True
except ImportError:
    ZCOMM_AVAILABLE = False

try:
    from zTestSuite import zAuth_Test
    ZAUTH_AVAILABLE = True
except ImportError:
    ZAUTH_AVAILABLE = False


def run_subsystem_tests(test_module, name):
    """Run tests for a single subsystem and return results."""
    print()
    print("=" * 70)
    print(f"Testing: {name}")
    print("=" * 70)
    
    try:
        result = test_module.run_tests(verbose=False)
        return {
            "name": name,
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "error_count": len(result.errors),
            "skipped_count": len(result.skipped),
            "success": result.wasSuccessful(),
            "failures": result.failures,
            "errors": result.errors,
            "skipped": result.skipped
        }
    except Exception as e:
        print(f"ERROR: Failed to run {name} tests: {e}")
        return {
            "name": name,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "error_count": 1,
            "skipped_count": 0,
            "success": False,
            "failures": [],
            "errors": [],
            "skipped": []
        }


def print_summary(results):
    """Print overall summary of all test results."""
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    
    # Print per-subsystem results
    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"{status}  {result['name']:<20} {result['passed']}/{result['total']} passed", end="")
        
        if result['failed'] > 0:
            print(f"  ({result['failed']} failed)", end="")
        if result['error_count'] > 0:
            print(f"  ({result['error_count']} errors)", end="")
        if result['skipped_count'] > 0:
            print(f"  ({result['skipped_count']} skipped)", end="")
        print()
        
        total_tests += result['total']
        total_passed += result['passed']
        total_failed += result['failed']
        total_errors += result['error_count']
        total_skipped += result['skipped_count']
    
    # Print overall totals
    print()
    print("-" * 70)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_failed > 0:
        print(f"       {total_failed} tests failed")
    if total_errors > 0:
        print(f"       {total_errors} tests had errors")
    if total_skipped > 0:
        print(f"       {total_skipped} tests skipped")
    
    print("-" * 70)
    
    # Print detailed failure information
    has_failures = any(r['failed'] > 0 or r['error_count'] > 0 or r['skipped_count'] > 0 for r in results)
    if has_failures:
        print()
        print("DETAILED RESULTS:")
        print("-" * 70)
        
        for result in results:
            if result['failed'] > 0 or result['error_count'] > 0 or result['skipped_count'] > 0:
                print(f"\n{result['name']}:")
                
                # Print failed tests
                if result['failures']:
                    print("  FAILED:")
                    for test, traceback in result['failures']:
                        test_name = test._testMethodName if hasattr(test, '_testMethodName') else str(test)
                        print(f"    ✗ {test_name}")
                
                # Print error tests
                if result['errors']:
                    print("  ERRORS:")
                    for test, traceback in result['errors']:
                        test_name = test._testMethodName if hasattr(test, '_testMethodName') else str(test)
                        print(f"    ⚠ {test_name}")
                
                # Print skipped tests
                if result['skipped']:
                    print("  SKIPPED:")
                    for test, reason in result['skipped']:
                        test_name = test._testMethodName if hasattr(test, '_testMethodName') else str(test)
                        reason_str = f" ({reason})" if reason else ""
                        print(f"    ⊘ {test_name}{reason_str}")
    
    print()
    print("-" * 70)
    
    # Overall status
    all_passed = all(r["success"] for r in results)
    if all_passed:
        print()
        print("✓ ALL TESTS PASSED")
        print()
    else:
        print()
        print("✗ SOME TESTS FAILED")
        print()
    
    return all_passed


def main():
    """Main test runner."""
    print()
    print("=" * 70)
    print("zCLI Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run zConfig tests
    if ZCONFIG_AVAILABLE:
        result = run_subsystem_tests(zConfig_Test, "zConfig")
        results.append(result)
    else:
        print("\nWARNING: zConfig tests not available")
    
    # Run zComm tests
    if ZCOMM_AVAILABLE:
        result = run_subsystem_tests(zComm_Test, "zComm")
        results.append(result)
    else:
        print("\nWARNING: zComm tests not available")
    
    # Run zAuth tests
    if ZAUTH_AVAILABLE:
        result = run_subsystem_tests(zAuth_Test, "zAuth")
        results.append(result)
    else:
        print("\nWARNING: zAuth tests not available")
    
    # Print summary
    all_passed = print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

