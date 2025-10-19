#!/usr/bin/env python3
# zTestSuite/zDispatch_Test.py

"""
Comprehensive test suite for zDispatch subsystem.
Tests command dispatch, modifiers, and launcher without walker context.
Walker-specific tests will be in the zWalker test suite.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zDispatch import zDispatch
from zCLI.subsystems.zDispatch.zDispatch_modules.modifiers import ModifierProcessor
from zCLI.subsystems.zDispatch.zDispatch_modules.launcher import CommandLauncher


class TestzDispatchInitialization(unittest.TestCase):
    """Test zDispatch initialization and basic setup."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()

    def test_initialization_with_valid_zcli(self):
        """Test zDispatch initializes correctly with valid zCLI instance."""
        dispatch = zDispatch(self.mock_zcli)
        
        self.assertIsNotNone(dispatch)
        self.assertEqual(dispatch.zcli, self.mock_zcli)
        self.assertEqual(dispatch.session, self.mock_zcli.session)
        self.assertEqual(dispatch.logger, self.mock_zcli.logger)
        self.assertEqual(dispatch.mycolor, "DISPATCH")

    def test_initialization_without_zcli(self):
        """Test zDispatch raises error when initialized without zCLI instance."""
        with self.assertRaises(ValueError) as context:
            zDispatch(None)
        
        self.assertIn("requires a zCLI instance", str(context.exception))

    def test_modifiers_initialization(self):
        """Test ModifierProcessor is initialized."""
        dispatch = zDispatch(self.mock_zcli)
        
        self.assertIsNotNone(dispatch.modifiers)
        self.assertIsInstance(dispatch.modifiers, ModifierProcessor)

    def test_launcher_initialization(self):
        """Test CommandLauncher is initialized."""
        dispatch = zDispatch(self.mock_zcli)
        
        self.assertIsNotNone(dispatch.launcher)
        self.assertIsInstance(dispatch.launcher, CommandLauncher)

    def test_ready_message_displayed(self):
        """Test ready message is displayed on initialization."""
        dispatch = zDispatch(self.mock_zcli)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called_once_with(
            "zDispatch Ready", color="DISPATCH", indent=0, style="full"
        )


class TestModifierProcessor(unittest.TestCase):
    """Test ModifierProcessor functionality."""

    def setUp(self):
        """Set up mock dispatch and zCLI for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.dispatch = zDispatch(self.mock_zcli)
        self.processor = self.dispatch.modifiers

    def test_check_prefix_with_caret(self):
        """Test prefix modifier detection with ^."""
        result = self.processor.check_prefix("^test")
        self.assertEqual(result, ["^"])

    def test_check_prefix_with_tilde(self):
        """Test prefix modifier detection with ~."""
        result = self.processor.check_prefix("~test")
        self.assertEqual(result, ["~"])

    def test_check_prefix_no_modifier(self):
        """Test prefix detection with no modifier."""
        result = self.processor.check_prefix("test")
        self.assertEqual(result, [])

    def test_check_suffix_with_exclamation(self):
        """Test suffix modifier detection with !."""
        result = self.processor.check_suffix("test!")
        self.assertEqual(result, ["!"])

    def test_check_suffix_with_asterisk(self):
        """Test suffix modifier detection with *."""
        result = self.processor.check_suffix("test*")
        self.assertEqual(result, ["*"])

    def test_check_suffix_no_modifier(self):
        """Test suffix detection with no modifier."""
        result = self.processor.check_suffix("test")
        self.assertEqual(result, [])

    def test_process_caret_modifier(self):
        """Test ^ modifier processing (returns zBack)."""
        self.dispatch.launcher.launch = Mock(return_value="result")
        
        result = self.processor.process(["^"], "^test", "zFunc('test')")
        
        self.assertEqual(result, "zBack")
        self.dispatch.launcher.launch.assert_called_once()


class TestCommandLauncher(unittest.TestCase):
    """Test CommandLauncher functionality."""

    def setUp(self):
        """Set up mock dispatch and zCLI for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.data = Mock()
        self.mock_zcli.navigation = Mock()
        
        self.dispatch = zDispatch(self.mock_zcli)
        self.launcher = self.dispatch.launcher

    def test_launch_displays_message(self):
        """Test launch displays zLauncher message."""
        self.launcher.launch("unknown")
        
        self.mock_zcli.display.zDeclare.assert_called_with(
            "zLauncher", color="DISPATCH", indent=4, style="single"
        )

    def test_launch_with_none(self):
        """Test launch with None returns None."""
        result = self.launcher.launch(None)
        self.assertIsNone(result)

    def test_launch_with_unknown_string(self):
        """Test launch with unknown string returns None."""
        result = self.launcher.launch("unknown_command")
        self.assertIsNone(result)


class TestCommandLauncherStringCommands(unittest.TestCase):
    """Test CommandLauncher string-based commands."""

    def setUp(self):
        """Set up mock dispatch and zCLI for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.zfunc.handle = Mock(return_value="func_result")
        self.mock_zcli.open = Mock()
        self.mock_zcli.open.handle = Mock(return_value="open_result")
        self.mock_zcli.data = Mock()
        self.mock_zcli.data.handle_request = Mock(return_value="data_result")
        self.mock_zcli.navigation = Mock()
        
        self.dispatch = zDispatch(self.mock_zcli)
        self.launcher = self.dispatch.launcher

    def test_launch_zfunc_string(self):
        """Test launching zFunc with string format."""
        result = self.launcher.launch("zFunc('test_function')")
        
        self.mock_zcli.zfunc.handle.assert_called_once_with("zFunc('test_function')")
        self.assertEqual(result, "func_result")

    def test_launch_zopen_string(self):
        """Test launching zOpen with string format."""
        result = self.launcher.launch("zOpen('test.txt')")
        
        self.mock_zcli.open.handle.assert_called_once_with("zOpen('test.txt')")
        self.assertEqual(result, "open_result")

    def test_launch_zread_string(self):
        """Test launching zRead with string format."""
        result = self.launcher.launch("zRead('TestModel')")
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["action"], "read")
        # The string includes quotes from the function call
        self.assertEqual(req["model"], "'TestModel'")
        self.assertEqual(result, "data_result")

    def test_launch_zread_string_empty(self):
        """Test launching zRead with empty string."""
        result = self.launcher.launch("zRead()")
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["action"], "read")
        self.assertNotIn("model", req)


class TestCommandLauncherDictCommands(unittest.TestCase):
    """Test CommandLauncher dict-based commands."""

    def setUp(self):
        """Set up mock dispatch and zCLI for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.data = Mock()
        self.mock_zcli.data.handle_request = Mock(return_value="data_result")
        
        self.dispatch = zDispatch(self.mock_zcli)
        self.launcher = self.dispatch.launcher

    def test_launch_zdisplay_dict(self):
        """Test launching zDisplay with dict format."""
        display_obj = {"event": "text", "content": "Test"}
        result = self.launcher.launch({"zDisplay": display_obj})
        
        # After modernization, launcher uses modern display methods
        self.mock_zcli.display.text.assert_called_once_with("Test", 0)
        self.assertIsNone(result)

    def test_launch_zread_dict_with_string(self):
        """Test launching zRead dict with string value."""
        result = self.launcher.launch({"zRead": "TestModel"})
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["action"], "read")
        self.assertEqual(req["model"], "TestModel")

    def test_launch_zread_dict_with_dict(self):
        """Test launching zRead dict with dict value."""
        read_obj = {"model": "TestModel", "filters": {"id": 1}}
        result = self.launcher.launch({"zRead": read_obj})
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["action"], "read")
        self.assertEqual(req["model"], "TestModel")
        self.assertEqual(req["filters"], {"id": 1})

    def test_launch_crud_dict(self):
        """Test launching generic CRUD dict."""
        crud_obj = {
            "model": "TestModel",
            "action": "create",
            "values": {"name": "test"}
        }
        result = self.launcher.launch(crud_obj)
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["model"], "TestModel")
        self.assertEqual(req["action"], "create")
        self.assertEqual(req["values"], {"name": "test"})

    def test_launch_crud_dict_defaults_to_read(self):
        """Test CRUD dict defaults action to read."""
        crud_obj = {"model": "TestModel"}
        result = self.launcher.launch(crud_obj)
        
        self.mock_zcli.data.handle_request.assert_called_once()
        call_args = self.mock_zcli.data.handle_request.call_args
        req = call_args[0][0]
        
        self.assertEqual(req["action"], "read")

    def test_launch_unknown_dict(self):
        """Test launching unknown dict returns None."""
        result = self.launcher.launch({"unknown": "value"})
        self.assertIsNone(result)


class TestzDispatchHandle(unittest.TestCase):
    """Test zDispatch.handle() method."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.dispatch = zDispatch(self.mock_zcli)

    def test_handle_displays_message(self):
        """Test handle displays system message."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=[])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.launcher.launch = Mock(return_value=None)
        
        self.dispatch.handle("test", "zFunc('test')")
        
        # Should display handle message
        calls = self.mock_zcli.display.zDeclare.call_args_list
        handle_call = [c for c in calls if "handle zDispatch" in str(c)]
        self.assertTrue(len(handle_call) > 0)

    def test_handle_without_modifiers(self):
        """Test handle without modifiers calls launcher."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=[])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.launcher.launch = Mock(return_value="result")
        
        result = self.dispatch.handle("test", "zFunc('test')")
        
        self.dispatch.launcher.launch.assert_called_once_with(
            "zFunc('test')", context=None, walker=None
        )
        self.assertEqual(result, "result")

    def test_handle_with_modifiers(self):
        """Test handle with modifiers calls modifier processor."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=["^"])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.modifiers.process = Mock(return_value="modified_result")
        
        result = self.dispatch.handle("^test", "zFunc('test')")
        
        self.dispatch.modifiers.process.assert_called_once()
        self.assertEqual(result, "modified_result")

    def test_handle_with_prefix_and_suffix(self):
        """Test handle with both prefix and suffix modifiers."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=["^"])
        self.dispatch.modifiers.check_suffix = Mock(return_value=["!"])
        self.dispatch.modifiers.process = Mock(return_value="result")
        
        result = self.dispatch.handle("^test!", "zFunc('test')")
        
        # Should combine modifiers
        call_args = self.dispatch.modifiers.process.call_args
        modifiers = call_args[0][0]
        self.assertIn("^", modifiers)
        self.assertIn("!", modifiers)


class TestStandaloneHandleFunction(unittest.TestCase):
    """Test standalone handle_zDispatch function."""

    def test_handle_with_zcli(self):
        """Test handle_zDispatch with zcli parameter."""
        from zCLI.subsystems.zDispatch.zDispatch import handle_zDispatch
        
        mock_zcli = Mock()
        mock_zcli.dispatch = Mock()
        mock_zcli.dispatch.handle = Mock(return_value="result")
        
        result = handle_zDispatch("test", "zFunc('test')", zcli=mock_zcli)
        
        mock_zcli.dispatch.handle.assert_called_once_with(
            "test", "zFunc('test')", context=None, walker=None
        )
        self.assertEqual(result, "result")

    def test_handle_without_zcli_or_walker(self):
        """Test handle_zDispatch raises error without zcli or walker."""
        from zCLI.subsystems.zDispatch.zDispatch import handle_zDispatch
        
        with self.assertRaises(ValueError) as context:
            handle_zDispatch("test", "zFunc('test')")
        
        self.assertIn("requires either zcli or walker", str(context.exception))


class TestContextPassing(unittest.TestCase):
    """Test context parameter passing through dispatch chain."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.data = Mock()
        self.mock_zcli.data.handle_request = Mock(return_value="result")
        
        self.dispatch = zDispatch(self.mock_zcli)

    def test_context_passed_to_launcher(self):
        """Test context is passed to launcher."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=[])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.launcher.launch = Mock(return_value=None)
        
        context = {"wizard_data": "test"}
        self.dispatch.handle("test", "zFunc('test')", context=context)
        
        self.dispatch.launcher.launch.assert_called_once_with(
            "zFunc('test')", context=context, walker=None
        )

    def test_context_passed_to_data_handler(self):
        """Test context is passed through to data handler."""
        context = {"wizard_data": "test"}
        self.dispatch.launcher.launch("zRead('TestModel')", context=context)
        
        call_args = self.mock_zcli.data.handle_request.call_args
        passed_context = call_args[1].get("context")
        
        self.assertEqual(passed_context, context)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.dispatch = zDispatch(self.mock_zcli)

    def test_handle_with_empty_key(self):
        """Test handle with empty key."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=[])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.launcher.launch = Mock(return_value=None)
        
        result = self.dispatch.handle("", "zFunc('test')")
        
        # Should still process
        self.dispatch.launcher.launch.assert_called_once()

    def test_handle_with_none_horizontal(self):
        """Test handle with None zHorizontal."""
        self.dispatch.modifiers.check_prefix = Mock(return_value=[])
        self.dispatch.modifiers.check_suffix = Mock(return_value=[])
        self.dispatch.launcher.launch = Mock(return_value=None)
        
        result = self.dispatch.handle("test", None)
        
        self.dispatch.launcher.launch.assert_called_once_with(
            None, context=None, walker=None
        )

    def test_launcher_with_empty_dict(self):
        """Test launcher with empty dict."""
        result = self.dispatch.launcher.launch({})
        self.assertIsNone(result)

    def test_launcher_with_malformed_string(self):
        """Test launcher with malformed string command."""
        # Malformed string still matches zFunc( prefix, so it gets handled
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.zfunc.handle = Mock(return_value="result")
        result = self.dispatch.launcher.launch("zFunc(")
        # It will be passed to zfunc.handle, not return None
        self.assertIsNotNone(result)


def run_tests(verbose=False):
    """Run all zDispatch tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzDispatchInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestModifierProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLauncher))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLauncherStringCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLauncherDictCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestzDispatchHandle))
    suite.addTests(loader.loadTestsFromTestCase(TestStandaloneHandleFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestContextPassing))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

