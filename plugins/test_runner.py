"""
zCLI Test Runner Plugin
Declarative test execution for zCLI test suites
"""

import subprocess
import sys
from pathlib import Path


def run_test_suite(suite_name, zcli=None):
    """
    Run a test suite using pytest.
    
    Args:
        suite_name: Name of test suite to run ('all' for all tests)
        zcli: zCLI instance (auto-injected)
    
    Returns:
        dict: Test results
    """
    if not zcli:
        return {"error": "zCLI instance not available"}
    
    # Map suite names to test files
    test_map = {
        "all": "zTestSuite/",
        "zConfig_Validator": "zTestSuite/zConfig_Validator_Test.py",
        "zConfig": "zTestSuite/zConfig_Test.py",
        "zComm": "zTestSuite/zComm_Test.py",
        "zServer": "zTestSuite/zServer_Test.py",
        "zBifrost": "zTestSuite/zBifrost_Test.py",
        "zBifrost_Integration": "zTestSuite/zBifrost_Integration_Test.py",
        "zBifrost_Unit": "zTestSuite/zBifrost_Unit_Test.py",
        "zLayer0_Integration": "zTestSuite/zLayer0_Integration_Test.py",
        "zShutdown": "zTestSuite/zShutdown_Test.py",
        "zDisplay": "zTestSuite/zDisplay_Test.py",
        "zDisplay_Widgets": "zTestSuite/zDisplay_Widgets_Test.py",
        "zAuth": "zTestSuite/zAuth_Test.py",
        "zAuth_Comprehensive": "zTestSuite/zAuth_Comprehensive_Test.py",
        "zRBAC": "zTestSuite/zRBAC_Test.py",
        "zDispatch": "zTestSuite/zDispatch_Test.py",
        "zNavigation": "zTestSuite/zNavigation_Test.py",
        "zParser": "zTestSuite/zParser_Test.py",
        "zLoader": "zTestSuite/zLoader_Test.py",
        "zFunc": "zTestSuite/zFunc_Test.py",
        "zDialog": "zTestSuite/zDialog_Test.py",
        "zDialog_AutoValidation": "zTestSuite/zDialog_AutoValidation_Test.py",
        "zOpen": "zTestSuite/zOpen_Test.py",
        "zShell": "zTestSuite/zShell_Test.py",
        "zWizard": "zTestSuite/zWizard_Test.py",
        "zUtils": "zTestSuite/zUtils_Test.py",
        "zTraceback": "zTestSuite/zTraceback_Test.py",
        "zExceptions": "zTestSuite/zExceptions_Test.py",
        "zExceptions_Traceback_Integration": "zTestSuite/zExceptions_Traceback_Integration_Test.py",
        "zUninstall": "zTestSuite/zUninstall_Test.py",
        "zData": "zTestSuite/zData_Test.py",
        "zData_Validation": "zTestSuite/zData_Validation_Test.py",
        "zData_PluginValidation": "zTestSuite/zData_PluginValidation_Test.py",
        "zData_Migration": "zTestSuite/zData_Migration_Test.py",
        "zWalker": "zTestSuite/zWalker_Test.py",
        "zIntegration": "zTestSuite/zIntegration_Test.py",
        "zEndToEnd": "zTestSuite/zEndToEnd_Test.py",
    }
    
    test_path = test_map.get(suite_name)
    if not test_path:
        zcli.display.text(f"❌ Unknown test suite: {suite_name}")
        return {"error": f"Unknown test suite: {suite_name}"}
    
    workspace = Path(zcli.config.zWorkspace)
    full_path = workspace / test_path
    
    if not full_path.exists():
        zcli.display.text(f"❌ Test file not found: {full_path}")
        return {"error": f"Test file not found: {full_path}"}
    
    # Display header
    zcli.display.text(f"\n{'='*70}")
    zcli.display.text(f"Running: {suite_name}")
    zcli.display.text(f"Path: {test_path}")
    zcli.display.text(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(full_path), "-v"],
            cwd=str(workspace),
            capture_output=True,
            text=True
        )
        
        # Display output
        zcli.display.text(result.stdout)
        if result.stderr:
            zcli.display.warning(result.stderr)
        
        # Display result
        if result.returncode == 0:
            zcli.display.success(f"\n✅ {suite_name} PASSED")
            return {"status": "success", "suite": suite_name}
        else:
            zcli.display.error(f"\n❌ {suite_name} FAILED")
            return {"status": "failed", "suite": suite_name, "return_code": result.returncode}
    
    except Exception as e:
        zcli.display.error(f"❌ Error running tests: {str(e)}")
        zcli.logger.error(f"Test execution error: {e}", exc_info=True)
        return {"error": str(e)}


def run_specific_test(suite_name, test_name, zcli=None):
    """
    Run a specific test from a test suite.
    
    Args:
        suite_name: Name of test suite
        test_name: Specific test name (e.g., 'test_basic_plugin_execution')
        zcli: zCLI instance (auto-injected)
    
    Returns:
        dict: Test results
    """
    if not zcli:
        return {"error": "zCLI instance not available"}
    
    # Map suite names to test files
    test_map = {
        "zConfig": "zTestSuite/zConfig_Test.py",
        "zFunc": "zTestSuite/zFunc_Test.py",
        "zDialog": "zTestSuite/zDialog_Test.py",
        "zAuth": "zTestSuite/zAuth_Test.py",
        "zData": "zTestSuite/zData_Test.py",
        # Add more as needed
    }
    
    test_path = test_map.get(suite_name)
    if not test_path:
        zcli.display.text(f"❌ Unknown test suite: {suite_name}")
        return {"error": f"Unknown test suite: {suite_name}"}
    
    workspace = Path(zcli.config.zWorkspace)
    full_path = workspace / test_path
    
    if not full_path.exists():
        zcli.display.text(f"❌ Test file not found: {full_path}")
        return {"error": f"Test file not found: {full_path}"}
    
    # Display header
    zcli.display.text(f"\n{'='*70}")
    zcli.display.text(f"Running: {suite_name}::{test_name}")
    zcli.display.text(f"Path: {test_path}")
    zcli.display.text(f"{'='*70}\n")
    
    try:
        # Run specific test with -k filter
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(full_path), "-v", "-k", test_name],
            cwd=str(workspace),
            capture_output=True,
            text=True
        )
        
        # Display output
        zcli.display.text(result.stdout)
        if result.stderr:
            zcli.display.warning(result.stderr)
        
        # Display result
        if result.returncode == 0:
            zcli.display.success(f"\n✅ {test_name} PASSED")
            return {"status": "success", "suite": suite_name, "test": test_name}
        else:
            zcli.display.error(f"\n❌ {test_name} FAILED")
            return {"status": "failed", "suite": suite_name, "test": test_name}
    
    except Exception as e:
        zcli.display.error(f"❌ Error running test: {str(e)}")
        zcli.logger.error(f"Test execution error: {e}", exc_info=True)
        return {"error": str(e)}
