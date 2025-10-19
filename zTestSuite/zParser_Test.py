#!/usr/bin/env python3
# zTestSuite/zParser_Test.py

"""
Comprehensive test suite for zParser subsystem.
Tests path resolution, command parsing, file parsing, and function path parsing.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zParser import zParser


class TestzParserInitialization(unittest.TestCase):
    """Test zParser initialization and basic setup."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()

    def test_initialization_with_valid_zcli(self):
        """Test zParser initializes correctly with valid zCLI instance."""
        parser = zParser(self.mock_zcli)
        
        self.assertIsNotNone(parser)
        self.assertEqual(parser.zcli, self.mock_zcli)
        self.assertEqual(parser.zSession, self.mock_zcli.session)
        self.assertEqual(parser.logger, self.mock_zcli.logger)
        self.assertEqual(parser.mycolor, "PARSER")

    def test_initialization_without_zcli(self):
        """Test zParser raises error when initialized without zCLI instance."""
        with self.assertRaises(ValueError) as context:
            zParser(None)
        
        self.assertIn("requires a zCLI instance", str(context.exception))

    def test_initialization_with_invalid_zcli(self):
        """Test zParser raises error when zCLI instance lacks session."""
        invalid_zcli = Mock(spec=[])  # Mock without session attribute
        
        with self.assertRaises(ValueError) as context:
            zParser(invalid_zcli)
        
        self.assertIn("missing 'session' attribute", str(context.exception))

    def test_ready_message_displayed(self):
        """Test ready message is displayed on initialization."""
        parser = zParser(self.mock_zcli)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called_once_with(
            "zParser Ready", color="PARSER", indent=0, style="full"
        )


class TestResolveSymbolPath(unittest.TestCase):
    """Test resolve_symbol_path method."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_resolve_workspace_symbol(self):
        """Test resolving @ symbol (workspace-relative)."""
        result = self.parser.resolve_symbol_path("@", ["@", "utils", "helpers"], "/workspace")
        
        self.assertEqual(result, "/workspace/utils/helpers")

    def test_resolve_absolute_symbol(self):
        """Test resolving ~ symbol (absolute path)."""
        result = self.parser.resolve_symbol_path("~", ["~", "home", "user"], "/workspace")
        
        # Absolute path doesn't include leading slash from os.path.join
        self.assertEqual(result, "home/user")

    def test_resolve_no_symbol(self):
        """Test resolving path with no symbol (relative to workspace)."""
        result = self.parser.resolve_symbol_path(None, ["utils", "helpers"], "/workspace")
        
        self.assertEqual(result, "/workspace/utils/helpers")

    def test_resolve_with_default_workspace(self):
        """Test resolving uses session workspace when not provided."""
        result = self.parser.resolve_symbol_path("@", ["@", "utils"])
        
        # Should use workspace from session
        self.assertIn("/test/workspace", result)


class TestParseFunctionPath(unittest.TestCase):
    """Test parse_function_path method (refactored from parse_function_spec)."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_parse_dict_format(self):
        """Test parsing dict format zFunc spec."""
        spec = {
            "zFunc_path": "/path/to/myfile.py",
            "zFunc_args": "arg1, arg2"
        }
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertEqual(func_path, "/path/to/myfile.py")
        self.assertEqual(arg_str, "arg1, arg2")
        self.assertEqual(function_name, "myfile")

    def test_parse_dict_format_no_args(self):
        """Test parsing dict format without args."""
        spec = {"zFunc_path": "/path/to/myfile.py"}
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertEqual(func_path, "/path/to/myfile.py")
        self.assertIsNone(arg_str)
        self.assertEqual(function_name, "myfile")

    def test_parse_string_format_with_args(self):
        """Test parsing string format with arguments."""
        spec = "zFunc(@utils.myfile.my_function, arg1, arg2)"
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertIn("myfile.py", func_path)
        self.assertEqual(arg_str, "arg1, arg2")
        self.assertEqual(function_name, "my_function")

    def test_parse_string_format_no_args(self):
        """Test parsing string format without arguments."""
        spec = "zFunc(@utils.myfile.my_function)"
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertIn("myfile.py", func_path)
        self.assertIsNone(arg_str)
        self.assertEqual(function_name, "my_function")

    def test_parse_with_workspace_symbol(self):
        """Test parsing with @ workspace symbol."""
        spec = "zFunc(@utils.helpers.process_data)"
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertIn("/test/workspace", func_path)
        self.assertIn("helpers.py", func_path)
        self.assertEqual(function_name, "process_data")

    def test_parse_with_absolute_symbol(self):
        """Test parsing with ~ absolute symbol."""
        spec = "zFunc(~home.user.scripts.myfile.my_func)"
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertIn("myfile.py", func_path)
        self.assertEqual(function_name, "my_func")

    def test_parse_without_symbol(self):
        """Test parsing without symbol (relative to workspace)."""
        spec = "zFunc(utils.myfile.my_function)"
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec)
        
        self.assertIn("myfile.py", func_path)
        self.assertEqual(function_name, "my_function")


class TestParseCommand(unittest.TestCase):
    """Test parse_command method."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_parse_simple_command(self):
        """Test parsing simple command."""
        result = self.parser.parse_command("ls -la")
        
        self.assertIsNotNone(result)
        # parse_command returns error for unknown commands
        self.assertIsInstance(result, dict)

    def test_parse_empty_command(self):
        """Test parsing empty command."""
        result = self.parser.parse_command("")
        
        self.assertIsNotNone(result)


class TestFileContentParsing(unittest.TestCase):
    """Test file content parsing methods."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_parse_json_content(self):
        """Test parsing JSON content."""
        json_content = '{"key": "value", "number": 42}'
        result = self.parser.parse_json(json_content)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")
        self.assertEqual(result["number"], 42)

    def test_parse_yaml_content(self):
        """Test parsing YAML content."""
        yaml_content = "key: value\nnumber: 42"
        result = self.parser.parse_yaml(yaml_content)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")
        self.assertEqual(result["number"], 42)

    def test_detect_json_format(self):
        """Test detecting JSON format."""
        json_content = '{"key": "value"}'
        result = self.parser.detect_format(json_content)
        
        # Format detection returns with dot prefix
        self.assertEqual(result, ".json")

    def test_detect_yaml_format(self):
        """Test detecting YAML format."""
        yaml_content = "key: value\nother: data"
        result = self.parser.detect_format(yaml_content)
        
        # Format detection returns with dot prefix
        self.assertEqual(result, ".yaml")


class TestResolveDataPath(unittest.TestCase):
    """Test resolve_data_path method."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_resolve_workspace_path(self):
        """Test resolving @ workspace path."""
        result = self.parser.resolve_data_path("@.data.files")
        
        self.assertIn("/test/workspace", result)
        self.assertIn("data", result)
        self.assertIn("files", result)

    def test_resolve_regular_path(self):
        """Test resolving regular path (no special prefix)."""
        result = self.parser.resolve_data_path("/regular/path")
        
        self.assertEqual(result, "/regular/path")

    def test_resolve_non_string(self):
        """Test resolving non-string returns as-is."""
        result = self.parser.resolve_data_path(123)
        
        self.assertEqual(result, 123)


class TestExpressionEvaluation(unittest.TestCase):
    """Test expression evaluation methods."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_eval_dict_expression(self):
        """Test evaluating dict expression."""
        expr = '{"key": "value", "num": 42}'
        result = self.parser.zExpr_eval(expr)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["key"], "value")
        self.assertEqual(result["num"], 42)

    def test_eval_list_expression(self):
        """Test evaluating list expression."""
        expr = '["item1", "item2", "item3"]'
        result = self.parser.zExpr_eval(expr)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_eval_quoted_string(self):
        """Test evaluating quoted string."""
        expr = '"test string"'
        result = self.parser.zExpr_eval(expr)
        
        self.assertEqual(result, "test string")


class TestParseDottedPath(unittest.TestCase):
    """Test parse_dotted_path method."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_parse_valid_dotted_path(self):
        """Test parsing valid dotted path."""
        result = self.parser.parse_dotted_path("path.to.table")
        
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["table"], "table")
        self.assertEqual(result["parts"], ["path", "to", "table"])

    def test_parse_short_path(self):
        """Test parsing path with insufficient parts."""
        result = self.parser.parse_dotted_path("single")
        
        self.assertFalse(result["is_valid"])
        self.assertIn("error", result)

    def test_parse_non_string(self):
        """Test parsing non-string input."""
        result = self.parser.parse_dotted_path(123)
        
        self.assertFalse(result["is_valid"])
        self.assertIn("error", result)


class TestPluginInvocation(unittest.TestCase):
    """Test plugin invocation methods (& modifier)."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        # Mock utils with plugins
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        
        # Mock loader with plugin cache
        self.mock_zcli.loader = Mock()
        self.mock_zcli.loader.cache = Mock()
        self.mock_zcli.loader.cache.plugin_cache = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_is_plugin_invocation_valid(self):
        """Test identifying valid plugin invocations."""
        self.assertTrue(self.parser.is_plugin_invocation("&test_plugin.hello_world()"))
        self.assertTrue(self.parser.is_plugin_invocation("&@.utils.test_plugin.hello_world()"))
        self.assertTrue(self.parser.is_plugin_invocation("&~.plugins.test.func()"))
        self.assertTrue(self.parser.is_plugin_invocation("&zMachine.plugins.test.func()"))

    def test_is_plugin_invocation_invalid(self):
        """Test identifying invalid plugin invocations."""
        self.assertFalse(self.parser.is_plugin_invocation("test_plugin.hello_world()"))
        self.assertFalse(self.parser.is_plugin_invocation("@utils.test_plugin"))
        self.assertFalse(self.parser.is_plugin_invocation(""))
        self.assertFalse(self.parser.is_plugin_invocation(None))
        self.assertFalse(self.parser.is_plugin_invocation(123))

    def test_resolve_plugin_invocation_cached(self):
        """Test resolving plugin invocation from cache."""
        # Mock a cached plugin module
        mock_module = Mock()
        mock_module.hello_world = Mock(return_value="Hello, World!")
        
        # Mock cache to return the module
        self.mock_zcli.loader.cache.get = Mock(return_value=mock_module)
        
        result = self.parser.resolve_plugin_invocation("&test_plugin.hello_world()")
        
        # Should get from cache by plugin name
        self.mock_zcli.loader.cache.get.assert_called_with("test_plugin", cache_type="plugin")
        self.assertEqual(result, "Hello, World!")

    def test_resolve_plugin_invocation_with_args(self):
        """Test resolving plugin invocation with arguments."""
        # Mock a cached plugin module
        mock_module = Mock()
        mock_module.greet = Mock(return_value="Hello, Alice!")
        
        # Mock cache to return the module
        self.mock_zcli.loader.cache.get = Mock(return_value=mock_module)
        
        result = self.parser.resolve_plugin_invocation("&test_plugin.greet('Alice')")
        
        self.assertEqual(result, "Hello, Alice!")

    def test_resolve_plugin_invocation_invalid_syntax(self):
        """Test resolving plugin invocation with invalid syntax."""
        with self.assertRaises(ValueError) as context:
            self.parser.resolve_plugin_invocation("&test_plugin.hello_world")  # Missing ()
        
        self.assertIn("Invalid plugin invocation syntax", str(context.exception))

    def test_resolve_plugin_invocation_not_found(self):
        """Test resolving plugin invocation when plugin not found."""
        # Mock cache miss (returns None)
        self.mock_zcli.loader.cache.get = Mock(return_value=None)
        
        # Mock zparser to simulate file not found in search paths
        self.mock_zcli.zparser.resolve_symbol_path = Mock(return_value="/nonexistent/path")
        
        with self.assertRaises(ValueError) as context:
            self.parser.resolve_plugin_invocation("&nonexistent.func()")
        
        # Should fail with "Plugin not found" after searching standard paths
        self.assertIn("plugin not found", str(context.exception).lower())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up mock zCLI and zParser for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        
        self.parser = zParser(self.mock_zcli)

    def test_parse_function_path_with_context(self):
        """Test parse_function_path with context."""
        spec = "zFunc(@utils.myfile.my_function)"
        context = {"model": "TestModel"}
        
        func_path, arg_str, function_name = self.parser.parse_function_path(spec, context)
        
        self.assertIsNotNone(func_path)
        self.assertEqual(function_name, "my_function")

    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        invalid_json = '{"key": invalid}'
        result = self.parser.parse_json(invalid_json)
        
        # Should handle error gracefully
        self.assertIsNone(result)

    def test_parse_yaml_invalid(self):
        """Test parsing invalid YAML."""
        invalid_yaml = "key: :\ninvalid"
        result = self.parser.parse_yaml(invalid_yaml)
        
        # Should handle error gracefully
        self.assertIsNone(result)


def run_tests(verbose=False):
    """Run all zParser tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzParserInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestResolveSymbolPath))
    suite.addTests(loader.loadTestsFromTestCase(TestParseFunctionPath))
    suite.addTests(loader.loadTestsFromTestCase(TestParseCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestFileContentParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestResolveDataPath))
    suite.addTests(loader.loadTestsFromTestCase(TestExpressionEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestParseDottedPath))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginInvocation))
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

