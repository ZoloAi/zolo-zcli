#!/usr/bin/env python3
# zTestSuite/run_tests.py

"""
Unified Test Runner for zCLI Test Suite

Usage:
    python zTestSuite/run_tests.py              # Run all tests
    python zTestSuite/run_tests.py zConfig      # Run specific subsystem tests
    python zTestSuite/run_tests.py -v           # Verbose output
    python zTestSuite/run_tests.py --list       # List available tests
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from zTestSuite import zConfig_Test


def list_available_tests():
    """List all available test modules."""
    print("\n[INFO] Available Test Modules:")
    print("=" * 50)
    print("  • zConfig  - Configuration subsystem tests")
    # Add more as they're created
    # print("  • zAuth    - Authentication subsystem tests")
    # print("  • zData    - Data subsystem tests")
    print()


def run_subsystem_tests(subsystem, verbose=False):
    """Run tests for a specific subsystem."""
    test_map = {
        'zconfig': zConfig_Test,
        # Add more mappings as tests are created
    }
    
    subsystem_lower = subsystem.lower()
    if subsystem_lower not in test_map:
        print(f"[ERROR] Unknown subsystem: {subsystem}")
        list_available_tests()
        return False
    
    print(f"\n[TEST] Running {subsystem} Tests...")
    print("=" * 70)
    
    result = test_map[subsystem_lower].run_tests(verbose=verbose)
    return result.wasSuccessful()


def run_all_tests(verbose=False):
    """Run all available tests."""
    print("\n[TEST] Running All zCLI Tests...")
    print("=" * 70)
    print()
    
    all_successful = True
    
    # Run zConfig tests
    print("\n📦 zConfig Subsystem Tests:")
    print("-" * 70)
    result = zConfig_Test.run_tests(verbose=verbose)
    all_successful = all_successful and result.wasSuccessful()
    
    # Add more subsystems here as tests are created
    
    print("\n" + "=" * 70)
    if all_successful:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed.")
    print("=" * 70)
    
    return all_successful


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(
        description='zCLI Test Suite Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run all tests
  %(prog)s zConfig            # Run zConfig tests only
  %(prog)s -v                 # Run all tests with verbose output
  %(prog)s --list             # List available test modules
        """
    )
    
    parser.add_argument(
        'subsystem',
        nargs='?',
        help='Specific subsystem to test (zConfig, zAuth, etc.)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose test output'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available test modules'
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        list_available_tests()
        return 0
    
    # Run specific subsystem or all tests
    if args.subsystem:
        success = run_subsystem_tests(args.subsystem, verbose=args.verbose)
    else:
        success = run_all_tests(verbose=args.verbose)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

