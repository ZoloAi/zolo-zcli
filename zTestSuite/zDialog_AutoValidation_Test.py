#!/usr/bin/env python3
# zTestSuite/zDialog_AutoValidation_Test.py

"""
Comprehensive test suite for zDialog Auto-Validation (Week 5.2).
Tests automatic validation of form data against zSchema rules before submission.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zDialog import zDialog


class TestzDialogAutoValidation(unittest.TestCase):
    """Test zDialog auto-validation with valid zSchema model."""

    def setUp(self):
        """Set up mock zCLI instance and schema for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "testuser",
            "email": "test@example.com",
            "age": 25
        })
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        
        # Mock zLoader to return a schema
        self.mock_zcli.loader = Mock()
        self.mock_schema = {
            "users": {
                "id": {"type": "int", "pk": True},
                "username": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "pattern": "^[a-zA-Z0-9_]{3,20}$",
                        "pattern_message": "Username must be 3-20 characters (letters, numbers, underscore only)"
                    }
                },
                "email": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "format": "email"
                    }
                },
                "age": {
                    "type": "int",
                    "rules": {
                        "min": 18,
                        "max": 120
                    }
                }
            }
        }
        self.mock_zcli.loader.handle = Mock(return_value=self.mock_schema)

    def test_auto_validation_with_valid_data(self):
        """Test auto-validation passes with valid form data."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email", "age"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return collected data (validation passed)
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["age"], 25)
        
        # Verify schema was loaded
        self.mock_zcli.loader.handle.assert_called_once_with("@.zSchema.users")

    def test_auto_validation_with_invalid_username_pattern(self):
        """Test auto-validation fails with invalid username pattern."""
        # Return invalid username (too short, contains special chars)
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "ab",  # Too short (< 3 chars)
            "email": "test@example.com",
            "age": 25
        })
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email", "age"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return None (validation failed)
        self.assertIsNone(result)
        
        # Verify schema was loaded
        self.mock_zcli.loader.handle.assert_called_once_with("@.zSchema.users")

    def test_auto_validation_with_invalid_email_format(self):
        """Test auto-validation fails with invalid email format."""
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "testuser",
            "email": "not-an-email",  # Invalid email format
            "age": 25
        })
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email", "age"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return None (validation failed)
        self.assertIsNone(result)

    def test_auto_validation_with_age_out_of_range(self):
        """Test auto-validation fails with age out of range."""
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "testuser",
            "email": "test@example.com",
            "age": 15  # Below minimum (18)
        })
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email", "age"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return None (validation failed)
        self.assertIsNone(result)

    def test_auto_validation_with_missing_required_field(self):
        """Test auto-validation fails with missing required field."""
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "testuser"
            # Missing required 'email' field
        })
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return None (validation failed)
        self.assertIsNone(result)


class TestzDialogAutoValidationFallback(unittest.TestCase):
    """Test zDialog auto-validation graceful fallback scenarios."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.zDialog = Mock(return_value={
            "name": "Test User"
        })
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.loader = Mock()

    def test_auto_validation_skipped_no_model(self):
        """Test auto-validation is skipped when no model specified."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": None,  # No model
                "fields": ["name"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return collected data (validation skipped)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test User")
        
        # Verify loader was NOT called
        self.mock_zcli.loader.handle.assert_not_called()

    def test_auto_validation_skipped_non_zpath_model(self):
        """Test auto-validation is skipped when model doesn't start with '@'."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "User",  # Not a zPath (doesn't start with '@')
                "fields": ["name"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return collected data (validation skipped)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test User")
        
        # Verify loader was NOT called
        self.mock_zcli.loader.handle.assert_not_called()

    def test_auto_validation_proceeds_on_schema_load_error(self):
        """Test auto-validation proceeds when schema fails to load."""
        # Make loader raise exception
        self.mock_zcli.loader.handle = Mock(side_effect=Exception("Schema not found"))
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.nonexistent",
                "fields": ["name"],
                "onSubmit": None
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should return collected data (validation error logged but proceed)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test User")
        
        # Verify loader was called but failed gracefully
        self.mock_zcli.loader.handle.assert_called_once_with("@.zSchema.nonexistent")


class TestzDialogAutoValidationWebSocket(unittest.TestCase):
    """Test zDialog auto-validation WebSocket integration (zBifrost mode)."""

    def setUp(self):
        """Set up mock zCLI instance for zBifrost mode testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "zBifrost"}  # zBifrost mode
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        
        # Mock WebSocket
        self.mock_zcli.comm = Mock()
        self.mock_zcli.comm.websocket = Mock()
        self.mock_zcli.comm.websocket.broadcast = Mock()
        
        # Mock zLoader
        self.mock_zcli.loader = Mock()
        self.mock_schema = {
            "users": {
                "username": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "pattern": "^[a-zA-Z0-9_]{3,20}$"
                    }
                },
                "email": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "format": "email"
                    }
                }
            }
        }
        self.mock_zcli.loader.handle = Mock(return_value=self.mock_schema)

    def test_websocket_validation_error_broadcast(self):
        """Test validation errors are broadcast via WebSocket in zBifrost mode."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email"],
                "onSubmit": None
            }
        }
        
        # Pre-provided invalid data (WebSocket mode)
        context = {
            "websocket_data": {
                "data": {
                    "username": "ab",  # Invalid (too short)
                    "email": "not-an-email"  # Invalid format
                }
            }
        }
        
        result = zdialog.handle(zHorizontal, context=context)
        
        # Should return None (validation failed)
        self.assertIsNone(result)
        
        # Verify WebSocket broadcast was called with validation errors
        self.mock_zcli.comm.websocket.broadcast.assert_called_once()
        call_args = self.mock_zcli.comm.websocket.broadcast.call_args[0][0]
        
        self.assertEqual(call_args['event'], 'validation_error')
        self.assertEqual(call_args['table'], 'users')
        self.assertIn('errors', call_args)
        self.assertIsInstance(call_args['errors'], dict)
        self.assertIn('fields', call_args)

    def test_websocket_validation_success_no_broadcast(self):
        """Test no WebSocket broadcast when validation succeeds."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email"],
                "onSubmit": None
            }
        }
        
        # Pre-provided valid data (WebSocket mode)
        context = {
            "websocket_data": {
                "data": {
                    "username": "validuser",
                    "email": "valid@example.com"
                }
            }
        }
        
        result = zdialog.handle(zHorizontal, context=context)
        
        # Should return collected data (validation passed)
        self.assertIsNotNone(result)
        
        # Verify NO WebSocket broadcast for successful validation
        self.mock_zcli.comm.websocket.broadcast.assert_not_called()


class TestzDialogAutoValidationWithOnSubmit(unittest.TestCase):
    """Test zDialog auto-validation with onSubmit handling."""

    def setUp(self):
        """Set up mock zCLI instance for onSubmit testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "testuser",
            "email": "test@example.com"
        })
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        
        # Mock zLoader
        self.mock_zcli.loader = Mock()
        self.mock_schema = {
            "users": {
                "username": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "pattern": "^[a-zA-Z0-9_]{3,20}$"
                    }
                },
                "email": {
                    "type": "str",
                    "required": True,
                    "rules": {
                        "format": "email"
                    }
                }
            }
        }
        self.mock_zcli.loader.handle = Mock(return_value=self.mock_schema)

    @patch('zCLI.subsystems.zDialog.zDialog.handle_submit')
    def test_onsubmit_called_after_successful_validation(self, mock_handle_submit):
        """Test onSubmit is called only after successful validation."""
        mock_handle_submit.return_value = {"success": True}
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email"],
                "onSubmit": {"zData": {"action": "insert", "table": "users"}}
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should call handle_submit (validation passed)
        mock_handle_submit.assert_called_once()

    @patch('zCLI.subsystems.zDialog.zDialog.handle_submit')
    def test_onsubmit_not_called_after_failed_validation(self, mock_handle_submit):
        """Test onSubmit is NOT called when validation fails."""
        # Return invalid data
        self.mock_zcli.display.zDialog = Mock(return_value={
            "username": "ab",  # Invalid (too short)
            "email": "test@example.com"
        })
        
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "@.zSchema.users",
                "fields": ["username", "email"],
                "onSubmit": {"zData": {"action": "insert", "table": "users"}}
            }
        }
        
        result = zdialog.handle(zHorizontal)
        
        # Should NOT call handle_submit (validation failed)
        mock_handle_submit.assert_not_called()
        
        # Should return None
        self.assertIsNone(result)


def run_tests(verbose=False):
    """Run all zDialog auto-validation tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogAutoValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogAutoValidationFallback))
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogAutoValidationWebSocket))
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogAutoValidationWithOnSubmit))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    import sys
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

