#!/usr/bin/env python3
# zTestSuite/zUtils_Test.py

"""
Test Suite for zUtils Subsystem

Tests:
    - Plugin loading and management
    - Plugin function exposure
    - Plugin invocation via & modifier
    - Error handling and validation
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI

# Get demos directory path for plugin loading
DEMOS_DIR = Path(__file__).parent / 'demos'
TEST_PLUGIN_PATH = str(DEMOS_DIR / 'test_plugin.py')


class TestzUtilsPluginLoading(unittest.TestCase):
    """Test plugin loading functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI()

    def test_utils_initialization(self):
        """Test that zUtils initializes correctly."""
        self.assertIsNotNone(self.zcli.utils)
        self.assertTrue(hasattr(self.zcli.utils, 'load_plugins'))
        self.assertTrue(hasattr(self.zcli.utils, 'plugins'))
        self.assertIsInstance(self.zcli.utils.plugins, dict)

    def test_load_single_plugin(self):
        """Test loading a single plugin."""
        plugins = self.zcli.utils.load_plugins([TEST_PLUGIN_PATH])
        
        self.assertEqual(len(plugins), 1)
        self.assertIn(TEST_PLUGIN_PATH, plugins)

    def test_load_multiple_plugins(self):
        """Test loading multiple plugins."""
        # Load test plugin from demos directory
        plugins = self.zcli.utils.load_plugins([TEST_PLUGIN_PATH])
        
        self.assertGreaterEqual(len(plugins), 1)

    def test_plugin_function_exposure(self):
        """Test that plugin functions are exposed on zUtils instance."""
        self.zcli.utils.load_plugins([TEST_PLUGIN_PATH])
        
        # Check that functions are exposed
        self.assertTrue(hasattr(self.zcli.utils, 'hello_world'))
        self.assertTrue(hasattr(self.zcli.utils, 'random_number'))
        self.assertTrue(hasattr(self.zcli.utils, 'get_plugin_info'))
        
        # Check that they are callable
        self.assertTrue(callable(self.zcli.utils.hello_world))
        self.assertTrue(callable(self.zcli.utils.random_number))

    def test_plugin_function_execution(self):
        """Test executing plugin functions."""
        self.zcli.utils.load_plugins([TEST_PLUGIN_PATH])
        
        # Test hello_world
        result = self.zcli.utils.hello_world("Test")
        self.assertEqual(result, "Hello, Test!")
        
        # Test random_number
        num = self.zcli.utils.random_number(1, 10)
        self.assertIsInstance(num, int)
        self.assertGreaterEqual(num, 1)
        self.assertLessEqual(num, 10)

    def test_load_nonexistent_plugin(self):
        """Test loading a plugin that doesn't exist."""
        # Should not raise an error (best-effort loading)
        plugins = self.zcli.utils.load_plugins(['nonexistent.plugin'])
        
        # Plugin should not be loaded
        self.assertNotIn('nonexistent.plugin', plugins)

    def test_empty_plugin_list(self):
        """Test loading with empty plugin list."""
        plugins = self.zcli.utils.load_plugins([])
        self.assertEqual(len(plugins), 0)

    def test_none_plugin_list(self):
        """Test loading with None plugin list."""
        plugins = self.zcli.utils.load_plugins(None)
        self.assertEqual(len(plugins), 0)


class TestzUtilsPluginInvocation(unittest.TestCase):
    """Test plugin invocation via & modifier."""

    def setUp(self):
        """Set up test fixtures."""
        # Create zCLI instance with test plugin loaded
        self.zcli = zCLI({"plugins": [TEST_PLUGIN_PATH]})

    def test_is_plugin_invocation(self):
        """Test plugin invocation detection."""
        # Valid plugin invocations
        self.assertTrue(self.zcli.zparser.is_plugin_invocation("&test_plugin.hello_world()"))
        self.assertTrue(self.zcli.zparser.is_plugin_invocation("&test_plugin.random_number(1, 10)"))
        
        # Invalid plugin invocations
        self.assertFalse(self.zcli.zparser.is_plugin_invocation("hello_world()"))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation("@path.to.file"))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation("$alias"))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation(123))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation(None))

    def test_resolve_hello_world_no_args(self):
        """Test resolving hello_world with no arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        self.assertEqual(result, "Hello, World!")

    def test_resolve_hello_world_with_args(self):
        """Test resolving hello_world with arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world('Alice')")
        self.assertEqual(result, "Hello, Alice!")
        
        result = self.zcli.zparser.resolve_plugin_invocation('&test_plugin.hello_world("Bob")')
        self.assertEqual(result, "Hello, Bob!")

    def test_resolve_random_number_no_args(self):
        """Test resolving random_number with no arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number()")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)

    def test_resolve_random_number_with_args(self):
        """Test resolving random_number with arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number(1, 10)")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 10)

    def test_resolve_non_plugin_value(self):
        """Test that non-plugin values are returned as-is."""
        result = self.zcli.zparser.resolve_plugin_invocation("regular string")
        self.assertEqual(result, "regular string")
        
        result = self.zcli.zparser.resolve_plugin_invocation(123)
        self.assertEqual(result, 123)

    def test_invalid_syntax(self):
        """Test error handling for invalid syntax."""
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&invalid syntax")
        self.assertIn("Invalid plugin invocation syntax", str(context.exception))

    def test_plugin_not_loaded(self):
        """Test error when plugin is not loaded and file doesn't exist."""
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&nonexistent.function()")
        # New unified behavior: searches standard paths, returns "Plugin not found"
        self.assertIn("Plugin not found", str(context.exception))

    def test_function_not_found(self):
        """Test error when function doesn't exist in plugin."""
        # First load the plugin (auto-discovery)
        self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        
        # Now try non-existent function
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&test_plugin.nonexistent_function()")
        # Should find the cached plugin but fail on function lookup
        self.assertIn("Function not found", str(context.exception))


class TestzUtilsPluginArgumentParsing(unittest.TestCase):
    """Test argument parsing for plugin invocations."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({"plugins": [TEST_PLUGIN_PATH]})

    def test_string_arguments(self):
        """Test parsing string arguments."""
        # Single quotes
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world('Test')")
        self.assertEqual(result, "Hello, Test!")
        
        # Double quotes
        result = self.zcli.zparser.resolve_plugin_invocation('&test_plugin.hello_world("Test")')
        self.assertEqual(result, "Hello, Test!")

    def test_integer_arguments(self):
        """Test parsing integer arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number(5, 15)")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 5)
        self.assertLessEqual(result, 15)

    def test_multiple_arguments(self):
        """Test parsing multiple arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number(10, 20)")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 10)
        self.assertLessEqual(result, 20)

    def test_no_arguments(self):
        """Test parsing with no arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        self.assertEqual(result, "Hello, World!")


class TestzUtilsSessionInjection(unittest.TestCase):
    """Test CLI session injection into plugins."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI()

    def test_preloaded_plugin_has_zcli(self):
        """Test that pre-loaded plugins have zcli injected."""
        # Load plugin
        self.zcli.utils.load_plugins([TEST_PLUGIN_PATH])
        
        # Get the module from plugins dict
        plugin_module = self.zcli.utils.plugins[TEST_PLUGIN_PATH]
        
        # Check that zcli is injected
        self.assertTrue(hasattr(plugin_module, 'zcli'))
        self.assertEqual(plugin_module.zcli, self.zcli)

    def test_dynamic_plugin_has_zcli(self):
        """Test that dynamically loaded plugins have zcli injected."""
        # Load plugin dynamically via unified syntax
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        self.assertEqual(result, "Hello, World!")
        
        # Check cache for the module (by filename, not path)
        cached_module = self.zcli.loader.cache.get("test_plugin", cache_type="plugin")
        
        # Module should have zcli injected
        self.assertIsNotNone(cached_module)
        self.assertTrue(hasattr(cached_module, 'zcli'))
        self.assertEqual(cached_module.zcli, self.zcli)

    def test_session_aware_plugin_access(self):
        """Test that session-aware plugin can access zcli subsystems."""
        # Load session-aware plugin using unified syntax
        result = self.zcli.zparser.resolve_plugin_invocation("&session_aware_plugin.get_workspace()")
        
        # Should return the workspace path
        self.assertEqual(result, self.zcli.session["zWorkspace"])

    def test_session_aware_plugin_logger(self):
        """Test that plugin can access logger."""
        result = self.zcli.zparser.resolve_plugin_invocation("&session_aware_plugin.log_message('test')")
        
        # Should return True (logged successfully)
        self.assertTrue(result)

    def test_session_aware_plugin_display(self):
        """Test that plugin can access display."""
        result = self.zcli.zparser.resolve_plugin_invocation("&session_aware_plugin.display_message('test')")
        
        # Should return True (displayed successfully)
        self.assertTrue(result)


class TestzUtilsPluginzPathInvocation(unittest.TestCase):
    """Test plugin invocation with unified filename-based syntax."""

    def setUp(self):
        """Set up test fixtures."""
        # No pre-loaded plugins - testing auto-discovery and caching
        self.zcli = zCLI()

    def test_unified_syntax_auto_discovery(self):
        """Test unified &PluginName.function() syntax with auto-discovery."""
        # Should auto-discover from @.zCLI.utils
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        self.assertEqual(result, "Hello, World!")

    def test_unified_syntax_with_args(self):
        """Test unified syntax with arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world('Unified')")
        self.assertEqual(result, "Hello, Unified!")

    def test_unified_syntax_random_number(self):
        """Test unified syntax with numeric arguments."""
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number(50, 60)")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 50)
        self.assertLessEqual(result, 60)

    def test_cache_hit_after_first_load(self):
        """Test that second invocation hits cache."""
        # First call - loads plugin
        self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        
        # Check cache
        cached = self.zcli.loader.cache.get("test_plugin", cache_type="plugin")
        self.assertIsNotNone(cached)
        
        # Second call - should hit cache
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.random_number(1, 10)")
        self.assertIsInstance(result, int)

    def test_different_plugin_file(self):
        """Test loading different plugin file."""
        result = self.zcli.zparser.resolve_plugin_invocation("&workspace_plugin.workspace_greeting('Test')")
        self.assertEqual(result, "Hello from workspace, Test!")

    def test_multiple_functions_same_plugin(self):
        """Test calling multiple functions from same plugin."""
        result1 = self.zcli.zparser.resolve_plugin_invocation("&workspace_plugin.workspace_multiply(7, 8)")
        self.assertEqual(result1, 56)
        
        result2 = self.zcli.zparser.resolve_plugin_invocation("&workspace_plugin.get_workspace_info()")
        self.assertIsInstance(result2, dict)
        self.assertEqual(result2['name'], 'Workspace Plugin')

    def test_plugin_not_found(self):
        """Test error when plugin doesn't exist."""
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&nonexistent_plugin.function()")
        self.assertIn("Plugin not found", str(context.exception))

    def test_function_not_found(self):
        """Test error when function doesn't exist in valid plugin."""
        # First load the plugin so it's in cache
        self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")
        
        # Now try to call non-existent function
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&test_plugin.nonexistent_func()")
        self.assertIn("Function not found", str(context.exception))

    def test_invalid_syntax_multi_dots(self):
        """Test that multi-dot syntax is rejected."""
        with self.assertRaises(ValueError) as context:
            self.zcli.zparser.resolve_plugin_invocation("&path.to.plugin.function()")
        self.assertIn("Invalid plugin invocation syntax", str(context.exception))

    def test_plugin_invocation_detection(self):
        """Test that plugin invocations are correctly detected."""
        self.assertTrue(self.zcli.zparser.is_plugin_invocation("&test_plugin.hello()"))
        self.assertTrue(self.zcli.zparser.is_plugin_invocation("&MyPlugin.do_something()"))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation("test_plugin.hello()"))
        self.assertFalse(self.zcli.zparser.is_plugin_invocation("&invalid"))


class TestzUtilsIntegration(unittest.TestCase):
    """Test integration with other subsystems."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({"plugins": [TEST_PLUGIN_PATH]})

    def test_utils_before_zdata(self):
        """Test that zUtils initializes before zData."""
        # This is verified by the initialization order in zCLI.py
        self.assertIsNotNone(self.zcli.utils)
        self.assertIsNotNone(self.zcli.data)
        
        # Verify plugin is loaded and accessible
        self.assertIn(TEST_PLUGIN_PATH, self.zcli.utils.plugins)

    def test_plugin_access_from_parser(self):
        """Test that zParser can access plugins through zCLI."""
        # Parser should be able to resolve plugin invocations (old style with pre-loaded plugins)
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world('Parser')")
        self.assertEqual(result, "Hello, Parser!")

    def test_plugin_access_via_unified_syntax(self):
        """Test that zParser can access plugins via unified syntax (auto-discovery)."""
        # Unified syntax - auto-discovers from standard paths
        result = self.zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world('Unified')")
        self.assertEqual(result, "Hello, Unified!")

    def test_plugin_info_retrieval(self):
        """Test retrieving plugin information."""
        info = self.zcli.utils.get_plugin_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], 'Test Plugin')
        self.assertEqual(info['version'], '1.0.0')
        self.assertIn('hello_world', info['functions'])
        self.assertIn('random_number', info['functions'])


def run_tests(verbose=True):
    """Run all zUtils tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsPluginLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsPluginInvocation))
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsPluginArgumentParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsSessionInjection))
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsPluginzPathInvocation))
    suite.addTests(loader.loadTestsFromTestCase(TestzUtilsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("zUtils Test Suite")
    print("=" * 70)
    
    result = run_tests(verbose=True)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

