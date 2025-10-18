#!/usr/bin/env python3
# zTestSuite/zDisplay_Test.py

"""
Comprehensive test suite for zDisplay subsystem.
Tests both Terminal and GUI (WebSocket) adapters and event handlers.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import asyncio
import json

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zDisplay import zDisplay
from zCLI.subsystems.zDisplay.zDisplay_modules.output import OutputFactory
from zCLI.subsystems.zDisplay.zDisplay_modules.input import InputFactory
from zCLI.subsystems.zDisplay.zDisplay_modules.output.output_terminal import TerminalOutput
from zCLI.subsystems.zDisplay.zDisplay_modules.output.output_websocket import WebSocketOutput
from zCLI.subsystems.zDisplay.zDisplay_modules.input.input_terminal import TerminalInput
from zCLI.subsystems.zDisplay.zDisplay_modules.input.input_websocket import WebSocketInput


class TestOutputFactory(unittest.TestCase):
    """Test OutputFactory creates correct adapters based on mode."""

    def test_factory_creates_terminal_output(self):
        """Test factory creates TerminalOutput for Terminal mode."""
        session = {"zMode": "Terminal"}
        output = OutputFactory.create(session)
        self.assertIsInstance(output, TerminalOutput)

    def test_factory_creates_websocket_output(self):
        """Test factory creates WebSocketOutput for WebSocket mode."""
        session = {"zMode": "WebSocket"}
        output = OutputFactory.create(session)
        self.assertIsInstance(output, WebSocketOutput)

    def test_factory_creates_websocket_output_for_ui_mode(self):
        """Test factory creates WebSocketOutput for UI mode."""
        session = {"zMode": "UI"}
        output = OutputFactory.create(session)
        self.assertIsInstance(output, WebSocketOutput)

    def test_factory_defaults_to_terminal(self):
        """Test factory defaults to Terminal when no session."""
        output = OutputFactory.create(None)
        self.assertIsInstance(output, TerminalOutput)


class TestInputFactory(unittest.TestCase):
    """Test InputFactory creates correct adapters based on mode."""

    def test_factory_creates_terminal_input(self):
        """Test factory creates TerminalInput for Terminal mode."""
        session = {"zMode": "Terminal"}
        input_adapter = InputFactory.create(session)
        self.assertIsInstance(input_adapter, TerminalInput)

    def test_factory_creates_websocket_input(self):
        """Test factory creates WebSocketInput for WebSocket mode."""
        session = {"zMode": "WebSocket"}
        input_adapter = InputFactory.create(session)
        self.assertIsInstance(input_adapter, WebSocketInput)

    def test_factory_creates_websocket_input_for_ui_mode(self):
        """Test factory creates WebSocketInput for UI mode."""
        session = {"zMode": "UI"}
        input_adapter = InputFactory.create(session)
        self.assertIsInstance(input_adapter, WebSocketInput)

    def test_factory_defaults_to_terminal(self):
        """Test factory defaults to Terminal when no session."""
        input_adapter = InputFactory.create(None)
        self.assertIsInstance(input_adapter, TerminalInput)


class TestWebSocketOutput(unittest.TestCase):
    """Test WebSocketOutput adapter."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = {"zMode": "WebSocket"}
        self.logger = Mock()
        self.output = WebSocketOutput(self.session, self.logger)

    def test_websocket_output_initialization(self):
        """Test WebSocketOutput initializes correctly."""
        self.assertEqual(self.output.session, self.session)
        self.assertEqual(self.output.logger, self.logger)
        self.assertIsNone(self.output.websocket)
        self.assertIsNone(self.output.zcli)

    def test_set_zcli(self):
        """Test setting zCLI instance."""
        mock_zcli = Mock()
        self.output.set_zcli(mock_zcli)
        self.assertEqual(self.output.zcli, mock_zcli)

    def test_write_raw_sends_json(self):
        """Test write_raw sends JSON event."""
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mock_zcli = Mock()
        mock_zcli.comm = Mock()
        mock_zcli.comm.broadcast_websocket = Mock(return_value=loop.create_future())
        self.output.set_zcli(mock_zcli)

        self.output.write_raw("test content")
        # Verify logger was called
        self.logger.debug.assert_called()
        
        loop.close()

    def test_write_line_sends_json(self):
        """Test write_line sends JSON event."""
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mock_zcli = Mock()
        mock_zcli.comm = Mock()
        mock_zcli.comm.broadcast_websocket = Mock(return_value=loop.create_future())
        self.output.set_zcli(mock_zcli)

        self.output.write_line("test line\n")
        self.logger.debug.assert_called()
        
        loop.close()

    def test_send_event(self):
        """Test send_event method."""
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mock_zcli = Mock()
        mock_zcli.comm = Mock()
        mock_zcli.comm.broadcast_websocket = Mock(return_value=loop.create_future())
        self.output.set_zcli(mock_zcli)

        self.output.send_event("test_event", {"key": "value"})
        self.logger.debug.assert_called()
        
        loop.close()


class TestWebSocketInput(unittest.TestCase):
    """Test WebSocketInput adapter."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = {"zMode": "WebSocket"}
        self.logger = Mock()
        self.input_adapter = WebSocketInput(self.session, self.logger)

    def test_websocket_input_initialization(self):
        """Test WebSocketInput initializes correctly."""
        self.assertEqual(self.input_adapter.session, self.session)
        self.assertEqual(self.input_adapter.logger, self.logger)
        self.assertIsNone(self.input_adapter.zcli)
        self.assertEqual(len(self.input_adapter.pending_requests), 0)
        self.assertEqual(len(self.input_adapter.response_futures), 0)

    def test_set_zcli(self):
        """Test setting zCLI instance."""
        mock_zcli = Mock()
        self.input_adapter.set_zcli(mock_zcli)
        self.assertEqual(self.input_adapter.zcli, mock_zcli)

    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id = self.input_adapter._generate_request_id()
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)

    def test_read_string_returns_future(self):
        """Test read_string returns a future."""
        mock_zcli = Mock()
        mock_zcli.comm = Mock()
        mock_zcli.comm.broadcast_websocket = Mock(return_value=asyncio.Future())
        self.input_adapter.set_zcli(mock_zcli)

        # Create event loop for test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = self.input_adapter.read_string("Enter name:")
        self.assertIsInstance(result, asyncio.Future)

        loop.close()

    def test_handle_input_response(self):
        """Test handling input response from GUI."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create a future and store it
        future = loop.create_future()
        request_id = "test-request-123"
        self.input_adapter.response_futures[request_id] = future

        # Handle response
        self.input_adapter.handle_input_response(request_id, "test value")

        # Verify future was resolved
        self.assertTrue(future.done())
        self.assertEqual(future.result(), "test value")

        loop.close()


class TestzDisplayInitialization(unittest.TestCase):
    """Test zDisplay initialization."""

    def test_zdisplay_requires_zcli(self):
        """Test zDisplay requires zCLI instance."""
        with self.assertRaises(ValueError):
            zDisplay(None)

    def test_zdisplay_requires_session(self):
        """Test zDisplay requires session attribute."""
        mock_zcli = Mock(spec=[])  # No attributes
        with self.assertRaises(ValueError):
            zDisplay(mock_zcli)

    def test_zdisplay_terminal_mode_initialization(self):
        """Test zDisplay initializes in Terminal mode."""
        mock_zcli = Mock()
        mock_zcli.session = {"zMode": "Terminal", "zS_id": "test"}
        mock_zcli.logger = Mock()

        display = zDisplay(mock_zcli)

        self.assertEqual(display.mode, "Terminal")
        self.assertIsInstance(display.output, TerminalOutput)
        self.assertIsInstance(display.input, TerminalInput)

    def test_zdisplay_websocket_mode_initialization(self):
        """Test zDisplay initializes in WebSocket mode."""
        mock_zcli = Mock()
        mock_zcli.session = {"zMode": "WebSocket", "zS_id": "test"}
        mock_zcli.logger = Mock()
        mock_zcli.comm = Mock()

        display = zDisplay(mock_zcli)

        self.assertEqual(display.mode, "WebSocket")
        self.assertIsInstance(display.output, WebSocketOutput)
        self.assertIsInstance(display.input, WebSocketInput)


class TestzDisplayEventHandling(unittest.TestCase):
    """Test zDisplay event handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zS_id": "test"}
        self.mock_zcli.logger = Mock()
        self.display = zDisplay(self.mock_zcli)

    def test_handle_unknown_event(self):
        """Test handling unknown event."""
        result = self.display.handle({"event": "unknown_event"})
        self.assertIsNone(result)

    def test_handle_unimplemented_event(self):
        """Test handling unimplemented event."""
        result = self.display.handle({"event": "notification"})
        self.assertIsNone(result)

    @patch('builtins.print')
    def test_handle_text_event(self, mock_print):
        """Test handling text event."""
        result = self.display.handle({
            "event": "text",
            "content": "Hello, World!",
            "break": False
        })
        # Text event should execute without error
        self.assertIsNone(result)

    @patch('builtins.print')
    def test_handle_error_event(self, mock_print):
        """Test handling error event."""
        result = self.display.handle({
            "event": "error",
            "message": "Test error"
        })
        self.assertIsNone(result)


class TestGUIEventHandlers(unittest.TestCase):
    """Test GUI-specific event handlers."""

    def setUp(self):
        """Set up test fixtures for GUI mode."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "WebSocket", "zS_id": "test"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.comm = Mock()
        self.mock_zcli.comm.broadcast_websocket = Mock(return_value=asyncio.Future())
        self.display = zDisplay(self.mock_zcli)

    def test_handle_loading_event_gui(self):
        """Test handling loading event in GUI mode."""
        result = self.display.handle({
            "event": "loading",
            "message": "Processing..."
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "sent")
        self.assertEqual(result.get("event"), "loading")

    def test_handle_idle_event_gui(self):
        """Test handling idle event in GUI mode."""
        result = self.display.handle({
            "event": "idle"
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "sent")
        self.assertEqual(result.get("event"), "idle")

    def test_handle_await_event_gui(self):
        """Test handling await event in GUI mode."""
        result = self.display.handle({
            "event": "await",
            "message": "Waiting for response..."
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "sent")


class TestModeAwareRouting(unittest.TestCase):
    """Test mode-aware handler routing."""

    def test_terminal_mode_uses_terminal_handlers(self):
        """Test Terminal mode uses terminal handlers."""
        mock_zcli = Mock()
        mock_zcli.session = {"zMode": "Terminal", "zS_id": "test"}
        mock_zcli.logger = Mock()
        display = zDisplay(mock_zcli)

        # Get handler for break event
        handler = display._get_handler(Mock(), Mock())
        # In Terminal mode, should return first handler (terminal)
        self.assertIsNotNone(handler)

    def test_websocket_mode_uses_gui_handlers(self):
        """Test WebSocket mode uses GUI handlers."""
        mock_zcli = Mock()
        mock_zcli.session = {"zMode": "WebSocket", "zS_id": "test"}
        mock_zcli.logger = Mock()
        mock_zcli.comm = Mock()
        display = zDisplay(mock_zcli)

        # Get handler for break event with GUI handler
        terminal_handler = Mock()
        gui_handler = Mock()
        handler = display._get_handler(terminal_handler, gui_handler)
        # In WebSocket mode, should return GUI handler
        self.assertEqual(handler, gui_handler)


def run_tests(verbose=False):
    """Run all zDisplay tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestInputFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketOutput))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketInput))
    suite.addTests(loader.loadTestsFromTestCase(TestzDisplayInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzDisplayEventHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIEventHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestModeAwareRouting))

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

