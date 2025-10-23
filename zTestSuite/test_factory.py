#!/usr/bin/env python3
# zTestSuite/test_factory.py

"""
Test Factory Template for Unified UX across all zCLI Tests
Provides standardized test titles, progress tracking, and table summaries.
"""

import unittest
import sys
from typing import Dict, Any


def print_subsystem_header(subsystem_name: str):
    """Print standardized subsystem header."""
    print()
    print("=" * 80)
    print(f"[TEST] TESTING: {subsystem_name}")
    print("=" * 80)


def print_test_overview(test_module, subsystem_name: str):
    """Print test suite overview before running tests."""
    # Load test classes to get overview
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load all test classes from the module
    for attr_name in dir(test_module):
        attr = getattr(test_module, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, unittest.TestCase) and 
            attr is not unittest.TestCase and
            attr_name.startswith('Test')):
            suite.addTests(loader.loadTestsFromTestCase(attr))
    
    print("\n[INFO] Test Suite Overview:")
    print("-" * 80)
    
    test_cases = []
    for test in suite:
        if hasattr(test, '_testMethodName'):
            class_name = test.__class__.__name__.replace('Test', '')
            method_name = test._testMethodName.replace('test_', '').replace('_', ' ').title()
            test_cases.append(f"{class_name}.{method_name}")
    
    for i, test_name in enumerate(test_cases, 1):
        print(f"  {i:2d}. {test_name}")
    
    print(f"\n[STATS] Total Tests: {len(test_cases)}")
    print("-" * 80)
    print()


def run_subsystem_tests_with_factory(test_module, subsystem_name: str, verbose: bool = False) -> Dict[str, Any]:
    """Run subsystem tests using the test factory."""
    
    # Print the subsystem header
    print()
    print("=" * 80)
    print(f"[TEST] TESTING: {subsystem_name}")
    print("=" * 80)
    
    # Get test suite from module using the same approach as existing run_tests functions
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load all test classes from the module (same pattern as existing modules)
    for attr_name in dir(test_module):
        attr = getattr(test_module, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, unittest.TestCase) and 
            attr is not unittest.TestCase and
            attr_name.startswith('Test')):
            suite.addTests(loader.loadTestsFromTestCase(attr))
    
    # Print test titles before running
    print("\n[INFO] Test Suite Overview:")
    print("-" * 80)
    
    test_cases = []
    for test in suite:
        if hasattr(test, '_testMethodName'):
            class_name = test.__class__.__name__.replace('Test', '')
            method_name = test._testMethodName.replace('test_', '').replace('_', ' ').title()
            test_cases.append(f"{class_name}.{method_name}")
    
    for i, test_name in enumerate(test_cases, 1):
        print(f"  {i:2d}. {test_name}")
    
    print(f"\n[STATS] Total Tests: {len(test_cases)}")
    print("-" * 80)
    print()
    
    # Capture stdout to suppress the default unittest output while still running tests
    import io
    from contextlib import redirect_stdout
    
    # Run the tests silently first to get results, then print our enhanced output
    f = io.StringIO()
    with redirect_stdout(f):
        runner = unittest.TextTestRunner(verbosity=0, stream=sys.stdout)
        result = runner.run(suite)
    
    # Print detailed table after tests
    print_detailed_results_table(result, subsystem_name)
    
    return {
        "name": subsystem_name,
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


def print_detailed_results_table(result: unittest.TestResult, subsystem_name: str):
    """Print detailed table showing each test and its status."""
    print()
    print("=" * 80)
    print(f"[STATS] DETAILED TEST RESULTS - {subsystem_name}")
    print("=" * 80)
    
    # Table header
    print(f"{'#':<3} {'Test Name':<50} {'Status':<8}")
    print("-" * 80)
    
    # Collect all test info
    all_tests = {}
    
    # Process failures
    for test, _ in result.failures:
        if hasattr(test, '_testMethodName'):
            test_name = f"{test.__class__.__name__}.{test._testMethodName.replace('test_', '').replace('_', ' ').title()}"
            all_tests[test] = ('[FAIL] FAIL', test_name)
    
    # Process errors
    for test, _ in result.errors:
        if hasattr(test, '_testMethodName'):
            test_name = f"{test.__class__.__name__}.{test._testMethodName.replace('test_', '').replace('_', ' ').title()}"
            all_tests[test] = ('[ERROR] ERROR', test_name)
    
    # Process skipped
    for test, reason in result.skipped:
        if hasattr(test, '_testMethodName'):
            test_name = f"{test.__class__.__name__}.{test._testMethodName.replace('test_', '').replace('_', ' ').title()}"
            all_tests[test] = ('[SKIP]', test_name)
    
    # Print results table
    test_counter = 1
    for test in sorted(all_tests.keys(), key=lambda x: (x.__class__.__name__, x._testMethodName)):
        status, test_name = all_tests[test]
        print(f"{test_counter:<3} {test_name:<50} {status:<8}")
        test_counter += 1
    
    # Add passed tests (approximate - we can't easily get the exact list)
    if result.testsRun > len(all_tests):
        passed_count = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        if passed_count > 0:
            print(f"... and {passed_count} more tests passed")
    
    print("-" * 80)
    print(f"[STATISTICS]:")
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors) - len(result.skipped)
    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    
    percentage = (passed/total*100) if total > 0 else 0
    print(f"   [OK] Passed:  {passed}/{total} ({percentage:.1f}%)")
    if failed > 0:
        print(f"   [FAIL] Failed:  {failed}")
    if errors > 0:
        print(f"   [ERROR] Errors:  {errors}")
    if skipped > 0:
        print(f"   [SKIP] Skipped: {skipped}")
    
    print()
