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

# Import test factory
from zTestSuite.test_factory import (
    run_subsystem_tests_with_factory,
    print_subsystem_header,
    print_test_overview,
    print_detailed_results_table
)

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

try:
    from zTestSuite import zDisplay_Test
    ZDISPLAY_AVAILABLE = True
except ImportError:
    ZDISPLAY_AVAILABLE = False

try:
    from zTestSuite import zDispatch_Test
    ZDISPATCH_AVAILABLE = True
except ImportError:
    ZDISPATCH_AVAILABLE = False

try:
    from zTestSuite import zParser_Test
    ZPARSER_AVAILABLE = True
except ImportError:
    ZPARSER_AVAILABLE = False

try:
    from zTestSuite import zLoader_Test
    ZLOADER_AVAILABLE = True
except ImportError:
    ZLOADER_AVAILABLE = False

try:
    from zTestSuite import zFunc_Test
    ZFUNC_AVAILABLE = True
except ImportError:
    ZFUNC_AVAILABLE = False

try:
    from zTestSuite import zDialog_Test
    ZDIALOG_AVAILABLE = True
except ImportError:
    ZDIALOG_AVAILABLE = False

try:
    from zTestSuite import zOpen_Test
    ZOPEN_AVAILABLE = True
except ImportError:
    ZOPEN_AVAILABLE = False

try:
    from zTestSuite import zShell_Test
    ZSHELL_AVAILABLE = True
except ImportError:
    ZSHELL_AVAILABLE = False

try:
    from zTestSuite import zWizard_Test
    ZWIZARD_AVAILABLE = True
except ImportError:
    ZWIZARD_AVAILABLE = False

try:
    from zTestSuite import zUtils_Test
    ZUTILS_AVAILABLE = True
except ImportError:
    ZUTILS_AVAILABLE = False

try:
    from zTestSuite import zData_Test
    ZDATA_AVAILABLE = True
except ImportError:
    ZDATA_AVAILABLE = False

try:
    from zTestSuite import zWalker_Test
    ZWALKER_AVAILABLE = True
except ImportError:
    ZWALKER_AVAILABLE = False


def run_subsystem_tests(test_module, name):
    """Run tests for a single subsystem with enhanced UX."""
    try:
        # Print the enhanced header
        print_subsystem_header(name)
        
        # Get test suite info and print overview
        print_test_overview(test_module, name)
        
        # Run the actual tests using the module's existing run_tests function
        result = test_module.run_tests(verbose=False)
        
        # Print enhanced results table
        print_detailed_results_table(result, name)
        
        return {
            "name": name,
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
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
    """Print overall summary with enhanced table formatting."""
    print()
    print("=" * 90)
    print("🏁 COMPREHENSIVE TEST SUMMARY")
    print("=" * 90)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    
    # Print table header
    print()
    print(f"{'Subsystem':<15} {'Status':<8} {'Passed':<8} {'Failed':<8} {'Errors':<8} {'Skipped':<8} {'Total':<6} {'%':<6}")
    print("-" * 90)
    
    # Print each subsystem result in table format
    for result in results:
        subsystem = result['name']
        status_icon = "✅ PASS" if result["success"] else "❌ FAIL"
        passed = result['passed']
        failed = result['failed']
        errors = result['error_count']
        skipped = result['skipped_count']
        total = result['total']
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"{subsystem:<15} {status_icon:<8} {passed:<8} {failed:<8} {errors:<8} {skipped:<8} {total:<6} {percentage:5.1f}%")
        
        total_tests += total
        total_passed += passed
        total_failed += failed
        total_errors += errors
        total_skipped += skipped
    
    # Print totals row
    print("-" * 90)
    total_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"{'TOTAL':<15} {'':<8} {total_passed:<8} {total_failed:<8} {total_errors:<8} {total_skipped:<8} {total_tests:<6} {total_percentage:5.1f}%")
    print("-" * 90)
    
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


def show_test_menu():
    """Show interactive test menu and return user selection."""
    print()
    print("=" * 70)
    print("zCLI Test Suite")
    print("=" * 70)
    print()
    
    # Build list of available test suites in dependency order
    available_tests = []
    
    if ZCONFIG_AVAILABLE:
        available_tests.append(("zConfig", "zConfig_Test"))
    if ZCOMM_AVAILABLE:
        available_tests.append(("zComm", "zComm_Test"))
    if ZDISPLAY_AVAILABLE:
        available_tests.append(("zDisplay", "zDisplay_Test"))
    if ZAUTH_AVAILABLE:
        available_tests.append(("zAuth", "zAuth_Test"))  # zAuth depends on zDisplay
    if ZDISPATCH_AVAILABLE:
        available_tests.append(("zDispatch", "zDispatch_Test"))
    if ZPARSER_AVAILABLE:
        available_tests.append(("zParser", "zParser_Test"))
    if ZLOADER_AVAILABLE:
        available_tests.append(("zLoader", "zLoader_Test"))
    if ZFUNC_AVAILABLE:
        available_tests.append(("zFunc", "zFunc_Test"))
    if ZDIALOG_AVAILABLE:
        available_tests.append(("zDialog", "zDialog_Test"))
    if ZOPEN_AVAILABLE:
        available_tests.append(("zOpen", "zOpen_Test"))
    if ZSHELL_AVAILABLE:
        available_tests.append(("zShell", "zShell_Test"))
    if ZWIZARD_AVAILABLE:
        available_tests.append(("zWizard", "zWizard_Test"))
    if ZUTILS_AVAILABLE:
        available_tests.append(("zUtils", "zUtils_Test"))
    if ZDATA_AVAILABLE:
        available_tests.append(("zData", "zData_Test"))
    if ZWALKER_AVAILABLE:
        available_tests.append(("zWalker", "zWalker_Test"))
    
    if not available_tests:
        print("❌ No test suites available!")
        return None
    
    print("Select test suite to run:")
    print()
    print("  0) All Tests")
    
    # Show numbered options for each available test suite
    for i, (name, module) in enumerate(available_tests, 1):
        print(f"  {i}) {name}")
    
    print()
    
    while True:
        try:
            choice = input("Enter choice (0-{}): ".format(len(available_tests)))
            
            # Handle empty input
            if not choice.strip():
                continue
                
            choice_num = int(choice.strip())
            
            if choice_num == 0:
                return "all"
            elif 1 <= choice_num <= len(available_tests):
                return available_tests[choice_num - 1][1]  # Return module name
            else:
                print(f"Invalid choice. Please enter 0-{len(available_tests)}")
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return None


def run_selected_tests(test_choice=None):
    """Run selected tests based on choice."""
    results = []
    
    if test_choice == "all" or test_choice is None:
        # Run all available tests in dependency order
        test_suites = []
        if ZCONFIG_AVAILABLE:
            test_suites.append((zConfig_Test, "zConfig"))
        if ZCOMM_AVAILABLE:
            test_suites.append((zComm_Test, "zComm"))
        if ZDISPLAY_AVAILABLE:
            test_suites.append((zDisplay_Test, "zDisplay"))
        if ZAUTH_AVAILABLE:
            test_suites.append((zAuth_Test, "zAuth"))  # zAuth depends on zDisplay
        if ZDISPATCH_AVAILABLE:
            test_suites.append((zDispatch_Test, "zDispatch"))
        if ZPARSER_AVAILABLE:
            test_suites.append((zParser_Test, "zParser"))
        if ZLOADER_AVAILABLE:
            test_suites.append((zLoader_Test, "zLoader"))
        if ZFUNC_AVAILABLE:
            test_suites.append((zFunc_Test, "zFunc"))
        if ZDIALOG_AVAILABLE:
            test_suites.append((zDialog_Test, "zDialog"))
        if ZOPEN_AVAILABLE:
            test_suites.append((zOpen_Test, "zOpen"))
        if ZSHELL_AVAILABLE:
            test_suites.append((zShell_Test, "zShell"))
        if ZWIZARD_AVAILABLE:
            test_suites.append((zWizard_Test, "zWizard"))
        if ZUTILS_AVAILABLE:
            test_suites.append((zUtils_Test, "zUtils"))
        if ZDATA_AVAILABLE:
            test_suites.append((zData_Test, "zData"))
        if ZWALKER_AVAILABLE:
            test_suites.append((zWalker_Test, "zWalker"))
        
        for test_module, name in test_suites:
            result = run_subsystem_tests(test_module, name)
            results.append(result)
    else:
        # Run specific test suite
        if test_choice == "zConfig_Test" and ZCONFIG_AVAILABLE:
            result = run_subsystem_tests(zConfig_Test, "zConfig")
            results.append(result)
        elif test_choice == "zComm_Test" and ZCOMM_AVAILABLE:
            result = run_subsystem_tests(zComm_Test, "zComm")
            results.append(result)
        elif test_choice == "zAuth_Test" and ZAUTH_AVAILABLE:
            result = run_subsystem_tests(zAuth_Test, "zAuth")
            results.append(result)
        elif test_choice == "zDisplay_Test" and ZDISPLAY_AVAILABLE:
            result = run_subsystem_tests(zDisplay_Test, "zDisplay")
            results.append(result)
        elif test_choice == "zDispatch_Test" and ZDISPATCH_AVAILABLE:
            result = run_subsystem_tests(zDispatch_Test, "zDispatch")
            results.append(result)
        elif test_choice == "zParser_Test" and ZPARSER_AVAILABLE:
            result = run_subsystem_tests(zParser_Test, "zParser")
            results.append(result)
        elif test_choice == "zLoader_Test" and ZLOADER_AVAILABLE:
            result = run_subsystem_tests(zLoader_Test, "zLoader")
            results.append(result)
        elif test_choice == "zFunc_Test" and ZFUNC_AVAILABLE:
            result = run_subsystem_tests(zFunc_Test, "zFunc")
            results.append(result)
        elif test_choice == "zDialog_Test" and ZDIALOG_AVAILABLE:
            result = run_subsystem_tests(zDialog_Test, "zDialog")
            results.append(result)
        elif test_choice == "zOpen_Test" and ZOPEN_AVAILABLE:
            result = run_subsystem_tests(zOpen_Test, "zOpen")
            results.append(result)
        elif test_choice == "zShell_Test" and ZSHELL_AVAILABLE:
            result = run_subsystem_tests(zShell_Test, "zShell")
            results.append(result)
        elif test_choice == "zWizard_Test" and ZWIZARD_AVAILABLE:
            result = run_subsystem_tests(zWizard_Test, "zWizard")
            results.append(result)
        elif test_choice == "zUtils_Test" and ZUTILS_AVAILABLE:
            result = run_subsystem_tests(zUtils_Test, "zUtils")
            results.append(result)
        elif test_choice == "zData_Test" and ZDATA_AVAILABLE:
            result = run_subsystem_tests(zData_Test, "zData")
            results.append(result)
        elif test_choice == "zWalker_Test" and ZWALKER_AVAILABLE:
            result = run_subsystem_tests(zWalker_Test, "zWalker")
            results.append(result)
        else:
            print(f"❌ Test suite '{test_choice}' not available!")
            return False
    
    # Print summary
    if results:
        all_passed = print_summary(results)
        return all_passed
    else:
        print("❌ No test results to show!")
        return False


def main():
    """Main test runner with interactive menu."""
    # Check if we should show menu or run all tests
    test_choice = show_test_menu()
    
    if test_choice is None:
        sys.exit(1)
    
    # Run the selected tests
    success = run_selected_tests(test_choice)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

