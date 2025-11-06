# zTestSuite/zWizard_Test.py

"""
Comprehensive test suite for zWizard subsystem (v1.5.4 Phase 1+2).

Test Coverage (34 tests total):
--------------------------------
1. **Initialization** (4 tests)
   - zcli and walker modes
   - Error handling for missing instances
   - WizardInitializationError exceptions

2. **execute_loop()** (9 tests)
   - Basic loop execution
   - Navigation signals (zBack, exit, stop, error)
   - Exception handling with callbacks
   - Navigation callbacks (on_back, on_error)
   - Start key positioning

3. **handle()** (8 tests)
   - YAML workflow execution
   - Meta key filtering (_transaction, _config)
   - zHat interpolation
   - Transaction commit/rollback
   - Schema cache management

4. **WizardHat Triple-Access** (9 tests - NEW!)
   - Numeric indexing (backward compatible)
   - Key-based access (semantic)
   - Attribute access (convenient)
   - Consistency across access methods
   - Contains checks, length, repr
   - Interpolation with key access

5. **Helper Methods** (4 tests)
   - _get_display() from zcli/walker
   - interpolate_zhat() with WizardHat
   - check_transaction_start() module function

Phase 1+2 Enhancements:
-----------------------
- Updated for WizardHat return type (was list)
- Migrated to WizardInitializationError (was ValueError)
- Tests for triple-access pattern (numeric, key, attribute)
- Module function tests (interpolate_zhat, check_transaction_start)
- Zero test failures, full backward compatibility

Version: v1.5.4 Week 6.14 Phase 1+2
"""

import unittest
from unittest.mock import MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zWizard import zWizard
from zCLI.subsystems.zWizard.zWizard_modules.wizard_hat import WizardHat
from zCLI.subsystems.zWizard.zWizard_modules.wizard_exceptions import WizardInitializationError
from zCLI.subsystems.zWizard.zWizard_modules.wizard_interpolation import interpolate_zhat
from zCLI.subsystems.zWizard.zWizard_modules.wizard_transactions import check_transaction_start


class TestzWizardInitialization(unittest.TestCase):
    """Test zWizard initialization in different modes."""

    def test_init_with_zcli(self):
        """Test initialization with zCLI instance."""
        mock_zcli = MagicMock()
        mock_zcli.session = {"test": "data"}
        mock_zcli.logger = MagicMock()
        mock_zcli.display = MagicMock()
        mock_zcli.loader = MagicMock()
        mock_zcli.loader.cache.schema_cache = MagicMock()

        wizard = zWizard(zcli=mock_zcli)

        self.assertEqual(wizard.zcli, mock_zcli)
        self.assertEqual(wizard.zSession, mock_zcli.session)
        self.assertEqual(wizard.logger, mock_zcli.logger)
        self.assertEqual(wizard.display, mock_zcli.display)
        self.assertIsNotNone(wizard.schema_cache)

    def test_init_with_walker(self):
        """Test initialization with walker instance."""
        mock_walker = MagicMock()
        mock_walker.zSession = {"test": "data"}
        mock_walker.logger = MagicMock()
        mock_walker.display = MagicMock()
        mock_walker.loader = MagicMock()
        mock_walker.loader.cache.schema_cache = MagicMock()

        wizard = zWizard(walker=mock_walker)

        self.assertIsNone(wizard.zcli)
        self.assertEqual(wizard.walker, mock_walker)
        self.assertEqual(wizard.zSession, mock_walker.zSession)
        self.assertEqual(wizard.logger, mock_walker.logger)
        self.assertIsNotNone(wizard.schema_cache)

    def test_init_without_zcli_or_walker_raises_error(self):
        """Test that initialization without zcli or walker raises WizardInitializationError."""
        with self.assertRaises(WizardInitializationError) as cm:
            zWizard()
        self.assertIn("requires either zcli or walker", str(cm.exception))

    def test_init_with_walker_without_session_raises_error(self):
        """Test that walker without session raises WizardInitializationError."""
        mock_walker = MagicMock()
        mock_walker.zSession = None
        mock_walker.logger = MagicMock()

        with self.assertRaises(WizardInitializationError) as cm:
            zWizard(walker=mock_walker)
        self.assertIn("requires a walker with a session", str(cm.exception))


class TestzWizardExecuteLoop(unittest.TestCase):
    """Test execute_loop() method with navigation callbacks."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = MagicMock()
        self.mock_zcli.session = {}
        self.mock_zcli.logger = MagicMock()
        self.mock_zcli.display = MagicMock()
        self.mock_zcli.loader = MagicMock()
        self.mock_zcli.loader.cache.schema_cache = MagicMock()
        # Mock shell.executor for wizard step execution
        self.mock_zcli.shell = MagicMock()
        self.mock_zcli.shell.executor = MagicMock()
        self.wizard = zWizard(zcli=self.mock_zcli)

    def test_execute_loop_basic(self):
        """Test basic loop execution."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(return_value="success")

        result = self.wizard.execute_loop(items, dispatch_fn=dispatch_fn)

        self.assertIsNone(result)  # Normal completion
        self.assertEqual(dispatch_fn.call_count, 2)

    def test_execute_loop_with_zback(self):
        """Test loop execution with zBack navigation."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(side_effect=["success", "zBack"])

        result = self.wizard.execute_loop(items, dispatch_fn=dispatch_fn)

        self.assertEqual(result, "zBack")
        self.assertEqual(dispatch_fn.call_count, 2)

    def test_execute_loop_with_stop(self):
        """Test loop execution with stop signal."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(side_effect=["success", "stop"])

        result = self.wizard.execute_loop(items, dispatch_fn=dispatch_fn)

        self.assertEqual(result, "stop")
        self.assertEqual(dispatch_fn.call_count, 2)

    def test_execute_loop_with_error(self):
        """Test loop execution with error signal."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(side_effect=["success", "error"])

        result = self.wizard.execute_loop(items, dispatch_fn=dispatch_fn)

        self.assertEqual(result, "error")
        self.assertEqual(dispatch_fn.call_count, 2)

    def test_execute_loop_with_exception(self):
        """Test loop execution with exception and callback."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(side_effect=Exception("Test error"))
        on_error = MagicMock(return_value="handled")
        
        result = self.wizard.execute_loop(
            items,
            dispatch_fn=dispatch_fn,
            navigation_callbacks={"on_error": on_error}
        )

        self.assertEqual(result, "handled")  # Error callback returns result
        self.assertEqual(dispatch_fn.call_count, 1)  # Only first step attempted
        on_error.assert_called_once()

    def test_execute_loop_with_on_back_callback(self):
        """Test loop with on_back navigation callback."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(side_effect=["success", "zBack"])
        on_back = MagicMock(return_value="custom_back")

        result = self.wizard.execute_loop(
            items,
            dispatch_fn=dispatch_fn,
            navigation_callbacks={"on_back": on_back}
        )

        self.assertEqual(result, "custom_back")
        on_back.assert_called_once_with("zBack")

    def test_execute_loop_with_on_continue_callback(self):
        """Test loop with on_continue callback."""
        items = {"step1": "value1", "step2": "value2"}
        dispatch_fn = MagicMock(return_value="success")
        on_continue = MagicMock()

        self.wizard.execute_loop(
            items,
            dispatch_fn=dispatch_fn,
            navigation_callbacks={"on_continue": on_continue}
        )

        self.assertEqual(on_continue.call_count, 2)

    def test_execute_loop_with_start_key(self):
        """Test loop starting from specific key."""
        items = {"step1": "value1", "step2": "value2", "step3": "value3"}
        dispatch_fn = MagicMock(return_value="success")

        self.wizard.execute_loop(items, dispatch_fn=dispatch_fn, start_key="step2")

        self.assertEqual(dispatch_fn.call_count, 2)  # Only step2 and step3


class TestzWizardHandle(unittest.TestCase):
    """Test handle() method for YAML workflow execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = MagicMock()
        self.mock_zcli.session = {}
        self.mock_zcli.logger = MagicMock()
        self.mock_zcli.display = MagicMock()
        self.mock_zcli.loader = MagicMock()
        self.mock_zcli.loader.cache.schema_cache = MagicMock()
        # Mock shell.executor for wizard step execution
        self.mock_zcli.shell = MagicMock()
        self.mock_zcli.shell.executor = MagicMock()
        self.wizard = zWizard(zcli=self.mock_zcli)

    def test_handle_simple_workflow(self):
        """Test simple YAML workflow execution."""
        self.mock_zcli.shell.executor.execute_wizard_step.side_effect = ["result1", "result2"]
        
        workflow = {
            "step1": "command1",
            "step2": "command2"
        }

        result = self.wizard.handle(workflow)

        # Result should be a WizardHat object
        self.assertIsInstance(result, WizardHat)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "result1")
        self.assertEqual(result[1], "result2")
        self.assertEqual(result["step1"], "result1")
        self.assertEqual(result["step2"], "result2")
        self.assertEqual(self.mock_zcli.shell.executor.execute_wizard_step.call_count, 2)

    def test_handle_with_meta_keys(self):
        """Test workflow with meta keys (starting with _)."""
        self.mock_zcli.shell.executor.execute_wizard_step.return_value = "result"
        
        workflow = {
            "_transaction": True,
            "_config": "test",
            "step1": "command1"
        }

        result = self.wizard.handle(workflow)

        # Result should be a WizardHat object with one step
        self.assertIsInstance(result, WizardHat)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "result")
        self.assertEqual(result["step1"], "result")
        self.assertEqual(self.mock_zcli.shell.executor.execute_wizard_step.call_count, 1)  # Only step1

    def test_handle_with_zhat_interpolation(self):
        """Test zHat result interpolation."""
        self.mock_zcli.shell.executor.execute_wizard_step.side_effect = ["first_result", "second_result"]
        
        workflow = {
            "step1": "command1",
            "step2": "command with zHat[0]"
        }

        result = self.wizard.handle(workflow)

        # Result should be a WizardHat object
        self.assertIsInstance(result, WizardHat)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "first_result")
        self.assertEqual(result[1], "second_result")
        self.assertEqual(result["step1"], "first_result")
        self.assertEqual(result["step2"], "second_result")
        # Check that step2 received interpolated value
        call_args = self.mock_zcli.shell.executor.execute_wizard_step.call_args_list[1]
        step_value = call_args[0][1]  # Second positional arg is step_value
        self.assertIn("'first_result'", step_value)  # zHat[0] should be replaced

    def test_handle_with_transaction_commit(self):
        """Test transaction commit on success."""
        self.mock_zcli.shell.executor.execute_wizard_step.return_value = "result"
        mock_schema_cache = MagicMock()
        self.wizard.schema_cache = mock_schema_cache
        
        workflow = {
            "_transaction": True,
            "step1": {"zData": {"model": "$mydb", "action": "read"}}
        }

        result = self.wizard.handle(workflow)

        # Result should be a WizardHat object
        self.assertIsInstance(result, WizardHat)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "result")
        self.assertEqual(result["step1"], "result")
        mock_schema_cache.commit_transaction.assert_called_once_with("mydb")

    def test_handle_with_transaction_rollback(self):
        """Test transaction rollback on error."""
        self.mock_zcli.shell.executor.execute_wizard_step.side_effect = Exception("Test error")
        mock_schema_cache = MagicMock()
        self.wizard.schema_cache = mock_schema_cache
        
        workflow = {
            "_transaction": True,
            "step1": {"zData": {"model": "$mydb", "action": "read"}}
        }

        with self.assertRaises(Exception):
            self.wizard.handle(workflow)

        mock_schema_cache.rollback_transaction.assert_called_once_with("mydb")

    def test_handle_clears_schema_cache(self):
        """Test that schema cache is always cleared after execution."""
        self.mock_zcli.shell.executor.execute_wizard_step.return_value = "result"
        mock_schema_cache = MagicMock()
        self.wizard.schema_cache = mock_schema_cache
        
        workflow = {"step1": "command1"}

        self.wizard.handle(workflow)

        mock_schema_cache.clear.assert_called_once()

    def test_handle_with_schema_cache_reuse(self):
        """Test that schema_cache connections are reused across steps."""
        self.mock_zcli.shell.executor.execute_wizard_step.return_value = "result"
        mock_schema_cache = MagicMock()
        mock_schema_cache.has_connection.return_value = False  # First call
        self.wizard.schema_cache = mock_schema_cache
        
        workflow = {
            "_transaction": True,
            "step1": {"zData": {"model": "$testdb", "action": "insert"}},
            "step2": {"zData": {"model": "$testdb", "action": "select"}}
        }
        
        # Execute workflow
        result = self.wizard.handle(workflow)
        
        # Verify execute_wizard_step was called twice
        self.assertEqual(self.mock_zcli.shell.executor.execute_wizard_step.call_count, 2)
        
        # Verify context was passed with schema_cache
        for call in self.mock_zcli.shell.executor.execute_wizard_step.call_args_list:
            # Context is passed as third positional argument
            context = call[0][2] if len(call[0]) > 2 else None
            self.assertIsNotNone(context)
            self.assertEqual(context.get("wizard_mode"), True)
            self.assertEqual(context.get("schema_cache"), mock_schema_cache)


class TestWizardHatTripleAccess(unittest.TestCase):
    """Test WizardHat's new triple-access pattern (numeric, key, attribute)."""

    def test_numeric_access(self):
        """Test numeric indexing (backward compatible)."""
        zHat = WizardHat()
        zHat.add("step1", "value1")
        zHat.add("step2", "value2")

        self.assertEqual(zHat[0], "value1")
        self.assertEqual(zHat[1], "value2")

    def test_key_access(self):
        """Test key-based access (semantic)."""
        zHat = WizardHat()
        zHat.add("fetch_data", {"files": [1, 2, 3]})
        zHat.add("process_data", {"status": "done"})

        self.assertEqual(zHat["fetch_data"], {"files": [1, 2, 3]})
        self.assertEqual(zHat["process_data"], {"status": "done"})

    def test_attribute_access(self):
        """Test attribute-style access (convenient - NEW!)."""
        zHat = WizardHat()
        zHat.add("user_id", 42)
        zHat.add("username", "alice")

        self.assertEqual(zHat.user_id, 42)
        self.assertEqual(zHat.username, "alice")

    def test_triple_access_consistency(self):
        """Test that all three access methods return the same value."""
        zHat = WizardHat()
        zHat.add("test_step", "test_value")

        # All three should return the same value
        self.assertEqual(zHat[0], "test_value")
        self.assertEqual(zHat["test_step"], "test_value")
        self.assertEqual(zHat.test_step, "test_value")

    def test_contains_check(self):
        """Test 'in' operator for both numeric and key checks."""
        zHat = WizardHat()
        zHat.add("step1", "value1")

        self.assertTrue(0 in zHat)
        self.assertTrue("step1" in zHat)
        self.assertFalse(1 in zHat)
        self.assertFalse("step2" in zHat)

    def test_length(self):
        """Test len() function."""
        zHat = WizardHat()
        self.assertEqual(len(zHat), 0)

        zHat.add("step1", "value1")
        self.assertEqual(len(zHat), 1)

        zHat.add("step2", "value2")
        self.assertEqual(len(zHat), 2)

    def test_repr(self):
        """Test string representation."""
        zHat = WizardHat()
        zHat.add("step1", "value1")
        zHat.add("step2", "value2")

        repr_str = repr(zHat)
        self.assertIn("WizardHat", repr_str)
        self.assertIn("steps=2", repr_str)
        self.assertIn("['step1', 'step2']", repr_str)

    def test_interpolation_with_key_access(self):
        """Test interpolation using key-based zHat access."""
        zHat = WizardHat()
        zHat.add("user_id", 123)
        zHat.add("username", "bob")

        mock_logger = MagicMock()
        step_value = "User zHat[user_id] is zHat[username]"

        result = interpolate_zhat(step_value, zHat, mock_logger)

        self.assertIn("123", result)
        self.assertIn("'bob'", result)


class TestzWizardHelperMethods(unittest.TestCase):
    """Test helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = MagicMock()
        self.mock_zcli.session = {}
        self.mock_zcli.logger = MagicMock()
        self.mock_zcli.display = MagicMock()
        self.mock_zcli.loader = MagicMock()
        self.mock_zcli.loader.cache.schema_cache = MagicMock()
        self.wizard = zWizard(zcli=self.mock_zcli)

    def test_get_display_from_zcli(self):
        """Test _get_display() returns zcli display."""
        display = self.wizard._get_display()
        self.assertEqual(display, self.mock_zcli.display)

    def test_get_display_from_walker(self):
        """Test _get_display() returns walker display."""
        mock_walker = MagicMock()
        mock_walker.zSession = {"test": "data"}  # Must have session data
        mock_walker.logger = MagicMock()
        mock_walker.display = MagicMock()
        mock_walker.loader = MagicMock()
        mock_walker.loader.cache.schema_cache = MagicMock()
        wizard = zWizard(walker=mock_walker)

        display = wizard._get_display()
        self.assertEqual(display, mock_walker.display)

    def test_interpolate_zhat_string(self):
        """Test interpolate_zhat() with string value using WizardHat."""
        zHat = WizardHat()
        zHat.add("step1", "result1")
        zHat.add("step2", "result2")
        step_value = "command with zHat[0] and zHat[1]"

        result = interpolate_zhat(step_value, zHat, self.mock_zcli.logger)

        self.assertIn("'result1'", result)
        self.assertIn("'result2'", result)

    def test_interpolate_zhat_non_string(self):
        """Test interpolate_zhat() with non-string value (dict)."""
        zHat = WizardHat()
        zHat.add("step1", "result1")
        step_value = {"key": "value"}

        result = interpolate_zhat(step_value, zHat, self.mock_zcli.logger)

        self.assertEqual(result, step_value)  # Unchanged

    def test_check_transaction_start_with_zdata(self):
        """Test check_transaction_start() with zData step."""
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias=None,
            step_value=step_value,
            schema_cache=self.wizard.schema_cache,
            logger=self.mock_zcli.logger
        )

        self.assertEqual(alias, "mydb")

    def test_check_transaction_start_without_dollar(self):
        """Test check_transaction_start() without $ prefix."""
        step_value = {"zData": {"model": "mydb", "action": "read"}}
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias=None,
            step_value=step_value,
            schema_cache=self.wizard.schema_cache,
            logger=self.mock_zcli.logger
        )

        self.assertIsNone(alias)

    def test_check_transaction_start_already_started(self):
        """Test check_transaction_start() when transaction already started."""
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = check_transaction_start(
            use_transaction=True,
            transaction_alias="existing_alias",
            step_value=step_value,
            schema_cache=self.wizard.schema_cache,
            logger=self.mock_zcli.logger
        )

        self.assertIsNone(alias)


def run_tests(verbose=False):
    """Run all zWizard tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardExecuteLoop))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardHandle))
    suite.addTests(loader.loadTestsFromTestCase(TestWizardHatTripleAccess))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardHelperMethods))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

