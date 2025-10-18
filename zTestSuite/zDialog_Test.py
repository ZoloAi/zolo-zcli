#!/usr/bin/env python3
# zTestSuite/zDialog_Test.py

"""
Comprehensive test suite for zDialog subsystem.
Tests dialog initialization, context creation, placeholder injection, and submission handling.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zDialog import zDialog, handle_zDialog
from zCLI.subsystems.zDialog.zDialog_modules import (
    create_dialog_context, inject_placeholders, handle_submit
)


class TestzDialogInitialization(unittest.TestCase):
    """Test zDialog initialization and basic setup."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()

    def test_initialization_with_valid_zcli(self):
        """Test zDialog initializes correctly with valid zCLI instance."""
        zdialog = zDialog(self.mock_zcli)
        
        self.assertIsNotNone(zdialog)
        self.assertEqual(zdialog.zcli, self.mock_zcli)
        self.assertEqual(zdialog.session, self.mock_zcli.session)
        self.assertEqual(zdialog.logger, self.mock_zcli.logger)
        self.assertEqual(zdialog.display, self.mock_zcli.display)
        self.assertEqual(zdialog.zparser, self.mock_zcli.zparser)
        self.assertEqual(zdialog.zfunc, self.mock_zcli.zfunc)
        self.assertEqual(zdialog.mycolor, "ZDIALOG")

    def test_initialization_with_walker(self):
        """Test zDialog initializes correctly with walker."""
        mock_walker = Mock()
        zdialog = zDialog(self.mock_zcli, walker=mock_walker)
        
        self.assertEqual(zdialog.walker, mock_walker)

    def test_initialization_without_zcli(self):
        """Test zDialog raises error when zcli is None."""
        with self.assertRaises(ValueError) as context:
            zDialog(None)
        
        self.assertIn("requires a zCLI instance", str(context.exception))

    def test_initialization_with_invalid_zcli(self):
        """Test zDialog raises error when zcli is missing session."""
        invalid_zcli = Mock(spec=[])  # No attributes
        
        with self.assertRaises(ValueError) as context:
            zDialog(invalid_zcli)
        
        self.assertIn("missing 'session' attribute", str(context.exception))

    def test_ready_message_displayed(self):
        """Test ready message is displayed on initialization."""
        zdialog = zDialog(self.mock_zcli)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called_with(
            "zDialog Ready", color="ZDIALOG", indent=0, style="full"
        )


class TestDialogContext(unittest.TestCase):
    """Test dialog context creation and management."""

    def setUp(self):
        """Set up test logger."""
        self.logger = Mock()

    def test_create_dialog_context_basic(self):
        """Test creating basic dialog context."""
        model = "User"
        fields = ["username", "email"]
        
        context = create_dialog_context(model, fields, self.logger)
        
        self.assertIsInstance(context, dict)
        self.assertEqual(context["model"], "User")
        self.assertEqual(context["fields"], ["username", "email"])
        self.assertNotIn("zConv", context)

    def test_create_dialog_context_with_zconv(self):
        """Test creating dialog context with zConv data."""
        model = "User"
        fields = ["username", "email"]
        zConv = {"username": "testuser", "email": "test@example.com"}
        
        context = create_dialog_context(model, fields, self.logger, zConv=zConv)
        
        self.assertEqual(context["model"], "User")
        self.assertEqual(context["fields"], ["username", "email"])
        self.assertEqual(context["zConv"], zConv)


class TestPlaceholderInjection(unittest.TestCase):
    """Test placeholder injection functionality."""

    def setUp(self):
        """Set up test logger and context."""
        self.logger = Mock()
        self.zContext = {
            "model": "User",
            "zConv": {
                "username": "testuser",
                "email": "test@example.com",
                "age": 25
            }
        }

    def test_inject_zconv_entire_dict(self):
        """Test injecting entire zConv dictionary."""
        obj = "zConv"
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result, self.zContext["zConv"])

    def test_inject_zconv_dot_notation(self):
        """Test injecting zConv field using dot notation."""
        obj = "zConv.username"
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result, "testuser")

    def test_inject_zconv_bracket_notation_single_quotes(self):
        """Test injecting zConv field using bracket notation with single quotes."""
        obj = "zConv['email']"
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result, "test@example.com")

    def test_inject_zconv_bracket_notation_double_quotes(self):
        """Test injecting zConv field using bracket notation with double quotes."""
        obj = 'zConv["age"]'
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result, 25)

    def test_inject_placeholders_in_dict(self):
        """Test injecting placeholders in nested dictionary."""
        obj = {
            "user": "zConv.username",
            "contact": "zConv.email",
            "static": "value"
        }
        
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result["user"], "testuser")
        self.assertEqual(result["contact"], "test@example.com")
        self.assertEqual(result["static"], "value")

    def test_inject_placeholders_in_list(self):
        """Test injecting placeholders in list."""
        obj = ["zConv.username", "zConv.email", "static"]
        
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result[0], "testuser")
        self.assertEqual(result[1], "test@example.com")
        self.assertEqual(result[2], "static")

    def test_inject_placeholders_nested_structure(self):
        """Test injecting placeholders in deeply nested structure."""
        obj = {
            "data": {
                "user": "zConv.username",
                "details": ["zConv.email", "zConv.age"]
            }
        }
        
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result["data"]["user"], "testuser")
        self.assertEqual(result["data"]["details"][0], "test@example.com")
        self.assertEqual(result["data"]["details"][1], 25)

    def test_inject_placeholders_missing_field(self):
        """Test injecting placeholder for non-existent field."""
        obj = "zConv.nonexistent"
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertIsNone(result)

    def test_inject_placeholders_no_zconv(self):
        """Test injecting placeholders when zConv is missing."""
        context = {"model": "User"}
        obj = "zConv.username"
        
        result = inject_placeholders(obj, context, self.logger)
        
        self.assertIsNone(result)

    def test_inject_placeholders_non_placeholder_string(self):
        """Test that non-placeholder strings are returned as-is."""
        obj = "regular string"
        result = inject_placeholders(obj, self.zContext, self.logger)
        
        self.assertEqual(result, "regular string")


class TestzDialogHandle(unittest.TestCase):
    """Test zDialog handle method."""

    def setUp(self):
        """Set up mock zCLI instance and zDialog."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock(return_value={"username": "testuser"})
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        
        self.zdialog = zDialog(self.mock_zcli)

    def test_handle_with_valid_dialog_no_submit(self):
        """Test handling dialog without onSubmit."""
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username", "email"]
            }
        }
        
        result = self.zdialog.handle(zHorizontal)
        
        # Should return the collected data
        self.assertEqual(result, {"username": "testuser"})
        
        # Should call display.handle with zDialog event
        self.mock_zcli.display.handle.assert_called_once()
        call_args = self.mock_zcli.display.handle.call_args[0][0]
        self.assertEqual(call_args["event"], "zDialog")

    def test_handle_with_invalid_type(self):
        """Test handling with invalid input type."""
        with self.assertRaises(TypeError) as context:
            self.zdialog.handle("invalid string")
        
        self.assertIn("Unsupported zDialog expression type", str(context.exception))

    def test_handle_calls_display_methods(self):
        """Test that handle calls appropriate display methods."""
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"]
            }
        }
        
        self.zdialog.handle(zHorizontal)
        
        # Should call zDeclare for entry message
        declare_calls = self.mock_zcli.display.zDeclare.call_args_list
        self.assertTrue(any("zDialog" in str(call) for call in declare_calls))

    def test_handle_with_onsubmit_string(self):
        """Test handling dialog with string-based onSubmit."""
        mock_walker = Mock()
        mock_walker.display = Mock()
        mock_walker.display.zDeclare = Mock()
        mock_walker.zcli = self.mock_zcli
        
        zdialog = zDialog(self.mock_zcli, walker=mock_walker)
        
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"],
                "onSubmit": "zFunc(@utils.process, zConv.username)"
            }
        }
        
        self.mock_zcli.display.handle.return_value = {"username": "testuser"}
        self.mock_zcli.zfunc.handle = Mock(return_value={"status": "success"})
        
        result = zdialog.handle(zHorizontal)
        
        # Should call zfunc.handle
        self.mock_zcli.zfunc.handle.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_handle_with_onsubmit_dict(self):
        """Test handling dialog with dict-based onSubmit."""
        mock_walker = Mock()
        mock_walker.display = Mock()
        mock_walker.display.zDeclare = Mock()
        mock_walker.zcli = self.mock_zcli
        
        zdialog = zDialog(self.mock_zcli, walker=mock_walker)
        
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"],
                "onSubmit": {
                    "zCRUD": {
                        "action": "create",
                        "data": "zConv"
                    }
                }
            }
        }
        
        self.mock_zcli.display.handle.return_value = {"username": "testuser"}
        
        with patch('zCLI.subsystems.zDispatch.handle_zDispatch') as mock_dispatch:
            mock_dispatch.return_value = {"status": "created"}
            result = zdialog.handle(zHorizontal)
            
            # Should call zDispatch
            mock_dispatch.assert_called_once()
            self.assertEqual(result, {"status": "created"})


class TestSubmissionHandling(unittest.TestCase):
    """Test submission handling functionality."""

    def setUp(self):
        """Set up mock walker and context."""
        self.mock_walker = Mock()
        self.mock_walker.display = Mock()
        self.mock_walker.display.zDeclare = Mock()
        self.mock_walker.zcli = Mock()
        self.mock_walker.zcli.zfunc = Mock()
        
        self.logger = Mock()
        self.zContext = {
            "model": "User",
            "fields": ["username", "email"],
            "zConv": {"username": "testuser", "email": "test@example.com"}
        }

    def test_handle_submit_with_string(self):
        """Test handling string-based submission."""
        submit_expr = "zFunc(@utils.process, zConv.username)"
        self.mock_walker.zcli.zfunc.handle = Mock(return_value={"status": "success"})
        
        result = handle_submit(submit_expr, self.zContext, self.logger, walker=self.mock_walker)
        
        # Should call zfunc.handle
        self.mock_walker.zcli.zfunc.handle.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_handle_submit_with_dict(self):
        """Test handling dict-based submission."""
        submit_expr = {
            "zCRUD": {
                "action": "create",
                "data": "zConv"
            }
        }
        
        with patch('zCLI.subsystems.zDispatch.handle_zDispatch') as mock_dispatch:
            mock_dispatch.return_value = {"status": "created"}
            result = handle_submit(submit_expr, self.zContext, self.logger, walker=self.mock_walker)
            
            # Should call zDispatch
            mock_dispatch.assert_called_once()
            self.assertEqual(result, {"status": "created"})

    def test_handle_submit_without_walker(self):
        """Test handle_submit raises error without walker."""
        with self.assertRaises(ValueError) as context:
            handle_submit("zFunc(test)", self.zContext, self.logger, walker=None)
        
        self.assertIn("requires a walker instance", str(context.exception))

    def test_handle_submit_with_invalid_type(self):
        """Test handle_submit with invalid submission type."""
        submit_expr = 123  # Invalid type
        
        result = handle_submit(submit_expr, self.zContext, self.logger, walker=self.mock_walker)
        
        # Should return False for invalid type
        self.assertEqual(result, False)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility functions."""

    def setUp(self):
        """Set up mock zCLI and walker."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock(return_value={"username": "testuser"})
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        
        self.mock_walker = Mock()
        self.mock_walker.zcli = self.mock_zcli

    def test_handle_zdialog_with_zcli(self):
        """Test handle_zDialog with zcli parameter."""
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"]
            }
        }
        
        result = handle_zDialog(zHorizontal, zcli=self.mock_zcli)
        
        self.assertEqual(result, {"username": "testuser"})

    def test_handle_zdialog_with_walker(self):
        """Test handle_zDialog with walker parameter."""
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"]
            }
        }
        
        result = handle_zDialog(zHorizontal, walker=self.mock_walker)
        
        self.assertEqual(result, {"username": "testuser"})

    def test_handle_zdialog_without_zcli_or_walker(self):
        """Test handle_zDialog raises error without zcli or walker."""
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"]
            }
        }
        
        with self.assertRaises(ValueError) as context:
            handle_zDialog(zHorizontal)
        
        self.assertIn("requires either zcli or walker", str(context.exception))

    def test_handle_zdialog_with_walker_no_zcli_attr(self):
        """Test handle_zDialog raises error when walker has no zcli."""
        mock_walker = Mock(spec=[])  # No zcli attribute
        
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"]
            }
        }
        
        with self.assertRaises(ValueError):
            handle_zDialog(zHorizontal, walker=mock_walker)


class TestzDialogEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up mock zCLI instance."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()

    def test_handle_with_missing_model(self):
        """Test handling dialog with missing model."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "fields": ["username"]
            }
        }
        
        with self.assertRaises(KeyError):
            zdialog.handle(zHorizontal)

    def test_handle_with_missing_fields(self):
        """Test handling dialog with missing fields."""
        zdialog = zDialog(self.mock_zcli)
        
        zHorizontal = {
            "zDialog": {
                "model": "User"
            }
        }
        
        with self.assertRaises(KeyError):
            zdialog.handle(zHorizontal)

    def test_handle_with_onsubmit_exception(self):
        """Test handling dialog when onSubmit raises exception."""
        mock_walker = Mock()
        mock_walker.display = Mock()
        mock_walker.display.zDeclare = Mock()
        mock_walker.zcli = self.mock_zcli
        
        zdialog = zDialog(self.mock_zcli, walker=mock_walker)
        
        zHorizontal = {
            "zDialog": {
                "model": "User",
                "fields": ["username"],
                "onSubmit": "zFunc(@invalid.function)"
            }
        }
        
        self.mock_zcli.display.handle.return_value = {"username": "testuser"}
        self.mock_zcli.zfunc.handle = Mock(side_effect=Exception("Function error"))
        
        with self.assertRaises(Exception):
            zdialog.handle(zHorizontal)

    def test_inject_placeholders_with_malformed_bracket(self):
        """Test injecting placeholders with malformed bracket notation."""
        logger = Mock()
        zContext = {"zConv": {"field": "value"}}
        
        # Missing closing bracket
        obj = "zConv['field'"
        result = inject_placeholders(obj, zContext, logger)
        
        # Should log warning and return original
        logger.warning.assert_called()


def run_tests(verbose=False):
    """Run all zDialog tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestDialogContext))
    suite.addTests(loader.loadTestsFromTestCase(TestPlaceholderInjection))
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogHandle))
    suite.addTests(loader.loadTestsFromTestCase(TestSubmissionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestzDialogEdgeCases))
    
    # Run tests with appropriate verbosity
    verbosity_level = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity_level)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

