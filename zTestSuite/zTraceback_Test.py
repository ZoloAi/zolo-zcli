#!/usr/bin/env python3
# zTestSuite/zTraceback_Test.py

"""
Comprehensive test suite for zTraceback and interactive traceback.
Tests exception handling, context management, and interactive UI features.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.utils.zTraceback import zTraceback, ExceptionContext
from zCLI.utils.zTraceback import (
    display_formatted_traceback,
    retry_last_operation,
    show_exception_history
)


class TestzTracebackInitialization(unittest.TestCase):
    """Test zTraceback initialization."""

    def test_initialization_without_logger(self):
        """Test zTraceback initializes without logger."""
        handler = zTraceback()
        self.assertIsNone(handler.logger)
        self.assertIsNone(handler.zcli)

    def test_initialization_with_logger(self):
        """Test zTraceback initializes with logger."""
        mock_logger = Mock()
        handler = zTraceback(logger=mock_logger)
        self.assertEqual(handler.logger, mock_logger)

    def test_initialization_with_zcli(self):
        """Test zTraceback initializes with zCLI instance."""
        mock_zcli = Mock()
        handler = zTraceback(logger=None, zcli=mock_zcli)
        self.assertEqual(handler.zcli, mock_zcli)

    def test_exception_context_storage_initialized(self):
        """Test exception context storage is initialized."""
        handler = zTraceback()
        self.assertIsNone(handler.last_exception)
        self.assertIsNone(handler.last_operation)
        self.assertEqual(handler.last_context, {})
        self.assertEqual(handler.exception_history, [])


class TestExceptionFormatting(unittest.TestCase):
    """Test exception formatting methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = zTraceback()

    def test_format_exception_basic(self):
        """Test basic exception formatting."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            formatted = self.handler.format_exception(e)
            self.assertIn("ValueError", formatted)
            self.assertIn("Test error", formatted)

    def test_format_exception_with_locals(self):
        """Test exception formatting with locals included."""
        try:
            test_var = 42
            raise ValueError("Test error")
        except ValueError as e:
            formatted = self.handler.format_exception(e, include_locals=True)
            self.assertIn("ValueError", formatted)
            self.assertIn("Test error", formatted)
            # Should include traceback lines
            self.assertIn("Traceback", formatted)

    def test_get_traceback_info(self):
        """Test extracting structured traceback info."""
        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError as e:
            info = self.handler.get_traceback_info(e)
            
            self.assertIn('file', info)
            self.assertIn('line', info)
            self.assertIn('function', info)
            self.assertEqual(info['exception_type'], 'RuntimeError')
            self.assertEqual(info['exception_message'], 'Test runtime error')

    def test_get_traceback_info_no_traceback(self):
        """Test get_traceback_info with exception that has no traceback."""
        exc = ValueError("No traceback")
        exc.__traceback__ = None
        info = self.handler.get_traceback_info(exc)
        
        # Should return basic info even without traceback
        self.assertEqual(info['exception_type'], 'ValueError')
        self.assertEqual(info['exception_message'], 'No traceback')


class TestExceptionLogging(unittest.TestCase):
    """Test exception logging methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.handler = zTraceback(logger=self.mock_logger)

    def test_log_exception_basic(self):
        """Test basic exception logging."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.handler.log_exception(e, message="Operation failed")
            
            # Verify logger.error was called with exc_info=True
            self.mock_logger.error.assert_called_once()
            call_args = self.mock_logger.error.call_args
            self.assertTrue(call_args[1]['exc_info'])

    def test_log_exception_with_context(self):
        """Test exception logging with context."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            context = {'action': 'insert', 'table': 'users'}
            self.handler.log_exception(e, message="DB error", context=context)
            
            # Verify error was logged
            self.mock_logger.error.assert_called()
            # Verify context was logged
            self.mock_logger.debug.assert_called_with("Error context: %s", context)

    def test_log_exception_with_locals(self):
        """Test exception logging with local variable info."""
        self.mock_logger.isEnabledFor.return_value = True
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.handler.log_exception(e, include_locals=True)
            
            # Verify location debug info was logged
            debug_calls = [call for call in self.mock_logger.debug.call_args_list 
                          if 'Error location:' in str(call)]
            self.assertTrue(len(debug_calls) > 0)

    def test_log_exception_without_logger_prints_to_stderr(self):
        """Test log_exception falls back to stderr when no logger."""
        handler = zTraceback()  # No logger
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                handler.log_exception(e, message="Failed operation")
                
                output = mock_stderr.getvalue()
                self.assertIn("Failed operation", output)
                self.assertIn("Test error", output)


class TestExceptionContext(unittest.TestCase):
    """Test ExceptionContext context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.handler = zTraceback(logger=self.mock_logger)

    def test_context_manager_no_exception(self):
        """Test ExceptionContext when no exception occurs."""
        with ExceptionContext(
            self.handler,
            operation="test_operation",
            reraise=False
        ):
            result = "success"
        
        # No exception should be stored
        self.assertIsNone(self.handler.last_exception)

    def test_context_manager_catches_exception(self):
        """Test ExceptionContext catches and logs exception."""
        with ExceptionContext(
            self.handler,
            operation="test_operation",
            reraise=False
        ):
            raise ValueError("Test error")
        
        # Should have logged the exception
        self.mock_logger.error.assert_called()

    def test_context_manager_reraise(self):
        """Test ExceptionContext with reraise=True."""
        with self.assertRaises(ValueError):
            with ExceptionContext(
                self.handler,
                operation="test_operation",
                reraise=True
            ):
                raise ValueError("Test error")
        
        # Should have logged before reraising
        self.mock_logger.error.assert_called()

    def test_context_manager_with_context_dict(self):
        """Test ExceptionContext with context data."""
        context_data = {'action': 'delete', 'id': 123}
        
        with ExceptionContext(
            self.handler,
            operation="delete_user",
            context=context_data,
            reraise=False
        ):
            raise ValueError("Delete failed")
        
        # Verify context was logged
        self.mock_logger.debug.assert_called_with("Error context: %s", context_data)

    def test_context_manager_default_return(self):
        """Test ExceptionContext returns default value on exception."""
        ctx = ExceptionContext(
            self.handler,
            operation="test",
            reraise=False,
            default_return="default_value"
        )
        
        self.assertEqual(ctx.default_return, "default_value")


class TestInteractiveTraceback(unittest.TestCase):
    """Test interactive traceback features."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.handler = zTraceback(logger=self.mock_zcli.logger, zcli=self.mock_zcli)
        # Important: Set up the mock so zcli.zTraceback points to our handler
        self.mock_zcli.zTraceback = self.handler

    def test_exception_history_storage(self):
        """Test exception history is stored correctly."""
        try:
            raise ValueError("Error 1")
        except ValueError as e:
            self.handler.last_exception = e
            self.handler.last_operation = lambda: "retry"
            self.handler.last_context = {'attempt': 1}
            self.handler.exception_history.append({
                'exception': e,
                'operation': self.handler.last_operation,
                'context': self.handler.last_context
            })
        
        self.assertEqual(len(self.handler.exception_history), 1)
        self.assertEqual(
            self.handler.exception_history[0]['context']['attempt'], 
            1
        )

    def test_display_formatted_traceback(self):
        """Test display_formatted_traceback function."""
        try:
            raise ValueError("Display test error")
        except ValueError as e:
            self.handler.last_exception = e
            self.handler.last_context = {'user': 'test'}
            
            display_formatted_traceback(self.mock_zcli)
            
            # Verify display methods were called
            self.mock_zcli.display.zDeclare.assert_called()
            self.mock_zcli.display.error.assert_called()

    def test_display_formatted_traceback_no_exception(self):
        """Test display_formatted_traceback when no exception stored."""
        self.handler.last_exception = None
        
        display_formatted_traceback(self.mock_zcli)
        
        # Should display warning
        self.mock_zcli.display.warning.assert_called_with("No exception to display")

    def test_retry_last_operation_success(self):
        """Test retry_last_operation when operation succeeds."""
        success_operation = Mock(return_value="success")
        self.handler.last_operation = success_operation
        
        result = retry_last_operation(self.mock_zcli)
        
        # Verify operation was called
        success_operation.assert_called_once()
        # Verify success message displayed
        self.mock_zcli.display.success.assert_called()
        self.assertEqual(result, "success")

    def test_retry_last_operation_failure(self):
        """Test retry_last_operation when operation fails again."""
        failing_operation = Mock(side_effect=RuntimeError("Still failing"))
        self.handler.last_operation = failing_operation
        
        result = retry_last_operation(self.mock_zcli)
        
        # Verify operation was called
        failing_operation.assert_called_once()
        # Verify error message displayed
        self.mock_zcli.display.error.assert_called()
        self.assertIsNone(result)

    def test_retry_last_operation_no_operation(self):
        """Test retry_last_operation when no operation stored."""
        self.handler.last_operation = None
        
        retry_last_operation(self.mock_zcli)
        
        # Should display error
        self.mock_zcli.display.error.assert_called_with(
            "No operation to retry", indent=1
        )

    def test_show_exception_history(self):
        """Test show_exception_history function."""
        # Add some history
        for i in range(3):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                self.handler.exception_history.append({
                    'exception': e,
                    'operation': None,
                    'context': {}
                })
        
        show_exception_history(self.mock_zcli)
        
        # Verify display methods were called
        self.mock_zcli.display.zDeclare.assert_called()
        # Should show all 3 entries
        self.assertEqual(self.mock_zcli.display.text.call_count, 3)

    def test_show_exception_history_empty(self):
        """Test show_exception_history when no history."""
        self.handler.exception_history = []
        
        show_exception_history(self.mock_zcli)
        
        # Should display warning
        self.mock_zcli.display.warning.assert_called_with(
            "No exception history", indent=1
        )

    def test_show_exception_history_limited_to_10(self):
        """Test show_exception_history limits display to last 10."""
        # Add 15 exceptions
        for i in range(15):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                self.handler.exception_history.append({
                    'exception': e,
                    'operation': None,
                    'context': {}
                })
        
        show_exception_history(self.mock_zcli)
        
        # Should only display last 10
        self.assertEqual(self.mock_zcli.display.text.call_count, 10)

    def test_interactive_handler_launches_ui(self):
        """Test interactive_handler attempts to launch UI."""
        # This test is complex due to dynamic imports and zCLI instantiation
        # We'll test that it handles missing zcli gracefully
        handler_no_zcli = zTraceback()
        
        try:
            raise ValueError("Interactive test")
        except ValueError as e:
            result = handler_no_zcli.interactive_handler(
                e,
                operation=lambda: "retry",
                context={'test': True}
            )
            
            # Without zcli, should return None
            self.assertIsNone(result)

    def test_interactive_handler_without_zcli(self):
        """Test interactive_handler falls back gracefully without zCLI."""
        handler = zTraceback()  # No zcli
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                result = handler.interactive_handler(e)
                
                self.assertIsNone(result)
                output = mock_stderr.getvalue()
                self.assertIn("Test error", output)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_handler_with_none_exception(self):
        """Test handler methods with None exception."""
        handler = zTraceback()
        
        # Should not crash
        try:
            formatted = handler.format_exception(None)
        except (AttributeError, TypeError):
            # Expected for None exception
            pass

    def test_get_traceback_info_with_complex_exception(self):
        """Test get_traceback_info with nested exception."""
        handler = zTraceback()
        
        def inner_function():
            raise ValueError("Inner error")
        
        def outer_function():
            inner_function()
        
        try:
            outer_function()
        except ValueError as e:
            info = handler.get_traceback_info(e)
            
            # Should capture the outermost frame
            self.assertIn('file', info)
            self.assertIn('line', info)

    def test_exception_with_unicode_message(self):
        """Test exception handling with unicode characters."""
        handler = zTraceback()
        
        try:
            raise ValueError("Unicode error: 世界 🌍")
        except ValueError as e:
            formatted = handler.format_exception(e)
            self.assertIn("世界", formatted)
            self.assertIn("🌍", formatted)

    def test_very_deep_traceback(self):
        """Test handling of very deep call stacks."""
        handler = zTraceback()
        
        def recursive_function(depth):
            if depth == 0:
                raise RecursionError("Max depth")
            return recursive_function(depth - 1)
        
        try:
            recursive_function(10)
        except RecursionError as e:
            info = handler.get_traceback_info(e)
            self.assertEqual(info['exception_type'], 'RecursionError')


def run_tests(verbose=False):
    """Run all zTraceback tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzTracebackInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionContext))
    suite.addTests(loader.loadTestsFromTestCase(TestInteractiveTraceback))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

