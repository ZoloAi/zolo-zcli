#!/usr/bin/env python3
# zTestSuite/zComm_Test.py

"""
Test Suite for zComm Subsystem

Tests WebSocket server, service management, HTTP communication,
and integration with zAuth subsystem.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock, AsyncMock
import sys
import os
import json

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zComm import zComm
from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
from zCLI.subsystems.zComm.zComm_modules.service_manager import ServiceManager


class TestzCommInitialization(unittest.TestCase):
    """Test zComm subsystem initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create minimal zCLI mock
        self.mock_zcli = Mock()
        self.mock_zcli.session = {}
        self.mock_zcli.zspark_obj = {}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.logger.level = "INFO"
        self.mock_zcli.logger.handlers = []
        
        # Mock config
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
    
    def test_zcomm_initialization(self):
        """Test that zComm initializes correctly."""
        comm = zComm(self.mock_zcli)
        
        self.assertIsNotNone(comm)
        self.assertEqual(comm.zcli, self.mock_zcli)
        self.assertEqual(comm.session, self.mock_zcli.session)
        self.assertIsNotNone(comm.logger)
    
    def test_zcomm_requires_zcli(self):
        """Test that zComm requires a zCLI instance."""
        with self.assertRaises(ValueError):
            zComm(None)
    
    def test_zcomm_requires_session(self):
        """Test that zComm requires zCLI with session."""
        mock_zcli = Mock(spec=[])  # Mock with no attributes
        # No session attribute - should raise ValueError
        with self.assertRaises(ValueError):
            zComm(mock_zcli)
    
    def test_zcomm_service_manager(self):
        """Test that service manager is initialized."""
        comm = zComm(self.mock_zcli)
        
        self.assertIsNotNone(comm.services)
        self.assertIsInstance(comm.services, ServiceManager)
    
    def test_zcomm_websocket_not_auto_started_terminal(self):
        """Test that WebSocket is not auto-started in terminal mode."""
        comm = zComm(self.mock_zcli)
        
        # In terminal mode (no zVaFilename), websocket should be None initially
        self.assertIsNone(comm.websocket)


class TestHTTPCommunication(unittest.TestCase):
    """Test HTTP client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {}
        self.mock_zcli.zspark_obj = {}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.logger.level = "INFO"
        self.mock_zcli.logger.handlers = []
        
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        
        self.comm = zComm(self.mock_zcli)
    
    @patch('zCLI.subsystems.zComm.zComm_modules.http_client.requests.post')
    def test_http_post_success(self, mock_post):
        """Test successful HTTP POST request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        response = self.comm.http_post("http://test.com", {"key": "value"})
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once_with(
            "http://test.com",
            json={"key": "value"},
            timeout=10
        )
    
    @patch('zCLI.subsystems.zComm.zComm_modules.http_client.requests.post')
    def test_http_post_timeout(self, mock_post):
        """Test HTTP POST with custom timeout."""
        mock_response = Mock()
        mock_post.return_value = mock_response
        
        self.comm.http_post("http://test.com", {"key": "value"}, timeout=5)
        
        mock_post.assert_called_once_with(
            "http://test.com",
            json={"key": "value"},
            timeout=5
        )
    
    @patch('zCLI.subsystems.zComm.zComm_modules.http_client.requests.post')
    def test_http_post_failure(self, mock_post):
        """Test HTTP POST request failure."""
        mock_post.side_effect = Exception("Connection failed")
        
        response = self.comm.http_post("http://test.com", {"key": "value"})
        
        self.assertIsNone(response)
    
    @patch('zCLI.subsystems.zComm.zComm_modules.http_client.requests.post')
    def test_http_post_no_data(self, mock_post):
        """Test HTTP POST without data."""
        mock_response = Mock()
        mock_post.return_value = mock_response
        
        self.comm.http_post("http://test.com")
        
        mock_post.assert_called_once_with(
            "http://test.com",
            json=None,
            timeout=10
        )


class TestWebSocketManagement(unittest.TestCase):
    """Test WebSocket server management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {}
        self.mock_zcli.zspark_obj = {}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.logger.level = "INFO"
        self.mock_zcli.logger.handlers = []
        
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        
        self.comm = zComm(self.mock_zcli)
    
    def test_create_websocket(self):
        """Test WebSocket server creation."""
        websocket = self.comm.create_websocket()
        
        self.assertIsNotNone(websocket)
        self.assertIsInstance(websocket, zBifrost)
        self.assertEqual(self.comm.websocket, websocket)
    
    def test_create_websocket_custom_port(self):
        """Test WebSocket creation with custom port."""
        websocket = self.comm.create_websocket(port=8080)
        
        self.assertEqual(websocket.port, 8080)
    
    def test_create_websocket_custom_host(self):
        """Test WebSocket creation with custom host."""
        websocket = self.comm.create_websocket(host="0.0.0.0")
        
        self.assertEqual(websocket.host, "0.0.0.0")
    
    def test_create_websocket_uses_config(self):
        """Test that WebSocket uses zCLI configuration."""
        websocket = self.comm.create_websocket()
        
        # Should use config values
        self.assertEqual(websocket.host, "127.0.0.1")
        self.assertEqual(websocket.port, 56891)
    
    def test_create_websocket_fallback_defaults(self):
        """Test WebSocket fallback to defaults when config unavailable."""
        # Remove config
        self.mock_zcli.config = None
        comm = zComm(self.mock_zcli)
        
        websocket = comm.create_websocket()
        
        # Should use defaults
        self.assertEqual(websocket.host, "127.0.0.1")
        self.assertEqual(websocket.port, 56891)


class TestServiceManagement(unittest.TestCase):
    """Test service management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {}
        self.mock_zcli.zspark_obj = {}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.logger.level = "INFO"
        self.mock_zcli.logger.handlers = []
        
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        
        self.comm = zComm(self.mock_zcli)
    
    def test_start_service(self):
        """Test starting a service."""
        with patch.object(self.comm.services, 'start', return_value=True) as mock_start:
            result = self.comm.start_service("test_service")
            
            self.assertTrue(result)
            mock_start.assert_called_once_with("test_service")
    
    def test_stop_service(self):
        """Test stopping a service."""
        with patch.object(self.comm.services, 'stop', return_value=True) as mock_stop:
            result = self.comm.stop_service("test_service")
            
            self.assertTrue(result)
            mock_stop.assert_called_once_with("test_service")
    
    def test_restart_service(self):
        """Test restarting a service."""
        with patch.object(self.comm.services, 'restart', return_value=True) as mock_restart:
            result = self.comm.restart_service("test_service")
            
            self.assertTrue(result)
            mock_restart.assert_called_once_with("test_service")
    
    def test_service_status(self):
        """Test getting service status."""
        mock_status = {"test_service": {"running": True}}
        with patch.object(self.comm.services, 'status', return_value=mock_status) as mock_status_fn:
            result = self.comm.service_status("test_service")
            
            self.assertEqual(result, mock_status)
            mock_status_fn.assert_called_once_with("test_service")
    
    def test_service_status_all(self):
        """Test getting all services status."""
        mock_status = {
            "service1": {"running": True},
            "service2": {"running": False}
        }
        with patch.object(self.comm.services, 'status', return_value=mock_status) as mock_status_fn:
            result = self.comm.service_status()
            
            self.assertEqual(result, mock_status)
            mock_status_fn.assert_called_once_with(None)
    
    def test_get_service_connection_info(self):
        """Test getting service connection information."""
        mock_info = {"host": "localhost", "port": 5432}
        with patch.object(self.comm.services, 'get_connection_info', return_value=mock_info) as mock_get_info:
            result = self.comm.get_service_connection_info("postgres")
            
            self.assertEqual(result, mock_info)
            mock_get_info.assert_called_once_with("postgres")


class TestUtilityMethods(unittest.TestCase):
    """Test utility methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {}
        self.mock_zcli.zspark_obj = {}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.logger.level = "INFO"
        self.mock_zcli.logger.handlers = []
        
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        
        self.comm = zComm(self.mock_zcli)
    
    def test_check_port_available(self):
        """Test checking if a port is available."""
        # Check a high port that should be available
        result = self.comm.check_port(65432)
        
        # Should return True (available) or False (in use)
        self.assertIsInstance(result, bool)
    
    def test_check_port_in_use(self):
        """Test checking a port that's likely in use."""
        # Port 80 is often in use (HTTP)
        result = self.comm.check_port(80)
        
        # Result depends on system, just verify it returns a bool
        self.assertIsInstance(result, bool)


class TestzBifrostWebSocket(unittest.TestCase):
    """Test zBifrost WebSocket server class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.mock_zcli = Mock()
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        self.mock_zcli.config.websocket.require_auth = True
        self.mock_zcli.config.websocket.allowed_origins = []
    
    def test_bifrost_initialization(self):
        """Test zBifrost initialization."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        self.assertIsNotNone(bifrost)
        self.assertEqual(bifrost.logger, self.mock_logger)
        self.assertEqual(bifrost.zcli, self.mock_zcli)
    
    def test_bifrost_uses_config(self):
        """Test that zBifrost uses zCLI config."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        self.assertEqual(bifrost.host, "127.0.0.1")
        self.assertEqual(bifrost.port, 56891)
        self.assertTrue(bifrost.require_auth)
    
    def test_bifrost_custom_port(self):
        """Test zBifrost with custom port."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli, port=8080)
        
        self.assertEqual(bifrost.port, 8080)
    
    def test_bifrost_custom_host(self):
        """Test zBifrost with custom host."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli, host="0.0.0.0")
        
        self.assertEqual(bifrost.host, "0.0.0.0")
    
    def test_bifrost_fallback_defaults(self):
        """Test zBifrost fallback to defaults."""
        bifrost = zBifrost(self.mock_logger)
        
        # Should use defaults when no config
        self.assertEqual(bifrost.host, "127.0.0.1")
        self.assertEqual(bifrost.port, 56891)
    
    def test_bifrost_clients_tracking(self):
        """Test that client tracking is initialized."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        self.assertIsInstance(bifrost.clients, set)
        self.assertEqual(len(bifrost.clients), 0)
        self.assertIsInstance(bifrost.authenticated_clients, dict)
    
    def test_validate_origin_no_origins_configured(self):
        """Test origin validation when no origins configured."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        mock_ws = Mock()
        mock_ws.request_headers = {"Origin": "http://localhost:3000"}
        
        # Should allow localhost when no origins configured
        result = bifrost.validate_origin(mock_ws)
        self.assertTrue(result)
    
    def test_validate_origin_allowed(self):
        """Test origin validation with allowed origin."""
        self.mock_zcli.config.websocket.allowed_origins = ["http://localhost:3000"]
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        mock_ws = Mock()
        mock_ws.request_headers = {"Origin": "http://localhost:3000"}
        
        result = bifrost.validate_origin(mock_ws)
        self.assertTrue(result)
    
    def test_validate_origin_not_allowed(self):
        """Test origin validation with unauthorized origin."""
        self.mock_zcli.config.websocket.allowed_origins = ["http://allowed.com"]
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        mock_ws = Mock()
        mock_ws.request_headers = {"Origin": "http://evil.com"}
        
        result = bifrost.validate_origin(mock_ws)
        self.assertFalse(result)


class TestAsyncWebSocketOperations(unittest.IsolatedAsyncioTestCase):
    """Test async WebSocket operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.mock_zcli = Mock()
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        self.mock_zcli.config.websocket.require_auth = False  # Disable auth for testing
        self.mock_zcli.config.websocket.allowed_origins = []
    
    async def test_broadcast_to_clients(self):
        """Test broadcasting message to clients."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        # Mock clients
        mock_client1 = AsyncMock()
        mock_client1.open = True
        mock_client2 = AsyncMock()
        mock_client2.open = True
        
        bifrost.clients.add(mock_client1)
        bifrost.clients.add(mock_client2)
        
        # Broadcast message from client1
        await bifrost.broadcast("test message", sender=mock_client1)
        
        # client1 should not receive (it's the sender)
        mock_client1.send.assert_not_called()
        
        # client2 should receive
        mock_client2.send.assert_called_once_with("test message")
    
    async def test_broadcast_no_clients(self):
        """Test broadcasting with no clients."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        # Should not raise exception
        await bifrost.broadcast("test message")
    
    async def test_broadcast_skips_closed_clients(self):
        """Test broadcasting skips closed connections."""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        # Mock clients - one open, one closed
        mock_client1 = AsyncMock()
        mock_client1.open = True
        mock_client2 = AsyncMock()
        mock_client2.open = False
        
        bifrost.clients.add(mock_client1)
        bifrost.clients.add(mock_client2)
        
        await bifrost.broadcast("test message")
        
        # Only open client should receive
        mock_client1.send.assert_called_once_with("test message")
        mock_client2.send.assert_not_called()


def run_tests(verbose=True):
    """Run all zComm tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes in logical order
    suite.addTests(loader.loadTestsFromTestCase(TestzCommInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestHTTPCommunication))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostWebSocket))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncWebSocketOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zCLI Communication Test Suite")
    print("=" * 70)
    print()
    
    result = run_tests(verbose=True)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

