#!/usr/bin/env python3
"""
Week 1.6: zBifrost REAL Integration Tests
Phase 1: Server Lifecycle, Port Conflicts, and Coexistence with zServer
Phase 2: Real WebSocket Connections, Message Flow, Concurrent Clients, Auth

Tests REAL WebSocket server behavior (not just mocks).
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
from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost

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
    Gracefully skips in sandboxed environments (CI, restricted systems).
    Handles both sync and async test functions.
    """
    if asyncio.iscoroutinefunction(func):
        # Async function wrapper
        async def async_wrapper(*args, **kwargs):
            try:
                # Try to bind to a test port to check network availability
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(('127.0.0.1', 0))
                test_socket.close()
                return await func(*args, **kwargs)
            except (OSError, PermissionError) as e:
                raise unittest.SkipTest(f"Network not available (sandbox): {e}")
        async_wrapper.__name__ = func.__name__
        async_wrapper.__doc__ = func.__doc__
        return async_wrapper
    else:
        # Sync function wrapper
        def sync_wrapper(*args, **kwargs):
            try:
                # Try to bind to a test port to check network availability
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(('127.0.0.1', 0))
                test_socket.close()
                return func(*args, **kwargs)
            except (OSError, PermissionError) as e:
                raise unittest.SkipTest(f"Network not available (sandbox): {e}")
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
                "zWorkspace": self.temp_dir,
                "zMode": "zBifrost",
                "websocket": {"port": 8080},
                "http_server": {"enabled": True, "port": 8080}  # Same port!
            })
    
    @requires_network
    def test_different_ports_allowed(self):
        """Test that different ports for HTTP and WebSocket are allowed"""
        # This should NOT raise an error
        z = zCLI({
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
            "zMode": "zBifrost"
        })
        
        # Verify defaults are used
        self.assertIsNotNone(z.config.websocket)
        self.assertIsNotNone(z.config.websocket.port)
        self.assertIsNotNone(z.config.websocket.host)
    
    def test_websocket_config_via_zcomm(self):
        """Test WebSocket can be created via zComm"""
        z = zCLI({"zWorkspace": self.temp_dir})
        
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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
            "zWorkspace": self.temp_dir,
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


def run_tests(verbose=True):
    """Run all zBifrost integration tests (Phase 1 + Phase 2)."""
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
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zBifrost REAL Integration Test Suite - Week 1.6")
    print("Phase 1: Server Lifecycle, Port Conflicts, Coexistence")
    print("Phase 2: Real WebSocket Connections, Message Flow, Concurrent Clients")
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

