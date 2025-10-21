#!/usr/bin/env python3
# zTestSuite/run_all_tests.py

"""
Centralized Test Runner for zCLI
Runs all test suites and provides summary per subsystem.
"""

import sys
import importlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test factory
from zTestSuite.test_factory import (
    print_subsystem_header,
    print_test_overview,
    print_detailed_results_table
)

# Define test modules to import (in dependency order)
TEST_MODULES = [
    'zConfig',
    'zComm',
    'zDisplay',
    'zAuth',      # zAuth depends on zDisplay
    'zDispatch',
    'zParser',
    'zLoader',
    'zFunc',
    'zDialog',
    'zOpen',
    'zShell',
    'zWizard',
    'zUtils',
    'zData',
    'zWalker',
]

# Dynamically import all test modules
AVAILABLE_MODULES = {}
for module_name in TEST_MODULES:
    module_test_name = f'{module_name}_Test'
    try:
        module = importlib.import_module(f'zTestSuite.{module_test_name}')
        AVAILABLE_MODULES[module_name] = module
    except ImportError:
        pass


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
    available_tests = [(name, f'{name}_Test') for name in TEST_MODULES if name in AVAILABLE_MODULES]
    
    if not available_tests:
        print("❌ No test suites available!")
        return None
    
    print("Select test suite to run:")
    print()
    print("  0) All Tests")
    
    # Show numbered options for each available test suite
    for i, (name, _) in enumerate(available_tests, 1):
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
        for module_name in TEST_MODULES:
            if module_name in AVAILABLE_MODULES:
                test_module = AVAILABLE_MODULES[module_name]
                result = run_subsystem_tests(test_module, module_name)
                results.append(result)
    else:
        # Run specific test suite
        # Extract module name from test_choice (e.g., "zConfig_Test" -> "zConfig")
        module_name = test_choice.replace('_Test', '')
        
        if module_name in AVAILABLE_MODULES:
            test_module = AVAILABLE_MODULES[module_name]
            result = run_subsystem_tests(test_module, module_name)
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

