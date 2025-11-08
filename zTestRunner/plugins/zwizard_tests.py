# zTestRunner/plugins/zwizard_tests.py
"""
zWizard Comprehensive Test Suite (45 tests)
===========================================

Declarative tests for zWizard subsystem covering all real-world usage patterns.

Test Coverage:
--------------
A. WizardHat Triple-Access (8 tests) - Numeric, key, attribute access patterns
B. Initialization (5 tests) - zcli/walker modes, error handling, schema cache
C. Workflow Execution (10 tests) - handle() method, meta keys, context, caching
D. Interpolation (6 tests) - zHat interpolation with various data types
E. Transactions (6 tests) - Transaction lifecycle, commit, rollback
F. Helper Methods (5 tests) - _get_display, interpolate_zhat, transaction helpers
G. Exception Handling (5 tests) - Custom exceptions, hierarchy, error messages

Note: execute_loop() low-level mechanics are tested in zTestSuite/zWizard_Test.py (9 unit tests)
"""

from typing import Any, Dict, Optional
from zCLI.zCLI import zCLI

__all__ = [
    # WizardHat tests
    "test_wizardhat_creation",
    "test_wizardhat_numeric_access",
    "test_wizardhat_key_access",
    "test_wizardhat_attribute_access",
    "test_wizardhat_triple_access_consistency",
    "test_wizardhat_length",
    "test_wizardhat_contains",
    "test_wizardhat_repr",
    # Initialization tests
    "test_init_zcli_mode",
    "test_init_walker_mode",
    "test_init_missing_instance_error",
    "test_init_walker_missing_session_error",
    "test_init_schema_cache_setup",
    # Workflow execution tests
    "test_handle_simple_workflow",
    "test_handle_with_meta_keys",
    "test_handle_returns_wizardhat",
    "test_handle_empty_workflow",
    "test_handle_single_step",
    "test_handle_multiple_steps",
    "test_handle_with_context",
    "test_handle_context_inheritance",
    "test_handle_schema_cache_cleared",
    "test_handle_schema_cache_reuse",
    # Interpolation tests
    "test_interpolation_numeric_access",
    "test_interpolation_key_access",
    "test_interpolation_mixed_access",
    "test_interpolation_with_dicts",
    "test_interpolation_with_lists",
    "test_interpolation_non_string_passthrough",
    # Transaction tests
    "test_transaction_check_start",
    "test_transaction_no_dollar_prefix",
    "test_transaction_already_started",
    "test_transaction_commit_success",
    "test_transaction_rollback_on_error",
    "test_transaction_disabled",
    # Helper methods tests
    "test_get_display_from_zcli",
    "test_get_display_from_walker",
    "test_interpolate_zhat_string",
    "test_interpolate_zhat_non_string",
    "test_check_transaction_helper",
    # Exception handling tests
    "test_wizard_initialization_error",
    "test_exception_hierarchy",
    "test_exception_messages",
    "test_custom_exception_catching",
    "test_exception_inheritance",
    # Display
    "display_test_results",
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _store_result(
    zcli: Optional[Any],
    test_name: str,
    status: str,
    message: str
) -> Dict[str, Any]:
    """Return test result dict for zWizard/zHat accumulation."""
    result = {"test": test_name, "status": status, "message": message}
    return result


# ============================================================================
# A. WIZARDHAT TRIPLE-ACCESS TESTS (8 tests)
# ============================================================================

def test_wizardhat_creation(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test WizardHat creation and basic functionality"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        assert isinstance(zHat, WizardHat), "Should create WizardHat instance"
        assert len(zHat) == 0, "New WizardHat should be empty"
        
        return _store_result(zcli, "WizardHat: Creation", "PASSED", "Instance created successfully")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Creation", "ERROR", str(e))


def test_wizardhat_numeric_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test numeric indexing: zHat[0], zHat[1]"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("step1", "value1")
        zHat.add("step2", "value2")
        
        assert zHat[0] == "value1", "Numeric access [0] failed"
        assert zHat[1] == "value2", "Numeric access [1] failed"
        
        return _store_result(zcli, "WizardHat: Numeric access", "PASSED", "zHat[0], zHat[1] work")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Numeric access", "ERROR", str(e))


def test_wizardhat_key_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test key-based access: zHat['step_name']"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("fetch_data", {"files": [1, 2, 3]})
        zHat.add("process_data", {"status": "done"})
        
        assert zHat["fetch_data"] == {"files": [1, 2, 3]}, "Key access failed"
        assert zHat["process_data"] == {"status": "done"}, "Key access failed"
        
        return _store_result(zcli, "WizardHat: Key access", "PASSED", "zHat['key'] works")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Key access", "ERROR", str(e))


def test_wizardhat_attribute_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test attribute access: zHat.step_name"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("user_id", 42)
        zHat.add("username", "alice")
        
        assert zHat.user_id == 42, "Attribute access failed"
        assert zHat.username == "alice", "Attribute access failed"
        
        return _store_result(zcli, "WizardHat: Attribute access", "PASSED", "zHat.key works")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Attribute access", "ERROR", str(e))


def test_wizardhat_triple_access_consistency(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test that numeric, key, and attribute access return same value"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("test_step", "test_value")
        
        numeric = zHat[0]
        key_based = zHat["test_step"]
        attribute = zHat.test_step
        
        assert numeric == key_based == attribute == "test_value", "Triple access inconsistent"
        
        return _store_result(zcli, "WizardHat: Triple access consistency", "PASSED", "All methods return same value")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Triple access consistency", "ERROR", str(e))


def test_wizardhat_length(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test len() function on WizardHat"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        assert len(zHat) == 0, "Empty WizardHat should have length 0"
        
        zHat.add("step1", "value1")
        assert len(zHat) == 1, "WizardHat should have length 1"
        
        zHat.add("step2", "value2")
        assert len(zHat) == 2, "WizardHat should have length 2"
        
        return _store_result(zcli, "WizardHat: Length", "PASSED", "len() function works")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Length", "ERROR", str(e))


def test_wizardhat_contains(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test 'in' operator for WizardHat"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("step1", "value1")
        
        assert 0 in zHat, "Numeric index should be in zHat"
        assert "step1" in zHat, "Key should be in zHat"
        assert 1 not in zHat, "Non-existent index should not be in zHat"
        assert "step2" not in zHat, "Non-existent key should not be in zHat"
        
        return _store_result(zcli, "WizardHat: Contains", "PASSED", "'in' operator works")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Contains", "ERROR", str(e))


def test_wizardhat_repr(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test string representation"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        
        zHat = WizardHat()
        zHat.add("step1", "value1")
        zHat.add("step2", "value2")
        
        repr_str = repr(zHat)
        assert "WizardHat" in repr_str, "repr should contain 'WizardHat'"
        assert "steps=2" in repr_str, "repr should contain step count"
        assert "step1" in repr_str or "['step1', 'step2']" in repr_str, "repr should contain keys"
        
        return _store_result(zcli, "WizardHat: Repr", "PASSED", "String representation works")
    except Exception as e:
        return _store_result(zcli, "WizardHat: Repr", "ERROR", str(e))


# ============================================================================
# B. INITIALIZATION TESTS (5 tests)
# ============================================================================

def test_init_zcli_mode(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zWizard initialization with zcli instance"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        mock_zcli = MagicMock()
        mock_zcli.session = {"test": "data"}
        mock_zcli.logger = MagicMock()
        mock_zcli.display = MagicMock()
        mock_zcli.loader = MagicMock()
        mock_zcli.loader.cache.schema_cache = MagicMock()
        
        wizard = zWizard(zcli=mock_zcli)
        
        assert wizard.zcli == mock_zcli, "Should store zcli instance"
        assert wizard.zSession == mock_zcli.session, "Should use zcli session"
        assert wizard.logger == mock_zcli.logger, "Should use zcli logger"
        assert wizard.walker is None, "walker should be None in zcli mode"
        
        return _store_result(zcli, "Init: zcli mode", "PASSED", "zcli mode initialized correctly")
    except Exception as e:
        return _store_result(zcli, "Init: zcli mode", "ERROR", str(e))


def test_init_walker_mode(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zWizard initialization with walker instance"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        mock_walker = MagicMock()
        mock_walker.zSession = {"test": "data"}
        mock_walker.logger = MagicMock()
        mock_walker.display = MagicMock()
        mock_walker.loader = MagicMock()
        mock_walker.loader.cache.schema_cache = MagicMock()
        
        wizard = zWizard(walker=mock_walker)
        
        assert wizard.walker == mock_walker, "Should store walker instance"
        assert wizard.zSession == mock_walker.zSession, "Should use walker session"
        assert wizard.logger == mock_walker.logger, "Should use walker logger"
        assert wizard.zcli is None, "zcli should be None in walker mode"
        
        return _store_result(zcli, "Init: walker mode", "PASSED", "walker mode initialized correctly")
    except Exception as e:
        return _store_result(zcli, "Init: walker mode", "ERROR", str(e))


def test_init_missing_instance_error(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zWizard raises error when neither zcli nor walker provided"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import WizardInitializationError
        
        try:
            wizard = zWizard()
            return _store_result(zcli, "Init: Missing instance error", "ERROR", "Should have raised WizardInitializationError")
        except WizardInitializationError as e:
            if "requires either zcli or walker" in str(e):
                return _store_result(zcli, "Init: Missing instance error", "PASSED", "Correctly rejects missing instance")
            else:
                return _store_result(zcli, "Init: Missing instance error", "ERROR", f"Wrong error message: {e}")
    except Exception as e:
        return _store_result(zcli, "Init: Missing instance error", "ERROR", str(e))


def test_init_walker_missing_session_error(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zWizard raises error when walker has no session"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import WizardInitializationError
        from unittest.mock import MagicMock
        
        mock_walker = MagicMock()
        mock_walker.zSession = None  # No session!
        mock_walker.logger = MagicMock()
        
        try:
            wizard = zWizard(walker=mock_walker)
            return _store_result(zcli, "Init: Walker session error", "ERROR", "Should have raised error for missing session")
        except WizardInitializationError as e:
            if "session" in str(e).lower():
                return _store_result(zcli, "Init: Walker session error", "PASSED", "Correctly requires walker session")
            else:
                return _store_result(zcli, "Init: Walker session error", "ERROR", f"Wrong error: {e}")
    except Exception as e:
        return _store_result(zcli, "Init: Walker session error", "ERROR", str(e))


def test_init_schema_cache_setup(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test schema_cache is properly initialized"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        mock_zcli = MagicMock()
        mock_zcli.session = {}
        mock_zcli.logger = MagicMock()
        mock_zcli.display = MagicMock()
        mock_zcli.loader = MagicMock()
        mock_schema_cache = MagicMock()
        mock_zcli.loader.cache.schema_cache = mock_schema_cache
        
        wizard = zWizard(zcli=mock_zcli)
        
        assert wizard.schema_cache is not None, "schema_cache should be initialized"
        assert wizard.schema_cache == mock_schema_cache, "schema_cache should reference zcli.loader.cache.schema_cache"
        
        return _store_result(zcli, "Init: Schema cache setup", "PASSED", "schema_cache initialized correctly")
    except Exception as e:
        return _store_result(zcli, "Init: Schema cache setup", "ERROR", str(e))


# ============================================================================
# C. WORKFLOW EXECUTION (handle) TESTS (10 tests)
# ============================================================================

def test_handle_simple_workflow(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zWizard.handle() with simple workflow"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        # Mock shell executor
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.side_effect = ["result1", "result2"]
        
        wizard = zWizard(zcli=zcli)
        workflow = {"step1": "command1", "step2": "command2"}
        
        result = wizard.handle(workflow)
        
        assert result is not None, "Should return WizardHat"
        assert len(result) == 2, "Should have 2 results"
        
        return _store_result(zcli, "Handle: Simple workflow", "PASSED", "Simple 2-step workflow executes")
    except Exception as e:
        return _store_result(zcli, "Handle: Simple workflow", "ERROR", str(e))


def test_handle_with_meta_keys(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test workflow with meta keys (starting with _)"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.return_value = "result"
        
        wizard = zWizard(zcli=zcli)
        workflow = {
            "_transaction": True,
            "_config": "test",
            "step1": "command1"
        }
        
        result = wizard.handle(workflow)
        
        assert len(result) == 1, "Meta keys (_transaction, _config) should be filtered out"
        
        return _store_result(zcli, "Handle: Meta keys filtering", "PASSED", "Meta keys filtered correctly")
    except Exception as e:
        return _store_result(zcli, "Handle: Meta keys filtering", "ERROR", str(e))


def test_handle_returns_wizardhat(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() returns WizardHat instance"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.return_value = "result"
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "command1"})
        
        assert isinstance(result, WizardHat), "Should return WizardHat instance"
        
        return _store_result(zcli, "Handle: Returns WizardHat", "PASSED", "Returns WizardHat instance")
    except Exception as e:
        return _store_result(zcli, "Handle: Returns WizardHat", "ERROR", str(e))


def test_handle_empty_workflow(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() with empty workflow"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({})
        
        assert len(result) == 0, "Empty workflow should return empty WizardHat"
        
        return _store_result(zcli, "Handle: Empty workflow", "PASSED", "Empty workflow handled gracefully")
    except Exception as e:
        return _store_result(zcli, "Handle: Empty workflow", "ERROR", str(e))


def test_handle_single_step(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() with single step"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.return_value = "single_result"
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "command1"})
        
        assert len(result) == 1, "Should have 1 result"
        assert result[0] == "single_result", "Result should match"
        
        return _store_result(zcli, "Handle: Single step", "PASSED", "Single step workflow works")
    except Exception as e:
        return _store_result(zcli, "Handle: Single step", "ERROR", str(e))


def test_handle_multiple_steps(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() with multiple steps"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.side_effect = ["r1", "r2", "r3", "r4"]
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({
            "step1": "cmd1",
            "step2": "cmd2",
            "step3": "cmd3",
            "step4": "cmd4"
        })
        
        assert len(result) == 4, "Should have 4 results"
        
        return _store_result(zcli, "Handle: Multiple steps", "PASSED", "4-step workflow executes in order")
    except Exception as e:
        return _store_result(zcli, "Handle: Multiple steps", "ERROR", str(e))


def test_handle_with_context(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() passes context to steps"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.return_value = "result"
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "cmd1"})
        
        # Verify context was passed
        call_args = zcli.shell.executor.execute_wizard_step.call_args
        context_arg = call_args[0][2] if len(call_args[0]) > 2 else None
        
        assert context_arg is not None, "Context should be passed"
        assert "zHat" in context_arg, "Context should contain zHat"
        
        return _store_result(zcli, "Handle: Context passing", "PASSED", "Context passed to steps")
    except Exception as e:
        return _store_result(zcli, "Handle: Context passing", "ERROR", str(e))


def test_handle_context_inheritance(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test handle() preserves context between steps"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.side_effect = ["r1", "r2"]
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "cmd1", "step2": "cmd2"})
        
        # Verify both steps got context with same zHat
        calls = zcli.shell.executor.execute_wizard_step.call_args_list
        context1 = calls[0][0][2] if len(calls[0][0]) > 2 else {}
        context2 = calls[1][0][2] if len(calls[1][0]) > 2 else {}
        
        assert context1.get("zHat") is context2.get("zHat"), "zHat should be same object across steps"
        
        return _store_result(zcli, "Handle: Context inheritance", "PASSED", "Context preserved across steps")
    except Exception as e:
        return _store_result(zcli, "Handle: Context inheritance", "ERROR", str(e))


def test_handle_schema_cache_cleared(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test schema cache is cleared after workflow"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.return_value = "result"
        
        mock_schema_cache = MagicMock()
        zcli.loader.cache.schema_cache = mock_schema_cache
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "cmd1"})
        
        mock_schema_cache.clear.assert_called_once()
        
        return _store_result(zcli, "Handle: Schema cache cleared", "PASSED", "Schema cache cleared after workflow")
    except Exception as e:
        return _store_result(zcli, "Handle: Schema cache cleared", "ERROR", str(e))


def test_handle_schema_cache_reuse(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test schema cache is reused across steps"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        if not zcli:
            zcli = zCLI({'zWorkspace': '.', 'zMode': 'Terminal', 'zLoggerLevel': 'ERROR'})
        
        zcli.shell = MagicMock()
        zcli.shell.executor = MagicMock()
        zcli.shell.executor.execute_wizard_step.side_effect = ["r1", "r2"]
        
        mock_schema_cache = MagicMock()
        zcli.loader.cache.schema_cache = mock_schema_cache
        
        wizard = zWizard(zcli=zcli)
        result = wizard.handle({"step1": "cmd1", "step2": "cmd2"})
        
        # Verify both steps got same schema_cache
        calls = zcli.shell.executor.execute_wizard_step.call_args_list
        ctx1 = calls[0][0][2] if len(calls[0][0]) > 2 else {}
        ctx2 = calls[1][0][2] if len(calls[1][0]) > 2 else {}
        
        assert ctx1.get("schema_cache") is ctx2.get("schema_cache"), "schema_cache should be reused"
        
        return _store_result(zcli, "Handle: Schema cache reuse", "PASSED", "Schema cache reused across steps")
    except Exception as e:
        return _store_result(zcli, "Handle: Schema cache reuse", "ERROR", str(e))


# ============================================================================
# D. INTERPOLATION TESTS (6 tests)
# ============================================================================

def test_interpolation_numeric_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zHat interpolation with numeric access"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("step1", "result1")
        zHat.add("step2", "result2")
        
        mock_logger = MagicMock()
        step_value = "command with zHat[0] and zHat[1]"
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        assert "'result1'" in result, "zHat[0] should be interpolated"
        assert "'result2'" in result, "zHat[1] should be interpolated"
        
        return _store_result(zcli, "Interpolation: Numeric access", "PASSED", "zHat[0], zHat[1] interpolated")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Numeric access", "ERROR", str(e))


def test_interpolation_key_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zHat interpolation with key-based access"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("user_id", 123)
        zHat.add("username", "bob")
        
        mock_logger = MagicMock()
        step_value = "User zHat[user_id] is zHat[username]"
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        assert "123" in result, "zHat[user_id] should be interpolated"
        assert "'bob'" in result, "zHat[username] should be interpolated"
        
        return _store_result(zcli, "Interpolation: Key access", "PASSED", "zHat[key] interpolated")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Key access", "ERROR", str(e))


def test_interpolation_mixed_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test zHat interpolation with mixed numeric and key access"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("data", "mydata")
        zHat.add("count", 42)
        
        mock_logger = MagicMock()
        step_value = "First: zHat[0], Named: zHat[data], Count: zHat[1]"
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        assert "'mydata'" in result, "Both numeric and key access should work"
        assert "42" in result, "Both access methods should interpolate"
        
        return _store_result(zcli, "Interpolation: Mixed access", "PASSED", "Mixed numeric/key access works")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Mixed access", "ERROR", str(e))


def test_interpolation_with_dicts(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test interpolation works with dict step values"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("name", "test")
        
        mock_logger = MagicMock()
        step_value = {
            "key1": "value with zHat[0]",
            "key2": "nested zHat[name]"
        }
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        assert "'test'" in result["key1"], "Dict values should be interpolated"
        assert "'test'" in result["key2"], "Nested dict values should be interpolated"
        
        return _store_result(zcli, "Interpolation: Dicts", "PASSED", "Dict interpolation works")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Dicts", "ERROR", str(e))


def test_interpolation_with_lists(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test interpolation works with list step values"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("item", "apple")
        
        mock_logger = MagicMock()
        step_value = ["item: zHat[0]", "name: zHat[item]"]
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        assert "'apple'" in result[0], "List items should be interpolated"
        assert "'apple'" in result[1], "All list items should be interpolated"
        
        return _store_result(zcli, "Interpolation: Lists", "PASSED", "List interpolation works")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Lists", "ERROR", str(e))


def test_interpolation_non_string_passthrough(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test non-string values pass through unchanged"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("num", 42)
        
        mock_logger = MagicMock()
        
        # Test various non-string types
        assert interpolate_zhat(123, zHat, mock_logger) == 123, "Integers should pass through"
        assert interpolate_zhat(True, zHat, mock_logger) == True, "Booleans should pass through"
        assert interpolate_zhat(None, zHat, mock_logger) is None, "None should pass through"
        
        return _store_result(zcli, "Interpolation: Non-string passthrough", "PASSED", "Non-strings pass through unchanged")
    except Exception as e:
        return _store_result(zcli, "Interpolation: Non-string passthrough", "ERROR", str(e))


# ============================================================================
# E. TRANSACTION TESTS (6 tests)
# ============================================================================

def test_transaction_check_start(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test check_transaction_start with $ prefix"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import check_transaction_start
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias=None,
            step_value=step_value,
            schema_cache=mock_schema_cache,
            logger=mock_logger
        )
        
        assert alias == "mydb", "Should extract alias from $mydb"
        
        return _store_result(zcli, "Transaction: Check start", "PASSED", "$ prefix triggers transaction")
    except Exception as e:
        return _store_result(zcli, "Transaction: Check start", "ERROR", str(e))


def test_transaction_no_dollar_prefix(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test transaction doesn't start without $ prefix"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import check_transaction_start
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        step_value = {"zData": {"model": "mydb", "action": "read"}}  # No $ prefix
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias=None,
            step_value=step_value,
            schema_cache=mock_schema_cache,
            logger=mock_logger
        )
        
        assert alias is None, "Should not start transaction without $ prefix"
        
        return _store_result(zcli, "Transaction: No $ prefix", "PASSED", "Transaction requires $ prefix")
    except Exception as e:
        return _store_result(zcli, "Transaction: No $ prefix", "ERROR", str(e))


def test_transaction_already_started(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test transaction doesn't restart if already started"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import check_transaction_start
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias="existing_alias",  # Already started!
            step_value=step_value,
            schema_cache=mock_schema_cache,
            logger=mock_logger
        )
        
        assert alias is None, "Should not restart transaction"
        
        return _store_result(zcli, "Transaction: Already started", "PASSED", "Transaction not restarted")
    except Exception as e:
        return _store_result(zcli, "Transaction: Already started", "ERROR", str(e))


def test_transaction_commit_success(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test transaction commit on success"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import commit_transaction
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        commit_transaction(
            use_transaction=True,
            transaction_alias="mydb",
            schema_cache=mock_schema_cache,
            logger=mock_logger
        )
        
        mock_schema_cache.commit_transaction.assert_called_once_with("mydb")
        
        return _store_result(zcli, "Transaction: Commit success", "PASSED", "Transaction commits on success")
    except Exception as e:
        return _store_result(zcli, "Transaction: Commit success", "ERROR", str(e))


def test_transaction_rollback_on_error(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test transaction rollback on error"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import rollback_transaction
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        test_error = Exception("Test error")
        
        rollback_transaction(
            use_transaction=True,
            transaction_alias="mydb",
            schema_cache=mock_schema_cache,
            logger=mock_logger,
            error=test_error
        )
        
        mock_schema_cache.rollback_transaction.assert_called_once_with("mydb")
        
        return _store_result(zcli, "Transaction: Rollback on error", "PASSED", "Transaction rolls back on error")
    except Exception as e:
        return _store_result(zcli, "Transaction: Rollback on error", "ERROR", str(e))


def test_transaction_disabled(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test transaction functions do nothing when disabled"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import (
            check_transaction_start, commit_transaction, rollback_transaction
        )
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        # All should do nothing when use_transaction=False
        alias = check_transaction_start(False, None, {}, mock_schema_cache, mock_logger)
        assert alias is None, "check_transaction_start should return None"
        
        commit_transaction(False, "mydb", mock_schema_cache, mock_logger)
        assert not mock_schema_cache.commit_transaction.called, "commit should not be called"
        
        rollback_transaction(False, "mydb", mock_schema_cache, mock_logger, Exception())
        assert not mock_schema_cache.rollback_transaction.called, "rollback should not be called"
        
        return _store_result(zcli, "Transaction: Disabled", "PASSED", "Transactions disabled when use_transaction=False")
    except Exception as e:
        return _store_result(zcli, "Transaction: Disabled", "ERROR", str(e))


# ============================================================================
# F. HELPER METHODS TESTS (5 tests)
# ============================================================================

def test_get_display_from_zcli(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test _get_display() returns zcli display"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        mock_zcli = MagicMock()
        mock_zcli.session = {}
        mock_zcli.logger = MagicMock()
        mock_zcli.display = MagicMock()
        mock_zcli.loader = MagicMock()
        mock_zcli.loader.cache.schema_cache = MagicMock()
        
        wizard = zWizard(zcli=mock_zcli)
        display = wizard._get_display()
        
        assert display == mock_zcli.display, "Should return zcli.display"
        
        return _store_result(zcli, "Helpers: _get_display from zcli", "PASSED", "Returns zcli.display")
    except Exception as e:
        return _store_result(zcli, "Helpers: _get_display from zcli", "ERROR", str(e))


def test_get_display_from_walker(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test _get_display() returns walker display"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from unittest.mock import MagicMock
        
        mock_walker = MagicMock()
        mock_walker.zSession = {"test": "data"}
        mock_walker.logger = MagicMock()
        mock_walker.display = MagicMock()
        mock_walker.loader = MagicMock()
        mock_walker.loader.cache.schema_cache = MagicMock()
        
        wizard = zWizard(walker=mock_walker)
        display = wizard._get_display()
        
        assert display == mock_walker.display, "Should return walker.display"
        
        return _store_result(zcli, "Helpers: _get_display from walker", "PASSED", "Returns walker.display")
    except Exception as e:
        return _store_result(zcli, "Helpers: _get_display from walker", "ERROR", str(e))


def test_interpolate_zhat_string(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test interpolate_zhat() with string value"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("step1", "result1")
        
        mock_logger = MagicMock()
        result = interpolate_zhat("value: zHat[0]", zHat, mock_logger)
        
        assert "'result1'" in result, "Should interpolate string"
        
        return _store_result(zcli, "Helpers: interpolate_zhat string", "PASSED", "String interpolation works")
    except Exception as e:
        return _store_result(zcli, "Helpers: interpolate_zhat string", "ERROR", str(e))


def test_interpolate_zhat_non_string(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test interpolate_zhat() with non-string value (dict)"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
        from unittest.mock import MagicMock
        
        zHat = WizardHat()
        zHat.add("step1", "result1")
        
        mock_logger = MagicMock()
        step_value = {"key": "value"}
        
        result = interpolate_zhat(step_value, zHat, mock_logger)
        
        # Dict values should be interpolated, but dict structure preserved
        assert isinstance(result, dict), "Should return dict"
        
        return _store_result(zcli, "Helpers: interpolate_zhat non-string", "PASSED", "Non-string handled correctly")
    except Exception as e:
        return _store_result(zcli, "Helpers: interpolate_zhat non-string", "ERROR", str(e))


def test_check_transaction_helper(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test check_transaction_start() helper function"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import check_transaction_start
        from unittest.mock import MagicMock
        
        mock_schema_cache = MagicMock()
        mock_logger = MagicMock()
        
        # Test with transaction enabled
        step_value = {"zData": {"model": "$testdb", "action": "insert"}}
        alias = check_transaction_start(True, None, step_value, mock_schema_cache, mock_logger)
        
        assert alias == "testdb", "Should return alias"
        
        return _store_result(zcli, "Helpers: check_transaction_start", "PASSED", "Transaction helper works")
    except Exception as e:
        return _store_result(zcli, "Helpers: check_transaction_start", "ERROR", str(e))


# ============================================================================
# G. EXCEPTION HANDLING TESTS (5 tests)
# ============================================================================

def test_wizard_initialization_error(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test WizardInitializationError is raised correctly"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import WizardInitializationError
        
        try:
            wizard = zWizard()  # No zcli or walker
            return _store_result(zcli, "Exceptions: WizardInitializationError", "ERROR", "Should have raised exception")
        except WizardInitializationError:
            return _store_result(zcli, "Exceptions: WizardInitializationError", "PASSED", "Exception raised correctly")
    except Exception as e:
        return _store_result(zcli, "Exceptions: WizardInitializationError", "ERROR", str(e))


def test_exception_hierarchy(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test exception hierarchy (all inherit from zWizardError)"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import (
            zWizardError, WizardInitializationError, WizardExecutionError, WizardRBACError
        )
        
        assert issubclass(WizardInitializationError, zWizardError), "Should inherit from zWizardError"
        assert issubclass(WizardExecutionError, zWizardError), "Should inherit from zWizardError"
        assert issubclass(WizardRBACError, zWizardError), "Should inherit from zWizardError"
        
        return _store_result(zcli, "Exceptions: Hierarchy", "PASSED", "All exceptions inherit from zWizardError")
    except Exception as e:
        return _store_result(zcli, "Exceptions: Hierarchy", "ERROR", str(e))


def test_exception_messages(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test exception messages are descriptive"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import WizardInitializationError
        
        try:
            wizard = zWizard()
        except WizardInitializationError as e:
            msg = str(e)
            assert len(msg) > 10, "Error message should be descriptive"
            assert "zcli" in msg.lower() or "walker" in msg.lower(), "Should mention missing instance"
            return _store_result(zcli, "Exceptions: Messages", "PASSED", "Error messages are descriptive")
        
        return _store_result(zcli, "Exceptions: Messages", "ERROR", "No exception raised")
    except Exception as e:
        return _store_result(zcli, "Exceptions: Messages", "ERROR", str(e))


def test_custom_exception_catching(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test catching specific wizard exceptions"""
    try:
        from zCLI.subsystems.zWizard import zWizard
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import (
            zWizardError, WizardInitializationError
        )
        
        caught_specific = False
        caught_base = False
        
        # Test catching specific exception
        try:
            wizard = zWizard()
        except WizardInitializationError:
            caught_specific = True
        
        # Test catching base exception
        try:
            wizard = zWizard()
        except zWizardError:
            caught_base = True
        
        assert caught_specific, "Should catch WizardInitializationError"
        assert caught_base, "Should catch zWizardError (base)"
        
        return _store_result(zcli, "Exceptions: Catching", "PASSED", "Exceptions can be caught at multiple levels")
    except Exception as e:
        return _store_result(zcli, "Exceptions: Catching", "ERROR", str(e))


def test_exception_inheritance(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test exceptions inherit from Python Exception"""
    try:
        from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import (
            zWizardError, WizardInitializationError, WizardExecutionError, WizardRBACError
        )
        
        assert issubclass(zWizardError, Exception), "zWizardError should inherit from Exception"
        assert issubclass(WizardInitializationError, Exception), "Should inherit from Exception"
        assert issubclass(WizardExecutionError, Exception), "Should inherit from Exception"
        assert issubclass(WizardRBACError, Exception), "Should inherit from Exception"
        
        return _store_result(zcli, "Exceptions: Inheritance", "PASSED", "All inherit from Python Exception")
    except Exception as e:
        return _store_result(zcli, "Exceptions: Inheritance", "ERROR", str(e))


# ============================================================================
# DISPLAY RESULTS
# ============================================================================

def display_test_results(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> None:
    """Display comprehensive test results with statistics."""
    import sys
    
    if not zcli or not context:
        print("\n[ERROR] No zcli or context provided")
        return None
    
    # Get zHat from context (accumulated by zWizard.handle())
    zHat = context.get("zHat")
    if not zHat:
        print("\n[WARN] No zHat found in context")
        return None
    
    # Extract all results from zHat (skip display_and_return itself)
    results = []
    for i in range(len(zHat)):
        result = zHat[i]
        if result and isinstance(result, dict) and "test" in result:
            results.append(result)
    
    if not results:
        print("\n[WARN] No test results found")
        if sys.stdin.isatty():
            input("Press Enter to return to main menu...")
        return None
    
    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASSED")
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    warnings = sum(1 for r in results if r.get("status") == "WARN")
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    # Display header
    print("\n" + "=" * 90)
    print(f"zWizard Comprehensive Test Suite - {total} Tests")
    print("=" * 90 + "\n")
    
    # Display results by category
    categories = {
        "A. WizardHat Triple-Access (8 tests)": [],
        "B. Initialization (5 tests)": [],
        "C. Workflow Execution (10 tests)": [],
        "D. Interpolation (6 tests)": [],
        "E. Transactions (6 tests)": [],
        "F. Helper Methods (5 tests)": [],
        "G. Exception Handling (5 tests)": []
    }
    
    for r in results:
        test_name = r.get("test", "")
        if "WizardHat:" in test_name:
            categories["A. WizardHat Triple-Access (8 tests)"].append(r)
        elif "Init:" in test_name:
            categories["B. Initialization (5 tests)"].append(r)
        elif "Handle:" in test_name:
            categories["C. Workflow Execution (10 tests)"].append(r)
        elif "Interpolation:" in test_name:
            categories["D. Interpolation (6 tests)"].append(r)
        elif "Transaction:" in test_name:
            categories["E. Transactions (6 tests)"].append(r)
        elif "Helpers:" in test_name:
            categories["F. Helper Methods (5 tests)"].append(r)
        elif "Exceptions:" in test_name:
            categories["G. Exception Handling (5 tests)"].append(r)
    
    # Display by category
    for category, tests in categories.items():
        if not tests:
            continue
        
        print(f"{category}")
        print("-" * 90)
        for test in tests:
            status = test.get("status", "UNKNOWN")
            status_symbol = {
                "PASSED": "[OK] ",
                "ERROR": "[ERR]",
                "WARN": "[WARN]"
            }.get(status, "[?]  ")
            
            print(f"  {status_symbol} {test.get('test', 'Unknown'):50s} {test.get('message', '')}")
        print()
    
    # Display summary
    print("=" * 90)
    print(f"SUMMARY: {passed}/{total} passed ({pass_pct:.1f}%) | Errors: {errors} | Warnings: {warnings}")
    print("=" * 90 + "\n")
    
    # Pause for user review
    if sys.stdin.isatty():
        input("Press Enter to return to main menu...")
    
    return None
