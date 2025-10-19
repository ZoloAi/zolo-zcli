#!/usr/bin/env python3
# zTestSuite/zFunc_Test.py

"""
Comprehensive test suite for zFunc subsystem.
Tests external function loading, argument parsing, function resolution, and execution.
"""

import unittest
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zFunc import zFunc
from zCLI.subsystems.zFunc.zFunc_modules import (
    parse_arguments, split_arguments, resolve_callable
)


class TestzFuncInitialization(unittest.TestCase):
    """Test zFunc initialization and basic setup."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.zparser = Mock()

    def test_initialization_with_valid_zcli(self):
        """Test zFunc initializes correctly with valid zCLI instance."""
        zfunc = zFunc(self.mock_zcli)
        
        self.assertIsNotNone(zfunc)
        self.assertEqual(zfunc.zcli, self.mock_zcli)
        self.assertEqual(zfunc.logger, self.mock_zcli.logger)
        self.assertEqual(zfunc.session, self.mock_zcli.session)
        self.assertEqual(zfunc.display, self.mock_zcli.display)
        self.assertEqual(zfunc.zparser, self.mock_zcli.zparser)
        self.assertEqual(zfunc.mycolor, "ZFUNC")

    def test_ready_message_displayed(self):
        """Test ready message is displayed on initialization."""
        zfunc = zFunc(self.mock_zcli)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called_with(
            "zFunc Ready", color="ZFUNC", indent=0, style="full"
        )


class TestArgumentParsing(unittest.TestCase):
    """Test argument parsing functionality."""

    def setUp(self):
        """Set up test logger and parser."""
        self.logger = Mock()
        self.mock_zparser = Mock()

    def test_parse_no_arguments(self):
        """Test parsing when no arguments are provided."""
        result = parse_arguments(None, {}, split_arguments, self.logger)
        self.assertEqual(result, [])

    def test_parse_empty_arguments(self):
        """Test parsing empty argument string."""
        result = parse_arguments("", {}, split_arguments, self.logger)
        self.assertEqual(result, [])

    def test_parse_literal_arguments(self):
        """Test parsing literal arguments with zParser."""
        self.mock_zparser.parse_json_expr = Mock(side_effect=lambda x: x.strip('"'))
        
        result = parse_arguments(
            '"hello", "world"',
            {},
            split_arguments,
            self.logger,
            self.mock_zparser
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "hello")
        self.assertEqual(result[1], "world")

    def test_parse_zcontext_injection(self):
        """Test zContext injection."""
        zContext = {"key": "value", "model": "TestModel"}
        
        result = parse_arguments(
            "zContext",
            zContext,
            split_arguments,
            self.logger,
            self.mock_zparser
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], zContext)

    def test_parse_zconv_injection(self):
        """Test zConv injection from context."""
        zContext = {"zConv": {"field1": "value1", "field2": "value2"}}
        
        result = parse_arguments(
            "zConv",
            zContext,
            split_arguments,
            self.logger,
            self.mock_zparser
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"field1": "value1", "field2": "value2"})

    def test_parse_zconv_field_notation(self):
        """Test zConv.field notation."""
        zContext = {"zConv": {"username": "testuser", "email": "test@example.com"}}
        
        result = parse_arguments(
            "zConv.username, zConv.email",
            zContext,
            split_arguments,
            self.logger,
            self.mock_zparser
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "testuser")
        self.assertEqual(result[1], "test@example.com")

    def test_parse_this_notation(self):
        """Test this.field notation."""
        zContext = {"name": "TestName", "value": 42}
        
        result = parse_arguments(
            "this.name, this.value",
            zContext,
            split_arguments,
            self.logger,
            self.mock_zparser
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "TestName")
        self.assertEqual(result[1], 42)

    def test_parse_without_zparser(self):
        """Test parsing without zParser falls back to literal."""
        result = parse_arguments(
            "arg1, arg2",
            {},
            split_arguments,
            self.logger,
            zparser=None
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[1], "arg2")

    def test_split_arguments_simple(self):
        """Test simple argument splitting."""
        result = split_arguments("arg1, arg2, arg3")
        self.assertEqual(result, ["arg1", " arg2", " arg3"])

    def test_split_arguments_nested_brackets(self):
        """Test splitting with nested brackets."""
        result = split_arguments("arg1, [1, 2, 3], arg3")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1], " [1, 2, 3]")

    def test_split_arguments_nested_dicts(self):
        """Test splitting with nested dictionaries."""
        result = split_arguments('{"key": "value", "nested": {"a": 1}}, arg2')
        self.assertEqual(len(result), 2)
        self.assertIn('"key": "value"', result[0])


class TestFunctionResolver(unittest.TestCase):
    """Test function resolution and loading."""

    def setUp(self):
        """Set up test logger."""
        self.logger = Mock()

    def test_resolve_callable_file_not_found(self):
        """Test error when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            resolve_callable("/nonexistent/file.py", "test_func", self.logger)

    def test_resolve_callable_success(self):
        """Test successful function resolution."""
        # Create a temporary Python file with a test function
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 'success'\n")
            temp_file = f.name

        try:
            func = resolve_callable(temp_file, "test_function", self.logger)
            self.assertIsNotNone(func)
            self.assertEqual(func.__name__, "test_function")
            self.assertEqual(func(), "success")
        finally:
            Path(temp_file).unlink()

    def test_resolve_callable_function_not_found(self):
        """Test error when function doesn't exist in module."""
        # Create a temporary Python file without the target function
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def other_function():\n    return 'other'\n")
            temp_file = f.name

        try:
            with self.assertRaises(AttributeError):
                resolve_callable(temp_file, "nonexistent_function", self.logger)
        finally:
            Path(temp_file).unlink()


class TestzFuncExecution(unittest.TestCase):
    """Test zFunc execution flow."""

    def setUp(self):
        """Set up mock zCLI instance and zFunc."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.zparser = Mock()
        
        self.zfunc = zFunc(self.mock_zcli)

    def test_handle_calls_display(self):
        """Test that handle() calls display methods."""
        # Mock the internal methods to avoid actual execution
        self.mock_zcli.zparser.parse_function_path = Mock(
            return_value=("/path/to/file.py", "arg1", "test_func")
        )
        
        with patch.object(self.zfunc, '_parse_args_with_display', return_value=[]):
            with patch.object(self.zfunc, '_resolve_callable_with_display', return_value=lambda: "result"):
                with patch.object(self.zfunc, '_execute_function', return_value={"status": "success"}):
                    with patch.object(self.zfunc, '_display_result'):
                        result = self.zfunc.handle("zFunc(test.func)")
                        
                        # Verify display was called
                        self.mock_zcli.display.zDeclare.assert_called()
                        self.assertEqual(result, {"status": "success"})

    def test_parse_args_with_display(self):
        """Test _parse_args_with_display calls display and parser."""
        with patch('zCLI.subsystems.zFunc.zFunc_modules.func_args.parse_arguments', return_value=["arg1"]):
            result = self.zfunc._parse_args_with_display("arg1", {})
            
            self.mock_zcli.display.zDeclare.assert_called_with(
                "Parse Arguments", color="ZFUNC", indent=1, style="single"
            )
            self.assertEqual(result, ["arg1"])

    def test_resolve_callable_with_display(self):
        """Test _resolve_callable_with_display calls display and resolver."""
        mock_func = Mock()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_func():\n    return 'test'\n")
            temp_file = f.name

        try:
            result = self.zfunc._resolve_callable_with_display(temp_file, "test_func")
            
            self.mock_zcli.display.zDeclare.assert_called_with(
                "Resolve Callable", color="ZFUNC", indent=1, style="single"
            )
            self.assertIsNotNone(result)
            self.assertEqual(result.__name__, "test_func")
        finally:
            Path(temp_file).unlink()

    def test_execute_function_without_session(self):
        """Test executing function that doesn't require session."""
        mock_func = Mock(return_value="result")
        mock_func.__name__ = "test_func"
        
        with patch('zCLI.inspect.signature') as mock_sig:
            mock_sig.return_value.parameters = {}
            result = self.zfunc._execute_function(mock_func, ["arg1", "arg2"])
            
            mock_func.assert_called_once_with("arg1", "arg2")
            self.assertEqual(result, "result")

    def test_execute_function_with_session_injection(self):
        """Test executing function with automatic session injection."""
        mock_func = Mock(return_value="result")
        mock_func.__name__ = "test_func"
        
        with patch('zCLI.inspect.signature') as mock_sig:
            mock_param = Mock()
            mock_sig.return_value.parameters = {'session': mock_param}
            
            result = self.zfunc._execute_function(mock_func, ["arg1"])
            
            # Should be called with session kwarg
            mock_func.assert_called_once_with("arg1", session=self.mock_zcli.session)
            self.assertEqual(result, "result")

    def test_execute_function_session_already_in_args(self):
        """Test that session is not injected if already in args."""
        mock_func = Mock(return_value="result")
        mock_func.__name__ = "test_func"
        
        with patch('zCLI.inspect.signature') as mock_sig:
            mock_param = Mock()
            mock_sig.return_value.parameters = {'session': mock_param}
            
            # Session already in first arg
            result = self.zfunc._execute_function(mock_func, [{"session": "custom"}])
            
            # Should be called without session injection
            mock_func.assert_called_once_with({"session": "custom"})
            self.assertEqual(result, "result")

    def test_display_result(self):
        """Test _display_result calls display methods."""
        result_data = {"status": "success", "data": [1, 2, 3]}
        
        self.zfunc._display_result(result_data)
        
        # After modernization, should call json_data instead of handle
        self.mock_zcli.display.json_data.assert_called_once_with(result_data, color=True, indent=0)
        
        # Should call text for break (empty line)
        text_calls = self.mock_zcli.display.text.call_args_list
        self.assertTrue(any(call[0][0] == "" for call in text_calls))
        
        # Should call zDeclare for separator and return header
        declare_calls = self.mock_zcli.display.zDeclare.call_args_list
        self.assertTrue(any("zFunction Return" in str(call) for call in declare_calls))

    def test_model_merge_with_dict_arg(self):
        """Test model merging when first arg is a dict."""
        self.mock_zcli.zparser.parse_function_path = Mock(
            return_value=("/path/to/file.py", "arg1", "test_func")
        )
        
        with patch.object(self.zfunc, '_parse_args_with_display', return_value=[{"key": "value"}]):
            with patch.object(self.zfunc, '_resolve_callable_with_display', return_value=lambda x: x):
                with patch.object(self.zfunc, '_execute_function', return_value={"status": "success"}) as mock_exec:
                    with patch.object(self.zfunc, '_display_result'):
                        zContext = {"model": "TestModel"}
                        self.zfunc.handle("zFunc(test.func)", zContext)
                        
                        # Check that model was merged into first arg
                        call_args = mock_exec.call_args[0]
                        self.assertIn("model", call_args[1][0])
                        self.assertEqual(call_args[1][0]["model"], "TestModel")

    def test_model_merge_without_dict_arg(self):
        """Test model merging when first arg is not a dict."""
        self.mock_zcli.zparser.parse_function_path = Mock(
            return_value=("/path/to/file.py", "arg1", "test_func")
        )
        
        with patch.object(self.zfunc, '_parse_args_with_display', return_value=["string_arg"]):
            with patch.object(self.zfunc, '_resolve_callable_with_display', return_value=lambda x: x):
                with patch.object(self.zfunc, '_execute_function', return_value={"status": "success"}) as mock_exec:
                    with patch.object(self.zfunc, '_display_result'):
                        zContext = {"model": "TestModel"}
                        self.zfunc.handle("zFunc(test.func)", zContext)
                        
                        # Check that model was inserted as first arg
                        call_args = mock_exec.call_args[0]
                        self.assertEqual(call_args[1][0], {"model": "TestModel"})
                        self.assertEqual(call_args[1][1], "string_arg")


class TestzFuncEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up mock zCLI instance and zFunc."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.zparser = Mock()
        
        self.zfunc = zFunc(self.mock_zcli)

    def test_handle_with_exception(self):
        """Test handle() with exception during execution."""
        self.mock_zcli.zparser.parse_function_path = Mock(
            side_effect=Exception("Parse error")
        )
        
        with self.assertRaises(Exception):
            self.zfunc.handle("zFunc(invalid.func)")
        
        # Logger should record the error
        self.mock_zcli.logger.error.assert_called()

    def test_execute_function_with_typeerror_fallback(self):
        """Test function execution falls back when session injection fails."""
        mock_func = Mock(side_effect=[TypeError("Invalid"), "fallback_result"])
        mock_func.__name__ = "test_func"
        
        with patch('zCLI.inspect.signature') as mock_sig:
            mock_param = Mock()
            mock_sig.return_value.parameters = {'session': mock_param}
            
            result = self.zfunc._execute_function(mock_func, [])
            
            # Should try with session, then fallback without
            self.assertEqual(mock_func.call_count, 2)
            self.assertEqual(result, "fallback_result")

    def test_parse_arguments_with_exception(self):
        """Test argument parsing with exception."""
        logger = Mock()
        mock_zparser = Mock()
        mock_zparser.parse_json_expr = Mock(side_effect=Exception("Parse error"))
        
        with self.assertRaises(Exception):
            parse_arguments(
                "invalid_arg",
                {},
                split_arguments,
                logger,
                mock_zparser
            )
        
        logger.error.assert_called()

    def test_handle_without_context(self):
        """Test handle() without zContext."""
        self.mock_zcli.zparser.parse_function_path = Mock(
            return_value=("/path/to/file.py", None, "test_func")
        )
        
        with patch.object(self.zfunc, '_parse_args_with_display', return_value=[]):
            with patch.object(self.zfunc, '_resolve_callable_with_display', return_value=lambda: "result"):
                with patch.object(self.zfunc, '_execute_function', return_value={"status": "success"}):
                    with patch.object(self.zfunc, '_display_result'):
                        result = self.zfunc.handle("zFunc(test.func)", zContext=None)
                        
                        self.assertEqual(result, {"status": "success"})


def run_tests(verbose=False):
    """Run all zFunc tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzFuncInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestArgumentParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestzFuncExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestzFuncEdgeCases))
    
    # Run tests with appropriate verbosity
    verbosity_level = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity_level)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

