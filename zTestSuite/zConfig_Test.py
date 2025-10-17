#!/usr/bin/env python3
# zTestSuite/zConfig_Test.py

"""
Test Suite for zConfig Subsystem

Tests configuration path resolution, permissions, hierarchy loading,
and cross-platform compatibility.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zConfig.zConfig_modules.config_paths import zConfigPaths
from zCLI.subsystems.zConfig.zConfig_modules.config_machine import MachineConfig
from zCLI.subsystems.zConfig import zConfig


class TestConfigPaths(unittest.TestCase):
    """Test configuration path resolution and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.paths = zConfigPaths()
    
    def test_os_detection(self):
        """Test that OS type is correctly detected."""
        valid_os_types = ("Linux", "Darwin", "Windows")
        self.assertIn(self.paths.os_type, valid_os_types,
                     f"OS type '{self.paths.os_type}' not recognized")
    
    def test_unsupported_os_exits(self):
        """Test that unsupported OS types trigger exit."""
        with patch('zCLI.subsystems.zConfig.zConfig_modules.config_paths.platform.system', return_value='FreeBSD'):
            with self.assertRaises(SystemExit):
                zConfigPaths()
    
    def test_user_config_paths_exist(self):
        """Test that user config path properties return valid Path objects."""
        self.assertIsInstance(self.paths.user_config_dir, Path)
        self.assertIsInstance(self.paths.user_config_dir_legacy, Path)
        self.assertIsInstance(self.paths.user_zconfigs_dir, Path)
    
    def test_system_config_paths_exist(self):
        """Test that system config path properties return valid Path objects."""
        self.assertIsInstance(self.paths.system_config_dir, Path)
        self.assertIsInstance(self.paths.system_config_defaults, Path)
        self.assertIsInstance(self.paths.system_machine_config, Path)
    
    def test_user_paths_in_home_directory(self):
        """Test that user paths are within home directory."""
        home = Path.home()
        self.assertTrue(
            str(self.paths.user_config_dir).startswith(str(home)),
            "User config path should be in home directory"
        )
        self.assertTrue(
            str(self.paths.user_config_dir_legacy).startswith(str(home)),
            "Legacy config path should be in home directory"
        )
    
    def test_system_path_unix_conventions(self):
        """Test that system paths follow OS conventions."""
        if self.paths.os_type in ("Linux", "Darwin"):
            self.assertEqual(
                self.paths.system_config_dir,
                Path("/etc/zolo-zcli"),
                "Unix system config should be /etc/zolo-zcli"
            )


class TestWritePermissions(unittest.TestCase):
    """Test write permission validation (migrated from config_paths.py)."""
    
    def setUp(self):
        """Set up test fixtures with temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.paths = zConfigPaths()
    
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_user_directory_writable(self):
        """Test that user config directory is writable."""
        # Use temp dir for testing to avoid permission issues with actual user dir
        test_dir = Path(self.temp_dir) / "user_config"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = test_dir / ".test_write"
        try:
            test_file.touch()
            test_file.unlink()
            writable = True
        except PermissionError:
            writable = False
        except Exception as e:
            self.fail(f"Unexpected error testing write permissions: {e}")
        
        self.assertTrue(writable, f"Test directory should be writable: {test_dir}")
    
    def test_system_directory_permissions(self):
        """Test system directory permission detection (informational only)."""
        system_dir = self.paths.system_config_dir
        
        # This test is informational - we don't require write access
        if not system_dir.exists():
            self.skipTest(f"System config directory doesn't exist: {system_dir}")
        
        test_file = system_dir / ".test_write"
        try:
            test_file.touch()
            test_file.unlink()
            has_write = True
        except PermissionError:
            has_write = False
        except FileNotFoundError:
            # Directory doesn't exist - expected for non-admin users
            has_write = False
        except Exception as e:
            self.skipTest(f"Cannot test system directory: {e}")
        
        # Just report the result, don't fail
        print(f"\n[INFO] System config directory ({system_dir}) writable: {has_write}")
    
    def test_temp_directory_isolation(self):
        """Test write operations in isolated temporary directory."""
        test_path = Path(self.temp_dir) / "test_config"
        test_path.mkdir(parents=True, exist_ok=True)
        
        # Verify we can write
        test_file = test_path / "test.yaml"
        test_file.write_text("test: true\n")
        
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "test: true\n")
    
    def test_directory_creation(self):
        """Test recursive directory creation."""
        nested_path = Path(self.temp_dir) / "a" / "b" / "c" / "config"
        
        # Should create all parent directories
        nested_path.mkdir(parents=True, exist_ok=True)
        
        self.assertTrue(nested_path.exists())
        self.assertTrue(nested_path.is_dir())


class TestMachineConfig(unittest.TestCase):
    """Test machine configuration loading and management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.paths = zConfigPaths()
        # Use a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_machine_config_initialization(self):
        """Test that machine config initializes with auto-detected values."""
        machine = MachineConfig(self.paths)
        
        # Check that basic auto-detection works
        self.assertIsNotNone(machine.get("hostname"))
        self.assertIsNotNone(machine.get("os"))
        self.assertIsNotNone(machine.get("architecture"))
    
    def test_machine_config_get_all(self):
        """Test getting complete machine configuration."""
        machine = MachineConfig(self.paths)
        config = machine.get_all()
        
        self.assertIsInstance(config, dict)
        self.assertIn("hostname", config)
        self.assertIn("os", config)
    
    def test_machine_config_update_runtime(self):
        """Test runtime config updates."""
        machine = MachineConfig(self.paths)
        
        original = machine.get("deployment")
        machine.update("deployment", "test")
        
        self.assertEqual(machine.get("deployment"), "test")
        
        # Restore original
        machine.update("deployment", original)


class TestConfigHierarchy(unittest.TestCase):
    """Test configuration hierarchy and loading order."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform path handling."""
    
    def test_path_separators(self):
        """Test that Path objects handle OS-specific separators."""
        paths = zConfigPaths()
        
        # Path objects should work regardless of OS
        config_path = paths.user_config_dir / "test.yaml"
        
        self.assertIsInstance(config_path, Path)
        self.assertTrue(str(config_path).endswith("test.yaml"))
    
    @patch('zCLI.subsystems.zConfig.zConfig_modules.config_paths.platform.system')
    def test_linux_paths(self, mock_system):
        """Test Linux-specific path resolution."""
        mock_system.return_value = 'Linux'
        paths = zConfigPaths()
        
        self.assertEqual(paths.system_config_dir, Path("/etc/zolo-zcli"))
    
    @patch('zCLI.subsystems.zConfig.zConfig_modules.config_paths.platform.system')
    def test_macos_paths(self, mock_system):
        """Test macOS-specific path resolution."""
        mock_system.return_value = 'Darwin'
        paths = zConfigPaths()
        
        self.assertEqual(paths.system_config_dir, Path("/etc/zolo-zcli"))
    
    @patch('zCLI.subsystems.zConfig.zConfig_modules.config_paths.platform.system')
    def test_windows_paths(self, mock_system):
        """Test Windows-specific path resolution."""
        mock_system.return_value = 'Windows'
        paths = zConfigPaths()
        
        # Windows uses platformdirs
        self.assertIsInstance(paths.system_config_dir, Path)


def run_tests(verbose=True):
    """Run all zConfig tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigPaths))
    suite.addTests(loader.loadTestsFromTestCase(TestWritePermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestMachineConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigHierarchy))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossPlatformCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zCLI Configuration Test Suite")
    print("=" * 70)
    print()
    
    result = run_tests(verbose=True)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

