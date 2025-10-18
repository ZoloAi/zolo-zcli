#!/usr/bin/env python3
# zTestSuite/zDisplay_New_Test.py

"""
Comprehensive test suite for new zDisplay architecture.
Tests primitives, events, and package composition.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from io import StringIO

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zDisplay import zDisplay
from zCLI.subsystems.zDisplay.zDisplay_modules.zPrimitives import zPrimitives
from zCLI.subsystems.zDisplay.zDisplay_modules.zEvents import zEvents
from zCLI.subsystems.zDisplay.zDisplay_modules.zEvents_packages import (
    BasicOutputs, BasicInputs, Signals, BasicData, AdvancedData, zSystem
)


class TestzDisplayInitialization(unittest.TestCase):
    """Test zDisplay initialization and setup."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()

    def test_zdisplay_initializes_successfully(self):
        """Test zDisplay initializes with valid zCLI instance."""
        display = zDisplay(self.mock_zcli)
        self.assertIsNotNone(display)
        self.assertEqual(display.mode, "Terminal")

    def test_zdisplay_requires_zcli_instance(self):
        """Test zDisplay raises error without zCLI instance."""
        with self.assertRaises(ValueError):
            zDisplay(None)

    def test_zdisplay_requires_session_attribute(self):
        """Test zDisplay raises error if zCLI missing session."""
        bad_zcli = Mock(spec=[])  # No session attribute
        with self.assertRaises(ValueError):
            zDisplay(bad_zcli)

    def test_zdisplay_initializes_primitives(self):
        """Test zDisplay initializes zPrimitives."""
        display = zDisplay(self.mock_zcli)
        self.assertIsInstance(display.zPrimitives, zPrimitives)

    def test_zdisplay_initializes_events(self):
        """Test zDisplay initializes zEvents."""
        display = zDisplay(self.mock_zcli)
        self.assertIsInstance(display.zEvents, zEvents)


class TestzPrimitives(unittest.TestCase):
    """Test zPrimitives package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_write_raw(self, mock_stdout):
        """Test write_raw primitive."""
        self.display.write_raw("test")
        output = mock_stdout.getvalue()
        self.assertIn("test", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_write_line(self, mock_stdout):
        """Test write_line primitive."""
        self.display.write_line("test line")
        output = mock_stdout.getvalue()
        self.assertIn("test line", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_write_block(self, mock_stdout):
        """Test write_block primitive."""
        self.display.write_block("block content")
        output = mock_stdout.getvalue()
        self.assertIn("block content", output)


class TestBasicOutputs(unittest.TestCase):
    """Test BasicOutputs package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_header_event(self, mock_stdout):
        """Test header event."""
        self.display.header("Test Header")
        output = mock_stdout.getvalue()
        self.assertIn("Test Header", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_text_event(self, mock_stdout):
        """Test text event without break."""
        self.display.text("Test text", break_after=False)
        output = mock_stdout.getvalue()
        self.assertIn("Test text", output)


class TestSignals(unittest.TestCase):
    """Test Signals package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_error_signal(self, mock_stdout):
        """Test error signal."""
        self.display.error("Error message")
        output = mock_stdout.getvalue()
        self.assertIn("Error message", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_signal(self, mock_stdout):
        """Test warning signal."""
        self.display.warning("Warning message")
        output = mock_stdout.getvalue()
        self.assertIn("Warning message", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_success_signal(self, mock_stdout):
        """Test success signal."""
        self.display.success("Success message")
        output = mock_stdout.getvalue()
        self.assertIn("Success message", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_info_signal(self, mock_stdout):
        """Test info signal."""
        self.display.info("Info message")
        output = mock_stdout.getvalue()
        self.assertIn("Info message", output)


class TestBasicData(unittest.TestCase):
    """Test BasicData package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_list_event(self, mock_stdout):
        """Test list event."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.display.list(items)
        output = mock_stdout.getvalue()
        for item in items:
            self.assertIn(item, output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_json_event(self, mock_stdout):
        """Test json_data event."""
        data = {"key": "value", "number": 42}
        self.display.json_data(data)
        output = mock_stdout.getvalue()
        self.assertIn("key", output)
        self.assertIn("value", output)


class TestAdvancedData(unittest.TestCase):
    """Test AdvancedData package with pagination."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ztable_basic(self, mock_stdout):
        """Test zTable basic display."""
        columns = ["ID", "Name"]
        rows = [{"ID": 1, "Name": "Alice"}, {"ID": 2, "Name": "Bob"}]
        self.display.zTable("Users", columns, rows)
        output = mock_stdout.getvalue()
        self.assertIn("Users", output)
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ztable_with_limit(self, mock_stdout):
        """Test zTable with positive limit."""
        columns = ["ID", "Name"]
        rows = [
            {"ID": i, "Name": f"User{i}"} for i in range(1, 11)
        ]
        self.display.zTable("Users", columns, rows, limit=3)
        output = mock_stdout.getvalue()
        self.assertIn("showing 1-3 of 10", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ztable_with_negative_limit(self, mock_stdout):
        """Test zTable with negative limit (from bottom)."""
        columns = ["ID", "Name"]
        rows = [
            {"ID": i, "Name": f"User{i}"} for i in range(1, 11)
        ]
        self.display.zTable("Users", columns, rows, limit=-3)
        output = mock_stdout.getvalue()
        self.assertIn("showing 8-10 of 10", output)


class TestzSystem(unittest.TestCase):
    """Test zSystem package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "debug": True,
            "zS_id": "test-123"
        }
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    @patch('sys.stdout', new_callable=StringIO)
    def test_zdeclare(self, mock_stdout):
        """Test zDeclare event."""
        self.display.zDeclare("System Message")
        output = mock_stdout.getvalue()
        self.assertIn("System Message", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_zcrumbs(self, mock_stdout):
        """Test zCrumbs event."""
        session_data = {
            "zCrumbs": {
                "main": ["home", "users"],
                "admin": ["settings"]
            }
        }
        self.display.zCrumbs(session_data)
        output = mock_stdout.getvalue()
        self.assertIn("zCrumbs", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_zmenu_display_only(self, mock_stdout):
        """Test zMenu display-only mode."""
        menu_items = [(1, "Option 1"), (2, "Option 2")]
        self.display.zMenu(menu_items, return_selection=False)
        output = mock_stdout.getvalue()
        self.assertIn("Option 1", output)
        self.assertIn("Option 2", output)


class TestPackageComposition(unittest.TestCase):
    """Test package composition and references."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    def test_all_packages_initialized(self):
        """Test all event packages are initialized."""
        self.assertIsInstance(self.display.zEvents.BasicOutputs, BasicOutputs)
        self.assertIsInstance(self.display.zEvents.BasicInputs, BasicInputs)
        self.assertIsInstance(self.display.zEvents.Signals, Signals)
        self.assertIsInstance(self.display.zEvents.BasicData, BasicData)
        self.assertIsInstance(self.display.zEvents.AdvancedData, AdvancedData)
        self.assertIsInstance(self.display.zEvents.zSystem, zSystem)

    def test_composition_references_set(self):
        """Test composition references are properly set."""
        # BasicInputs should reference BasicOutputs
        self.assertIs(
            self.display.zEvents.BasicInputs.BasicOutputs,
            self.display.zEvents.BasicOutputs
        )
        
        # Signals should reference BasicOutputs
        self.assertIs(
            self.display.zEvents.Signals.BasicOutputs,
            self.display.zEvents.BasicOutputs
        )
        
        # BasicData should reference BasicOutputs
        self.assertIs(
            self.display.zEvents.BasicData.BasicOutputs,
            self.display.zEvents.BasicOutputs
        )
        
        # AdvancedData should reference BasicOutputs and Signals
        self.assertIs(
            self.display.zEvents.AdvancedData.BasicOutputs,
            self.display.zEvents.BasicOutputs
        )
        self.assertIs(
            self.display.zEvents.AdvancedData.Signals,
            self.display.zEvents.Signals
        )
        
        # zSystem should reference BasicOutputs, Signals, and BasicInputs
        self.assertIs(
            self.display.zEvents.zSystem.BasicOutputs,
            self.display.zEvents.BasicOutputs
        )
        self.assertIs(
            self.display.zEvents.zSystem.Signals,
            self.display.zEvents.Signals
        )
        self.assertIs(
            self.display.zEvents.zSystem.BasicInputs,
            self.display.zEvents.BasicInputs
        )


class TestPagination(unittest.TestCase):
    """Test Pagination helper class."""

    def setUp(self):
        """Set up test fixtures."""
        from zCLI.subsystems.zDisplay.zDisplay_modules.zEvents_packages.AdvancedData import Pagination
        self.pagination = Pagination()
        self.test_data = list(range(1, 11))  # [1, 2, 3, ..., 10]

    def test_paginate_no_limit(self):
        """Test pagination with no limit returns all data."""
        result = self.pagination.paginate(self.test_data, limit=None)
        self.assertEqual(len(result["items"]), 10)
        self.assertEqual(result["showing_start"], 1)
        self.assertEqual(result["showing_end"], 10)
        self.assertFalse(result["has_more"])

    def test_paginate_positive_limit(self):
        """Test pagination with positive limit."""
        result = self.pagination.paginate(self.test_data, limit=3)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["showing_start"], 1)
        self.assertEqual(result["showing_end"], 3)
        self.assertTrue(result["has_more"])

    def test_paginate_negative_limit(self):
        """Test pagination with negative limit (from bottom)."""
        result = self.pagination.paginate(self.test_data, limit=-3)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["showing_start"], 8)
        self.assertEqual(result["showing_end"], 10)
        self.assertTrue(result["has_more"])

    def test_paginate_with_offset(self):
        """Test pagination with offset."""
        result = self.pagination.paginate(self.test_data, limit=3, offset=5)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["showing_start"], 6)
        self.assertEqual(result["showing_end"], 8)
        self.assertTrue(result["has_more"])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzDisplayInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzPrimitives))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicOutputs))
    suite.addTests(loader.loadTestsFromTestCase(TestSignals))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicData))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedData))
    suite.addTests(loader.loadTestsFromTestCase(TestzSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestPackageComposition))
    suite.addTests(loader.loadTestsFromTestCase(TestPagination))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

