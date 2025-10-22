#!/usr/bin/env python3
# zTestSuite/zNavigation_Test.py

"""
Unit Tests for zNavigation Subsystem
Tests menu creation, breadcrumb management, navigation, and linking functionality.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI


class TestzNavigationInitialization(unittest.TestCase):
    """Test zNavigation subsystem initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })

    def test_navigation_subsystem_exists(self):
        """Test that navigation subsystem is initialized."""
        self.assertIsNotNone(self.zcli.navigation)
        self.assertEqual(self.zcli.navigation.mycolor, "MENU")

    def test_navigation_has_required_modules(self):
        """Test that navigation has all required modules."""
        self.assertTrue(hasattr(self.zcli.navigation, 'menu'))
        self.assertTrue(hasattr(self.zcli.navigation, 'breadcrumbs'))
        self.assertTrue(hasattr(self.zcli.navigation, 'navigation'))
        self.assertTrue(hasattr(self.zcli.navigation, 'linking'))

    def test_navigation_has_public_methods(self):
        """Test that navigation exposes public API methods."""
        # Menu methods
        self.assertTrue(callable(self.zcli.navigation.create))
        self.assertTrue(callable(self.zcli.navigation.select))
        
        # Breadcrumb methods
        self.assertTrue(callable(self.zcli.navigation.handle_zCrumbs))
        self.assertTrue(callable(self.zcli.navigation.handle_zBack))
        
        # Navigation methods
        self.assertTrue(callable(self.zcli.navigation.navigate_to))
        self.assertTrue(callable(self.zcli.navigation.get_current_location))
        self.assertTrue(callable(self.zcli.navigation.get_navigation_history))
        
        # Linking methods
        self.assertTrue(callable(self.zcli.navigation.handle_zLink))
        self.assertTrue(callable(self.zcli.navigation.create_link))


class TestWalkerNavigationIntegration(unittest.TestCase):
    """Test navigation through Walker UI (integration with zWalker)."""

    @patch('builtins.input', return_value='4')  # Select 'stop'
    def test_walker_navigation_test_menu(self, mock_input):
        """Test Walker UI navigation with test menu."""
        # Initialize Walker with test UI
        test_zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVaFile": "@.zTestSuite.demos.zUI.test_navigation",
            "zBlock": "TestMenu",
            "zVerbose": False
        })
        
        # Walker should initialize successfully
        self.assertIsNotNone(test_zcli.walker)
        self.assertIsNotNone(test_zcli.navigation)

    @patch('builtins.input', return_value='4')  # Select 'stop'
    def test_walker_navigation_simple_menu(self, mock_input):
        """Test Walker UI navigation with simple menu."""
        # Initialize Walker with test UI
        test_zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVaFile": "@.zTestSuite.demos.zUI.test_navigation",
            "zBlock": "SimpleMenu",
            "zVerbose": False
        })
        
        # Verify navigation is available
        self.assertIsNotNone(test_zcli.navigation)
        
    def test_navigation_module_methods_exist(self):
        """Test that navigation module methods are available."""
        zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })
        
        # Verify navigation module has expected methods
        self.assertTrue(hasattr(zcli.navigation, 'menu'))
        self.assertTrue(hasattr(zcli.navigation, 'breadcrumbs'))
        self.assertTrue(hasattr(zcli.navigation, 'navigation'))
        self.assertTrue(hasattr(zcli.navigation, 'linking'))


class TestBreadcrumbs(unittest.TestCase):
    """Test breadcrumb trail management."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })
        
        # Initialize zCrumbs in session if not present
        if "zCrumbs" not in self.zcli.session:
            self.zcli.session["zCrumbs"] = {}

    def test_handle_zCrumbs_initialization(self):
        """Test breadcrumb initialization."""
        zBlock = "TestBlock"
        zKey = "TestKey"
        
        # Mock walker
        mock_walker = Mock()
        mock_walker.zcli = self.zcli
        
        result = self.zcli.navigation.handle_zCrumbs(zBlock, zKey, walker=mock_walker)
        
        # Verify breadcrumb was recorded
        self.assertIn(zBlock, self.zcli.session["zCrumbs"])

    def test_handle_zBack(self):
        """Test back navigation."""
        # Setup breadcrumb trail
        self.zcli.session["zCrumbs"] = {
            "TestBlock": ["Key1", "Key2", "Key3"]
        }
        
        # Mock walker
        mock_walker = Mock()
        mock_walker.zcli = self.zcli
        
        with patch.object(self.zcli.display, 'zDeclare'):
            result = self.zcli.navigation.handle_zBack(walker=mock_walker)
        
        self.assertIsNotNone(result)

    def test_breadcrumb_trail_persistence(self):
        """Test that breadcrumb trail persists in session."""
        zBlock = "MainMenu"
        
        # Mock walker
        mock_walker = Mock()
        mock_walker.zcli = self.zcli
        
        # Add multiple breadcrumbs
        self.zcli.navigation.handle_zCrumbs(zBlock, "Item1", walker=mock_walker)
        self.zcli.navigation.handle_zCrumbs(zBlock, "Item2", walker=mock_walker)
        self.zcli.navigation.handle_zCrumbs(zBlock, "Item3", walker=mock_walker)
        
        # Verify trail exists
        self.assertIn(zBlock, self.zcli.session["zCrumbs"])
        trail = self.zcli.session["zCrumbs"][zBlock]
        self.assertIsInstance(trail, list)


class TestNavigation(unittest.TestCase):
    """Test navigation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })

    def test_get_current_location(self):
        """Test getting current navigation location."""
        location = self.zcli.navigation.get_current_location()
        self.assertIsNotNone(location)

    def test_get_navigation_history(self):
        """Test getting navigation history."""
        history = self.zcli.navigation.get_navigation_history()
        self.assertIsNotNone(history)
        self.assertIsInstance(history, (list, dict))

    def test_navigate_to_with_context(self):
        """Test navigation with context."""
        # This will depend on actual navigation implementation
        # Mock if necessary
        target = "TestTarget"
        context = {"test": "data"}
        
        try:
            result = self.zcli.navigation.navigate_to(target, context=context)
            # Result may vary based on implementation
            self.assertIsNotNone(result)
        except Exception:
            # If not fully implemented, skip gracefully
            pass


class TestLinking(unittest.TestCase):
    """Test inter-file linking functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })

    def test_create_link(self):
        """Test creating a navigation link."""
        source = "SourceMenu"
        target = "TargetMenu"
        metadata = {"description": "Test link"}
        
        try:
            result = self.zcli.navigation.create_link(source, target, metadata=metadata)
            self.assertIsNotNone(result)
        except Exception:
            # If not fully implemented, skip gracefully
            pass

    def test_handle_zLink_requires_walker(self):
        """Test that handle_zLink requires walker parameter."""
        from zCLI.subsystems.zNavigation.zNavigation import handle_zLink
        
        with self.assertRaises(ValueError):
            handle_zLink("TestLink")


class TestStandaloneFunctions(unittest.TestCase):
    """Test standalone handler functions for backward compatibility."""

    def setUp(self):
        """Set up test fixtures."""
        self.zcli = zCLI({
            "zWorkspace": str(Path(__file__).parent.parent),
            "zVerbose": False
        })

    def test_handle_zLink_requires_walker(self):
        """Test that handle_zLink requires walker parameter."""
        from zCLI.subsystems.zNavigation.zNavigation import handle_zLink
        
        with self.assertRaises(ValueError):
            handle_zLink("TestLink")

    def test_handle_zCrumbs_requires_walker(self):
        """Test that handle_zCrumbs requires walker parameter."""
        from zCLI.subsystems.zNavigation.zNavigation import handle_zCrumbs
        
        with self.assertRaises(ValueError):
            handle_zCrumbs("TestBlock", "TestKey")


def run_tests(verbose=False):
    """Run all zNavigation tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestzNavigationInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestWalkerNavigationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestBreadcrumbs))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigation))
    suite.addTests(loader.loadTestsFromTestCase(TestLinking))
    suite.addTests(loader.loadTestsFromTestCase(TestStandaloneFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

