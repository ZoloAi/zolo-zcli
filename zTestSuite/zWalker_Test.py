# zTestSuite/zWalker_Test.py

"""
Comprehensive test suite for zWalker subsystem.
Tests UI navigation, menu systems, and integration with all subsystems.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zCLI.subsystems.zWalker.zWalker import zWalker


class TestzWalkerInitialization(unittest.TestCase):
    """Test zWalker initialization and setup."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zCrumbs": {}}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    def test_zwalker_initialization(self):
        """Test zWalker initializes correctly."""
        walker = zWalker(self.mock_zcli)
        
        self.assertIsNotNone(walker)
        self.assertEqual(walker.zcli, self.mock_zcli)
        self.assertEqual(walker.session, self.mock_zcli.session)
        self.assertEqual(walker.display, self.mock_zcli.display)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called()

    def test_walker_extends_zwizard(self):
        """Test zWalker properly extends zWizard."""
        walker = zWalker(self.mock_zcli)
        
        # Should have zWizard methods
        self.assertTrue(hasattr(walker, 'handle'))
        self.assertTrue(hasattr(walker, 'execute_loop'))

    def test_walker_has_navigation_access(self):
        """Test zWalker has access to navigation subsystem."""
        walker = zWalker(self.mock_zcli)
        
        self.assertEqual(walker.navigation, self.mock_zcli.navigation)

    def test_walker_has_plugin_access(self):
        """Test zWalker has direct access to plugins."""
        walker = zWalker(self.mock_zcli)
        
        self.assertEqual(walker.plugins, self.mock_zcli.utils.plugins)


class TestzWalkerSessionManagement(unittest.TestCase):
    """Test zWalker session management."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    def test_init_walker_session(self):
        """Test _init_walker_session sets up session correctly."""
        walker = zWalker(self.mock_zcli)
        walker._init_walker_session()
        
        # Walker now preserves original zMode (Terminal or zBifrost)
        # It runs within the existing mode context
        self.assertIn(walker.session["zMode"], ["Terminal", "zBifrost"])
        self.assertIn("zCrumbs", walker.session)
        self.assertIn("zBlock", walker.session)

    def test_configure_logger_debug_mode(self):
        """Test logger configuration in debug mode."""
        self.mock_zcli.session = {"zMode": "Debug"}
        walker = zWalker(self.mock_zcli)
        
        # Should attempt to set debug level
        self.assertIsNotNone(walker.logger)


class TestzWalkerRun(unittest.TestCase):
    """Test zWalker run method and main execution."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zCrumbs": {}}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    def test_run_missing_zvafile(self):
        """Test run returns error when zVaFile missing."""
        self.mock_zcli.zspark_obj = {}
        walker = zWalker(self.mock_zcli)
        
        result = walker.run()
        
        self.assertIn("error", result)
        self.assertIn("No zVaFile", result["error"])

    def test_run_failed_load(self):
        """Test run returns error when file loading fails."""
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.loader.handle.return_value = None
        
        walker = zWalker(self.mock_zcli)
        result = walker.run()
        
        self.assertIn("error", result)

    def test_run_missing_root_block(self):
        """Test run returns error when root block not found."""
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "missing"}
        self.mock_zcli.loader.handle.return_value = {"root": {"key": "value"}}
        
        walker = zWalker(self.mock_zcli)
        result = walker.run()
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    @patch.object(zWalker, 'zBlock_loop')
    def test_run_success(self, mock_loop):
        """Test run executes successfully with valid inputs."""
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.loader.handle.return_value = {
            "root": {"key1": "value1", "key2": "value2"}
        }
        mock_loop.return_value = {"success": True}
        
        walker = zWalker(self.mock_zcli)
        result = walker.run()
        
        self.assertEqual(result, {"success": True})
        mock_loop.assert_called_once()


class TestzWalkerBlockLoop(unittest.TestCase):
    """Test zWalker zBlock_loop method."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zCrumbs": {"root": []}, "zBlock": "root"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.navigation.handle_zCrumbs = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    @patch.object(zWalker, 'execute_loop')
    def test_zblock_loop_basic(self, mock_execute):
        """Test zBlock_loop calls execute_loop correctly."""
        mock_execute.return_value = {"result": "success"}
        
        walker = zWalker(self.mock_zcli)
        active_block = {"key1": "value1", "key2": "value2"}
        
        result = walker.zBlock_loop(active_block)
        
        mock_execute.assert_called_once()
        self.assertEqual(result, {"result": "success"})
        
        # Should call zDeclare for loop start
        self.mock_zcli.display.zDeclare.assert_called()

    def test_zblock_loop_generates_keys_if_none(self):
        """Test zBlock_loop generates keys if not provided."""
        walker = zWalker(self.mock_zcli)
        active_block = {"key1": "value1", "key2": "value2"}
        
        with patch.object(walker, 'execute_loop') as mock_execute:
            mock_execute.return_value = {"result": "success"}
            walker.zBlock_loop(active_block)
            
            # Should call execute_loop with items_dict
            call_args = mock_execute.call_args
            self.assertEqual(call_args[1]['items_dict'], active_block)


class TestzWalkerNavigationCallbacks(unittest.TestCase):
    """Test zWalker navigation callbacks."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zCrumbs": {"root": []}, "zBlock": "root"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.navigation.handle_zBack = Mock(return_value=({}, [], None))
        self.mock_zcli.navigation.handle_zCrumbs = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    def test_walker_dispatch_tracks_breadcrumbs(self):
        """Test walker_dispatch tracks breadcrumbs correctly."""
        walker = zWalker(self.mock_zcli)
        active_block = {"key1": "value1"}
        
        with patch.object(walker, 'execute_loop') as mock_execute:
            # Capture the dispatch function
            def capture_dispatch_fn(*args, **kwargs):
                dispatch_fn = kwargs.get('dispatch_fn')
                if dispatch_fn:
                    # Call it to test breadcrumb tracking
                    dispatch_fn("key1", "value1")
                return {"success": True}
            
            mock_execute.side_effect = capture_dispatch_fn
            walker.zBlock_loop(active_block)
            
            # Should call handle_zCrumbs
            self.mock_zcli.navigation.handle_zCrumbs.assert_called()


class TestzWalkerIntegration(unittest.TestCase):
    """Test zWalker integration with other subsystems."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zCrumbs": {}}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.dispatch = Mock()
        self.mock_zcli.navigation = Mock()
        self.mock_zcli.loader = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.open = Mock()
        self.mock_zcli.utils = Mock()
        self.mock_zcli.utils.plugins = {}
        self.mock_zcli.zspark_obj = {"zVaFile": "@.test.ui", "zBlock": "root"}
        self.mock_zcli.data = Mock()
        self.mock_zcli.wizard = Mock()

    def test_walker_uses_dispatch(self):
        """Test zWalker uses dispatch subsystem."""
        walker = zWalker(self.mock_zcli)
        
        self.assertEqual(walker.dispatch, self.mock_zcli.dispatch)

    def test_walker_uses_navigation(self):
        """Test zWalker uses navigation subsystem."""
        walker = zWalker(self.mock_zcli)
        
        self.assertEqual(walker.navigation, self.mock_zcli.navigation)

    def test_walker_uses_loader(self):
        """Test zWalker uses loader subsystem."""
        walker = zWalker(self.mock_zcli)
        
        self.assertEqual(walker.loader, self.mock_zcli.loader)

    def test_walker_has_all_required_subsystems(self):
        """Test zWalker has access to all required subsystems."""
        walker = zWalker(self.mock_zcli)
        
        required_attrs = [
            'display', 'dispatch', 'navigation', 'loader',
            'zfunc', 'open', 'plugins', 'session'
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(walker, attr))


def run_tests(verbose=False):
    """Run all zWalker tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerSessionManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerRun))
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerBlockLoop))
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerNavigationCallbacks))
    suite.addTests(loader.loadTestsFromTestCase(TestzWalkerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    return result  # Return result object, not boolean


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

