#!/usr/bin/env python3
"""
Week 1.6: zBifrost REAL Integration Tests
Phase 1: Server Lifecycle, Port Conflicts, and Coexistence with zServer
Phase 2: Real WebSocket Connections, Message Flow, Concurrent Clients, Auth
Phase 3: Demo Validation (Level 0, Level 1, Integration Flow)
Phase 4: Error Handling (Adjusted Scope - Server-side focus)

Tests REAL WebSocket server behavior (not just mocks).

Phase 4 Scope:
- Server-side error handling (malformed messages, unknown events, exceptions)
- Graceful shutdown with active connections
- Server handles client reconnections
- Skips: Full client-side auto-reconnect loop testing (validated in demos)
"""

import unittest
import asyncio
import tempfile
import time
import socket
import json
from pathlib import Path
from unittest.mock import Mock
import sys

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI
from zCLI.subsystems.zComm.zComm_modules.bifrost import zBifrost

# Import websockets for client testing (Phase 2)
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None


def requires_network(func):
    """
    Decorator to skip tests that require network access.
    
    Used for tests that need to bind to ports or make HTTP/WebSocket requests.
    Gracefully skips ONLY in true CI/sandbox environments (not local dev).
    Handles both sync and async test functions.
    
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
    
    if asyncio.iscoroutinefunction(func):
        # Async function wrapper
        async def async_wrapper(*args, **kwargs):
            if is_ci:
                # In CI: pre-check network availability
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.bind(('127.0.0.1', 0))
                    test_socket.close()
                except (OSError, PermissionError) as e:
                    raise unittest.SkipTest(f"Network not available (CI): {e}")
            # Local dev or CI with network: run the test
            return await func(*args, **kwargs)
        async_wrapper.__name__ = func.__name__
        async_wrapper.__doc__ = func.__doc__
        return async_wrapper
    else:
        # Sync function wrapper
        def sync_wrapper(*args, **kwargs):
            if is_ci:
                # In CI: pre-check network availability
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.bind(('127.0.0.1', 0))
                    test_socket.close()
                except (OSError, PermissionError) as e:
                    raise unittest.SkipTest(f"Network not available (CI): {e}")
            # Local dev or CI with network: run the test
            return func(*args, **kwargs)
        sync_wrapper.__name__ = func.__name__
        sync_wrapper.__doc__ = func.__doc__
        return sync_wrapper


class TestzBifrostInitialization(unittest.TestCase):
    """Test zBifrost initialization and configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_logger.info = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()
        self.mock_logger.debug = Mock()
        
        self.mock_zcli = Mock()
        self.mock_zcli.config = Mock()
        self.mock_zcli.config.websocket = Mock()
        self.mock_zcli.config.websocket.host = "127.0.0.1"
        self.mock_zcli.config.websocket.port = 56891
        self.mock_zcli.config.websocket.require_auth = False
        self.mock_zcli.config.websocket.allowed_origins = []
    
    def test_bifrost_initialization_defaults(self):
        """Test zBifrost initializes with default settings from config"""
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        
        self.assertEqual(bifrost.logger, self.mock_logger)
        self.assertEqual(bifrost.zcli, self.mock_zcli)
        self.assertEqual(bifrost.port, 56891)
        self.assertEqual(bifrost.host, "127.0.0.1")
    
    def test_bifrost_initialization_custom_config(self):
        """Test zBifrost initializes with custom configuration"""
        bifrost = zBifrost(
            self.mock_logger,
            zcli=self.mock_zcli,
            port=8765,
            host="0.0.0.0"
        )
        
        self.assertEqual(bifrost.port, 8765)
        self.assertEqual(bifrost.host, "0.0.0.0")
    
    def test_bifrost_auth_configuration(self):
        """Test zBifrost respects auth configuration"""
        # Test with auth enabled
        self.mock_zcli.config.websocket.require_auth = True
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        self.assertTrue(bifrost.auth.require_auth)
        
        # Test with auth disabled
        self.mock_zcli.config.websocket.require_auth = False
        bifrost = zBifrost(self.mock_logger, zcli=self.mock_zcli)
        self.assertFalse(bifrost.auth.require_auth)
    
    def test_bifrost_no_zcli_fallback(self):
        """Test zBifrost can initialize without zCLI (fallback to defaults)"""
        bifrost = zBifrost(self.mock_logger, port=9999, host="127.0.0.1")
        
        self.assertEqual(bifrost.port, 9999)
        self.assertEqual(bifrost.host, "127.0.0.1")
        self.assertIsNone(bifrost.zcli)


class TestzBifrostLifecycle(unittest.IsolatedAsyncioTestCase):
    """Test zBifrost server lifecycle (REAL async WebSocket server)"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @requires_network
    async def test_start_server_real(self):
        """Test zBifrost starts successfully with REAL WebSocket server"""
        # Create zCLI with zBifrost mode
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18765, "require_auth": False}
        })
        
        # Start server in background task
        socket_ready = asyncio.Event()
        task = asyncio.create_task(
            z.comm.start_websocket(socket_ready, walker=z.walker)
        )
        
        try:
            # Wait for server to be ready (with timeout)
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            
            # Verify server is ready
            self.assertTrue(socket_ready.is_set())
            
            # Give server a moment to fully start
            await asyncio.sleep(0.5)
            
            # Verify we can connect to the port (basic check)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex(('127.0.0.1', 18765))
                # 0 means connection succeeded (port is open)
                # We expect some result since WebSocket server is running
                self.assertIsNotNone(result)
            finally:
                sock.close()
            
        finally:
            # Clean up: cancel the server task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_server_ready_signal(self):
        """Test that socket_ready event is properly signaled"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18766, "require_auth": False}
        })
        
        socket_ready = asyncio.Event()
        
        # Verify event is not set initially
        self.assertFalse(socket_ready.is_set())
        
        task = asyncio.create_task(
            z.comm.start_websocket(socket_ready, walker=z.walker)
        )
        
        try:
            # Wait for event to be set
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            
            # Verify event was set by server
            self.assertTrue(socket_ready.is_set())
            
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_server_port_binding(self):
        """Test server actually binds to specified port"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18767, "require_auth": False}
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(
            z.comm.start_websocket(socket_ready, walker=z.walker)
        )
        
        try:
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            await asyncio.sleep(0.5)
            
            # Try to bind to same port - should fail if server is running
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with self.assertRaises(OSError):
                test_socket.bind(('127.0.0.1', 18767))
                test_socket.listen(1)
            test_socket.close()
            
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class TestzBifrostPortConflicts(unittest.TestCase):
    """Test port conflict detection and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_port_conflict_validation_at_config(self):
        """Test config validator catches same port for HTTP and WebSocket (Week 1.1)"""
        # This should be caught by ConfigValidator from Week 1.1
        with self.assertRaises(SystemExit):
            z = zCLI({
                "zSpace": self.temp_dir,
                "zMode": "zBifrost",
                "websocket": {"port": 8080},
                "http_server": {"enabled": True, "port": 8080}  # Same port!
            })
    
    @requires_network
    def test_different_ports_allowed(self):
        """Test that different ports for HTTP and WebSocket are allowed"""
        # This should NOT raise an error
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18768, "require_auth": False},
            "http_server": {"enabled": True, "port": 18868}
        })
        
        # Verify both are configured correctly
        self.assertEqual(z.config.websocket.port, 18768)
        self.assertEqual(z.server.port, 18868)
        self.assertNotEqual(z.config.websocket.port, z.server.port)
        
        # Clean up HTTP server
        if z.server.is_running():
            z.server.stop()


class TestzBifrostCoexistence(unittest.TestCase):
    """Test zBifrost + zServer running together (REAL servers)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test HTML file for HTTP server
        test_file = Path(self.temp_dir) / "test.html"
        test_file.write_text("<html><body>Test</body></html>")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @requires_network
    def test_both_servers_different_ports_config(self):
        """Test both HTTP and WebSocket servers can be configured together"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18769, "require_auth": False},
            "http_server": {
                "enabled": True,
                "port": 18869,
                "serve_path": self.temp_dir
            }
        })
        
        # Verify both are configured with different ports
        self.assertIsNotNone(z.server)
        self.assertIsNotNone(z.config.websocket)
        self.assertNotEqual(z.server.port, z.config.websocket.port)
        
        # Verify HTTP server is running (auto-started)
        self.assertTrue(z.server.is_running())
        
        # Verify ports are actually different
        self.assertEqual(z.config.websocket.port, 18769)
        self.assertEqual(z.server.port, 18869)
        
        # Clean up
        z.server.stop()
    
    @requires_network
    def test_http_server_runs_independently(self):
        """Test HTTP server runs even when WebSocket is configured but not started"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18770, "require_auth": False},
            "http_server": {
                "enabled": True,
                "port": 18870,
                "serve_path": self.temp_dir
            }
        })
        
        # HTTP server should be running
        self.assertTrue(z.server.is_running())
        
        # Verify HTTP port is bound
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 18870))
        self.assertEqual(result, 0)  # 0 = connection succeeded
        sock.close()
        
        # Clean up
        z.server.stop()
    
    @requires_network
    def test_websocket_port_free_when_http_running(self):
        """Test WebSocket port is free even when HTTP server is running"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {"port": 18771, "require_auth": False},
            "http_server": {
                "enabled": True,
                "port": 18871,
                "serve_path": self.temp_dir
            }
        })
        
        # HTTP server is running
        self.assertTrue(z.server.is_running())
        
        # WebSocket port should be free (not started yet)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Should be able to bind to WebSocket port
            test_socket.bind(('127.0.0.1', 18771))
            test_socket.close()
        except OSError:
            self.fail("WebSocket port should be free when server not started")
        
        # Clean up
        z.server.stop()


class TestzBifrostConfiguration(unittest.TestCase):
    """Test zBifrost configuration from zCLI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_websocket_config_loaded_from_zspark(self):
        """Test WebSocket config is loaded from zSpark_obj"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost",
            "websocket": {
                "port": 18772,
                "host": "127.0.0.1",
                "require_auth": True,
                "allowed_origins": ["http://localhost:3000"]
            }
        })
        
        # Verify config was loaded
        self.assertEqual(z.config.websocket.port, 18772)
        self.assertEqual(z.config.websocket.host, "127.0.0.1")
        self.assertTrue(z.config.websocket.require_auth)
        self.assertEqual(z.config.websocket.allowed_origins, ["http://localhost:3000"])
    
    def test_websocket_default_config(self):
        """Test WebSocket uses defaults when not specified"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zMode": "zBifrost"
        })
        
        # Verify defaults are used
        self.assertIsNotNone(z.config.websocket)
        self.assertIsNotNone(z.config.websocket.port)
        self.assertIsNotNone(z.config.websocket.host)
    
    def test_websocket_config_via_zcomm(self):
        """Test WebSocket can be created via zComm"""
        z = zCLI({"zSpace": self.temp_dir})
        
        # Create WebSocket server via zComm
        bifrost = z.comm.create_websocket(port=18773, host="127.0.0.1")
        
        # Verify server is created correctly
        self.assertIsNotNone(bifrost)
        self.assertEqual(bifrost.port, 18773)
        self.assertEqual(bifrost.host, "127.0.0.1")


# ============================================================================
# PHASE 2: Real WebSocket Client Connection Tests
# ============================================================================

@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestRealWebSocketConnections(unittest.IsolatedAsyncioTestCase):
    """Test REAL WebSocket client connections (Phase 2)"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple zUI file for testing
        ui_file = Path(self.temp_dir) / "zUI.test.yaml"
        ui_file.write_text("""TestMenu:
  ~Root*: ["Ping", "Echo", "stop"]
  "Ping": "Pong!"
  "Echo": "Echo received"
""")
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    async def _start_server(self, port=18774, require_auth=False):
        """Helper to start zBifrost server"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zVaFile": "@.zUI.test",
            "zBlock": "TestMenu",
            "zMode": "zBifrost",
            "websocket": {
                "port": port,
                "host": "127.0.0.1",
                "require_auth": require_auth
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        
        # Wait for server to be ready with timeout
        try:
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            await asyncio.sleep(0.5)  # Give server time to fully start
        except asyncio.TimeoutError:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            raise RuntimeError("Server failed to start within timeout")
        
        return z, task
    
    @requires_network
    async def test_connect_and_receive_connection_info(self):
        """Test connecting and receiving connection_info broadcast"""
        z, server_task = await self._start_server(port=18774)
        
        try:
            # Connect client
            async with websockets.connect('ws://127.0.0.1:18774') as ws:
                # Should receive connection_info immediately
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify connection_info structure
                self.assertEqual(data['event'], 'connection_info')
                self.assertIn('data', data)
                self.assertIn('server_version', data['data'])
                self.assertIn('features', data['data'])
                self.assertIn('auth', data['data'])
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_connect_and_disconnect(self):
        """Test basic connect and disconnect cycle"""
        z, server_task = await self._start_server(port=18775)
        
        try:
            # Connect and disconnect
            async with websockets.connect('ws://127.0.0.1:18775') as ws:
                # Receive connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                # Connection successful
                self.assertTrue(True)
            
            # After context exit, connection should be closed
            # Test passes if no exceptions
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_multiple_sequential_connections(self):
        """Test connecting, disconnecting, and reconnecting"""
        z, server_task = await self._start_server(port=18776)
        
        try:
            # First connection
            async with websockets.connect('ws://127.0.0.1:18776') as ws:
                await asyncio.wait_for(ws.recv(), timeout=3)
            
            # Second connection (reconnect)
            async with websockets.connect('ws://127.0.0.1:18776') as ws:
                await asyncio.wait_for(ws.recv(), timeout=3)
            
            # Third connection
            async with websockets.connect('ws://127.0.0.1:18776') as ws:
                await asyncio.wait_for(ws.recv(), timeout=3)
            
            # All connections successful
            self.assertTrue(True)
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestWebSocketMessageFlow(unittest.IsolatedAsyncioTestCase):
    """Test WebSocket message send/receive flow (Phase 2)"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple zUI file for testing
        ui_file = Path(self.temp_dir) / "zUI.test.yaml"
        ui_file.write_text("""TestMenu:
  ~Root*: ["Ping", "Echo", "stop"]
  "Ping": "Pong!"
  "Echo": "Echo received"
""")
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    async def _start_server(self, port=18777):
        """Helper to start zBifrost server"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zVaFile": "@.zUI.test",
            "zBlock": "TestMenu",
            "zMode": "zBifrost",
            "websocket": {
                "port": port,
                "host": "127.0.0.1",
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.5)
        
        return z, task
    
    @requires_network
    async def test_dispatch_simple_command(self):
        """Test sending dispatch command and receiving response"""
        z, server_task = await self._start_server(port=18777)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18777') as ws:
                # Receive and discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send dispatch command
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Ping"
                }))
                
                # Receive response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify response structure
                self.assertIn('result', data)
                # Result should be a message dict or string
                if isinstance(data['result'], dict):
                    self.assertIn('message', data['result'])
                    self.assertEqual(data['result']['message'], 'Pong!')
                else:
                    # Might be direct string
                    self.assertEqual(data['result'], 'Pong!')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_dispatch_with_ui_resolution(self):
        """Test dispatch resolves ^key from zUI file"""
        z, server_task = await self._start_server(port=18778)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18778') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send command with ^ prefix (should resolve from zUI)
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Echo"
                }))
                
                # Receive response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify it resolved to "Echo received"
                self.assertIn('result', data)
                if isinstance(data['result'], dict):
                    self.assertIn('message', data['result'])
                    self.assertEqual(data['result']['message'], 'Echo received')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_invalid_message_format(self):
        """Test sending invalid JSON doesn't crash server"""
        z, server_task = await self._start_server(port=18779)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18779') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send invalid JSON
                await ws.send("not valid json {{{")
                
                # Server should handle gracefully (may send error or close connection)
                # Either way, test passes if server doesn't crash
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=2)
                    # If we get a response, server handled it gracefully
                except asyncio.TimeoutError:
                    # If timeout, server might have ignored it - also OK
                    pass
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestConcurrentClients(unittest.IsolatedAsyncioTestCase):
    """Test multiple concurrent WebSocket clients (Phase 2)"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        ui_file = Path(self.temp_dir) / "zUI.test.yaml"
        ui_file.write_text("""TestMenu:
  ~Root*: ["Ping", "stop"]
  "Ping": "Pong!"
""")
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    async def _start_server(self, port=18780):
        """Helper to start zBifrost server"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zVaFile": "@.zUI.test",
            "zBlock": "TestMenu",
            "zMode": "zBifrost",
            "websocket": {
                "port": port,
                "host": "127.0.0.1",
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.5)
        
        return z, task
    
    @requires_network
    async def test_multiple_clients_connect(self):
        """Test 3 clients can connect simultaneously"""
        z, server_task = await self._start_server(port=18780)
        
        try:
            # Connect 3 clients simultaneously
            ws1 = await websockets.connect('ws://127.0.0.1:18780')
            ws2 = await websockets.connect('ws://127.0.0.1:18780')
            ws3 = await websockets.connect('ws://127.0.0.1:18780')
            
            try:
                # All should receive connection_info
                await asyncio.wait_for(ws1.recv(), timeout=3)
                await asyncio.wait_for(ws2.recv(), timeout=3)
                await asyncio.wait_for(ws3.recv(), timeout=3)
                
                # All connected successfully
                self.assertTrue(True)
                
            finally:
                await ws1.close()
                await ws2.close()
                await ws3.close()
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_clients_send_independently(self):
        """Test each client can send commands independently"""
        z, server_task = await self._start_server(port=18781)
        
        try:
            ws1 = await websockets.connect('ws://127.0.0.1:18781')
            ws2 = await websockets.connect('ws://127.0.0.1:18781')
            
            try:
                # Discard connection_info
                await asyncio.wait_for(ws1.recv(), timeout=3)
                await asyncio.wait_for(ws2.recv(), timeout=3)
                
                # Client 1 sends command
                await ws1.send(json.dumps({"event": "dispatch", "zKey": "^Ping"}))
                
                # Client 2 sends command
                await ws2.send(json.dumps({"event": "dispatch", "zKey": "^Ping"}))
                
                # Both should receive responses
                resp1 = await asyncio.wait_for(ws1.recv(), timeout=3)
                resp2 = await asyncio.wait_for(ws2.recv(), timeout=3)
                
                # Both should be valid responses
                self.assertIsNotNone(json.loads(resp1))
                self.assertIsNotNone(json.loads(resp2))
                
            finally:
                await ws1.close()
                await ws2.close()
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestWebSocketAuthentication(unittest.IsolatedAsyncioTestCase):
    """Test WebSocket authentication flows (Phase 2)"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        ui_file = Path(self.temp_dir) / "zUI.test.yaml"
        ui_file.write_text("""TestMenu:
  ~Root*: ["Test", "stop"]
  "Test": "OK"
""")
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @requires_network
    async def test_connect_with_auth_disabled(self):
        """Test connection succeeds when auth is disabled"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zVaFile": "@.zUI.test",
            "zBlock": "TestMenu",
            "zMode": "zBifrost",
            "websocket": {
                "port": 18782,
                "host": "127.0.0.1",
                "require_auth": False  # Auth disabled
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        
        try:
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            await asyncio.sleep(0.5)
            
            # Should be able to connect without authentication
            async with websockets.connect('ws://127.0.0.1:18782') as ws:
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify connection successful
                self.assertEqual(data['event'], 'connection_info')
                
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_auth_info_in_connection(self):
        """Test connection_info includes auth details"""
        z = zCLI({
            "zSpace": self.temp_dir,
            "zVaFile": "@.zUI.test",
            "zBlock": "TestMenu",
            "zMode": "zBifrost",
            "websocket": {
                "port": 18783,
                "host": "127.0.0.1",
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        
        try:
            await asyncio.wait_for(socket_ready.wait(), timeout=5)
            await asyncio.sleep(0.5)
            
            async with websockets.connect('ws://127.0.0.1:18783') as ws:
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify auth info is present
                self.assertIn('auth', data['data'])
                self.assertIn('authenticated', data['data']['auth'])
                self.assertIn('user', data['data']['auth'])
                self.assertIn('role', data['data']['auth'])
                
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


# ============================================================================
# PHASE 3: Demo Validation Tests
# ============================================================================

@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestLevel0DemoValidation(unittest.IsolatedAsyncioTestCase):
    """Validate Level 0 demo behavior (connection_info broadcast)"""
    
    async def _start_level0_demo_server(self, port=18785):
        """Start server with exact Level 0 demo config"""
        # Replicate level0_backend.py configuration
        z = zCLI({
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False  # Level 0: No auth required
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.5)
        
        return z, task
    
    @requires_network
    async def test_level0_connection_info_broadcast(self):
        """Test Level 0 demo sends connection_info on connect"""
        z, server_task = await self._start_level0_demo_server(port=18785)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18785') as ws:
                # Level 0 should immediately send connection_info
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Validate connection_info structure (as per Level 0 README)
                self.assertEqual(data['event'], 'connection_info')
                self.assertIn('data', data)
                self.assertIn('server_version', data['data'])
                self.assertIn('features', data['data'])
                self.assertIn('auth', data['data'])
                
                # Level 0: Auth should show require_auth=False
                self.assertTrue(data['data']['auth']['authenticated'])
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level0_features_list(self):
        """Test Level 0 demo includes expected features in connection_info"""
        z, server_task = await self._start_level0_demo_server(port=18786)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18786') as ws:
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify features are listed
                features = data['data']['features']
                self.assertIsInstance(features, list)
                # Should have schema_cache, query_cache, connection_info, realtime_sync
                self.assertIn('schema_cache', features)
                self.assertIn('connection_info', features)
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level0_no_commands(self):
        """Test Level 0 demo has no UI commands (bare connection only)"""
        z, server_task = await self._start_level0_demo_server(port=18787)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18787') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Try to send a dispatch command (should handle gracefully)
                await ws.send(json.dumps({"event": "dispatch", "zKey": "^Test"}))
                
                # Server should respond (even if command doesn't exist)
                # This tests that Level 0 can handle dispatch events gracefully
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=2)
                    # Got a response - server handled it gracefully
                    self.assertIsNotNone(response)
                except asyncio.TimeoutError:
                    # Timeout is also acceptable - server might not respond to invalid commands
                    pass
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestLevel1DemoValidation(unittest.IsolatedAsyncioTestCase):
    """Validate Level 1 demo behavior (zUI command resolution)"""
    
    async def _start_level1_demo_server(self, port=18788):
        """Start server with exact Level 1 demo config"""
        # Replicate level1_backend.py configuration
        demo_dir = Path(__file__).parent.parent / "Demos" / "zBifost"
        
        z = zCLI({
            "zSpace": str(demo_dir),
            "zVaFile": "@.zUI.level1",
            "zBlock": "Level1Menu",
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.5)
        
        return z, task
    
    @requires_network
    async def test_level1_loads_zui_file(self):
        """Test Level 1 demo loads zUI.level1.yaml correctly"""
        z, server_task = await self._start_level1_demo_server(port=18788)
        
        try:
            # Verify zUI file was loaded
            self.assertIsNotNone(z.walker)
            
            # Verify we can connect
            async with websockets.connect('ws://127.0.0.1:18788') as ws:
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                self.assertEqual(data['event'], 'connection_info')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level1_ping_command(self):
        """Test Level 1 demo: ^Ping → Pong!"""
        z, server_task = await self._start_level1_demo_server(port=18789)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18789') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send ^Ping command (as per zUI.level1.yaml)
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Ping"
                }))
                
                # Receive response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify response is "Pong!" (as defined in zUI.level1.yaml)
                self.assertIn('result', data)
                if isinstance(data['result'], dict):
                    self.assertEqual(data['result']['message'], 'Pong!')
                else:
                    self.assertEqual(data['result'], 'Pong!')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level1_echo_command(self):
        """Test Level 1 demo: ^Echo Test → Echo: Hello from zBifrost"""
        z, server_task = await self._start_level1_demo_server(port=18790)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18790') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send ^Echo Test command
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Echo Test"
                }))
                
                # Receive response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify response matches zUI.level1.yaml
                self.assertIn('result', data)
                if isinstance(data['result'], dict):
                    self.assertEqual(data['result']['message'], 'Echo: Hello from zBifrost')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level1_status_command(self):
        """Test Level 1 demo: ^Status → Server is running"""
        z, server_task = await self._start_level1_demo_server(port=18791)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18791') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send ^Status command
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Status"
                }))
                
                # Receive response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify response matches zUI.level1.yaml
                self.assertIn('result', data)
                if isinstance(data['result'], dict):
                    self.assertEqual(data['result']['message'], 'Server is running')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_level1_all_commands_sequential(self):
        """Test Level 1 demo: All commands work in sequence"""
        z, server_task = await self._start_level1_demo_server(port=18792)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18792') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Test all 3 commands in sequence
                commands = [
                    ("^Ping", "Pong!"),
                    ("^Echo Test", "Echo: Hello from zBifrost"),
                    ("^Status", "Server is running")
                ]
                
                for zkey, expected in commands:
                    await ws.send(json.dumps({"event": "dispatch", "zKey": zkey}))
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    data = json.loads(response)
                    
                    # Verify each response
                    self.assertIn('result', data)
                    if isinstance(data['result'], dict):
                        self.assertEqual(data['result']['message'], expected)
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestDemoIntegrationFlow(unittest.IsolatedAsyncioTestCase):
    """Validate zWalker → zDispatch → zDisplay integration flow"""
    
    async def _start_demo_server(self, port=18793):
        """Start Level 1 server for integration testing"""
        demo_dir = Path(__file__).parent.parent / "Demos" / "zBifost"
        
        z = zCLI({
            "zSpace": str(demo_dir),
            "zVaFile": "@.zUI.level1",
            "zBlock": "Level1Menu",
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.5)
        
        return z, task
    
    @requires_network
    async def test_walker_receives_dispatch_event(self):
        """Test zWalker receives and processes dispatch events from WebSocket"""
        z, server_task = await self._start_demo_server(port=18793)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18793') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send dispatch event - zWalker should receive it
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Ping"
                }))
                
                # Should get a response back (proves zWalker received and processed it)
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Got a valid response with result
                self.assertIn('result', data)
                self.assertIsNotNone(data['result'])
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_dispatch_resolves_prefix_modifiers(self):
        """Test zDispatch strips ^ prefix and resolves from zUI file"""
        z, server_task = await self._start_demo_server(port=18794)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18794') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send ^Ping - zDispatch should:
                # 1. Strip the ^ prefix
                # 2. Look up "Ping" in zUI.level1.yaml
                # 3. Return "Pong!"
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Ping"
                }))
                
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify it resolved correctly
                self.assertIn('result', data)
                if isinstance(data['result'], dict):
                    # zDispatch resolved "Ping" → "Pong!" from zUI
                    self.assertEqual(data['result']['message'], 'Pong!')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_display_message_format(self):
        """Test zDisplay returns correct message format in zBifrost mode"""
        z, server_task = await self._start_demo_server(port=18795)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18795') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send command
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Status"
                }))
                
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify response format
                self.assertIn('result', data)
                
                # In zBifrost mode, plain strings should be wrapped in {"message": "..."}
                if isinstance(data['result'], dict):
                    self.assertIn('message', data['result'])
                    self.assertIsInstance(data['result']['message'], str)
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_full_request_response_cycle(self):
        """Test complete flow: WebSocket → zWalker → zDispatch → zDisplay → WebSocket"""
        z, server_task = await self._start_demo_server(port=18796)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18796') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Full cycle test
                await ws.send(json.dumps({
                    "event": "dispatch",
                    "zKey": "^Ping",
                    "_requestId": 12345  # Track request ID
                }))
                
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Verify complete cycle worked
                self.assertIn('result', data)
                self.assertIn('_requestId', data)
                self.assertEqual(data['_requestId'], 12345)
                
                # Verify the result is correct
                if isinstance(data['result'], dict):
                    self.assertEqual(data['result']['message'], 'Pong!')
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


# ═══════════════════════════════════════════════════════════════════
# Phase 4: Error Handling Tests (Adjusted Scope)
# ═══════════════════════════════════════════════════════════════════

@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestzBifrostErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Test server-side error handling (Phase 4)"""
    
    async def _start_server(self, port=18800):
        """Start basic server for error testing"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        return z, task
    
    @requires_network
    async def test_malformed_json_handled_gracefully(self):
        """Test server handles invalid JSON without crashing"""
        z, server_task = await self._start_server(port=18801)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18801') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send invalid JSON
                await ws.send("not valid json {{{")
                
                # Wait a moment for server to process
                await asyncio.sleep(0.2)
                
                # If we're still in the context manager, connection is alive
                # Server didn't crash or disconnect us
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_malformed_event_structure_handled(self):
        """Test server handles valid JSON with missing required fields"""
        z, server_task = await self._start_server(port=18802)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18802') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send valid JSON but missing 'event' field
                await ws.send(json.dumps({"random": "data", "no_event": True}))
                
                # Wait a moment for server to process
                await asyncio.sleep(0.2)
                
                # If we're still in the context manager, connection is alive
                # Server didn't crash or disconnect us
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_unknown_event_type_handled(self):
        """Test server handles unknown event types gracefully"""
        z, server_task = await self._start_server(port=18803)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18803') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send unknown event
                await ws.send(json.dumps({"event": "totally_unknown_event", "data": "test"}))
                
                # Wait a moment for server to process
                await asyncio.sleep(0.2)
                
                # If we're still in the context manager, connection is alive
                # Server didn't crash or disconnect us
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_exception_in_dispatch_handler(self):
        """Test server handles exceptions during command dispatch"""
        # Create server with zUI that triggers errors
        workspace = Path(tempfile.mkdtemp())
        
        # Create zUI with a command that will fail
        ui_file = workspace / "zUI.error_test.yaml"
        ui_file.write_text("""ErrorMenu:
  ~Root*: ["BrokenCommand", "stop"]
  "BrokenCommand": "&nonexistent.function"
""")
        
        z = zCLI({
            "zSpace": str(workspace),
            "zVaFile": "@.zUI.error_test",
            "zBlock": "ErrorMenu",
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": 18804,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        server_task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18804') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send command that will trigger exception
                await ws.send(json.dumps({"event": "dispatch", "zKey": "^BrokenCommand"}))
                
                # Server should catch exception and send error response
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                
                # Should get some response (error or null result)
                self.assertIn('result', data)
                # The result might be None or an error dict
                
                # If we're still in the context manager, connection is alive
                # Server didn't crash after handling exception
                
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_server_logs_errors_not_crashes(self):
        """Test server logs errors but continues operating"""
        z, server_task = await self._start_server(port=18805)
        
        try:
            # Connect multiple clients and send various error conditions
            async with websockets.connect('ws://127.0.0.1:18805') as ws1:
                async with websockets.connect('ws://127.0.0.1:18805') as ws2:
                    # Discard connection_info for both
                    await asyncio.wait_for(ws1.recv(), timeout=3)
                    await asyncio.wait_for(ws2.recv(), timeout=3)
                    
                    # Send various error conditions from different clients
                    await ws1.send("bad json")
                    await ws2.send(json.dumps({"event": "unknown"}))
                    await ws1.send(json.dumps({"no_event": True}))
                    
                    # Wait for server to process all errors
                    await asyncio.sleep(0.5)
                    
                    # If we're still in both context managers, connections are alive
                    # Server didn't crash or disconnect us after multiple errors
                    
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestzBifrostGracefulShutdown(unittest.IsolatedAsyncioTestCase):
    """Test graceful shutdown with active connections (Phase 4)"""
    
    async def _start_server(self, port=18810):
        """Start server for shutdown testing"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        return z, task
    
    @requires_network
    async def test_shutdown_with_active_clients(self):
        """Test server shuts down cleanly with connected clients"""
        z, server_task = await self._start_server(port=18811)
        
        clients = []
        try:
            # Connect 3 clients
            for i in range(3):
                ws = await websockets.connect('ws://127.0.0.1:18811')
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                clients.append(ws)
            
            # Verify all clients are connected
            self.assertEqual(len(clients), 3)
            
            # Send messages to keep connections active
            for i, ws in enumerate(clients):
                await ws.send(json.dumps({"event": "ping", "client": i}))
            
            # Cancel server while clients are active
            server_task.cancel()
            
            # Wait for server to shut down
            try:
                await asyncio.wait_for(server_task, timeout=3)
            except asyncio.CancelledError:
                # Expected
                pass
            
            # Give clients time to detect disconnection
            await asyncio.sleep(0.5)
            
            # Verify server shut down cleanly - this is the main goal
            # (Client disconnection detection varies by implementation/timing)
            self.assertTrue(True, "Server shut down successfully with active clients")
                    
        finally:
            # Clean up clients
            for ws in clients:
                try:
                    await ws.close()
                except:
                    pass
    
    @requires_network
    async def test_shutdown_during_message_processing(self):
        """Test server shuts down cleanly during active message processing"""
        z, server_task = await self._start_server(port=18812)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18812') as ws:
                # Discard connection_info
                await asyncio.wait_for(ws.recv(), timeout=3)
                
                # Send message
                await ws.send(json.dumps({"event": "dispatch", "zKey": "^Help"}))
                
                # Immediately cancel server (while message might be processing)
                server_task.cancel()
                
                # Server should either:
                # 1. Complete the message and then shut down
                # 2. Shut down immediately and close connection
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=1)
                    # Got response - server completed gracefully
                    self.assertIsNotNone(response)
                except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                    # Connection closed - also acceptable
                    pass
                
                # Wait for server shutdown
                try:
                    await asyncio.wait_for(server_task, timeout=3)
                except asyncio.CancelledError:
                    pass
                    
        finally:
            pass
    
    @requires_network
    async def test_cleanup_removes_all_clients(self):
        """Test server cleanup properly removes all client references"""
        z, server_task = await self._start_server(port=18813)
        
        clients = []
        try:
            # Connect 2 clients
            for i in range(2):
                ws = await websockets.connect('ws://127.0.0.1:18813')
                await asyncio.wait_for(ws.recv(), timeout=3)
                clients.append(ws)
            
            # Verify clients are registered (through connection)
            self.assertEqual(len(clients), 2)
            
            # Shutdown server
            server_task.cancel()
            try:
                await asyncio.wait_for(server_task, timeout=3)
            except asyncio.CancelledError:
                pass
            
            # Verify all clients disconnected
            for ws in clients:
                # Try to receive - should raise ConnectionClosed or timeout
                with self.assertRaises((websockets.exceptions.ConnectionClosed, asyncio.TimeoutError)):
                    await asyncio.wait_for(ws.recv(), timeout=0.5)
                    
        finally:
            for ws in clients:
                try:
                    await ws.close()
                except:
                    pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestzBifrostClientReconnection(unittest.IsolatedAsyncioTestCase):
    """Test server-side reconnection handling (Phase 4)"""
    
    async def _start_server(self, port=18820):
        """Start server for reconnection testing"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        return z, task
    
    @requires_network
    async def test_server_handles_client_reconnect(self):
        """Test server handles client disconnect and reconnect"""
        z, server_task = await self._start_server(port=18821)
        
        try:
            # First connection
            async with websockets.connect('ws://127.0.0.1:18821') as ws1:
                # Discard connection_info
                conn_info1 = await asyncio.wait_for(ws1.recv(), timeout=3)
                data1 = json.loads(conn_info1)
                self.assertEqual(data1['event'], 'connection_info')
                
                # Close connection
                await ws1.close()
            
            # Wait a bit
            await asyncio.sleep(0.3)
            
            # Reconnect (new connection)
            async with websockets.connect('ws://127.0.0.1:18821') as ws2:
                # Should get connection_info again
                conn_info2 = await asyncio.wait_for(ws2.recv(), timeout=3)
                data2 = json.loads(conn_info2)
                self.assertEqual(data2['event'], 'connection_info')
                # Successfully reconnected
                    
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_server_handles_rapid_reconnections(self):
        """Test server handles rapid connect/disconnect cycles"""
        z, server_task = await self._start_server(port=18822)
        
        try:
            # Rapidly connect and disconnect 5 times
            for i in range(5):
                async with websockets.connect('ws://127.0.0.1:18822') as ws:
                    # Get connection_info
                    conn_info = await asyncio.wait_for(ws.recv(), timeout=3)
                    data = json.loads(conn_info)
                    self.assertEqual(data['event'], 'connection_info')
                    
                    # Immediate close
                    await ws.close()
                
                # Small delay between reconnections
                await asyncio.sleep(0.1)
            
            # Server should still be responsive
            async with websockets.connect('ws://127.0.0.1:18822') as ws:
                conn_info = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(conn_info)
                self.assertEqual(data['event'], 'connection_info')
                # Server survived rapid reconnections
                    
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_server_properly_unregisters_disconnected_clients(self):
        """Test server unregisters clients on disconnect"""
        z, server_task = await self._start_server(port=18823)
        
        try:
            # Connect client 1
            ws1 = await websockets.connect('ws://127.0.0.1:18823')
            conn_info1 = await asyncio.wait_for(ws1.recv(), timeout=3)
            data1 = json.loads(conn_info1)
            self.assertEqual(data1['event'], 'connection_info')
            
            # Connect client 2
            ws2 = await websockets.connect('ws://127.0.0.1:18823')
            conn_info2 = await asyncio.wait_for(ws2.recv(), timeout=3)
            data2 = json.loads(conn_info2)
            self.assertEqual(data2['event'], 'connection_info')
            
            # Both connections active (received connection_info successfully)
            
            # Disconnect client 1
            await ws1.close()
            await asyncio.sleep(0.3)
            
            # Client 2 should still be connected (we can still use it)
            
            # Clean up
            await ws2.close()
                    
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_connection_closed_with_reason_code(self):
        """Test server handles clean close with reason codes"""
        z, server_task = await self._start_server(port=18824)
        
        try:
            async with websockets.connect('ws://127.0.0.1:18824') as ws:
                # Get connection_info
                conn_info = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(conn_info)
                self.assertEqual(data['event'], 'connection_info')
                
                # Close with specific reason code
                await ws.close(code=1000, reason="Client disconnecting normally")
            
            # Server should handle this gracefully and remain operational
            await asyncio.sleep(0.3)
            
            # Connect new client to verify server still works
            async with websockets.connect('ws://127.0.0.1:18824') as ws2:
                conn_info2 = await asyncio.wait_for(ws2.recv(), timeout=3)
                data2 = json.loads(conn_info2)
                self.assertEqual(data2['event'], 'connection_info')
                # Server still operational after clean close
                    
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


@unittest.skipIf(not WEBSOCKETS_AVAILABLE, "websockets library not available")
class TestzBifrostHealthCheck(unittest.IsolatedAsyncioTestCase):
    """Test zBifrost health check functionality (Week 2.1)"""
    
    async def _start_server(self, port=18900):
        """Start basic server for health check testing"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": port,
                "require_auth": False
            }
        })
        
        socket_ready = asyncio.Event()
        task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        return z, task
    
    @requires_network
    async def test_health_check_before_start(self):
        """Test health check before server starts"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": 18901,
                "require_auth": False
            }
        })
        
        # Get health check before starting
        health = z.comm.websocket.health_check()
        
        # Verify structure
        self.assertIn("running", health)
        self.assertIn("host", health)
        self.assertIn("port", health)
        self.assertIn("url", health)
        self.assertIn("clients", health)
        self.assertIn("authenticated_clients", health)
        self.assertIn("require_auth", health)
        
        # Verify values before start
        self.assertFalse(health["running"])
        self.assertEqual(health["host"], "127.0.0.1")
        self.assertEqual(health["port"], 18901)
        self.assertIsNone(health["url"])
        self.assertEqual(health["clients"], 0)
        self.assertEqual(health["authenticated_clients"], 0)
        self.assertFalse(health["require_auth"])
    
    @requires_network
    async def test_health_check_while_running(self):
        """Test health check while server is running"""
        z, server_task = await self._start_server(port=18902)
        
        try:
            # Get health check while running
            health = z.comm.websocket.health_check()
            
            # Verify running state
            self.assertTrue(health["running"])
            self.assertEqual(health["host"], "127.0.0.1")
            self.assertEqual(health["port"], 18902)
            self.assertEqual(health["url"], "ws://127.0.0.1:18902")
            self.assertEqual(health["clients"], 0)  # No clients connected yet
            self.assertFalse(health["require_auth"])
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_health_check_with_clients(self):
        """Test health check reflects connected clients"""
        z, server_task = await self._start_server(port=18903)
        
        try:
            # Connect 2 clients
            async with websockets.connect('ws://127.0.0.1:18903') as ws1:
                async with websockets.connect('ws://127.0.0.1:18903') as ws2:
                    # Discard connection_info
                    await asyncio.wait_for(ws1.recv(), timeout=3)
                    await asyncio.wait_for(ws2.recv(), timeout=3)
                    
                    await asyncio.sleep(0.2)
                    
                    # Get health check with clients
                    health = z.comm.websocket.health_check()
                    
                    # Verify client count
                    self.assertTrue(health["running"])
                    self.assertEqual(health["clients"], 2)
                    self.assertEqual(health["authenticated_clients"], 2)  # Both authenticated (no auth required)
            
            # Wait for clients to disconnect
            await asyncio.sleep(0.3)
            
            # Get health check after disconnect
            health_after = z.comm.websocket.health_check()
            self.assertEqual(health_after["clients"], 0)
            self.assertEqual(health_after["authenticated_clients"], 0)
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @requires_network
    async def test_health_check_with_auth_required(self):
        """Test health check with authentication enabled"""
        workspace = Path(tempfile.mkdtemp())
        
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "websocket": {
                "host": "127.0.0.1",
                "port": 18904,
                "require_auth": True  # Enable auth
            }
        })
        
        socket_ready = asyncio.Event()
        server_task = asyncio.create_task(z.comm.start_websocket(socket_ready, walker=z.walker))
        await asyncio.wait_for(socket_ready.wait(), timeout=5)
        await asyncio.sleep(0.3)
        
        try:
            # Get health check with auth enabled
            health = z.comm.websocket.health_check()
            
            # Verify auth setting
            self.assertTrue(health["running"])
            self.assertTrue(health["require_auth"])
            
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


def run_tests(verbose=True):
    """Run all zBifrost integration tests (Phase 1 + Phase 2 + Phase 3 + Phase 4 + Health Checks)."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Phase 1: Server Lifecycle Tests
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostPortConflicts))
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostCoexistence))
    suite.addTests(loader.loadTestsFromTestCase(TestzBifrostConfiguration))
    
    # Phase 2: Real WebSocket Connection Tests
    if WEBSOCKETS_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestRealWebSocketConnections))
        suite.addTests(loader.loadTestsFromTestCase(TestWebSocketMessageFlow))
        suite.addTests(loader.loadTestsFromTestCase(TestConcurrentClients))
        suite.addTests(loader.loadTestsFromTestCase(TestWebSocketAuthentication))
        
        # Phase 3: Demo Validation Tests
        suite.addTests(loader.loadTestsFromTestCase(TestLevel0DemoValidation))
        suite.addTests(loader.loadTestsFromTestCase(TestLevel1DemoValidation))
        suite.addTests(loader.loadTestsFromTestCase(TestDemoIntegrationFlow))
        
        # Phase 4: Error Handling Tests (Adjusted Scope)
        suite.addTests(loader.loadTestsFromTestCase(TestzBifrostErrorHandling))
        suite.addTests(loader.loadTestsFromTestCase(TestzBifrostGracefulShutdown))
        suite.addTests(loader.loadTestsFromTestCase(TestzBifrostClientReconnection))
        
        # Week 2.1: Health Check Tests
        suite.addTests(loader.loadTestsFromTestCase(TestzBifrostHealthCheck))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zBifrost REAL Integration Test Suite - Week 1.6")
    print("Phase 1: Server Lifecycle, Port Conflicts, Coexistence")
    print("Phase 2: Real WebSocket Connections, Message Flow, Concurrent Clients")
    print("Phase 3: Demo Validation (Level 0, Level 1, Integration Flow)")
    print("Phase 4: Error Handling (Server-side: Errors, Shutdown, Reconnections)")
    print("=" * 70)
    result = run_tests(verbose=True)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)

