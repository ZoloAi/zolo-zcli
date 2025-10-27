#!/usr/bin/env python3
# zTestSuite/zUninstall_Test.py

"""
Test Suite: zCLI Uninstall Utilities (Week 6.1.2)

Tests the refactored uninstall.py utility with:
- Constants usage (no magic strings)
- Standardized function signatures (all take zcli)
- DRY helper function (confirm_action)
- Consistent return values
- Error handling
"""

import unittest
from unittest.mock import Mock, patch
from zCLI.utils import uninstall


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined and used."""
    
    def test_package_name_constant_exists(self):
        """Test PACKAGE_NAME constant is defined."""
        self.assertEqual(uninstall.PACKAGE_NAME, "zolo-zcli")
    
    def test_optional_dependencies_constant_exists(self):
        """Test OPTIONAL_DEPENDENCIES constant is defined."""
        self.assertEqual(uninstall.OPTIONAL_DEPENDENCIES, ["pandas", "psycopg2-binary"])
    
    def test_confirmation_prompt_constant_exists(self):
        """Test CONFIRMATION_PROMPT constant is defined."""
        self.assertIn("yes", uninstall.CONFIRMATION_PROMPT.lower())
    
    def test_confirmation_value_constant_exists(self):
        """Test CONFIRMATION_VALUE constant is defined."""
        self.assertEqual(uninstall.CONFIRMATION_VALUE, "yes")


class TestConfirmAction(unittest.TestCase):
    """Test the confirm_action helper function (DRY fix)."""
    
    def setUp(self):
        """Create mock display for testing."""
        self.display = Mock()
    
    def test_confirm_action_with_yes(self):
        """Test confirm_action returns True when user says 'yes'."""
        self.display.read_string.return_value = "yes"
        result = uninstall.confirm_action(self.display, "test action")
        self.assertTrue(result)
        self.display.read_string.assert_called_once_with(uninstall.CONFIRMATION_PROMPT)
    
    def test_confirm_action_with_no(self):
        """Test confirm_action returns False when user says 'no'."""
        self.display.read_string.return_value = "no"
        result = uninstall.confirm_action(self.display, "test action")
        self.assertFalse(result)
        self.display.error.assert_called_once_with("Cancelled", indent=1)
    
    def test_confirm_action_with_empty_input(self):
        """Test confirm_action returns False with empty input."""
        self.display.read_string.return_value = ""
        result = uninstall.confirm_action(self.display, "test action")
        self.assertFalse(result)
        self.display.error.assert_called_once_with("Cancelled", indent=1)
    
    def test_confirm_action_case_insensitive(self):
        """Test confirm_action handles 'YES' (uppercase) correctly."""
        self.display.read_string.return_value = "YES"
        result = uninstall.confirm_action(self.display, "test action")
        self.assertTrue(result)
    
    def test_confirm_action_strips_whitespace(self):
        """Test confirm_action strips whitespace from input."""
        self.display.read_string.return_value = "  yes  "
        result = uninstall.confirm_action(self.display, "test action")
        self.assertTrue(result)


class TestFunctionSignatures(unittest.TestCase):
    """Test that all functions have standardized signatures."""
    
    def test_uninstall_package_takes_zcli(self):
        """Test uninstall_package accepts zcli parameter."""
        zcli = Mock()
        zcli.display = Mock()
        
        with patch('zCLI.utils.uninstall.subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = uninstall.uninstall_package(zcli)
            self.assertIsInstance(result, bool)
    
    def test_remove_dependencies_takes_zcli(self):
        """Test remove_dependencies accepts zcli parameter."""
        zcli = Mock()
        zcli.display = Mock()
        
        with patch('zCLI.utils.uninstall.subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = uninstall.remove_dependencies(zcli)
            self.assertIsInstance(result, bool)
    
    def test_remove_user_data_takes_zcli(self):
        """Test remove_user_data accepts zcli parameter."""
        zcli = Mock()
        zcli.display = Mock()
        zcli.config.sys_paths.user_config_dir = Mock()
        zcli.config.sys_paths.user_config_dir.exists.return_value = False
        zcli.config.sys_paths.user_data_dir = Mock()
        zcli.config.sys_paths.user_data_dir.exists.return_value = False
        zcli.config.sys_paths.user_cache_dir = Mock()
        zcli.config.sys_paths.user_cache_dir.exists.return_value = False
        
        result = uninstall.remove_user_data(zcli)
        self.assertIsInstance(result, bool)


class TestUninstallPackage(unittest.TestCase):
    """Test uninstall_package function."""
    
    def setUp(self):
        """Create mock zcli for testing."""
        self.zcli = Mock()
        self.zcli.display = Mock()
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_uninstall_package_success(self, mock_run):
        """Test successful package uninstall."""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = uninstall.uninstall_package(self.zcli)
        
        self.assertTrue(result)
        self.zcli.display.success.assert_called_once_with("Package removed", indent=1)
        mock_run.assert_called_once()
        
        # Verify correct command
        call_args = mock_run.call_args[0][0]
        self.assertIn("pip", call_args)
        self.assertIn("uninstall", call_args)
        self.assertIn(uninstall.PACKAGE_NAME, call_args)
        self.assertIn("-y", call_args)
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_uninstall_package_failure(self, mock_run):
        """Test failed package uninstall."""
        mock_run.return_value = Mock(returncode=1, stderr="Package not found")
        
        result = uninstall.uninstall_package(self.zcli)
        
        self.assertFalse(result)
        self.zcli.display.error.assert_called_once()
        error_call = self.zcli.display.error.call_args[0][0]
        self.assertIn("Package removal failed", error_call)
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_uninstall_package_exception(self, mock_run):
        """Test exception handling in uninstall_package."""
        mock_run.side_effect = Exception("pip not found")
        
        result = uninstall.uninstall_package(self.zcli)
        
        self.assertFalse(result)
        self.zcli.display.error.assert_called_once()
        error_call = self.zcli.display.error.call_args[0][0]
        self.assertIn("Package removal error", error_call)


class TestRemoveDependencies(unittest.TestCase):
    """Test remove_dependencies function."""
    
    def setUp(self):
        """Create mock zcli for testing."""
        self.zcli = Mock()
        self.zcli.display = Mock()
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_remove_dependencies_all_success(self, mock_run):
        """Test successful removal of all dependencies."""
        mock_run.return_value = Mock(returncode=0)
        
        result = uninstall.remove_dependencies(self.zcli)
        
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, len(uninstall.OPTIONAL_DEPENDENCIES))
        self.zcli.display.success.assert_called_once()
        
        # Verify both dependencies were attempted
        call_args_list = [call[0][0] for call in mock_run.call_args_list]
        for dep in uninstall.OPTIONAL_DEPENDENCIES:
            self.assertTrue(any(dep in str(args) for args in call_args_list))
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_remove_dependencies_partial_success(self, mock_run):
        """Test partial success when one dependency fails."""
        # First call succeeds, second fails
        mock_run.side_effect = [
            Mock(returncode=0),  # pandas success
            Mock(returncode=1)   # psycopg2 failure
        ]
        
        result = uninstall.remove_dependencies(self.zcli)
        
        self.assertTrue(result)  # At least one succeeded
        self.assertEqual(mock_run.call_count, len(uninstall.OPTIONAL_DEPENDENCIES))
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_remove_dependencies_all_fail(self, mock_run):
        """Test when all dependencies fail to remove."""
        mock_run.return_value = Mock(returncode=1)
        
        result = uninstall.remove_dependencies(self.zcli)
        
        self.assertFalse(result)  # None succeeded
        self.assertEqual(mock_run.call_count, len(uninstall.OPTIONAL_DEPENDENCIES))


class TestRemoveUserData(unittest.TestCase):
    """Test remove_user_data function."""
    
    def setUp(self):
        """Create mock zcli for testing."""
        self.zcli = Mock()
        self.zcli.display = Mock()
        
        # Mock path objects
        self.config_dir = Mock()
        self.data_dir = Mock()
        self.cache_dir = Mock()
        
        self.zcli.config.sys_paths.user_config_dir = self.config_dir
        self.zcli.config.sys_paths.user_data_dir = self.data_dir
        self.zcli.config.sys_paths.user_cache_dir = self.cache_dir
    
    @patch('zCLI.utils.uninstall.shutil.rmtree')
    def test_remove_user_data_all_exist(self, mock_rmtree):
        """Test successful removal when all directories exist."""
        self.config_dir.exists.return_value = True
        self.data_dir.exists.return_value = True
        self.cache_dir.exists.return_value = True
        
        result = uninstall.remove_user_data(self.zcli)
        
        self.assertTrue(result)
        self.assertEqual(mock_rmtree.call_count, 3)
        self.zcli.display.success.assert_called_once()
    
    @patch('zCLI.utils.uninstall.shutil.rmtree')
    def test_remove_user_data_none_exist(self, mock_rmtree):
        """Test when no directories exist."""
        self.config_dir.exists.return_value = False
        self.data_dir.exists.return_value = False
        self.cache_dir.exists.return_value = False
        
        result = uninstall.remove_user_data(self.zcli)
        
        self.assertFalse(result)  # None removed
        mock_rmtree.assert_not_called()
    
    @patch('zCLI.utils.uninstall.shutil.rmtree')
    def test_remove_user_data_partial_removal(self, mock_rmtree):
        """Test partial removal when some directories fail."""
        self.config_dir.exists.return_value = True
        self.data_dir.exists.return_value = True
        self.cache_dir.exists.return_value = True
        
        # First call succeeds, second fails, third succeeds
        mock_rmtree.side_effect = [None, Exception("Permission denied"), None]
        
        result = uninstall.remove_user_data(self.zcli)
        
        self.assertTrue(result)  # At least one succeeded
        self.assertEqual(mock_rmtree.call_count, 3)
        self.zcli.display.error.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """Test error handling across all functions."""
    
    def setUp(self):
        """Create mock zcli for testing."""
        self.zcli = Mock()
        self.zcli.display = Mock()
    
    @patch('zCLI.utils.uninstall.subprocess.run')
    def test_subprocess_exception_handled(self, mock_run):
        """Test that subprocess exceptions are caught and handled."""
        mock_run.side_effect = OSError("Command not found")
        
        result = uninstall.uninstall_package(self.zcli)
        
        self.assertFalse(result)
        self.zcli.display.error.assert_called_once()
    
    @patch('zCLI.utils.uninstall.shutil.rmtree')
    def test_filesystem_exception_handled(self, mock_rmtree):
        """Test that filesystem exceptions are caught and handled."""
        self.zcli.config.sys_paths.user_config_dir = Mock()
        self.zcli.config.sys_paths.user_config_dir.exists.return_value = True
        self.zcli.config.sys_paths.user_data_dir = Mock()
        self.zcli.config.sys_paths.user_data_dir.exists.return_value = False
        self.zcli.config.sys_paths.user_cache_dir = Mock()
        self.zcli.config.sys_paths.user_cache_dir.exists.return_value = False
        
        mock_rmtree.side_effect = PermissionError("Access denied")
        
        result = uninstall.remove_user_data(self.zcli)
        
        self.assertFalse(result)  # Failed to remove any
        self.zcli.display.error.assert_called_once()


def run_tests(verbose=False):
    """Run all uninstall utility tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConstants))
    suite.addTests(loader.loadTestsFromTestCase(TestConfirmAction))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionSignatures))
    suite.addTests(loader.loadTestsFromTestCase(TestUninstallPackage))
    suite.addTests(loader.loadTestsFromTestCase(TestRemoveDependencies))
    suite.addTests(loader.loadTestsFromTestCase(TestRemoveUserData))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    unittest.main()

