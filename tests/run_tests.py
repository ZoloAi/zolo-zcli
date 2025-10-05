#!/usr/bin/env python3
# tests/run_tests.py — Unified Test Runner
# ───────────────────────────────────────────────────────────────

"""
Unified Test Runner for zCLI

Runs all test suites organized by category:
- Core Tests: Session isolation, parser, plugins
- CRUD Tests: All CRUD operations and features
- RGB Tests: RGB migration tracking
- Integration Tests: End-to-end functionality

Usage:
    python tests/run_tests.py              # Run all tests
    python tests/run_tests.py --core       # Run core tests only
    python tests/run_tests.py --crud       # Run CRUD tests only
    python tests/run_tests.py --verbose    # Verbose output
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_suite(test_module, name):
    """Run a single test suite module."""
    print(f"\n{'='*80}")
    print(f"Running {name}")
    print('='*80)
    
    try:
        # Import and run the test
        if hasattr(test_module, '__name__'):
            # Already imported module
            module = test_module
        else:
            # Import by name
            module = __import__(test_module, fromlist=[''])
        
        # Look for main test function
        if hasattr(module, 'main'):
            result = module.main()
        elif hasattr(module, 'run_tests'):
            result = module.run_tests()
        elif hasattr(module, f'run_{name.lower().replace(" ", "_")}_tests'):
            result = getattr(module, f'run_{name.lower().replace(" ", "_")}_tests')()
        else:
            # Try to find any function that starts with 'run' or 'test'
            for attr_name in dir(module):
                if attr_name.startswith('run_') or attr_name.startswith('test_'):
                    func = getattr(module, attr_name)
                    if callable(func) and not attr_name.startswith('test_') or attr_name == 'test_main':
                        result = func()
                        break
            else:
                print(f"⚠️  No test runner function found in {name}")
                return False
        
        print(f"\n✅ {name} - PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ {name} - FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_core_tests():
    """Run core functionality tests."""
    print("\n" + "="*80)
    print("CORE TEST SUITE")
    print("="*80)
    
    from tests import test_core
    return run_test_suite(test_core, "Core Functionality Tests")


def run_crud_tests():
    """Run all CRUD test suites."""
    print("\n" + "="*80)
    print("CRUD TEST SUITE")
    print("="*80)
    
    test_modules = [
        ('tests.crud.test_direct_operations', 'Direct CRUD Operations'),
        ('tests.crud.test_crud_with_fixtures', 'CRUD with Fixtures'),
        ('tests.crud.test_composite_pk', 'Composite Primary Keys'),
        ('tests.crud.test_indexes', 'Index Management'),
        ('tests.crud.test_join_wrapper', 'JOIN Operations'),
        ('tests.crud.test_where', 'WHERE Clause Operators'),
        ('tests.crud.test_upsert', 'UPSERT Operations'),
        ('tests.crud.test_validation_wrapper', 'Validation Rules'),
        ('tests.crud.test_migration', 'Schema Migrations'),
        ('tests.crud.test_zApps_crud', 'zApps CRUD Operations'),
        ('tests.crud.test_csv_adapter', 'CSV Adapter (pandas)'),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, test_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            if run_test_suite(module, test_name):
                passed += 1
            else:
                failed += 1
        except ImportError as e:
            print(f"⚠️  Could not import {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"CRUD Tests Summary: {passed} passed, {failed} failed")
    print('='*80)
    
    return failed == 0


def run_rgb_tests():
    """Run RGB migration tracking tests."""
    print("\n" + "="*80)
    print("RGB MIGRATION TEST SUITE")
    print("="*80)
    
    test_modules = [
        ('tests.crud.test_rgb_phase1', 'RGB Phase 1: Column Auto-Addition'),
        ('tests.crud.test_rgb_phase2', 'RGB Phase 2: ALTER TABLE Integration'),
        ('tests.crud.test_rgb_phase3', 'RGB Phase 3: Advanced Features'),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, test_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            if run_test_suite(module, test_name):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"RGB Tests Summary: {passed} passed, {failed} failed")
    print('='*80)
    
    return failed == 0


def run_walker_tests():
    """Run zWalker test suite."""
    print("\n" + "="*80)
    print("WALKER TEST SUITE")
    print("="*80)
    
    from tests import test_walker
    return run_test_suite(test_walker, "zWalker Tests")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "🧪 " * 40)
    print("RUNNING ALL TESTS")
    print("🧪 " * 40)
    
    results = {
        'Core': run_core_tests(),
        'CRUD': run_crud_tests(),
        'RGB': run_rgb_tests(),
        'Walker': run_walker_tests(),
    }
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    total_passed = sum(1 for v in results.values() if v)
    total_suites = len(results)
    
    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite_name:20} {status}")
    
    print("="*80)
    print(f"Total: {total_passed}/{total_suites} test suites passed")
    print("="*80)
    
    return all(results.values())


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='zCLI Test Runner')
    parser.add_argument('--core', action='store_true', help='Run core tests only')
    parser.add_argument('--crud', action='store_true', help='Run CRUD tests only')
    parser.add_argument('--rgb', action='store_true', help='Run RGB tests only')
    parser.add_argument('--walker', action='store_true', help='Run Walker tests only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.core:
        success = run_core_tests()
    elif args.crud:
        success = run_crud_tests()
    elif args.rgb:
        success = run_rgb_tests()
    elif args.walker:
        success = run_walker_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
