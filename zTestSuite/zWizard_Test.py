# zTestSuite/zWizard_Test.py

"""
Comprehensive test suite for zWizard subsystem.

Tests cover:
  - Initialization (zcli and walker modes)
  - execute_loop() with navigation callbacks
  - handle() with YAML workflows
  - Transaction management (begin, commit, rollback)
  - zHat result interpolation
  - Error handling and recovery
  - Shell mode vs Walker mode execution
"""

import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zWizard import zWizard


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
        """Test that initialization without zcli or walker raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            zWizard()
        self.assertIn("requires either zcli or walker", str(cm.exception))

    def test_init_with_walker_without_session_raises_error(self):
        """Test that walker without session raises ValueError."""
        mock_walker = MagicMock()
        mock_walker.zSession = None
        mock_walker.logger = MagicMock()

        with self.assertRaises(ValueError) as cm:
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

        self.assertEqual(result, ["result1", "result2"])
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

        self.assertEqual(result, ["result"])
        self.assertEqual(self.mock_zcli.shell.executor.execute_wizard_step.call_count, 1)  # Only step1

    def test_handle_with_zhat_interpolation(self):
        """Test zHat result interpolation."""
        self.mock_zcli.shell.executor.execute_wizard_step.side_effect = ["first_result", "second_result"]
        
        workflow = {
            "step1": "command1",
            "step2": "command with zHat[0]"
        }

        result = self.wizard.handle(workflow)

        self.assertEqual(result, ["first_result", "second_result"])
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

        self.assertEqual(result, ["result"])
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
        """Test _interpolate_zhat() with string value."""
        zHat = ["result1", "result2"]
        step_value = "command with zHat[0] and zHat[1]"

        result = self.wizard._interpolate_zhat(step_value, zHat)

        self.assertIn("'result1'", result)
        self.assertIn("'result2'", result)

    def test_interpolate_zhat_non_string(self):
        """Test _interpolate_zhat() with non-string value."""
        zHat = ["result1"]
        step_value = {"key": "value"}

        result = self.wizard._interpolate_zhat(step_value, zHat)

        self.assertEqual(result, step_value)  # Unchanged

    def test_check_transaction_start_with_zdata(self):
        """Test _check_transaction_start() with zData step."""
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = self.wizard._check_transaction_start(True, None, step_value)

        self.assertEqual(alias, "mydb")

    def test_check_transaction_start_without_dollar(self):
        """Test _check_transaction_start() without $ prefix."""
        step_value = {"zData": {"model": "mydb", "action": "read"}}
        
        alias = self.wizard._check_transaction_start(True, None, step_value)

        self.assertIsNone(alias)

    def test_check_transaction_start_already_started(self):
        """Test _check_transaction_start() when transaction already started."""
        step_value = {"zData": {"model": "$mydb", "action": "read"}}
        
        alias = self.wizard._check_transaction_start(True, "existing_alias", step_value)

        self.assertIsNone(alias)


def run_tests(verbose=False):
    """Run all zWizard tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardExecuteLoop))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardHandle))
    suite.addTests(loader.loadTestsFromTestCase(TestzWizardHelperMethods))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

