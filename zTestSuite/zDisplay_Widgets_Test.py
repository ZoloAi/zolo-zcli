#!/usr/bin/env python3
# zTestSuite/zDisplay_Widgets_Test.py
"""Comprehensive tests for zDisplay TimeBased events (progress bars, spinners, swipers)."""

import unittest
import time
import io
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add zCLI to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.zCLI import zCLI


class TestProgressBar(unittest.TestCase):
    """Test progress_bar widget functionality."""

    def setUp(self):
        """Initialize zCLI instance for testing."""
        self.workspace = Path(__file__).parent
        self.z = zCLI({"zSpace": str(self.workspace)})

    def test_progress_bar_basic(self):
        """Test basic progress bar rendering."""
        # Capture output
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = self.z.display.progress_bar(50, 100, "Processing files")
            output = mock_stdout.getvalue()
        
        # Verify output contains expected elements
        self.assertIn("Processing files", result)
        self.assertIn("50%", result)
        self.assertIn("█", result)  # Filled bar
        self.assertIn("░", result)  # Empty bar

    def test_progress_bar_zero_percent(self):
        """Test progress bar at 0%."""
        result = self.z.display.progress_bar(0, 100, "Starting")
        self.assertIn("0%", result)
        self.assertIn("░" * 50, result)  # All empty

    def test_progress_bar_hundred_percent(self):
        """Test progress bar at 100%."""
        with patch('sys.stdout', new_callable=io.StringIO):
            result = self.z.display.progress_bar(100, 100, "Complete")
        
        self.assertIn("100%", result)
        self.assertIn("█" * 50, result)  # All filled

    def test_progress_bar_custom_width(self):
        """Test progress bar with custom width."""
        result = self.z.display.progress_bar(25, 100, "Processing", width=20)
        self.assertIn("Processing", result)
        # Width=20, 25% = 5 filled chars
        self.assertIn("█" * 5, result)

    def test_progress_bar_without_percentage(self):
        """Test progress bar without percentage display."""
        result = self.z.display.progress_bar(50, 100, "Processing", show_percentage=False)
        self.assertNotIn("%", result)
        self.assertIn("Processing", result)

    def test_progress_bar_with_eta(self):
        """Test progress bar with ETA calculation."""
        start = time.time()
        time.sleep(0.1)  # Simulate some work
        result = self.z.display.progress_bar(
            50, 100, "Processing", 
            show_eta=True, 
            start_time=start
        )
        self.assertIn("ETA:", result)

    def test_progress_bar_with_color(self):
        """Test progress bar with custom color."""
        result = self.z.display.progress_bar(60, 100, "Processing", color="GREEN")
        self.assertIn("Processing", result)
        # Color should be applied (difficult to test exact ANSI codes)

    def test_progress_bar_indeterminate(self):
        """Test indeterminate progress (total=None)."""
        result = self.z.display.progress_bar(None, None, "Loading")
        self.assertIn("Loading", result)
        # Should show spinner character instead of bar
        self.assertNotIn("█", result)
        self.assertNotIn("%", result)

    def test_progress_bar_via_handle(self):
        """Test progress bar via handle() method (zBifrost compatibility)."""
        with patch('sys.stdout', new_callable=io.StringIO):
            self.z.display.handle({
                "event": "progress_bar",
                "current": 75,
                "total": 100,
                "label": "Uploading"
            })
        # Should not raise exception

    def test_progress_bar_edge_case_negative(self):
        """Test progress bar with negative current (should clamp to 0%)."""
        result = self.z.display.progress_bar(-10, 100, "Test")
        self.assertIn("0%", result)

    def test_progress_bar_edge_case_over_total(self):
        """Test progress bar with current > total (should clamp to 100%)."""
        result = self.z.display.progress_bar(150, 100, "Test")
        self.assertIn("100%", result)


class TestSpinner(unittest.TestCase):
    """Test spinner widget functionality."""

    def setUp(self):
        """Initialize zCLI instance for testing."""
        self.workspace = Path(__file__).parent
        self.z = zCLI({"zSpace": str(self.workspace)})

    def test_spinner_context_manager(self):
        """Test spinner as context manager."""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with self.z.display.spinner("Loading data"):
                time.sleep(0.3)  # Let spinner animate
            output = mock_stdout.getvalue()
        
        # Should contain loading text and completion checkmark
        self.assertIn("Loading data", output)
        self.assertIn("✓", output)

    def test_spinner_default_style(self):
        """Test spinner with default (dots) style."""
        with patch('sys.stdout', new_callable=io.StringIO):
            with self.z.display.spinner("Processing"):
                time.sleep(0.2)
        # Should not raise exception

    def test_spinner_line_style(self):
        """Test spinner with line style."""
        with patch('sys.stdout', new_callable=io.StringIO):
            with self.z.display.spinner("Processing", style="line"):
                time.sleep(0.2)
        # Should not raise exception

    def test_spinner_arc_style(self):
        """Test spinner with arc style."""
        with patch('sys.stdout', new_callable=io.StringIO):
            with self.z.display.spinner("Processing", style="arc"):
                time.sleep(0.2)
        # Should not raise exception

    def test_spinner_with_exception(self):
        """Test spinner cleanup when exception occurs."""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            try:
                with self.z.display.spinner("Failing operation"):
                    time.sleep(0.1)
                    raise ValueError("Test error")
            except ValueError:
                pass
            output = mock_stdout.getvalue()
        
        # Spinner should still show completion mark despite exception
        self.assertIn("Failing operation", output)


class TestProgressIterator(unittest.TestCase):
    """Test progress_iterator wrapper functionality."""

    def setUp(self):
        """Initialize zCLI instance for testing."""
        self.workspace = Path(__file__).parent
        self.z = zCLI({"zSpace": str(self.workspace)})

    def test_progress_iterator_basic(self):
        """Test progress iterator with simple list."""
        items = list(range(10))
        processed = []
        
        with patch('sys.stdout', new_callable=io.StringIO):
            for item in self.z.display.progress_iterator(items, "Processing items"):
                processed.append(item)
        
        # All items should be processed
        self.assertEqual(processed, items)

    def test_progress_iterator_with_eta(self):
        """Test progress iterator with ETA display."""
        items = list(range(5))
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            for item in self.z.display.progress_iterator(items, "Processing", show_eta=True):
                time.sleep(0.05)
            output = mock_stdout.getvalue()
        
        # Should show ETA at some point
        self.assertIn("Processing", output)

    def test_progress_iterator_empty_list(self):
        """Test progress iterator with empty list."""
        items = []
        processed = []
        
        with patch('sys.stdout', new_callable=io.StringIO):
            for item in self.z.display.progress_iterator(items, "Processing"):
                processed.append(item)
        
        self.assertEqual(processed, [])


class TestIndeterminateProgress(unittest.TestCase):
    """Test indeterminate progress indicator."""

    def setUp(self):
        """Initialize zCLI instance for testing."""
        self.workspace = Path(__file__).parent
        self.z = zCLI({"zSpace": str(self.workspace)})

    def test_indeterminate_progress_basic(self):
        """Test indeterminate progress basic functionality."""
        with patch('sys.stdout', new_callable=io.StringIO):
            update = self.z.display.indeterminate_progress("Loading")
            for _ in range(5):
                update()
                time.sleep(0.05)
        # Should not raise exception

    def test_indeterminate_progress_custom_label(self):
        """Test indeterminate progress with custom label."""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            update = self.z.display.indeterminate_progress("Connecting to server")
            update()
            output = mock_stdout.getvalue()
        
        self.assertIn("Connecting to server", output)


class TestWidgetsIntegration(unittest.TestCase):
    """Integration tests for TimeBased events package."""

    def setUp(self):
        """Initialize zCLI instance for testing."""
        self.workspace = Path(__file__).parent
        self.z = zCLI({"zSpace": str(self.workspace)})

    def test_widgets_module_initialized(self):
        """Test that TimeBased module is properly initialized."""
        self.assertIsNotNone(self.z.display.zEvents.TimeBased)

    def test_all_widget_events_registered(self):
        """Test that all widget events are registered in event map."""
        event_map = self.z.display._event_map
        self.assertIn("progress_bar", event_map)
        self.assertIn("spinner", event_map)
        self.assertIn("progress_iterator", event_map)
        self.assertIn("indeterminate_progress", event_map)

    def test_convenience_methods_exist(self):
        """Test that convenience methods are available."""
        self.assertTrue(hasattr(self.z.display, 'progress_bar'))
        self.assertTrue(hasattr(self.z.display, 'spinner'))
        self.assertTrue(hasattr(self.z.display, 'progress_iterator'))
        self.assertTrue(hasattr(self.z.display, 'indeterminate_progress'))

    def test_eta_time_formatting(self):
        """Test ETA time formatting helper."""
        timebased = self.z.display.zEvents.TimeBased
        
        # Test seconds
        self.assertEqual(timebased._format_time(30), "30s")
        
        # Test minutes
        self.assertEqual(timebased._format_time(90), "1m 30s")
        
        # Test hours
        self.assertEqual(timebased._format_time(3661), "1h 1m")

    def test_spinner_styles_available(self):
        """Test that all spinner styles are available."""
        timebased = self.z.display.zEvents.TimeBased
        expected_styles = ["dots", "line", "arc", "arrow", "bouncingBall", "simple"]
        
        for style in expected_styles:
            self.assertIn(style, timebased._spinner_styles)
            self.assertIsInstance(timebased._spinner_styles[style], list)
            self.assertGreater(len(timebased._spinner_styles[style]), 0)


def run_tests(verbose=False):
    """Run all widget tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProgressBar))
    suite.addTests(loader.loadTestsFromTestCase(TestSpinner))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressIterator))
    suite.addTests(loader.loadTestsFromTestCase(TestIndeterminateProgress))
    suite.addTests(loader.loadTestsFromTestCase(TestWidgetsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

