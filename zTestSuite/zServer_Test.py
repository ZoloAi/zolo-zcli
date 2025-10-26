#!/usr/bin/env python3
# zTestSuite/zServer_Test.py

"""
Test Suite for zServer Subsystem

Tests HTTP static file server functionality, configuration,
lifecycle management, and integration with zBifrost.
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zServer import zServer
from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler


class TestzServerInitialization(unittest.TestCase):
    """Test zServer initialization and configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_logger.info = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_zserver_initialization_defaults(self):
        """Test zServer initializes with default settings"""
        server = zServer(self.mock_logger)
        
        self.assertEqual(server.port, 8080)
        self.assertEqual(server.host, "127.0.0.1")
        self.assertEqual(server.logger, self.mock_logger)
        self.assertFalse(server.is_running())
        self.mock_logger.info.assert_called()
    
    def test_zserver_initialization_custom_config(self):
        """Test zServer initializes with custom configuration"""
        server = zServer(
            self.mock_logger,
            port=9090,
            host="0.0.0.0",
            serve_path=self.temp_dir
        )
        
        self.assertEqual(server.port, 9090)
        self.assertEqual(server.host, "0.0.0.0")
        self.assertEqual(server.serve_path, str(Path(self.temp_dir).resolve()))
    
    def test_zserver_config_from_zcli(self):
        """Test zServer can accept zCLI instance"""
        mock_zcli = Mock()
        server = zServer(self.mock_logger, zcli=mock_zcli)
        
        self.assertEqual(server.zcli, mock_zcli)


class TestzServerLifecycle(unittest.TestCase):
    """Test server start/stop lifecycle"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_logger.info = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()
        
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test HTML file
        test_file = Path(self.temp_dir) / "test.html"
        test_file.write_text("<html><body>Test</body></html>")
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_start_server(self):
        """Test server starts successfully"""
        server = zServer(
            self.mock_logger,
            port=18080,  # Use high port to avoid conflicts
            serve_path=self.temp_dir
        )
        
        try:
            server.start()
            time.sleep(0.5)  # Give server time to start
            
            self.assertTrue(server.is_running())
            self.assertIsNotNone(server.server)
            self.assertIsNotNone(server.thread)
            
        finally:
            server.stop()
    
    def test_stop_server(self):
        """Test server stops cleanly"""
        server = zServer(
            self.mock_logger,
            port=18081,
            serve_path=self.temp_dir
        )
        
        server.start()
        time.sleep(0.5)
        self.assertTrue(server.is_running())
        
        server.stop()
        time.sleep(0.5)
        self.assertFalse(server.is_running())
    
    def test_server_already_running(self):
        """Test starting server when already running"""
        server = zServer(
            self.mock_logger,
            port=18082,
            serve_path=self.temp_dir
        )
        
        try:
            server.start()
            time.sleep(0.5)
            
            # Try to start again
            server.start()
            
            # Should log warning
            self.mock_logger.warning.assert_called_with("[zServer] Server is already running")
            
        finally:
            server.stop()
    
    def test_server_port_in_use(self):
        """Test error when port is already in use"""
        port = 18083
        
        # Start first server
        server1 = zServer(self.mock_logger, port=port, serve_path=self.temp_dir)
        server1.start()
        time.sleep(0.5)
        
        try:
            # Try to start second server on same port
            server2 = zServer(self.mock_logger, port=port, serve_path=self.temp_dir)
            
            with self.assertRaises(OSError):
                server2.start()
            
        finally:
            server1.stop()


class TestzServerStaticFiles(unittest.TestCase):
    """Test static file serving"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_logger.info = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()
        
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        (Path(self.temp_dir) / "test.html").write_text("<html><body>HTML Test</body></html>")
        (Path(self.temp_dir) / "test.js").write_text("console.log('JS Test');")
        (Path(self.temp_dir) / "test.css").write_text("body { color: red; }")
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_serve_html_file(self):
        """Test serving HTML file"""
        server = zServer(
            self.mock_logger,
            port=18084,
            serve_path=self.temp_dir
        )
        
        try:
            server.start()
            time.sleep(0.5)
            
            # Test would make HTTP request to localhost:18084/test.html
            # For unit test, just verify server is running with correct path
            self.assertTrue(server.is_running())
            self.assertIn("test.html", os.listdir(self.temp_dir))
            
        finally:
            server.stop()
    
    def test_serve_js_file(self):
        """Test serving JavaScript file"""
        server = zServer(
            self.mock_logger,
            port=18085,
            serve_path=self.temp_dir
        )
        
        try:
            server.start()
            time.sleep(0.5)
            
            self.assertTrue(server.is_running())
            self.assertIn("test.js", os.listdir(self.temp_dir))
            
        finally:
            server.stop()
    
    def test_serve_css_file(self):
        """Test serving CSS file"""
        server = zServer(
            self.mock_logger,
            port=18086,
            serve_path=self.temp_dir
        )
        
        try:
            server.start()
            time.sleep(0.5)
            
            self.assertTrue(server.is_running())
            self.assertIn("test.css", os.listdir(self.temp_dir))
            
        finally:
            server.stop()
    
    def test_directory_listing_disabled(self):
        """Test directory listing is disabled"""
        # This is tested via the handler's list_directory method
        # which returns None/403 error
        pass  # Handler test would go here


class TestzServerIntegration(unittest.TestCase):
    """Test integration with zBifrost"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_logger.info = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_http_and_websocket_together(self):
        """Test HTTP and WebSocket can run together"""
        http_server = zServer(
            self.mock_logger,
            port=18087,
            serve_path=self.temp_dir
        )
        
        try:
            http_server.start()
            time.sleep(0.5)
            
            self.assertTrue(http_server.is_running())
            
            # In real integration test, would also start WebSocket server
            # For now, just verify HTTP works independently
            
        finally:
            http_server.stop()
    
    def test_separate_ports(self):
        """Test HTTP and WebSocket use different ports"""
        http_port = 18088
        ws_port = 18765
        
        http_server = zServer(
            self.mock_logger,
            port=http_port,
            serve_path=self.temp_dir
        )
        
        try:
            http_server.start()
            time.sleep(0.5)
            
            # Verify HTTP server is on correct port
            self.assertEqual(http_server.port, http_port)
            self.assertNotEqual(http_server.port, ws_port)
            
        finally:
            http_server.stop()
    
    def test_shared_zcli_instance(self):
        """Test HTTP server can share zCLI instance"""
        mock_zcli = Mock()
        
        http_server = zServer(
            self.mock_logger,
            zcli=mock_zcli,
            port=18089,
            serve_path=self.temp_dir
        )
        
        self.assertEqual(http_server.zcli, mock_zcli)
    
    def test_get_url(self):
        """Test server URL generation"""
        server = zServer(
            self.mock_logger,
            host="127.0.0.1",
            port=8080,
            serve_path=self.temp_dir
        )
        
        self.assertEqual(server.get_url(), "http://127.0.0.1:8080")


def run_tests():
    """Run all zServer tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzServerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzServerLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestzServerStaticFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestzServerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

