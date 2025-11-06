# zTestSuite/zShutdown_Test.py

"""
Comprehensive test suite for graceful shutdown functionality (Week 2.2)

Tests cover:
- Signal handler registration
- z.shutdown() method
- WebSocket graceful shutdown
- HTTP server graceful shutdown
- Database connection cleanup
- Logger flushing
- Error handling during shutdown
- Idempotent shutdown (multiple calls)
"""

import unittest
import signal
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI


def requires_network(func):
    """
    Decorator to skip tests that require network access.
    
    Used for tests that need to bind to ports or make HTTP requests.
    Gracefully skips ONLY in true CI/sandbox environments (not local dev).
    
    Detection logic:
    1. Check for CI environment variables (CI=true, GITHUB_ACTIONS, etc.)
    2. If not CI, let test run (fail naturally if network unavailable)
    3. If CI, do socket pre-check and skip if fails
    """
    import os
    
    # Detect if we're in a CI environment
    is_ci = any([
        os.getenv('CI') == 'true',
        os.getenv('GITHUB_ACTIONS') == 'true',
        os.getenv('GITLAB_CI') == 'true',
        os.getenv('CIRCLECI') == 'true',
        os.getenv('TRAVIS') == 'true',
    ])
    
    # If not in CI, always run the test
    if not is_ci:
        return func
    
    # In CI, check if network operations are available
    import socket
    import functools
    
    def can_bind_socket():
        """Check if we can bind to a socket (network operations allowed)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', 0))  # Bind to any available port
                return True
        except (OSError, PermissionError):
            return False
    
    # If async test
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not can_bind_socket():
                args[0].skipTest("Network operations not available in CI sandbox")
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        # Sync test
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not can_bind_socket():
                args[0].skipTest("Network operations not available in CI sandbox")
            return func(*args, **kwargs)
        return wrapper


# ═══════════════════════════════════════════════════════════
# Test: Signal Handler Registration
# ═══════════════════════════════════════════════════════════

class TestSignalHandlerRegistration(unittest.TestCase):
    """Test signal handler registration in zCLI"""
    
    def test_signal_handlers_registered_on_init(self):
        """Signal handlers should be registered during zCLI initialization"""
        # Create temporary workspace
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Check SIGINT handler is registered
            sigint_handler = signal.getsignal(signal.SIGINT)
            self.assertIsNotNone(sigint_handler)
            self.assertNotEqual(sigint_handler, signal.SIG_DFL)
            self.assertNotEqual(sigint_handler, signal.SIG_IGN)
            
            # Check SIGTERM handler is registered
            sigterm_handler = signal.getsignal(signal.SIGTERM)
            self.assertIsNotNone(sigterm_handler)
            self.assertNotEqual(sigterm_handler, signal.SIG_DFL)
            self.assertNotEqual(sigterm_handler, signal.SIG_IGN)
    
    def test_signal_handler_prevents_double_shutdown(self):
        """Signal handler should prevent multiple concurrent shutdowns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Set shutdown in progress
            z._shutdown_in_progress = True
            
            # Get the signal handler
            sigint_handler = signal.getsignal(signal.SIGINT)
            
            # Mock logger to check warning
            z.logger = Mock()
            
            # Trigger signal handler (should exit early due to shutdown in progress)
            with patch('sys.exit'):
                sigint_handler(signal.SIGINT, None)
            
            # Verify warning was logged
            z.logger.warning.assert_called()


# ═══════════════════════════════════════════════════════════
# Test: Basic Shutdown Functionality
# ═══════════════════════════════════════════════════════════

class TestBasicShutdown(unittest.TestCase):
    """Test basic z.shutdown() functionality"""
    
    def test_shutdown_returns_status_dict(self):
        """shutdown() should return cleanup status dictionary"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            status = z.shutdown()
            
            # Verify status dict structure
            self.assertIsInstance(status, dict)
            self.assertIn('websocket', status)
            self.assertIn('http_server', status)
            self.assertIn('database', status)
            self.assertIn('logger', status)
            
            # All should be True (successful cleanup)
            for component, success in status.items():
                self.assertTrue(success, f"{component} cleanup failed")
    
    def test_shutdown_is_idempotent(self):
        """Multiple shutdown() calls should be safe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # First shutdown
            status1 = z.shutdown()
            self.assertTrue(z._shutdown_in_progress)
            
            # Second shutdown should return immediately
            z.logger = Mock()
            status2 = z.shutdown()
            
            # Warning should be logged
            z.logger.warning.assert_called()
            self.assertIsNone(status2)
    
    def test_shutdown_sets_flags_correctly(self):
        """shutdown() should set internal flags correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Initial state
            self.assertFalse(z._shutdown_requested)
            self.assertFalse(z._shutdown_in_progress)
            
            # After shutdown
            z.shutdown()
            self.assertTrue(z._shutdown_in_progress)


# ═══════════════════════════════════════════════════════════
# Test: WebSocket Shutdown
# ═══════════════════════════════════════════════════════════

class TestWebSocketShutdown(unittest.IsolatedAsyncioTestCase):
    """Test WebSocket graceful shutdown"""
    
    async def test_websocket_shutdown_closes_connections(self):
        """WebSocket shutdown should close all active connections"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create zBifrost instance
            from zCLI.subsystems.zComm.zComm_modules.bifrost import zBifrost
            
            z = zCLI({"zSpace": tmpdir})
            bifrost = zBifrost(z.logger, zcli=z, port=56899)
            
            # Mock client connections
            mock_client1 = MagicMock()
            async def mock_send1(x):
                pass
            async def mock_close1():
                pass
            mock_client1.send = mock_send1
            mock_client1.close = mock_close1
            
            mock_client2 = MagicMock()
            async def mock_send2(x):
                pass
            async def mock_close2():
                pass
            mock_client2.send = mock_send2
            mock_client2.close = mock_close2
            
            bifrost.clients.add(mock_client1)
            bifrost.clients.add(mock_client2)
            bifrost._running = True
            
            # Shutdown
            await bifrost.shutdown()
            
            # Verify clients cleared
            self.assertEqual(len(bifrost.clients), 0)
            self.assertEqual(len(bifrost.auth.authenticated_clients), 0)
            self.assertFalse(bifrost._running)
    
    async def test_websocket_shutdown_sends_notification(self):
        """WebSocket shutdown should send shutdown notification to clients"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from zCLI.subsystems.zComm.zComm_modules.bifrost import zBifrost
            
            z = zCLI({"zSpace": tmpdir})
            bifrost = zBifrost(z.logger, zcli=z, port=56899)
            
            # Mock client
            mock_client = MagicMock()
            sent_messages = []
            
            async def mock_send(msg):
                sent_messages.append(msg)
            
            async def mock_close():
                pass
            
            mock_client.send = mock_send
            mock_client.close = mock_close
            
            bifrost.clients.add(mock_client)
            bifrost._running = True
            
            # Shutdown
            await bifrost.shutdown()
            
            # Verify shutdown notification sent
            self.assertEqual(len(sent_messages), 1)
            import json
            notification = json.loads(sent_messages[0])
            self.assertEqual(notification['event'], 'server_shutdown')
    
    async def test_websocket_shutdown_handles_errors_gracefully(self):
        """WebSocket shutdown should handle client close errors gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from zCLI.subsystems.zComm.zComm_modules.bifrost import zBifrost
            
            z = zCLI({"zSpace": tmpdir})
            bifrost = zBifrost(z.logger, zcli=z, port=56899)
            
            # Mock client that raises error on close
            mock_client = MagicMock()
            
            async def mock_send_error(msg):
                raise Exception("Connection already closed")
            
            async def mock_close():
                pass
            
            mock_client.send = mock_send_error
            mock_client.close = mock_close
            
            bifrost.clients.add(mock_client)
            bifrost._running = True
            
            # Shutdown should not raise exception
            await bifrost.shutdown()
            
            # Should still clear clients
            self.assertEqual(len(bifrost.clients), 0)
            self.assertFalse(bifrost._running)
    
    async def test_websocket_shutdown_timeout_handling(self):
        """WebSocket shutdown should handle timeout gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from zCLI.subsystems.zComm.zComm_modules.bifrost import zBifrost
            
            z = zCLI({"zSpace": tmpdir})
            bifrost = zBifrost(z.logger, zcli=z, port=56899)
            
            # Mock server that never closes
            mock_server = MagicMock()
            
            async def never_closes():
                await asyncio.sleep(10)  # Longer than timeout
            
            mock_server.close = MagicMock()
            mock_server.wait_closed = never_closes
            
            bifrost.server = mock_server
            bifrost._running = True
            
            # Shutdown with short timeout
            await bifrost.shutdown(timeout=0.1)
            
            # Should still mark as not running
            self.assertFalse(bifrost._running)
            self.assertIsNone(bifrost.server)


# ═══════════════════════════════════════════════════════════
# Test: HTTP Server Shutdown
# ═══════════════════════════════════════════════════════════

class TestHTTPServerShutdown(unittest.TestCase):
    """Test HTTP server graceful shutdown"""
    
    @requires_network
    def test_http_server_shutdown_via_zcli(self):
        """z.shutdown() should stop HTTP server"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create zCLI with HTTP server enabled
            z = zCLI({
                "zSpace": tmpdir,
                "http_server": {
                    "enabled": True,
                    "port": 8899,
                    "host": "127.0.0.1",
                    "serve_path": tmpdir
                }
            })
            
            # Verify server is running
            self.assertIsNotNone(z.server)
            self.assertTrue(z.server.is_running())
            
            # Shutdown
            status = z.shutdown()
            
            # Verify server stopped
            self.assertFalse(z.server.is_running())
            self.assertTrue(status['http_server'])
    
    def test_http_server_shutdown_when_not_running(self):
        """Shutdown should handle non-running HTTP server gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # No HTTP server initialized
            self.assertIsNone(z.server)
            
            # Shutdown should succeed
            status = z.shutdown()
            self.assertTrue(status['http_server'])


# ═══════════════════════════════════════════════════════════
# Test: Database Connection Cleanup
# ═══════════════════════════════════════════════════════════

class TestDatabaseCleanup(unittest.TestCase):
    """Test database connection cleanup during shutdown"""
    
    def test_database_cleanup_when_active(self):
        """Shutdown should close active database connections"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Mock active database adapter
            z.data.adapter = Mock()
            z.data.adapter.disconnect = Mock()
            
            # Shutdown
            status = z.shutdown()
            
            # Verify disconnect was called
            z.data.adapter.disconnect.assert_called_once()
            self.assertTrue(status['database'])
    
    def test_database_cleanup_when_no_adapter(self):
        """Shutdown should handle missing database adapter gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # No adapter initialized
            self.assertIsNone(z.data.adapter)
            
            # Shutdown should succeed
            status = z.shutdown()
            self.assertTrue(status['database'])


# ═══════════════════════════════════════════════════════════
# Test: Logger Flushing
# ═══════════════════════════════════════════════════════════

class TestLoggerFlushing(unittest.TestCase):
    """Test logger flushing during shutdown"""
    
    def test_logger_handlers_flushed(self):
        """Shutdown should flush all logger handlers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Save original handlers
            original_handlers = z.logger.handlers.copy()
            
            # Add mock handlers with required attributes
            mock_handler1 = Mock()
            mock_handler1.level = 0
            mock_handler1.flush = Mock()
            mock_handler2 = Mock()
            mock_handler2.level = 0
            mock_handler2.flush = Mock()
            z.logger.handlers.append(mock_handler1)
            z.logger.handlers.append(mock_handler2)
            
            # Shutdown
            status = z.shutdown()
            
            # Verify all handlers flushed
            mock_handler1.flush.assert_called_once()
            mock_handler2.flush.assert_called_once()
            self.assertTrue(status['logger'])
            
            # Restore original handlers
            z.logger.handlers = original_handlers


# ═══════════════════════════════════════════════════════════
# Test: Error Handling During Shutdown
# ═══════════════════════════════════════════════════════════

class TestShutdownErrorHandling(unittest.TestCase):
    """Test error handling during shutdown"""
    
    @requires_network
    def test_websocket_error_does_not_prevent_other_cleanup(self):
        """WebSocket shutdown error should not prevent HTTP server cleanup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({
                "zSpace": tmpdir,
                "http_server": {
                    "enabled": True,
                    "port": 8898,
                    "host": "127.0.0.1",
                    "serve_path": tmpdir
                }
            })
            
            # Mock WebSocket with error by patching the _bifrost_mgr
            mock_websocket = Mock()
            mock_websocket._running = True
            
            async def mock_shutdown_error():
                raise Exception("WebSocket error")
            
            mock_websocket.shutdown = mock_shutdown_error
            
            # Patch the underlying websocket via _bifrost_mgr
            original_ws = z.comm._bifrost_mgr.websocket
            z.comm._bifrost_mgr.websocket = mock_websocket
            
            try:
                # Shutdown should continue despite WebSocket error
                status = z.shutdown()
                
                # HTTP server should still be stopped
                if z.server:
                    self.assertFalse(z.server.is_running())
            finally:
                # Restore original
                z.comm._bifrost_mgr.websocket = original_ws
    
    def test_http_server_error_does_not_prevent_other_cleanup(self):
        """HTTP server error should not prevent logger cleanup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Mock HTTP server with error
            z.server = Mock()
            z.server._running = True
            z.server.stop = Mock(side_effect=Exception("Server error"))
            
            # Save original handlers and add mock handler
            original_handlers = z.logger.handlers.copy()
            mock_handler = Mock()
            mock_handler.level = 0  # Add required attribute for logging
            mock_handler.flush = Mock()
            z.logger.handlers.append(mock_handler)
            
            # Shutdown should continue despite HTTP server error
            status = z.shutdown()
            
            # Logger should still be flushed
            mock_handler.flush.assert_called_once()
            self.assertTrue(status['logger'])
            
            # Restore original handlers
            z.logger.handlers = original_handlers


# ═══════════════════════════════════════════════════════════
# Test Suite Runner
# ═══════════════════════════════════════════════════════════

def run_tests(verbose=True):
    """Run all shutdown tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSignalHandlerRegistration))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicShutdown))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketShutdown))
    suite.addTests(loader.loadTestsFromTestCase(TestHTTPServerShutdown))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseCleanup))
    suite.addTests(loader.loadTestsFromTestCase(TestLoggerFlushing))
    suite.addTests(loader.loadTestsFromTestCase(TestShutdownErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

