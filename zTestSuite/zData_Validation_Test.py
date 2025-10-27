"""
zData Validation Tests (Week 5.1)
==================================
Comprehensive tests for DataValidator with pattern, format, min/max, and error messages.
"""

import unittest
import sys
from pathlib import Path

# Add zCLI to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zData.zData_modules.shared.validator import DataValidator


class TestPatternValidation(unittest.TestCase):
    """Test regex pattern validation."""
    
    def setUp(self):
        """Set up test schema with pattern rules."""
        self.schema = {
            'users': {
                'username': {
                    'type': 'str',
                    'required': True,
                    'rules': {
                        'pattern': '^[a-zA-Z0-9_]{3,20}$',
                        'pattern_message': 'Username must be 3-20 characters (letters, numbers, underscore only)'
                    }
                },
                'slug': {
                    'type': 'str',
                    'rules': {
                        'pattern': '^[a-z0-9]+(?:-[a-z0-9]+)*$',
                        'pattern_message': 'Slug must be lowercase letters, numbers, and hyphens'
                    }
                },
                'sku': {
                    'type': 'str',
                    'rules': {
                        'pattern': '^[A-Z]{2,4}-[0-9]{4,6}$',
                        'pattern_message': 'SKU must follow format: ABC-1234'
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_valid_username_pattern(self):
        """Test valid username passes pattern validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'valid_user123'
        })
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
    
    def test_invalid_username_with_spaces(self):
        """Test username with spaces fails pattern validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'invalid user'
        })
        self.assertFalse(is_valid)
        self.assertIn('username', errors)
        self.assertIn('3-20 characters', errors['username'])
    
    def test_invalid_username_with_special_chars(self):
        """Test username with special characters fails."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'user@name!'
        })
        self.assertFalse(is_valid)
        self.assertIn('username', errors)
    
    def test_valid_slug_pattern(self):
        """Test valid slug passes pattern validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'slug': 'my-blog-post'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_slug_with_uppercase(self):
        """Test slug with uppercase fails pattern validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'slug': 'My-Blog-Post'
        })
        self.assertFalse(is_valid)
        self.assertIn('slug', errors)
        self.assertIn('lowercase', errors['slug'])
    
    def test_valid_sku_pattern(self):
        """Test valid SKU passes pattern validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'sku': 'ABC-123456'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_sku_format(self):
        """Test invalid SKU format fails."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'sku': 'abc-123'  # lowercase and too few digits
        })
        self.assertFalse(is_valid)
        self.assertIn('sku', errors)


class TestFormatValidation(unittest.TestCase):
    """Test built-in format validators (email, url, phone)."""
    
    def setUp(self):
        """Set up test schema with format rules."""
        self.schema = {
            'contacts': {
                'email': {
                    'type': 'str',
                    'rules': {
                        'format': 'email',
                        'error_message': 'Please enter a valid email address'
                    }
                },
                'website': {
                    'type': 'str',
                    'rules': {
                        'format': 'url'
                    }
                },
                'phone': {
                    'type': 'str',
                    'rules': {
                        'format': 'phone'
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_valid_email(self):
        """Test valid email passes format validation."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'email': 'user@example.com'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_email_no_at(self):
        """Test email without @ fails."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'email': 'userexample.com'
        })
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
    
    def test_invalid_email_no_domain(self):
        """Test email without domain fails."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'email': 'user@'
        })
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
    
    def test_valid_url_http(self):
        """Test valid HTTP URL passes."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'website': 'http://example.com'
        })
        self.assertTrue(is_valid)
    
    def test_valid_url_https(self):
        """Test valid HTTPS URL passes."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'website': 'https://example.com/path'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_url_no_protocol(self):
        """Test URL without protocol fails."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'website': 'example.com'
        })
        self.assertFalse(is_valid)
        self.assertIn('website', errors)
    
    def test_valid_phone_with_plus(self):
        """Test phone with + prefix passes."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'phone': '+1234567890'
        })
        self.assertTrue(is_valid)
    
    def test_valid_phone_with_spaces(self):
        """Test phone with spaces passes."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'phone': '+1 234 567 8900'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_phone_too_short(self):
        """Test phone with too few digits fails."""
        is_valid, errors = self.validator.validate_insert('contacts', {
            'phone': '123'
        })
        self.assertFalse(is_valid)
        self.assertIn('phone', errors)


class TestNumericValidation(unittest.TestCase):
    """Test min/max numeric validation."""
    
    def setUp(self):
        """Set up test schema with numeric rules."""
        self.schema = {
            'products': {
                'price': {
                    'type': 'float',
                    'rules': {
                        'min': 0.01,
                        'max': 999999.99,
                        'error_message': 'Price must be between $0.01 and $999,999.99'
                    }
                },
                'stock': {
                    'type': 'int',
                    'rules': {
                        'min': 0,
                        'error_message': 'Stock cannot be negative'
                    }
                },
                'age': {
                    'type': 'int',
                    'rules': {
                        'min': 18,
                        'max': 120
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_valid_price_in_range(self):
        """Test price within range passes."""
        is_valid, errors = self.validator.validate_insert('products', {
            'price': 99.99
        })
        self.assertTrue(is_valid)
    
    def test_invalid_price_too_low(self):
        """Test price below minimum fails."""
        is_valid, errors = self.validator.validate_insert('products', {
            'price': 0.00
        })
        self.assertFalse(is_valid)
        self.assertIn('price', errors)
        self.assertIn('$0.01 and $999,999.99', errors['price'])
    
    def test_invalid_price_too_high(self):
        """Test price above maximum fails."""
        is_valid, errors = self.validator.validate_insert('products', {
            'price': 1000000.00
        })
        self.assertFalse(is_valid)
        self.assertIn('price', errors)
    
    def test_valid_stock_zero(self):
        """Test stock at minimum (0) passes."""
        is_valid, errors = self.validator.validate_insert('products', {
            'stock': 0
        })
        self.assertTrue(is_valid)
    
    def test_invalid_stock_negative(self):
        """Test negative stock fails."""
        is_valid, errors = self.validator.validate_insert('products', {
            'stock': -1
        })
        self.assertFalse(is_valid)
        self.assertIn('stock', errors)
        self.assertIn('cannot be negative', errors['stock'])
    
    def test_valid_age_in_range(self):
        """Test age within range passes."""
        is_valid, errors = self.validator.validate_insert('products', {
            'age': 25
        })
        self.assertTrue(is_valid)
    
    def test_invalid_age_too_young(self):
        """Test age below minimum fails."""
        is_valid, errors = self.validator.validate_insert('products', {
            'age': 17
        })
        self.assertFalse(is_valid)
        self.assertIn('age', errors)
    
    def test_invalid_age_too_old(self):
        """Test age above maximum fails."""
        is_valid, errors = self.validator.validate_insert('products', {
            'age': 121
        })
        self.assertFalse(is_valid)
        self.assertIn('age', errors)


class TestStringLengthValidation(unittest.TestCase):
    """Test min_length/max_length string validation."""
    
    def setUp(self):
        """Set up test schema with string length rules."""
        self.schema = {
            'posts': {
                'title': {
                    'type': 'str',
                    'rules': {
                        'min_length': 5,
                        'max_length': 200
                    }
                },
                'bio': {
                    'type': 'str',
                    'rules': {
                        'max_length': 500,
                        'error_message': 'Bio cannot exceed 500 characters'
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_valid_title_length(self):
        """Test title within length range passes."""
        is_valid, errors = self.validator.validate_insert('posts', {
            'title': 'Valid Title'
        })
        self.assertTrue(is_valid)
    
    def test_invalid_title_too_short(self):
        """Test title below minimum length fails."""
        is_valid, errors = self.validator.validate_insert('posts', {
            'title': 'Hi'
        })
        self.assertFalse(is_valid)
        self.assertIn('title', errors)
        self.assertIn('at least 5 characters', errors['title'])
    
    def test_invalid_title_too_long(self):
        """Test title above maximum length fails."""
        is_valid, errors = self.validator.validate_insert('posts', {
            'title': 'A' * 201
        })
        self.assertFalse(is_valid)
        self.assertIn('title', errors)
        self.assertIn('cannot exceed 200 characters', errors['title'])
    
    def test_valid_bio_at_max(self):
        """Test bio at maximum length passes."""
        is_valid, errors = self.validator.validate_insert('posts', {
            'bio': 'A' * 500
        })
        self.assertTrue(is_valid)
    
    def test_invalid_bio_too_long(self):
        """Test bio above maximum length fails."""
        is_valid, errors = self.validator.validate_insert('posts', {
            'bio': 'A' * 501
        })
        self.assertFalse(is_valid)
        self.assertIn('bio', errors)
        self.assertIn('cannot exceed 500 characters', errors['bio'])


class TestCombinedValidation(unittest.TestCase):
    """Test combining multiple validation rules."""
    
    def setUp(self):
        """Set up test schema with multiple rules per field."""
        self.schema = {
            'users': {
                'username': {
                    'type': 'str',
                    'required': True,
                    'rules': {
                        'min_length': 3,
                        'max_length': 20,
                        'pattern': '^[a-zA-Z0-9_]+$',
                        'pattern_message': 'Username must contain only letters, numbers, and underscores'
                    }
                },
                'email': {
                    'type': 'str',
                    'required': True,
                    'rules': {
                        'format': 'email',
                        'max_length': 255
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_valid_combined_rules(self):
        """Test data passing all combined rules."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'valid_user',
            'email': 'user@example.com'
        })
        self.assertTrue(is_valid)
    
    def test_username_fails_min_length(self):
        """Test username fails min_length before pattern."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'ab',  # Too short
            'email': 'user@example.com'
        })
        self.assertFalse(is_valid)
        self.assertIn('username', errors)
    
    def test_username_fails_pattern(self):
        """Test username fails pattern after length checks."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'user@name',  # Valid length but invalid pattern
            'email': 'user@example.com'
        })
        self.assertFalse(is_valid)
        self.assertIn('username', errors)
        self.assertIn('letters, numbers, and underscores', errors['username'])
    
    def test_email_fails_format_and_length(self):
        """Test email fails format validation."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'validuser',
            'email': 'not-an-email'
        })
        self.assertFalse(is_valid)
        self.assertIn('email', errors)


class TestRequiredFieldValidation(unittest.TestCase):
    """Test required field validation."""
    
    def setUp(self):
        """Set up test schema with required fields."""
        self.schema = {
            'users': {
                'id': {
                    'type': 'int',
                    'pk': True
                },
                'username': {
                    'type': 'str',
                    'required': True
                },
                'email': {
                    'type': 'str',
                    'required': True
                },
                'bio': {
                    'type': 'str',
                    'required': False
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_all_required_fields_present(self):
        """Test insert with all required fields passes."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'email': 'test@example.com'
        })
        self.assertTrue(is_valid)
    
    def test_missing_required_field(self):
        """Test insert missing required field fails."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser'
            # Missing required email
        })
        self.assertFalse(is_valid)
        self.assertIn('email', errors)
        self.assertIn('required', errors['email'])
    
    def test_optional_field_can_be_missing(self):
        """Test optional field can be omitted."""
        is_valid, errors = self.validator.validate_insert('users', {
            'username': 'testuser',
            'email': 'test@example.com'
            # bio is optional
        })
        self.assertTrue(is_valid)
    
    def test_update_does_not_require_fields(self):
        """Test update does not enforce required fields."""
        is_valid, errors = self.validator.validate_update('users', {
            'bio': 'Updated bio'
            # username and email not provided - OK for UPDATE
        })
        self.assertTrue(is_valid)


class TestCustomErrorMessages(unittest.TestCase):
    """Test custom error_message and pattern_message."""
    
    def setUp(self):
        """Set up test schema with custom error messages."""
        self.schema = {
            'products': {
                'price': {
                    'type': 'float',
                    'rules': {
                        'min': 0.01,
                        'max': 999999.99,
                        'error_message': 'Price must be between $0.01 and $999,999.99'
                    }
                },
                'sku': {
                    'type': 'str',
                    'rules': {
                        'pattern': '^[A-Z]{2,4}-[0-9]{4,6}$',
                        'pattern_message': 'SKU must follow format: ABC-1234 (2-4 uppercase letters, dash, 4-6 digits)'
                    }
                }
            }
        }
        self.validator = DataValidator(self.schema)
    
    def test_custom_error_message_shown(self):
        """Test custom error_message is shown instead of default."""
        is_valid, errors = self.validator.validate_insert('products', {
            'price': 0.00
        })
        self.assertFalse(is_valid)
        self.assertIn('price', errors)
        self.assertEqual(errors['price'], 'Price must be between $0.01 and $999,999.99')
    
    def test_custom_pattern_message_shown(self):
        """Test custom pattern_message is shown for regex failures."""
        is_valid, errors = self.validator.validate_insert('products', {
            'sku': 'invalid'
        })
        self.assertFalse(is_valid)
        self.assertIn('sku', errors)
        self.assertIn('ABC-1234', errors['sku'])


def run_tests(verbose=False):
    """Run all validation tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPatternValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestNumericValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestStringLengthValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestCombinedValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestRequiredFieldValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomErrorMessages))
    
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result  # Return result object, not boolean


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

