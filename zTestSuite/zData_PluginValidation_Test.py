"""Comprehensive test suite for zData plugin validator system (Week 5.4).

Tests the layered validation architecture where plugin validators AUGMENT built-in validators.
"""

import unittest
from unittest.mock import MagicMock, patch
from zCLI.subsystems.zData.zData_modules.shared.validator import DataValidator


class TestPluginValidatorExecution(unittest.TestCase):
    """Test plugin validator execution (valid/invalid)."""

    def setUp(self):
        """Set up test fixtures with plugin validator."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'required': True,
                    'rules': {
                        'format': 'email',
                        'validator': "&validators.check_email_domain(['company.com'])"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_plugin_validator_passes(self, mock_parse_inv, mock_parse_args):
        """Test plugin validator passes for valid data."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(return_value=(True, None))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Valid email from approved domain
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@company.com'})
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        mock_plugin.check_email_domain.assert_called_once()

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_plugin_validator_fails(self, mock_parse_inv, mock_parse_args):
        """Test plugin validator fails for invalid data."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(return_value=(False, "Email must use approved domain: company.com"))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Valid email format but wrong domain
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@gmail.com'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        self.assertIn('approved domain', errors['email'])


class TestLayeredValidation(unittest.TestCase):
    """Test layered validation: built-in → plugin (fail-fast)."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'format': 'email',  # Layer 4
                        'validator': "&validators.check_email_domain(['company.com'])"  # Layer 5
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    def test_builtin_fails_plugin_skipped(self):
        """Test plugin validator is NOT called if built-in fails (fail-fast)."""
        # Invalid email format (built-in Layer 4 fails)
        is_valid, errors = self.validator.validate_insert('users', {'email': 'not-an-email'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        # Plugin should NOT have been called (fail-fast)
        self.mock_zcli.loader.cache.get.assert_not_called()

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_builtin_passes_plugin_runs(self, mock_parse_inv, mock_parse_args):
        """Test plugin validator runs ONLY if built-in passes."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(return_value=(False, "Wrong domain"))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Valid email format (built-in passes) but wrong domain (plugin fails)
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@gmail.com'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        self.assertEqual(errors['email'], "Wrong domain")
        # Plugin WAS called (built-in passed)
        mock_plugin.check_email_domain.assert_called_once()


class TestPluginNotFound(unittest.TestCase):
    """Test graceful degradation when plugin not found."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "&nonexistent.check_something()"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_plugin_not_found_graceful_skip(self, mock_parse_inv):
        """Test validation continues if plugin not found (graceful degradation)."""
        # Mock plugin resolution - plugin not found
        mock_parse_inv.return_value = ('nonexistent', 'check_something', "()")
        self.mock_zcli.loader.cache.get.return_value = None  # Plugin not in cache
        
        # Validation should pass (plugin skipped gracefully)
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@example.com'})
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        # Warning should be logged
        self.mock_logger.warning.assert_called()


class TestPluginFunctionNotFound(unittest.TestCase):
    """Test graceful degradation when function not found in plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "&validators.nonexistent_function()"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_function_not_found_graceful_skip(self, mock_parse_inv):
        """Test validation continues if function not found (graceful degradation)."""
        # Mock plugin resolution - plugin exists but function doesn't
        mock_parse_inv.return_value = ('validators', 'nonexistent_function', "()")
        
        mock_plugin = MagicMock(spec=[])  # Empty spec = no attributes
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Validation should pass (plugin skipped gracefully)
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@example.com'})
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        # Warning should be logged
        self.mock_logger.warning.assert_called()


class TestPluginException(unittest.TestCase):
    """Test error handling when plugin execution raises exception."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "&validators.check_email_domain(['company.com'])"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_plugin_execution_exception(self, mock_parse_inv, mock_parse_args):
        """Test validation fails gracefully if plugin raises exception."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(side_effect=ValueError("Test error"))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Validation should fail with error message
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@company.com'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        self.assertIn('Plugin validator error', errors['email'])
        # Error should be logged
        self.mock_logger.error.assert_called()


class TestContextInjection(unittest.TestCase):
    """Test context injection (table, full_data) into plugin validators."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'password_confirm': {
                    'type': 'str',
                    'rules': {
                        'validator': "&validators.check_cross_field_match('password')"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_context_injected(self, mock_parse_inv, mock_parse_args):
        """Test table_name and full_data are injected into plugin."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_cross_field_match', "('password')")
        mock_parse_args.return_value = (['password'], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_cross_field_match = MagicMock(return_value=(True, None))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Validate with full data
        data = {'password': 'secret123', 'password_confirm': 'secret123'}
        is_valid, errors = self.validator.validate_insert('users', data)
        
        self.assertTrue(is_valid)
        
        # Check that context was injected
        call_args = mock_plugin.check_cross_field_match.call_args
        self.assertEqual(call_args[1]['table'], 'users')
        self.assertEqual(call_args[1]['full_data'], data)


class TestMultipleValidators(unittest.TestCase):
    """Test multiple fields with plugin validators."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'username': {
                    'type': 'str',
                    'rules': {
                        'pattern': '^[a-zA-Z0-9_]{3,20}$',
                        'validator': "&validators.check_username_blacklist(['admin', 'root'])"
                    }
                },
                'email': {
                    'type': 'str',
                    'rules': {
                        'format': 'email',
                        'validator': "&validators.check_email_domain(['company.com'])"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_multiple_validators_all_pass(self, mock_parse_inv, mock_parse_args):
        """Test multiple plugin validators all pass."""
        # Mock plugin resolution for both validators
        def side_effect_inv(spec):
            if 'username_blacklist' in spec:
                return ('validators', 'check_username_blacklist', "(['admin', 'root'])")
            else:
                return ('validators', 'check_email_domain', "(['company.com'])")
        
        def side_effect_args(spec):
            if 'admin' in spec:
                return ([['admin', 'root']], {})
            else:
                return ([['company.com']], {})
        
        mock_parse_inv.side_effect = side_effect_inv
        mock_parse_args.side_effect = side_effect_args
        
        mock_plugin = MagicMock()
        mock_plugin.check_username_blacklist = MagicMock(return_value=(True, None))
        mock_plugin.check_email_domain = MagicMock(return_value=(True, None))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Valid data for both fields
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'john_doe',
            'email': 'john@company.com'
        })
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_multiple_validators_one_fails(self, mock_parse_inv, mock_parse_args):
        """Test multiple plugin validators, one fails."""
        # Mock plugin resolution
        def side_effect_inv(spec):
            if 'username_blacklist' in spec:
                return ('validators', 'check_username_blacklist', "(['admin', 'root'])")
            else:
                return ('validators', 'check_email_domain', "(['company.com'])")
        
        def side_effect_args(spec):
            if 'admin' in spec:
                return ([['admin', 'root']], {})
            else:
                return ([['company.com']], {})
        
        mock_parse_inv.side_effect = side_effect_inv
        mock_parse_args.side_effect = side_effect_args
        
        mock_plugin = MagicMock()
        mock_plugin.check_username_blacklist = MagicMock(return_value=(False, "Username 'admin' is reserved"))
        mock_plugin.check_email_domain = MagicMock(return_value=(True, None))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Username is blacklisted
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'admin',
            'email': 'john@company.com'
        })
        
        self.assertFalse(is_valid)
        self.assertIn('username', errors)
        self.assertIn('reserved', errors['username'])


class TestNozcliInstance(unittest.TestCase):
    """Test graceful degradation when zcli not provided."""

    def test_no_zcli_skips_plugin(self):
        """Test plugin validator is skipped if zcli not provided."""
        schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "&validators.check_email_domain(['company.com'])"
                    }
                }
            }
        }
        
        mock_logger = MagicMock()
        validator = DataValidator(schema, logger=mock_logger, zcli=None)  # No zcli
        
        # Validation should pass (plugin skipped)
        is_valid, errors = validator.validate_insert('users', {'email': 'test@example.com'})
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        # Warning should be logged
        mock_logger.warning.assert_called()


class TestInvalidSyntax(unittest.TestCase):
    """Test handling of invalid plugin validator syntax."""

    def test_no_ampersand_skipped(self):
        """Test validator without & prefix is skipped."""
        schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "validators.check_email_domain(['company.com'])"  # Missing &
                    }
                }
            }
        }
        
        mock_zcli = MagicMock()
        mock_logger = MagicMock()
        validator = DataValidator(schema, logger=mock_logger, zcli=mock_zcli)
        
        # Validation should pass (invalid syntax skipped)
        is_valid, errors = validator.validate_insert('users', {'email': 'test@example.com'})
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        # Warning should be logged
        mock_logger.warning.assert_called()


class TestCustomErrorMessage(unittest.TestCase):
    """Test custom error_message overrides plugin error."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'format': 'email',
                        'validator': "&validators.check_email_domain(['company.com'])",
                        'error_message': "Custom error: Email must be corporate"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_custom_error_message_used(self, mock_parse_inv, mock_parse_args):
        """Test custom error_message overrides plugin error."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(return_value=(False, "Original plugin error"))
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Plugin fails
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@gmail.com'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        # Custom error message should be used, not plugin's
        self.assertEqual(errors['email'], "Custom error: Email must be corporate")


class TestInvalidReturnFormat(unittest.TestCase):
    """Test handling of invalid plugin return format."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            'users': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'validator': "&validators.check_email_domain(['company.com'])"
                    }
                }
            }
        }
        
        self.mock_zcli = MagicMock()
        self.mock_logger = MagicMock()
        self.validator = DataValidator(self.schema, logger=self.mock_logger, zcli=self.mock_zcli)

    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_arguments')
    @patch('zCLI.subsystems.zParser.zParser_modules.zParser_plugin._parse_invocation')
    def test_invalid_return_format_error(self, mock_parse_inv, mock_parse_args):
        """Test plugin returning invalid format (not tuple) fails validation."""
        # Mock plugin resolution
        mock_parse_inv.return_value = ('validators', 'check_email_domain', "(['company.com'])")
        mock_parse_args.return_value = ([['company.com']], {})
        
        mock_plugin = MagicMock()
        mock_plugin.check_email_domain = MagicMock(return_value=True)  # Invalid: not tuple
        self.mock_zcli.loader.cache.get.return_value = mock_plugin
        
        # Validation should fail with error
        is_valid, errors = self.validator.validate_insert('users', {'email': 'test@company.com'})
        
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        self.assertIn('invalid return format', errors['email'])
        # Error should be logged
        self.mock_logger.error.assert_called()


def run_tests(verbose=False):
    """Run all plugin validation tests."""
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    run_tests(verbose=True)

