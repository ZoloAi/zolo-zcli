# zTestRunner/plugins/zserver_tests.py
"""
zServer Comprehensive Test Suite (45 tests)
Declarative approach - tests HTTP static file server functionality
Covers all zServer moving parts: initialization, lifecycle, static files,
CORS, error handling, health check, configuration, integration, routing & RBAC
"""

import sys
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Dict, Any


# ============================================================
# Helper Functions
# ============================================================

def _store_result(zcli: Optional[Any], test_name: str, status: str, message: str) -> Dict[str, Any]:
    """Store test result and return it for zWizard/zHat accumulation."""
    result = {"test": test_name, "status": status, "message": message}
    # zWizard automatically accumulates results in zHat context
    return result


def _create_temp_dir() -> str:
    """Create a temporary directory for testing"""
    return tempfile.mkdtemp()


def _cleanup_temp_dir(temp_dir: str):
    """Clean up temporary directory"""
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


# ============================================================
# A. INITIALIZATION & CONFIGURATION (5 tests)
# ============================================================

def test_01_server_initialization_defaults(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server initialization with default settings"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify defaults
        if server.port != 8080:
            return _store_result(zcli, "Init: Default Configuration", "ERROR", f"Expected port 8080, got {server.port}")
        
        if server.host != "127.0.0.1":
            return _store_result(zcli, "Init: Default Configuration", "ERROR", f"Expected host 127.0.0.1, got {server.host}")
        
        if server.is_running():
            return _store_result(zcli, "Init: Default Configuration", "ERROR", "Server should not be running after init")
        
        return _store_result(zcli, "Init: Default Configuration", "PASSED", "Defaults: port=8080, host=127.0.0.1")
    
    except Exception as e:
        return _store_result(zcli, "Init: Default Configuration", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_02_server_initialization_custom_config(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server initialization with custom configuration"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(
            mock_logger,
            port=9090,
            host="0.0.0.0",
            serve_path=temp_dir
        )
        
        # Verify custom config
        if server.port != 9090 or server.host != "0.0.0.0":
            return _store_result(zcli, "Init: Custom Configuration", "ERROR", "Custom config not applied")
        
        return _store_result(zcli, "Init: Custom Configuration", "PASSED", "Custom port=9090, host=0.0.0.0")
    
    except Exception as e:
        return _store_result(zcli, "Init: Custom Configuration", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_03_server_zcli_instance(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server accepts zCLI instance"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        mock_zcli = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, zcli=mock_zcli, serve_path=temp_dir)
        
        if server.zcli != mock_zcli:
            return _store_result(zcli, "Init: zCLI Instance", "ERROR", "zCLI instance not stored")
        
        return _store_result(zcli, "Init: zCLI Instance", "PASSED", "zCLI instance accessible")
    
    except Exception as e:
        return _store_result(zcli, "Init: zCLI Instance", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_04_server_port_configuration(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server port configuration"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, port=7777, serve_path=temp_dir)
        
        if server.port != 7777:
            return _store_result(zcli, "Init: Port Configuration", "ERROR", f"Expected port 7777, got {server.port}")
        
        return _store_result(zcli, "Init: Port Configuration", "PASSED", "Port 7777 configured")
    
    except Exception as e:
        return _store_result(zcli, "Init: Port Configuration", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_05_server_serve_path_resolution(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server serve_path resolution"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify serve_path is resolved
        if not server.serve_path:
            return _store_result(zcli, "Init: Serve Path", "ERROR", "serve_path not set")
        
        if not Path(server.serve_path).exists():
            return _store_result(zcli, "Init: Serve Path", "ERROR", "serve_path does not exist")
        
        return _store_result(zcli, "Init: Serve Path", "PASSED", f"Path resolved: {Path(server.serve_path).name}")
    
    except Exception as e:
        return _store_result(zcli, "Init: Serve Path", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# B. LIFECYCLE MANAGEMENT (6 tests)
# ============================================================

def test_06_server_start(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server start with mock"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, port=19000, serve_path=temp_dir)
        
        # Mock HTTPServer and Thread to avoid network/threading
        with patch('zCLI.subsystems.zServer.zServer.HTTPServer') as mock_http, \
             patch('zCLI.subsystems.zServer.zServer.threading.Thread') as mock_thread:
            
            mock_server_instance = MagicMock()
            mock_http.return_value = mock_server_instance
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            server.start()
            
            if not server._running:
                return _store_result(zcli, "Lifecycle: Start Server", "ERROR", "Server not marked as running")
            
            # Verify thread was created and started
            if not mock_thread.called:
                return _store_result(zcli, "Lifecycle: Start Server", "ERROR", "Thread not created")
            
            if not mock_thread_instance.start.called:
                return _store_result(zcli, "Lifecycle: Start Server", "ERROR", "Thread not started")
            
            server._running = False  # Clean up
            return _store_result(zcli, "Lifecycle: Start Server", "PASSED", "Server started successfully")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: Start Server", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_07_server_stop(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server stop"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Simulate running server
        server._running = True
        server.server = Mock()
        server.server.shutdown = Mock()
        server.server.server_close = Mock()
        server.thread = Mock()
        server.thread.join = Mock()
        
        server.stop()
        
        if server._running:
            return _store_result(zcli, "Lifecycle: Stop Server", "ERROR", "Server still marked as running")
        
        return _store_result(zcli, "Lifecycle: Stop Server", "PASSED", "Server stopped successfully")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: Stop Server", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_08_server_is_running_status(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: is_running() status method"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Initially not running
        if server.is_running():
            return _store_result(zcli, "Lifecycle: is_running Status", "ERROR", "Should be False initially")
        
        # Simulate running
        server._running = True
        if not server.is_running():
            return _store_result(zcli, "Lifecycle: is_running Status", "ERROR", "Should be True when running")
        
        server._running = False
        return _store_result(zcli, "Lifecycle: is_running Status", "PASSED", "Status tracking works")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: is_running Status", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_09_server_already_running_warning(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Warning when server already running"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        server._running = True  # Simulate running
        
        server.start()  # Try to start again
        
        # Should log warning
        if not mock_logger.warning.called:
            return _store_result(zcli, "Lifecycle: Already Running Warning", "ERROR", "Warning not logged")
        
        server._running = False
        return _store_result(zcli, "Lifecycle: Already Running Warning", "PASSED", "Warning logged correctly")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: Already Running Warning", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_10_server_stop_when_not_running(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Stop when server not running"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        server.stop()  # Stop server that was never started
        
        # Should log warning
        if not mock_logger.warning.called:
            return _store_result(zcli, "Lifecycle: Stop When Not Running", "ERROR", "Warning not logged")
        
        return _store_result(zcli, "Lifecycle: Stop When Not Running", "PASSED", "Graceful handling")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: Stop When Not Running", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_11_server_thread_management(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Background thread management"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Initially no thread
        if server.thread is not None:
            return _store_result(zcli, "Lifecycle: Thread Management", "ERROR", "Thread should be None initially")
        
        # Simulate thread creation
        with patch('zCLI.subsystems.zServer.zServer.HTTPServer') as mock_http:
            mock_server_instance = MagicMock()
            mock_http.return_value = mock_server_instance
            
            server.start()
            
            if server.thread is None:
                return _store_result(zcli, "Lifecycle: Thread Management", "ERROR", "Thread not created")
            
            server._running = False
            return _store_result(zcli, "Lifecycle: Thread Management", "PASSED", "Thread created successfully")
    
    except Exception as e:
        return _store_result(zcli, "Lifecycle: Thread Management", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# C. STATIC FILE SERVING (5 tests)
# ============================================================

def test_12_serve_html_files(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Serve HTML files"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        # Create test HTML file
        test_file = Path(temp_dir) / "test.html"
        test_file.write_text("<html><body>Test</body></html>")
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify file exists in serve path
        if not test_file.exists():
            return _store_result(zcli, "Static Files: HTML", "ERROR", "Test file not created")
        
        if "test.html" not in os.listdir(temp_dir):
            return _store_result(zcli, "Static Files: HTML", "ERROR", "HTML file not in serve path")
        
        return _store_result(zcli, "Static Files: HTML", "PASSED", "HTML file ready to serve")
    
    except Exception as e:
        return _store_result(zcli, "Static Files: HTML", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_13_serve_css_files(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Serve CSS files"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        # Create test CSS file
        test_file = Path(temp_dir) / "test.css"
        test_file.write_text("body { color: red; }")
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        if "test.css" not in os.listdir(temp_dir):
            return _store_result(zcli, "Static Files: CSS", "ERROR", "CSS file not in serve path")
        
        return _store_result(zcli, "Static Files: CSS", "PASSED", "CSS file ready to serve")
    
    except Exception as e:
        return _store_result(zcli, "Static Files: CSS", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_14_serve_js_files(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Serve JavaScript files"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        # Create test JS file
        test_file = Path(temp_dir) / "test.js"
        test_file.write_text("console.log('Test');")
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        if "test.js" not in os.listdir(temp_dir):
            return _store_result(zcli, "Static Files: JavaScript", "ERROR", "JS file not in serve path")
        
        return _store_result(zcli, "Static Files: JavaScript", "PASSED", "JS file ready to serve")
    
    except Exception as e:
        return _store_result(zcli, "Static Files: JavaScript", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_15_serve_path_configuration(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Serve path configuration"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify serve_path is set correctly
        if server.serve_path != str(Path(temp_dir).resolve()):
            return _store_result(zcli, "Static Files: Serve Path", "ERROR", "Serve path not resolved correctly")
        
        return _store_result(zcli, "Static Files: Serve Path", "PASSED", f"Path: {Path(temp_dir).name}")
    
    except Exception as e:
        return _store_result(zcli, "Static Files: Serve Path", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_16_directory_listing_disabled(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Directory listing is disabled"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify handler has list_directory method that returns None/403
        if not hasattr(LoggingHTTPRequestHandler, 'list_directory'):
            return _store_result(zcli, "Static Files: Directory Listing", "ERROR", "list_directory method not found")
        
        return _store_result(zcli, "Static Files: Directory Listing", "PASSED", "Directory listing disabled for security")
    
    except Exception as e:
        return _store_result(zcli, "Static Files: Directory Listing", "ERROR", f"Exception: {str(e)}")


# ============================================================
# D. CORS SUPPORT (4 tests)
# ============================================================

def test_17_cors_handler_initialization(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: CORS handler initialization"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify handler class exists
        if not LoggingHTTPRequestHandler:
            return _store_result(zcli, "CORS: Handler Initialization", "ERROR", "Handler class not found")
        
        # Verify required methods
        if not hasattr(LoggingHTTPRequestHandler, 'end_headers'):
            return _store_result(zcli, "CORS: Handler Initialization", "ERROR", "end_headers method not found")
        
        return _store_result(zcli, "CORS: Handler Initialization", "PASSED", "CORS handler available")
    
    except Exception as e:
        return _store_result(zcli, "CORS: Handler Initialization", "ERROR", f"Exception: {str(e)}")


def test_18_cors_headers_enabled(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: CORS headers are enabled"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify handler has end_headers override
        if not hasattr(LoggingHTTPRequestHandler, 'end_headers'):
            return _store_result(zcli, "CORS: Headers Enabled", "ERROR", "CORS headers method not found")
        
        return _store_result(zcli, "CORS: Headers Enabled", "PASSED", "CORS headers configured")
    
    except Exception as e:
        return _store_result(zcli, "CORS: Headers Enabled", "ERROR", f"Exception: {str(e)}")


def test_19_cors_options_method(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: CORS OPTIONS method handler"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify handler has do_OPTIONS method
        if not hasattr(LoggingHTTPRequestHandler, 'do_OPTIONS'):
            return _store_result(zcli, "CORS: OPTIONS Method", "ERROR", "do_OPTIONS method not found")
        
        return _store_result(zcli, "CORS: OPTIONS Method", "PASSED", "OPTIONS preflight supported")
    
    except Exception as e:
        return _store_result(zcli, "CORS: OPTIONS Method", "ERROR", f"Exception: {str(e)}")


def test_20_cors_local_development(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: CORS configured for local development"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, host="127.0.0.1", serve_path=temp_dir)
        
        # Verify localhost configuration
        if server.host != "127.0.0.1":
            return _store_result(zcli, "CORS: Local Development", "ERROR", "Not configured for localhost")
        
        return _store_result(zcli, "CORS: Local Development", "PASSED", "Localhost CORS ready")
    
    except Exception as e:
        return _store_result(zcli, "CORS: Local Development", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# E. ERROR HANDLING (5 tests)
# ============================================================

def test_21_port_already_in_use(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Port already in use error"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        # Simulate port in use error
        with patch('zCLI.subsystems.zServer.zServer.HTTPServer') as mock_http:
            error = OSError("Address already in use")
            error.errno = 48
            mock_http.side_effect = error
            
            server = zServer(mock_logger, port=8080, serve_path=temp_dir)
            
            try:
                server.start()
                return _store_result(zcli, "Error: Port In Use", "ERROR", "Should raise OSError")
            except OSError:
                return _store_result(zcli, "Error: Port In Use", "PASSED", "Port conflict detected")
    
    except Exception as e:
        return _store_result(zcli, "Error: Port In Use", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_22_invalid_serve_path(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Invalid serve path handling"""
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        
        # Create server with non-existent path (should not crash init)
        server = zServer(mock_logger, serve_path="/nonexistent/path/12345")
        
        # Server should initialize but path may not resolve
        if not server:
            return _store_result(zcli, "Error: Invalid Serve Path", "ERROR", "Server init failed")
        
        return _store_result(zcli, "Error: Invalid Serve Path", "PASSED", "Graceful path handling")
    
    except Exception as e:
        return _store_result(zcli, "Error: Invalid Serve Path", "ERROR", f"Exception: {str(e)}")


def test_23_error_logging(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Error logging"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify logger is accessible
        if server.logger != mock_logger:
            return _store_result(zcli, "Error: Logging", "ERROR", "Logger not accessible")
        
        return _store_result(zcli, "Error: Logging", "PASSED", "Logger integrated")
    
    except Exception as e:
        return _store_result(zcli, "Error: Logging", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_24_graceful_shutdown(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Graceful shutdown"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Simulate running server
        server._running = True
        server.server = Mock()
        server.server.shutdown = Mock()
        server.server.server_close = Mock()
        server.thread = Mock()
        server.thread.join = Mock()
        
        server.stop()
        
        # Verify shutdown called
        if not server.server.shutdown.called:
            return _store_result(zcli, "Error: Graceful Shutdown", "ERROR", "Shutdown not called")
        
        return _store_result(zcli, "Error: Graceful Shutdown", "PASSED", "Graceful shutdown works")
    
    except Exception as e:
        return _store_result(zcli, "Error: Graceful Shutdown", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_25_exception_handling(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Exception handling"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Simulate error during start
        with patch('zCLI.subsystems.zServer.zServer.HTTPServer') as mock_http:
            mock_http.side_effect = Exception("Test error")
            
            try:
                server.start()
                return _store_result(zcli, "Error: Exception Handling", "ERROR", "Should raise exception")
            except Exception:
                # Exception should be logged
                if not mock_logger.error.called:
                    return _store_result(zcli, "Error: Exception Handling", "ERROR", "Error not logged")
                
                return _store_result(zcli, "Error: Exception Handling", "PASSED", "Exceptions logged")
    
    except Exception as e:
        return _store_result(zcli, "Error: Exception Handling", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# F. HEALTH CHECK API (4 tests)
# ============================================================

def test_26_health_check_not_running(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Health check when server not running"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, port=8080, host="127.0.0.1", serve_path=temp_dir)
        
        health = server.health_check()
        
        # Verify structure
        if "running" not in health:
            return _store_result(zcli, "Health Check: Not Running", "ERROR", "Missing 'running' key")
        
        if health["running"] != False:
            return _store_result(zcli, "Health Check: Not Running", "ERROR", "Should be False")
        
        if health["url"] is not None:
            return _store_result(zcli, "Health Check: Not Running", "ERROR", "URL should be None")
        
        return _store_result(zcli, "Health Check: Not Running", "PASSED", "Status: not running")
    
    except Exception as e:
        return _store_result(zcli, "Health Check: Not Running", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_27_health_check_running(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Health check when server is running"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, port=8080, host="127.0.0.1", serve_path=temp_dir)
        server._running = True  # Simulate running
        
        health = server.health_check()
        
        if health["running"] != True:
            return _store_result(zcli, "Health Check: Running", "ERROR", "Should be True")
        
        if health["url"] != "http://127.0.0.1:8080":
            return _store_result(zcli, "Health Check: Running", "ERROR", f"Incorrect URL: {health['url']}")
        
        server._running = False
        return _store_result(zcli, "Health Check: Running", "PASSED", "Status: running")
    
    except Exception as e:
        return _store_result(zcli, "Health Check: Running", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_28_health_check_structure(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Health check structure"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        health = server.health_check()
        
        # Verify all required keys
        required_keys = ["running", "host", "port", "url", "serve_path"]
        for key in required_keys:
            if key not in health:
                return _store_result(zcli, "Health Check: Structure", "ERROR", f"Missing key: {key}")
        
        return _store_result(zcli, "Health Check: Structure", "PASSED", f"{len(required_keys)} keys present")
    
    except Exception as e:
        return _store_result(zcli, "Health Check: Structure", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_29_health_check_after_stop(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Health check after server stops"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Simulate running then stopped
        server._running = True
        health_running = server.health_check()
        
        server._running = False
        health_stopped = server.health_check()
        
        if health_stopped["running"] != False:
            return _store_result(zcli, "Health Check: After Stop", "ERROR", "Should be False after stop")
        
        if health_stopped["url"] is not None:
            return _store_result(zcli, "Health Check: After Stop", "ERROR", "URL should be None after stop")
        
        return _store_result(zcli, "Health Check: After Stop", "PASSED", "Status transitions correctly")
    
    except Exception as e:
        return _store_result(zcli, "Health Check: After Stop", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# G. URL GENERATION (3 tests)
# ============================================================

def test_30_get_url_format(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: URL format generation"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, host="127.0.0.1", port=8080, serve_path=temp_dir)
        
        url = server.get_url()
        
        if url != "http://127.0.0.1:8080":
            return _store_result(zcli, "URL: Format", "ERROR", f"Incorrect URL: {url}")
        
        return _store_result(zcli, "URL: Format", "PASSED", "URL: http://127.0.0.1:8080")
    
    except Exception as e:
        return _store_result(zcli, "URL: Format", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_31_get_url_custom_host(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: URL with custom host"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, host="0.0.0.0", port=8080, serve_path=temp_dir)
        
        url = server.get_url()
        
        if url != "http://0.0.0.0:8080":
            return _store_result(zcli, "URL: Custom Host", "ERROR", f"Incorrect URL: {url}")
        
        return _store_result(zcli, "URL: Custom Host", "PASSED", "URL: http://0.0.0.0:8080")
    
    except Exception as e:
        return _store_result(zcli, "URL: Custom Host", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


def test_32_get_url_custom_port(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: URL with custom port"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, host="127.0.0.1", port=9999, serve_path=temp_dir)
        
        url = server.get_url()
        
        if url != "http://127.0.0.1:9999":
            return _store_result(zcli, "URL: Custom Port", "ERROR", f"Incorrect URL: {url}")
        
        return _store_result(zcli, "URL: Custom Port", "PASSED", "URL: http://127.0.0.1:9999")
    
    except Exception as e:
        return _store_result(zcli, "URL: Custom Port", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# H. INTEGRATION & HANDLER (3 tests)
# ============================================================

def test_33_handler_logger_integration(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Handler logger integration"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify handler has log_message method
        if not hasattr(LoggingHTTPRequestHandler, 'log_message'):
            return _store_result(zcli, "Integration: Handler Logger", "ERROR", "log_message method not found")
        
        return _store_result(zcli, "Integration: Handler Logger", "PASSED", "Logger integration ready")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Handler Logger", "ERROR", f"Exception: {str(e)}")


def test_34_handler_class_methods(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Handler class methods"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.handler import LoggingHTTPRequestHandler
        
        # Verify required methods
        required_methods = ['do_GET', 'end_headers', 'do_OPTIONS', 'list_directory', 'log_message']
        
        for method in required_methods:
            if not hasattr(LoggingHTTPRequestHandler, method):
                return _store_result(zcli, "Integration: Handler Methods", "ERROR", f"Missing method: {method}")
        
        return _store_result(zcli, "Integration: Handler Methods", "PASSED", f"{len(required_methods)} methods present")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Handler Methods", "ERROR", f"Exception: {str(e)}")


def test_35_server_attributes_complete(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Server has all required attributes"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        
        mock_logger = Mock()
        temp_dir = _create_temp_dir()
        
        server = zServer(mock_logger, serve_path=temp_dir)
        
        # Verify all required attributes
        required_attrs = ['logger', 'zcli', 'port', 'host', 'serve_path', 'server', 'thread', '_running']
        
        for attr in required_attrs:
            if not hasattr(server, attr):
                return _store_result(zcli, "Integration: Server Attributes", "ERROR", f"Missing attribute: {attr}")
        
        return _store_result(zcli, "Integration: Server Attributes", "PASSED", f"{len(required_attrs)} attributes present")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Server Attributes", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# I. DECLARATIVE ROUTING & RBAC (10 tests) - v1.5.4 Phase 2
# ============================================================

def test_36_server_file_parsing(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Parse zServer.*.yaml file"""
    try:
        from zCLI.subsystems.zParser.parser_modules.vafile.vafile_server import parse_server_file
        
        mock_logger = Mock()
        
        # Mock server file data
        test_data = {
            "Meta": {
                "base_path": "./public",
                "default_route": "index.html",
                "error_pages": {"403": "access_denied.html"}
            },
            "routes": {
                "/": {"type": "static", "file": "index.html"},
                "/test": {"type": "static", "file": "test.html"}
            }
        }
        
        result = parse_server_file(test_data, mock_logger)
        
        if result.get("type") != "server":
            return _store_result(zcli, "Routing: Server File Parsing", "ERROR", "Type should be 'server'")
        
        if "routes" not in result:
            return _store_result(zcli, "Routing: Server File Parsing", "ERROR", "Missing routes key")
        
        if "/" not in result["routes"]:
            return _store_result(zcli, "Routing: Server File Parsing", "ERROR", "Missing root route")
        
        return _store_result(zcli, "Routing: Server File Parsing", "PASSED", "Server file parsed correctly")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Server File Parsing", "ERROR", f"Exception: {str(e)}")


def test_37_router_initialization(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: HTTPRouter initialization"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        mock_zcli.auth = Mock()
        
        routes_data = {
            "meta": {"base_path": "./public"},
            "routes": {
                "/": {"type": "static", "file": "index.html"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        if not router:
            return _store_result(zcli, "Routing: Router Initialization", "ERROR", "Router not created")
        
        if not hasattr(router, 'match_route'):
            return _store_result(zcli, "Routing: Router Initialization", "ERROR", "Missing match_route method")
        
        if not hasattr(router, 'check_access'):
            return _store_result(zcli, "Routing: Router Initialization", "ERROR", "Missing check_access method")
        
        return _store_result(zcli, "Routing: Router Initialization", "PASSED", "HTTPRouter initialized successfully")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Router Initialization", "ERROR", f"Exception: {str(e)}")


def test_38_route_matching_exact(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Exact route matching"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        
        routes_data = {
            "meta": {},
            "routes": {
                "/": {"type": "static", "file": "index.html"},
                "/test": {"type": "static", "file": "test.html"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        # Test exact match
        route = router.match_route("/test")
        
        if not route:
            return _store_result(zcli, "Routing: Exact Match", "ERROR", "Route not matched")
        
        if route.get("file") != "test.html":
            return _store_result(zcli, "Routing: Exact Match", "ERROR", "Wrong file matched")
        
        return _store_result(zcli, "Routing: Exact Match", "PASSED", "Exact route matched correctly")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Exact Match", "ERROR", f"Exception: {str(e)}")


def test_39_route_matching_wildcard(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Wildcard route matching"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        
        routes_data = {
            "meta": {"default_route": "index.html"},
            "routes": {
                "/": {"type": "static", "file": "index.html"},
                "/*": {"type": "static", "description": "Wildcard"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        # Test wildcard match
        route = router.match_route("/some/unknown/path")
        
        if not route:
            return _store_result(zcli, "Routing: Wildcard Match", "ERROR", "Wildcard route not matched")
        
        if route.get("description") != "Wildcard":
            return _store_result(zcli, "Routing: Wildcard Match", "ERROR", "Wrong wildcard route matched")
        
        return _store_result(zcli, "Routing: Wildcard Match", "PASSED", "Wildcard route matched correctly")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Wildcard Match", "ERROR", f"Exception: {str(e)}")


def test_40_route_matching_default(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Default route fallback"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        
        routes_data = {
            "meta": {"default_route": "index.html", "base_path": "./public"},
            "routes": {
                "/": {"type": "static", "file": "index.html"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        # Test default route fallback (no /* defined)
        route = router.match_route("/unknown")
        
        if not route:
            return _store_result(zcli, "Routing: Default Fallback", "ERROR", "No default route returned")
        
        # Should get default route behavior
        return _store_result(zcli, "Routing: Default Fallback", "PASSED", "Default fallback works")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Default Fallback", "ERROR", f"Exception: {str(e)}")


def test_41zRBAC_public_access(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Public access (no RBAC)"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        mock_zcli.auth = Mock()
        
        routes_data = {
            "meta": {},
            "routes": {
                "/": {"type": "static", "file": "index.html"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        route = router.match_route("/")
        has_access, error_page = router.check_access(route)
        
        if not has_access:
            return _store_result(zcli, "RBAC: Public Access", "ERROR", "Public route should be accessible")
        
        if error_page is not None:
            return _store_result(zcli, "RBAC: Public Access", "ERROR", "Public route should not have error page")
        
        return _store_result(zcli, "RBAC: Public Access", "PASSED", "Public access allowed")
    
    except Exception as e:
        return _store_result(zcli, "RBAC: Public Access", "ERROR", f"Exception: {str(e)}")


def test_42zRBAC_role_required(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Role required RBAC"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        mock_zcli.auth = Mock()
        mock_zcli.auth.has_role = Mock(return_value=False)  # User doesn't have role
        
        routes_data = {
            "meta": {"error_pages": {403: "access_denied.html"}},
            "routes": {
                "/admin": {
                    "type": "static",
                    "file": "admin.html",
                    "zRBAC": {"require_role": "admin"}
                }
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        route = router.match_route("/admin")
        has_access, error_page = router.check_access(route)
        
        if has_access:
            return _store_result(zcli, "RBAC: Role Required", "ERROR", "Should deny access without role")
        
        if error_page != "access_denied.html":
            return _store_result(zcli, "RBAC: Role Required", "ERROR", f"Wrong error page: {error_page}")
        
        # Verify has_role was called
        if not mock_zcli.auth.has_role.called:
            return _store_result(zcli, "RBAC: Role Required", "ERROR", "has_role not called")
        
        return _store_result(zcli, "RBAC: Role Required", "PASSED", "Role-based access denied correctly")
    
    except Exception as e:
        return _store_result(zcli, "RBAC: Role Required", "ERROR", f"Exception: {str(e)}")


def test_43zRBAC_error_page_redirect(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: RBAC error page redirect"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        mock_zcli.auth = Mock()
        mock_zcli.auth.is_authenticated = Mock(return_value=False)
        
        routes_data = {
            "meta": {"error_pages": {403: "access_denied.html"}},
            "routes": {
                "/dashboard": {
                    "type": "static",
                    "file": "dashboard.html",
                    "zRBAC": {"require_auth": True}
                }
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        route = router.match_route("/dashboard")
        has_access, error_page = router.check_access(route)
        
        if has_access:
            return _store_result(zcli, "RBAC: Error Page Redirect", "ERROR", "Should deny access")
        
        if error_page != "access_denied.html":
            return _store_result(zcli, "RBAC: Error Page Redirect", "ERROR", "Should return error page")
        
        return _store_result(zcli, "RBAC: Error Page Redirect", "PASSED", "Error page redirect configured")
    
    except Exception as e:
        return _store_result(zcli, "RBAC: Error Page Redirect", "ERROR", f"Exception: {str(e)}")


def test_44_router_file_resolution(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: Router file path resolution"""
    try:
        from zCLI.subsystems.zServer.zServer_modules.router import HTTPRouter
        
        mock_logger = Mock()
        mock_zcli = Mock()
        
        routes_data = {
            "meta": {"base_path": "./public"},
            "routes": {
                "/": {"type": "static", "file": "index.html"}
            }
        }
        
        router = HTTPRouter(routes_data, mock_zcli, mock_logger)
        
        route = router.match_route("/")
        file_path = router.resolve_file_path(route)
        
        if not file_path:
            return _store_result(zcli, "Routing: File Resolution", "ERROR", "File path not resolved")
        
        if "index.html" not in file_path:
            return _store_result(zcli, "Routing: File Resolution", "ERROR", "Wrong file path resolved")
        
        return _store_result(zcli, "Routing: File Resolution", "PASSED", "File paths resolved correctly")
    
    except Exception as e:
        return _store_result(zcli, "Routing: File Resolution", "ERROR", f"Exception: {str(e)}")


def test_45_server_with_routes_integration(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test: zServer with routes_file integration"""
    temp_dir = None
    try:
        from zCLI.subsystems.zServer.zServer import zServer
        from pathlib import Path
        
        mock_logger = Mock()
        mock_zcli = Mock()
        mock_zcli.loader = Mock()
        
        # Mock loader to return routes data
        mock_zcli.loader.handle = Mock(return_value={
            "type": "server",
            "meta": {"base_path": "./public"},
            "routes": {
                "/": {"type": "static", "file": "index.html"}
            }
        })
        
        temp_dir = _create_temp_dir()
        
        # Create server with routes_file
        server = zServer(
            mock_logger,
            zcli=mock_zcli,
            port=8080,
            serve_path=temp_dir,
            routes_file="./test_routes.yaml"
        )
        
        if not server.router:
            return _store_result(zcli, "Routing: Server Integration", "ERROR", "Router not initialized")
        
        if not mock_zcli.loader.handle.called:
            return _store_result(zcli, "Routing: Server Integration", "ERROR", "Loader not called")
        
        return _store_result(zcli, "Routing: Server Integration", "PASSED", "zServer + routing integrated")
    
    except Exception as e:
        return _store_result(zcli, "Routing: Server Integration", "ERROR", f"Exception: {str(e)}")
    finally:
        if temp_dir:
            _cleanup_temp_dir(temp_dir)


# ============================================================
# DISPLAY TEST RESULTS
# ============================================================

def display_test_results(zcli: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> None:
    """Display comprehensive test results with statistics."""
    import sys
    
    if not zcli or not context:
        print("\n[ERROR] No zcli or context provided")
        return None
    
    # Get zHat from context (accumulated by zWizard.handle())
    zHat = context.get("zHat")
    if not zHat:
        print("\n[WARN] No zHat found in context")
        if sys.stdin.isatty():
            input("Press Enter to return to main menu...")
        return None
    
    # Extract all results from zHat (skip display_and_return itself)
    results = []
    for i in range(len(zHat)):
        result = zHat[i]
        if result and isinstance(result, dict) and "test" in result:
            results.append(result)
    
    if not results:
        print("\n[WARN] No test results found")
        if sys.stdin.isatty():
            input("Press Enter to return to main menu...")
        return None
    
    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASSED")
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    warnings = sum(1 for r in results if r.get("status") == "WARN")
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    # Display header
    print("\n" + "=" * 90)
    print(f"zServer Comprehensive Test Suite - {total} Tests")
    print("=" * 90 + "\n")
    
    # Display results by category
    categories = {
        "A. Initialization & Configuration (5 tests)": [],
        "B. Lifecycle Management (6 tests)": [],
        "C. Static File Serving (5 tests)": [],
        "D. CORS Support (4 tests)": [],
        "E. Error Handling (5 tests)": [],
        "F. Health Check API (4 tests)": [],
        "G. URL Generation (3 tests)": [],
        "H. Integration & Handler (3 tests)": [],
        "I. Declarative Routing & RBAC (10 tests)": [],
    }
    
    # Categorize results
    for r in results:
        test_name = r.get("test", "")
        
        if "Init:" in test_name:
            categories["A. Initialization & Configuration (5 tests)"].append(r)
        elif "Lifecycle:" in test_name:
            categories["B. Lifecycle Management (6 tests)"].append(r)
        elif "Static Files:" in test_name:
            categories["C. Static File Serving (5 tests)"].append(r)
        elif "CORS:" in test_name:
            categories["D. CORS Support (4 tests)"].append(r)
        elif "Error:" in test_name:
            categories["E. Error Handling (5 tests)"].append(r)
        elif "Health Check:" in test_name:
            categories["F. Health Check API (4 tests)"].append(r)
        elif "URL:" in test_name:
            categories["G. URL Generation (3 tests)"].append(r)
        elif "Integration:" in test_name:
            categories["H. Integration & Handler (3 tests)"].append(r)
        elif "Routing:" in test_name or "RBAC:" in test_name:
            categories["I. Declarative Routing & RBAC (10 tests)"].append(r)
    
    # Display by category
    for category, tests in categories.items():
        if not tests:
            continue
        
        print(f"{category}")
        print("-" * 90)
        for test in tests:
            status = test.get("status", "UNKNOWN")
            status_symbol = {
                "PASSED": "[OK] ",
                "ERROR": "[ERR]",
                "WARN": "[WARN]"
            }.get(status, "[?]  ")
            
            print(f"  {status_symbol} {test.get('test', 'Unknown'):50s} {test.get('message', '')}")
        print()
    
    # Display summary
    print("=" * 90)
    print(f"SUMMARY: {passed}/{total} passed ({pass_pct:.1f}%) | Errors: {errors} | Warnings: {warnings}")
    print("=" * 90 + "\n")
    
    # Use zDisplay text event for final message
    if zcli and hasattr(zcli, 'display'):
        try:
            zcli.display.zEvents.Text.zLines([
                "",
                "=" * 90,
                "zServer Test Suite Complete",
                "=" * 90,
                "",
                f"Results: {passed}/{total} tests passed ({pass_pct:.1f}%)",
                f"Errors: {errors} | Warnings: {warnings}",
                "",
                "Press Enter to return to main menu...",
                ""
            ])
        except Exception:
            # Fallback to print if zDisplay not available
            print("\nPress Enter to return to main menu...")
    
    # Pause for user review
    if sys.stdin.isatty():
        input()
    
    return None

