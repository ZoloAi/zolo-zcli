# zCLI/subsystems/zShell_modules/executor_commands/test_executor.py
# ───────────────────────────────────────────────────────────────
"""Test command execution for zCLI."""

import sys
import subprocess
import os
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_test(zcli, parsed):
    """
    Execute test commands using the unified test runner.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Test execution result
    """
    action = parsed["action"]
    
    # Find project root and test runner
    # Strategy: Look for tests/ directory starting from current working directory
    cwd = os.getcwd()
    test_runner = None
    
    # First try: from current working directory
    if os.path.exists(os.path.join(cwd, "tests", "run_tests.py")):
        test_runner = os.path.join(cwd, "tests", "run_tests.py")
    
    # Second try: walk up from current directory to find tests/
    elif not test_runner:
        search_path = cwd
        for _ in range(5):  # Search up to 5 levels
            candidate = os.path.join(search_path, "tests", "run_tests.py")
            if os.path.exists(candidate):
                test_runner = candidate
                break
            parent = os.path.dirname(search_path)
            if parent == search_path:  # Reached filesystem root
                break
            search_path = parent
    
    # Third try: relative to this file (fallback)
    if not test_runner:
        test_runner = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "../../../../tests/run_tests.py"
        ))
    
    if action == "run":
        # Run all tests using unified runner
        logger.info("Running all zCLI test suites...")
        
        if not os.path.exists(test_runner):
            return {"error": f"Test runner not found at: {test_runner}"}
        
        try:
            result = subprocess.run(
                [sys.executable, test_runner],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Print the test output
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode == 0:
                return {"success": "All tests passed!"}
            else:
                return {"error": "Some tests failed. See output above."}
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Failed to run tests: {str(e)}"}
    
    elif action == "session":
        # Quick session test - verify current instance has unique session
        session_id = zcli.session.get("zS_id")
        return {
            "success": "Session test passed",
            "session_id": session_id,
            "note": "This instance has a unique session ID"
        }
    
    else:
        return {"error": f"Unknown test action: {action}. Use: test run | test session"}
