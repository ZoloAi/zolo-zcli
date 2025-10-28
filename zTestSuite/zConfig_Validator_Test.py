#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for ConfigValidator (Week 1.1 - Layer 0: Foundation)

Tests the "fail fast" config validation that runs BEFORE subsystem initialization.
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zConfig.zConfig_modules.helpers.config_validator import (
    ConfigValidator,
    ConfigValidationError
)


class TestConfigValidatorValid(unittest.TestCase):
    """Test valid configurations pass validation"""
    
    def test_empty_config_is_valid(self):
        """Test that empty config is valid (uses defaults)"""
        validator = ConfigValidator({}, logger=None)
        # Should not raise
        validator.validate()
    
    def test_terminal_mode_valid(self):
        """Test Terminal mode is valid"""
        validator = ConfigValidator({"zMode": "Terminal"}, logger=None)
        validator.validate()
    
    def test_bifrost_mode_valid(self):
        """Test zBifrost mode is valid"""
        validator = ConfigValidator({"zMode": "zBifrost"}, logger=None)
        validator.validate()
    
    def test_valid_workspace(self):
        """Test that existing workspace directory is valid"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = ConfigValidator({"zWorkspace": tmpdir}, logger=None)
            validator.validate()
    
    def test_websocket_config_valid(self):
        """Test valid websocket config"""
        validator = ConfigValidator({
            "websocket": {
                "port": 8765,
                "host": "127.0.0.1",
                "require_auth": False
            }
        }, logger=None)
        validator.validate()
    
    def test_http_server_config_valid(self):
        """Test valid HTTP server config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = ConfigValidator({
                "http_server": {
                    "port": 8080,
                    "host": "127.0.0.1",
                    "serve_path": tmpdir,
                    "enabled": True
                }
            }, logger=None)
            validator.validate()


class TestConfigValidatorInvalidWorkspace(unittest.TestCase):
    """Test invalid workspace configurations"""
    
    def test_nonexistent_workspace_fails(self):
        """Test that non-existent workspace path fails validation"""
        validator = ConfigValidator({
            "zWorkspace": "/nonexistent/path/12345"
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError) as cm:
            validator.validate()
        
        self.assertIn("does not exist", str(cm.exception))
    
    def test_workspace_not_string_fails(self):
        """Test that non-string workspace fails validation"""
        validator = ConfigValidator({
            "zWorkspace": 12345
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError):
            validator.validate()


class TestConfigValidatorInvalidMode(unittest.TestCase):
    """Test invalid zMode configurations"""
    
    def test_invalid_mode_fails(self):
        """Test that invalid zMode fails validation"""
        validator = ConfigValidator({
            "zMode": "InvalidMode"
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError) as cm:
            validator.validate()
        
        self.assertIn("zMode", str(cm.exception))


class TestConfigValidatorInvalidWebsocket(unittest.TestCase):
    """Test invalid websocket configurations"""
    
    def test_websocket_invalid_port(self):
        """Test that invalid websocket port fails"""
        validator = ConfigValidator({
            "websocket": {"port": "not_a_port"}
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError) as cm:
            validator.validate()
        
        self.assertIn("port", str(cm.exception).lower())


class TestConfigValidatorInvalidHTTPServer(unittest.TestCase):
    """Test invalid HTTP server configurations"""
    
    def test_http_server_invalid_port(self):
        """Test that invalid HTTP server port fails"""
        validator = ConfigValidator({
            "http_server": {"port": "not_a_port"}
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError):
            validator.validate()


class TestConfigValidatorPortConflicts(unittest.TestCase):
    """Test port conflict detection"""
    
    def test_port_conflict_fails(self):
        """Test that same port for websocket and HTTP fails"""
        validator = ConfigValidator({
            "websocket": {"port": 8765},
            "http_server": {"port": 8765}
        }, logger=None)
        
        with self.assertRaises(ConfigValidationError) as cm:
            validator.validate()
        
        self.assertIn("port", str(cm.exception).lower())


def run_tests(verbose=True):
    """Run all validator tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorValid))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorInvalidWorkspace))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorInvalidMode))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorInvalidWebsocket))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorInvalidHTTPServer))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidatorPortConflicts))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

