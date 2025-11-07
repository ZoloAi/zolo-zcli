"""
Declarative zConfig Tests
Test functions for zConfig subsystem validation
Uses zWizard + zHat for result accumulation
"""

from zCLI import zCLI
from zCLI.utils.zExceptions import ConfigurationError


def test_initialization(zcli=None, context=None):
    """
    Test 1: Config Initialization
    Verify that zCLI can initialize with minimal config.
    
    Returns:
        dict: Test result with keys: test, status, message
    """
    if not zcli:
        result = {"test": "Config Initialization", "status": "ERROR", "message": "zCLI instance not available"}
        return result
    
    try:
        # Attempt to create a new zCLI instance with minimal config
        test_cli = zCLI({"zWorkspace": "."})
        
        # Verify basic subsystems exist (zCLI core functionality)
        checks = [
            (hasattr(test_cli, 'config'), "config"),
            (hasattr(test_cli, 'display'), "display"),
            (hasattr(test_cli, 'logger'), "logger"),
            (hasattr(test_cli, 'walker'), "walker"),
            (test_cli.config is not None, "config initialized")
        ]
        
        failed_checks = [name for passed, name in checks if not passed]
        
        if failed_checks:
            result = {
                "test": "Config Initialization",
                "status": "FAILED",
                "message": f"Missing: {', '.join(failed_checks)}"
            }
        else:
            result = {
                "test": "Config Initialization",
                "status": "PASSED",
                "message": "zCLI core subsystems initialized successfully"
            }
    
    except Exception as e:
        result = {
            "test": "Config Initialization",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        }
    
    # Store result in session for accumulation
    if "zTestRunner_results" not in zcli.session:
        zcli.session["zTestRunner_results"] = []
    zcli.session["zTestRunner_results"].append(result)
    
    # Return None - results are stored in session, not used for navigation
    return None


def test_workspace_required(zcli=None, context=None):
    """
    Test 2: Multiple Instances
    Verify that multiple zCLI instances can coexist.
    
    Returns:
        dict: Test result with keys: test, status, message
    """
    if not zcli:
        result = {"test": "Multiple Instances", "status": "ERROR", "message": "zCLI instance not available"}
        return result
    
    try:
        # Create two separate zCLI instances with different workspaces
        test_cli_1 = zCLI({"zWorkspace": "."})
        test_cli_2 = zCLI({"zWorkspace": "."})
        
        # Verify both instances exist and are separate objects
        checks = [
            (test_cli_1 is not None, "Instance 1 created"),
            (test_cli_2 is not None, "Instance 2 created"),
            (test_cli_1 is not test_cli_2, "Instances are separate"),
            (hasattr(test_cli_1, 'config'), "Instance 1 has config"),
            (hasattr(test_cli_2, 'config'), "Instance 2 has config"),
        ]
        
        failed_checks = [name for passed, name in checks if not passed]
        
        if failed_checks:
            result = {
                "test": "Multiple Instances",
                "status": "FAILED",
                "message": f"Failed: {', '.join(failed_checks)}"
            }
        else:
            result = {
                "test": "Multiple Instances",
                "status": "PASSED",
                "message": "Multiple zCLI instances can coexist"
            }
    
    except Exception as e:
        result = {
            "test": "Multiple Instances",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        }
    
    # Store result in session for accumulation
    if "zTestRunner_results" not in zcli.session:
        zcli.session["zTestRunner_results"] = []
    zcli.session["zTestRunner_results"].append(result)
    
    # Return None - results are stored in session, not used for navigation
    return None


def display_test_results(zcli=None, context=None):
    """
    Display accumulated test results as a table with statistics.
    
    Shows comprehensive test results including:
    - Individual test status (PASSED/FAILED/ERROR/WARN)
    - Summary statistics with percentages
    - Color-coded table output
    - Single pause at end for review
    
    Args:
        zcli: zCLI instance (for display and session access)
        context: Optional context (not used, for compatibility)
    
    Returns:
        None (all output via zDisplay)
    """
    if not zcli:
        return None
    
    # Get accumulated test results from session
    test_results_data = zcli.session.get("zTestRunner_results", [])
    
    if not test_results_data:
        zcli.display.warning("\n⚠️  No test results found in session")
        return None
    
    # Calculate comprehensive statistics
    total_tests = len(test_results_data)
    passed = sum(1 for r in test_results_data if r.get("status") == "PASSED")
    failed = sum(1 for r in test_results_data if r.get("status") == "FAILED")
    errors = sum(1 for r in test_results_data if r.get("status") == "ERROR")
    warnings = sum(1 for r in test_results_data if r.get("status") == "WARN")
    
    # Calculate percentages
    pass_pct = (passed / total_tests * 100) if total_tests > 0 else 0
    fail_pct = (failed / total_tests * 100) if total_tests > 0 else 0
    error_pct = (errors / total_tests * 100) if total_tests > 0 else 0
    warn_pct = (warnings / total_tests * 100) if total_tests > 0 else 0
    
    # Display header (using write_line to avoid pauses)
    print("\n" + "=" * 70)
    print(f"zConfig Test Suite Results - {total_tests} Tests")
    print("=" * 70 + "\n")
    
    # Format results for table display
    test_results = [
        [r.get("test", "Unknown"), r.get("status", "UNKNOWN"), r.get("message", "")]
        for r in test_results_data
    ]
    
    # Display results table
    zcli.display.zTable(
        title=f"Individual Test Results",
        columns=["Test Name", "Status", "Message"],
        rows=test_results,
        show_header=True
    )
    
    # Display comprehensive summary with percentages (no pauses)
    print("\n" + "─" * 70)
    print("Summary Statistics")
    print("─" * 70)
    print(f"  Total Tests:    {total_tests}")
    
    if passed > 0:
        print(f"  ✅ Passed:      {passed} ({pass_pct:.1f}%)")
    
    if failed > 0:
        print(f"  ❌ Failed:      {failed} ({fail_pct:.1f}%)")
    
    if errors > 0:
        print(f"  💥 Errors:      {errors} ({error_pct:.1f}%)")
    
    if warnings > 0:
        print(f"  ⚠️  Warnings:    {warnings} ({warn_pct:.1f}%)")
    
    print("─" * 70)
    
    # Final verdict
    if failed == 0 and errors == 0:
        print(f"\n🎉 SUCCESS! All {passed} tests passed ({pass_pct:.0f}%)")
    else:
        print(f"\n❌ FAILURE: {failed + errors} test(s) did not pass")
    
    # Single pause at the end for review
    print("\n📊 Review results above.")
    input("Press Enter to return to main menu...")
    
    # Clear results from session for next run
    zcli.session["zTestRunner_results"] = []
    
    return None

