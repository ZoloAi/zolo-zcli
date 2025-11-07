"""
Declarative zConfig Tests
Test functions for zConfig subsystem validation
"""

from zCLI import zCLI
from zCLI.utils.zExceptions import ConfigValidationError


def test_initialization(zcli=None):
    """
    Test 1: Config Initialization
    Verify that zCLI can initialize with minimal config.
    """
    if not zcli:
        return {"error": "zCLI instance not available"}
    
    try:
        # Attempt to create a new zCLI instance with minimal config
        test_cli = zCLI({"zWorkspace": "."})
        
        # Verify basic attributes exist
        assert hasattr(test_cli, 'config'), "Missing config attribute"
        assert hasattr(test_cli, 'display'), "Missing display attribute"
        assert hasattr(test_cli, 'logger'), "Missing logger attribute"
        
        # Verify workspace is set
        assert test_cli.config.zWorkspace is not None, "zWorkspace not set"
        
        zcli.display.text("  → zCLI instance created")
        zcli.display.text("  → config attribute exists")
        zcli.display.text("  → display attribute exists")
        zcli.display.text("  → logger attribute exists")
        zcli.display.text("  → zWorkspace is set")
        
        return {"status": "passed", "test": "test_initialization"}
    
    except Exception as e:
        zcli.display.error(f"  ❌ FAILED: {str(e)}")
        return {"status": "failed", "test": "test_initialization", "error": str(e)}


def test_workspace_required(zcli=None):
    """
    Test 2: Workspace Validation
    Verify that zCLI fails when zWorkspace is missing (fail-fast).
    """
    if not zcli:
        return {"error": "zCLI instance not available"}
    
    try:
        # Attempt to create zCLI without zWorkspace
        try:
            test_cli = zCLI({})  # Missing zWorkspace
            
            # If we get here, the test FAILED (should have raised error)
            zcli.display.error("  ❌ FAILED: zCLI did not raise error for missing zWorkspace")
            return {"status": "failed", "test": "test_workspace_required", "error": "No exception raised"}
        
        except (ConfigValidationError, TypeError, KeyError) as expected_error:
            # This is the EXPECTED behavior - zCLI should fail without zWorkspace
            zcli.display.text(f"  → Exception raised as expected: {type(expected_error).__name__}")
            zcli.display.text(f"  → Error message: {str(expected_error)}")
            zcli.display.text("  → Fail-fast validation working correctly")
            
            return {"status": "passed", "test": "test_workspace_required"}
    
    except Exception as e:
        zcli.display.error(f"  ❌ UNEXPECTED ERROR: {str(e)}")
        return {"status": "failed", "test": "test_workspace_required", "error": str(e)}

