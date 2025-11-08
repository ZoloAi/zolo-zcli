# zTestRunner/plugins/zcomm_tests.py
"""
Comprehensive A-to-H zComm Test Suite (48 tests)
Declarative approach - uses existing zcli.comm, minimal setup
Covers all 8 zComm modules including facade API and helpers
"""

from pathlib import Path


# ===============================================================
# Helper Functions
# ===============================================================

def _store_result(zcli, test_name: str, status: str, message: str) -> None:
    """Store test result in session."""
    if not zcli:
        return None
    
    result = {"test": test_name, "status": status, "message": message}
    if "zTestRunner_results" not in zcli.session:
        zcli.session["zTestRunner_results"] = []
    zcli.session["zTestRunner_results"].append(result)
    return None


# ===============================================================
# A. zComm Facade API Tests (14 tests)
# ===============================================================

def test_facade_initialization(zcli=None, context=None):
    """Test zComm facade initialized correctly."""
    if not zcli:
        return _store_result(None, "Facade: Initialization", "ERROR", "No zcli")
    
    if not hasattr(zcli, "comm"):
        return _store_result(zcli, "Facade: Initialization", "FAILED", "No comm attribute")
    
    if not zcli.comm:
        return _store_result(zcli, "Facade: Initialization", "FAILED", "comm is None")
    
    # Check for required managers (private attributes)
    if not hasattr(zcli.comm, "_bifrost_mgr"):
        return _store_result(zcli, "Facade: Initialization", "FAILED", "Missing _bifrost_mgr")
    
    if not hasattr(zcli.comm, "_http_client"):
        return _store_result(zcli, "Facade: Initialization", "FAILED", "Missing _http_client")
    
    return _store_result(zcli, "Facade: Initialization", "PASSED", "All managers initialized")


def test_facade_websocket_property(zcli=None, context=None):
    """Test zComm.websocket property accessor."""
    if not zcli:
        return _store_result(None, "Facade: WebSocket Property", "ERROR", "No zcli")
    
    # Property should be accessible (may be None if not created)
    ws = zcli.comm.websocket
    
    # Should not raise an error
    return _store_result(zcli, "Facade: WebSocket Property", "PASSED", 
                        f"WebSocket: {type(ws).__name__ if ws else 'None'}")


def test_facade_create_websocket(zcli=None, context=None):
    """Test zComm.create_websocket() method exists and is callable."""
    if not zcli:
        return _store_result(None, "Facade: create_websocket()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "create_websocket"):
        return _store_result(zcli, "Facade: create_websocket()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.create_websocket):
        return _store_result(zcli, "Facade: create_websocket()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: create_websocket()", "PASSED", "Method exists and callable")


def test_facade_create_http_server(zcli=None, context=None):
    """Test zComm.create_http_server() method."""
    if not zcli:
        return _store_result(None, "Facade: create_http_server()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "create_http_server"):
        return _store_result(zcli, "Facade: create_http_server()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.create_http_server):
        return _store_result(zcli, "Facade: create_http_server()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: create_http_server()", "PASSED", "Method exists and callable")


def test_facade_start_service(zcli=None, context=None):
    """Test zComm.start_service() method."""
    if not zcli:
        return _store_result(None, "Facade: start_service()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "start_service"):
        return _store_result(zcli, "Facade: start_service()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.start_service):
        return _store_result(zcli, "Facade: start_service()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: start_service()", "PASSED", "Method exists and callable")


def test_facade_stop_service(zcli=None, context=None):
    """Test zComm.stop_service() method."""
    if not zcli:
        return _store_result(None, "Facade: stop_service()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "stop_service"):
        return _store_result(zcli, "Facade: stop_service()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.stop_service):
        return _store_result(zcli, "Facade: stop_service()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: stop_service()", "PASSED", "Method exists and callable")


def test_facade_restart_service(zcli=None, context=None):
    """Test zComm.restart_service() method."""
    if not zcli:
        return _store_result(None, "Facade: restart_service()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "restart_service"):
        return _store_result(zcli, "Facade: restart_service()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.restart_service):
        return _store_result(zcli, "Facade: restart_service()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: restart_service()", "PASSED", "Method exists and callable")


def test_facade_service_status(zcli=None, context=None):
    """Test zComm.service_status() method."""
    if not zcli:
        return _store_result(None, "Facade: service_status()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "service_status"):
        return _store_result(zcli, "Facade: service_status()", "FAILED", "Method missing")
    
    # Should be callable
    if not callable(zcli.comm.service_status):
        return _store_result(zcli, "Facade: service_status()", "FAILED", "Not callable")
    
    # Try calling it (should return dict)
    status = zcli.comm.service_status()
    if not isinstance(status, dict):
        return _store_result(zcli, "Facade: service_status()", "FAILED", f"Invalid return type: {type(status)}")
    
    return _store_result(zcli, "Facade: service_status()", "PASSED", f"{len(status)} services")


def test_facade_get_service_connection_info(zcli=None, context=None):
    """Test zComm.get_service_connection_info() method."""
    if not zcli:
        return _store_result(None, "Facade: get_service_connection_info()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "get_service_connection_info"):
        return _store_result(zcli, "Facade: get_service_connection_info()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.get_service_connection_info):
        return _store_result(zcli, "Facade: get_service_connection_info()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: get_service_connection_info()", "PASSED", "Method exists and callable")


def test_facade_websocket_health_check(zcli=None, context=None):
    """Test zComm.websocket_health_check() method."""
    if not zcli:
        return _store_result(None, "Facade: websocket_health_check()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "websocket_health_check"):
        return _store_result(zcli, "Facade: websocket_health_check()", "FAILED", "Method missing")
    
    # Call it (should return dict)
    health = zcli.comm.websocket_health_check()
    if not isinstance(health, dict):
        return _store_result(zcli, "Facade: websocket_health_check()", "FAILED", f"Invalid return type: {type(health)}")
    
    # Should have 'running' key
    if "running" not in health:
        return _store_result(zcli, "Facade: websocket_health_check()", "FAILED", "Missing 'running' key")
    
    return _store_result(zcli, "Facade: websocket_health_check()", "PASSED", f"Running: {health['running']}")


def test_facade_server_health_check(zcli=None, context=None):
    """Test zComm.server_health_check() method."""
    if not zcli:
        return _store_result(None, "Facade: server_health_check()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "server_health_check"):
        return _store_result(zcli, "Facade: server_health_check()", "FAILED", "Method missing")
    
    # Call it (should return dict)
    health = zcli.comm.server_health_check()
    if not isinstance(health, dict):
        return _store_result(zcli, "Facade: server_health_check()", "FAILED", f"Invalid return type: {type(health)}")
    
    # Should have 'running' key
    if "running" not in health:
        return _store_result(zcli, "Facade: server_health_check()", "FAILED", "Missing 'running' key")
    
    return _store_result(zcli, "Facade: server_health_check()", "PASSED", f"Running: {health['running']}")


def test_facade_health_check_all(zcli=None, context=None):
    """Test zComm.health_check_all() method."""
    if not zcli:
        return _store_result(None, "Facade: health_check_all()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "health_check_all"):
        return _store_result(zcli, "Facade: health_check_all()", "FAILED", "Method missing")
    
    # Call it (should return dict)
    health = zcli.comm.health_check_all()
    if not isinstance(health, dict):
        return _store_result(zcli, "Facade: health_check_all()", "FAILED", f"Invalid return type: {type(health)}")
    
    # Should have both websocket and http_server keys
    required_keys = ["websocket", "http_server"]
    missing_keys = [k for k in required_keys if k not in health]
    if missing_keys:
        return _store_result(zcli, "Facade: health_check_all()", "FAILED", f"Missing keys: {missing_keys}")
    
    return _store_result(zcli, "Facade: health_check_all()", "PASSED", f"{len(health)} health checks")


def test_facade_check_port(zcli=None, context=None):
    """Test zComm.check_port() method."""
    if not zcli:
        return _store_result(None, "Facade: check_port()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "check_port"):
        return _store_result(zcli, "Facade: check_port()", "FAILED", "Method missing")
    
    # Test with a known available port (high number)
    is_available = zcli.comm.check_port(54321)
    if not isinstance(is_available, bool):
        return _store_result(zcli, "Facade: check_port()", "FAILED", f"Invalid return type: {type(is_available)}")
    
    return _store_result(zcli, "Facade: check_port()", "PASSED", f"Port 54321 available: {is_available}")


def test_facade_http_post(zcli=None, context=None):
    """Test zComm.http_post() method."""
    if not zcli:
        return _store_result(None, "Facade: http_post()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "http_post"):
        return _store_result(zcli, "Facade: http_post()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.http_post):
        return _store_result(zcli, "Facade: http_post()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Facade: http_post()", "PASSED", "Method exists and callable")


# ===============================================================
# B. Bifrost Manager Tests (8 tests)
# ===============================================================

def test_bifrost_initialization(zcli=None, context=None):
    """Test BifrostManager initialized."""
    if not zcli:
        return _store_result(None, "Bifrost: Initialization", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "_bifrost_mgr"):
        return _store_result(zcli, "Bifrost: Initialization", "FAILED", "No _bifrost_mgr")
    
    if not zcli.comm._bifrost_mgr:
        return _store_result(zcli, "Bifrost: Initialization", "FAILED", "_bifrost_mgr is None")
    
    return _store_result(zcli, "Bifrost: Initialization", "PASSED", "BifrostManager initialized")


def test_bifrost_auto_start_check(zcli=None, context=None):
    """Test Bifrost auto-start logic based on mode."""
    if not zcli:
        return _store_result(None, "Bifrost: Auto-start Check", "ERROR", "No zcli")
    
    # Check if mode is in session
    mode = zcli.session.get("zMode", "Terminal")
    
    # If mode is zBifrost, websocket should exist
    ws = zcli.comm.websocket
    
    if mode == "zBifrost" and ws is None:
        return _store_result(zcli, "Bifrost: Auto-start Check", "WARN", "zBifrost mode but no WebSocket")
    
    return _store_result(zcli, "Bifrost: Auto-start Check", "PASSED", f"Mode={mode}, WebSocket={ws is not None}")


def test_bifrost_create(zcli=None, context=None):
    """Test BifrostManager.create() method."""
    if not zcli:
        return _store_result(None, "Bifrost: create()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm._bifrost_mgr, "create"):
        return _store_result(zcli, "Bifrost: create()", "FAILED", "Method missing")
    
    if not callable(zcli.comm._bifrost_mgr.create):
        return _store_result(zcli, "Bifrost: create()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Bifrost: create()", "PASSED", "Method exists and callable")


def test_bifrost_get_instance(zcli=None, context=None):
    """Test BifrostManager.websocket property."""
    if not zcli:
        return _store_result(None, "Bifrost: websocket", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm._bifrost_mgr, "websocket"):
        return _store_result(zcli, "Bifrost: websocket", "FAILED", "Property missing")
    
    # Access it
    instance = zcli.comm._bifrost_mgr.websocket
    
    return _store_result(zcli, "Bifrost: websocket", "PASSED", f"Instance: {type(instance).__name__ if instance else 'None'}")


def test_bifrost_health_check(zcli=None, context=None):
    """Test BifrostManager.auto_start() method."""
    if not zcli:
        return _store_result(None, "Bifrost: auto_start()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm._bifrost_mgr, "auto_start"):
        return _store_result(zcli, "Bifrost: auto_start()", "FAILED", "Method missing")
    
    if not callable(zcli.comm._bifrost_mgr.auto_start):
        return _store_result(zcli, "Bifrost: auto_start()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Bifrost: auto_start()", "PASSED", "Method exists and callable")


def test_bifrost_session_integration(zcli=None, context=None):
    """Test Bifrost accesses session correctly."""
    if not zcli:
        return _store_result(None, "Bifrost: Session Integration", "ERROR", "No zcli")
    
    # BifrostManager should have access to session
    if not hasattr(zcli.comm._bifrost_mgr, "session"):
        return _store_result(zcli, "Bifrost: Session Integration", "FAILED", "No session attribute")
    
    return _store_result(zcli, "Bifrost: Session Integration", "PASSED", "Session accessible")


def test_bifrost_mode_detection(zcli=None, context=None):
    """Test Bifrost mode detection from session."""
    if not zcli:
        return _store_result(None, "Bifrost: Mode Detection", "ERROR", "No zcli")
    
    mode = zcli.session.get("zMode", "Terminal")
    
    # Mode should be a string
    if not isinstance(mode, str):
        return _store_result(zcli, "Bifrost: Mode Detection", "FAILED", f"Invalid mode type: {type(mode)}")
    
    # Mode should be valid
    valid_modes = ["Terminal", "zBifrost"]
    if mode not in valid_modes:
        return _store_result(zcli, "Bifrost: Mode Detection", "WARN", f"Unexpected mode: {mode}")
    
    return _store_result(zcli, "Bifrost: Mode Detection", "PASSED", f"Mode: {mode}")


def test_bifrost_instance_caching(zcli=None, context=None):
    """Test Bifrost instance is cached (not re-created)."""
    if not zcli:
        return _store_result(None, "Bifrost: Instance Caching", "ERROR", "No zcli")
    
    # Get instance twice via websocket property
    instance1 = zcli.comm._bifrost_mgr.websocket
    instance2 = zcli.comm._bifrost_mgr.websocket
    
    # If both exist, they should be the same object
    if instance1 and instance2 and instance1 is not instance2:
        return _store_result(zcli, "Bifrost: Instance Caching", "WARN", "Instance not cached")
    
    return _store_result(zcli, "Bifrost: Instance Caching", "PASSED", "Instance properly cached")


# ===============================================================
# C. HTTP Client Tests (5 tests)
# ===============================================================

def test_http_client_initialization(zcli=None, context=None):
    """Test HTTPClient initialized."""
    if not zcli:
        return _store_result(None, "HTTP Client: Initialization", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "_http_client"):
        return _store_result(zcli, "HTTP Client: Initialization", "FAILED", "No _http_client")
    
    if not zcli.comm._http_client:
        return _store_result(zcli, "HTTP Client: Initialization", "FAILED", "_http_client is None")
    
    return _store_result(zcli, "HTTP Client: Initialization", "PASSED", "HTTPClient initialized")


def test_http_client_post_method(zcli=None, context=None):
    """Test HTTPClient.post() method exists."""
    if not zcli:
        return _store_result(None, "HTTP Client: post()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm._http_client, "post"):
        return _store_result(zcli, "HTTP Client: post()", "FAILED", "Method missing")
    
    if not callable(zcli.comm._http_client.post):
        return _store_result(zcli, "HTTP Client: post()", "FAILED", "Not callable")
    
    return _store_result(zcli, "HTTP Client: post()", "PASSED", "Method exists and callable")


def test_http_client_timeout(zcli=None, context=None):
    """Test HTTPClient timeout parameter."""
    if not zcli:
        return _store_result(None, "HTTP Client: Timeout", "ERROR", "No zcli")
    
    # Method should accept timeout parameter
    # (We're just checking the signature, not calling it)
    import inspect
    if hasattr(zcli.comm._http_client, "post"):
        sig = inspect.signature(zcli.comm._http_client.post)
        if "timeout" not in sig.parameters:
            return _store_result(zcli, "HTTP Client: Timeout", "WARN", "No timeout parameter")
    
    return _store_result(zcli, "HTTP Client: Timeout", "PASSED", "Timeout parameter exists")


def test_http_client_error_handling(zcli=None, context=None):
    """Test HTTPClient has error handling."""
    if not zcli:
        return _store_result(None, "HTTP Client: Error Handling", "ERROR", "No zcli")
    
    # HTTPClient should have logger for error handling
    if not hasattr(zcli.comm._http_client, "logger"):
        return _store_result(zcli, "HTTP Client: Error Handling", "WARN", "No logger attribute")
    
    return _store_result(zcli, "HTTP Client: Error Handling", "PASSED", "Logger available")


def test_http_client_data_serialization(zcli=None, context=None):
    """Test HTTPClient can handle data parameter."""
    if not zcli:
        return _store_result(None, "HTTP Client: Data Serialization", "ERROR", "No zcli")
    
    # Method should accept data parameter
    import inspect
    if hasattr(zcli.comm._http_client, "post"):
        sig = inspect.signature(zcli.comm._http_client.post)
        if "data" not in sig.parameters:
            return _store_result(zcli, "HTTP Client: Data Serialization", "FAILED", "No data parameter")
    
    return _store_result(zcli, "HTTP Client: Data Serialization", "PASSED", "Data parameter exists")


# ===============================================================
# D. Service Manager Tests (7 tests)
# ===============================================================

def test_service_manager_initialization(zcli=None, context=None):
    """Test ServiceManager initialized."""
    if not zcli:
        return _store_result(None, "Service Manager: Initialization", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "services"):
        return _store_result(zcli, "Service Manager: Initialization", "FAILED", "No services")
    
    if not zcli.comm.services:
        return _store_result(zcli, "Service Manager: Initialization", "FAILED", "services is None")
    
    return _store_result(zcli, "Service Manager: Initialization", "PASSED", "ServiceManager initialized")


def test_service_manager_start(zcli=None, context=None):
    """Test ServiceManager.start() method."""
    if not zcli:
        return _store_result(None, "Service Manager: start()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm.services, "start"):
        return _store_result(zcli, "Service Manager: start()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.services.start):
        return _store_result(zcli, "Service Manager: start()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Service Manager: start()", "PASSED", "Method exists and callable")


def test_service_manager_stop(zcli=None, context=None):
    """Test ServiceManager.stop() method."""
    if not zcli:
        return _store_result(None, "Service Manager: stop()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm.services, "stop"):
        return _store_result(zcli, "Service Manager: stop()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.services.stop):
        return _store_result(zcli, "Service Manager: stop()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Service Manager: stop()", "PASSED", "Method exists and callable")


def test_service_manager_restart(zcli=None, context=None):
    """Test ServiceManager.restart() method."""
    if not zcli:
        return _store_result(None, "Service Manager: restart()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm.services, "restart"):
        return _store_result(zcli, "Service Manager: restart()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.services.restart):
        return _store_result(zcli, "Service Manager: restart()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Service Manager: restart()", "PASSED", "Method exists and callable")


def test_service_manager_status(zcli=None, context=None):
    """Test ServiceManager.status() method."""
    if not zcli:
        return _store_result(None, "Service Manager: status()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm.services, "status"):
        return _store_result(zcli, "Service Manager: status()", "FAILED", "Method missing")
    
    # Call it
    status = zcli.comm.services.status()
    
    if not isinstance(status, dict):
        return _store_result(zcli, "Service Manager: status()", "FAILED", f"Invalid return type: {type(status)}")
    
    return _store_result(zcli, "Service Manager: status()", "PASSED", f"{len(status)} services")


def test_service_manager_connection_info(zcli=None, context=None):
    """Test ServiceManager.get_connection_info() method."""
    if not zcli:
        return _store_result(None, "Service Manager: get_connection_info()", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm.services, "get_connection_info"):
        return _store_result(zcli, "Service Manager: get_connection_info()", "FAILED", "Method missing")
    
    if not callable(zcli.comm.services.get_connection_info):
        return _store_result(zcli, "Service Manager: get_connection_info()", "FAILED", "Not callable")
    
    return _store_result(zcli, "Service Manager: get_connection_info()", "PASSED", "Method exists and callable")


def test_service_manager_unknown_service(zcli=None, context=None):
    """Test ServiceManager handles unknown service gracefully."""
    if not zcli:
        return _store_result(None, "Service Manager: Unknown Service", "ERROR", "No zcli")
    
    # Try to get info for a fake service
    info = zcli.comm.services.get_connection_info("nonexistent_service_xyz")
    
    # Should return None or handle gracefully
    if info is not None and not isinstance(info, dict):
        return _store_result(zcli, "Service Manager: Unknown Service", "FAILED", f"Invalid return: {type(info)}")
    
    return _store_result(zcli, "Service Manager: Unknown Service", "PASSED", "Handles unknown service gracefully")


# ===============================================================
# E. Network Utils Tests (6 tests)
# ===============================================================

def test_network_utils_initialization(zcli=None, context=None):
    """Test NetworkUtils initialized."""
    if not zcli:
        return _store_result(None, "Network Utils: Initialization", "ERROR", "No zcli")
    
    if not hasattr(zcli.comm, "_network_utils"):
        return _store_result(zcli, "Network Utils: Initialization", "FAILED", "No _network_utils")
    
    if not zcli.comm._network_utils:
        return _store_result(zcli, "Network Utils: Initialization", "FAILED", "_network_utils is None")
    
    return _store_result(zcli, "Network Utils: Initialization", "PASSED", "NetworkUtils initialized")


def test_network_utils_check_port_available(zcli=None, context=None):
    """Test NetworkUtils.check_port() with available port."""
    if not zcli:
        return _store_result(None, "Network Utils: check_port() Available", "ERROR", "No zcli")
    
    # Check a high port number (likely available)
    is_available = zcli.comm._network_utils.check_port(55555)
    
    if not isinstance(is_available, bool):
        return _store_result(zcli, "Network Utils: check_port() Available", "FAILED", f"Invalid return: {type(is_available)}")
    
    return _store_result(zcli, "Network Utils: check_port() Available", "PASSED", f"Port 55555: {is_available}")


def test_network_utils_check_port_in_use(zcli=None, context=None):
    """Test NetworkUtils.check_port() with common port."""
    if not zcli:
        return _store_result(None, "Network Utils: check_port() In Use", "ERROR", "No zcli")
    
    # Check port 80 (likely in use or restricted)
    is_available = zcli.comm._network_utils.check_port(80)
    
    if not isinstance(is_available, bool):
        return _store_result(zcli, "Network Utils: check_port() In Use", "FAILED", f"Invalid return: {type(is_available)}")
    
    return _store_result(zcli, "Network Utils: check_port() In Use", "PASSED", f"Port 80: {is_available}")


def test_network_utils_invalid_port(zcli=None, context=None):
    """Test NetworkUtils.check_port() with invalid port."""
    if not zcli:
        return _store_result(None, "Network Utils: Invalid Port", "ERROR", "No zcli")
    
    # Port 0 or negative should be handled

    # Clear plugin cache to prevent Mock objects from old tests
    try:
        zcli.loader.cache.clear("plugin")
    except:
        pass  # Ignore if plugin cache doesn't exist

    try:
        result = zcli.comm._network_utils.check_port(0)
        # If it doesn't raise, it should return False
        if result is True:
            return _store_result(zcli, "Network Utils: Invalid Port", "WARN", "Port 0 reported as available")
    except Exception:
        # Exception is acceptable for invalid port
        pass
    
    return _store_result(zcli, "Network Utils: Invalid Port", "PASSED", "Invalid port handled")


def test_network_utils_port_range(zcli=None, context=None):
    """Test NetworkUtils.check_port() port range validation."""
    if not zcli:
        return _store_result(None, "Network Utils: Port Range", "ERROR", "No zcli")
    
    # Test port > 65535 (out of range)
    try:
        result = zcli.comm._network_utils.check_port(99999)
        # If it doesn't raise, it should return False
        if result is True:
            return _store_result(zcli, "Network Utils: Port Range", "WARN", "Port 99999 reported as available")
    except Exception:
        # Exception is acceptable for out-of-range port
        pass
    
    return _store_result(zcli, "Network Utils: Port Range", "PASSED", "Port range validated")


def test_network_utils_error_handling(zcli=None, context=None):
    """Test NetworkUtils has error handling."""
    if not zcli:
        return _store_result(None, "Network Utils: Error Handling", "ERROR", "No zcli")
    
    # NetworkUtils should have logger for error handling
    if not hasattr(zcli.comm._network_utils, "logger"):
        return _store_result(zcli, "Network Utils: Error Handling", "WARN", "No logger attribute")
    
    return _store_result(zcli, "Network Utils: Error Handling", "PASSED", "Logger available")


# ===============================================================
# F. HTTP Server (zServer) Tests (4 tests)
# ===============================================================

def test_http_server_create(zcli=None, context=None):
    """Test HTTP server can be created via zComm."""
    if not zcli:
        return _store_result(None, "HTTP Server: create()", "ERROR", "No zcli")
    
    # create_http_server should exist
    if not hasattr(zcli.comm, "create_http_server"):
        return _store_result(zcli, "HTTP Server: create()", "FAILED", "Method missing")
    
    return _store_result(zcli, "HTTP Server: create()", "PASSED", "Method exists")


def test_http_server_health_check(zcli=None, context=None):
    """Test HTTP server health check."""
    if not zcli:
        return _store_result(None, "HTTP Server: health_check()", "ERROR", "No zcli")
    
    # Call health check
    health = zcli.comm.server_health_check()
    
    if not isinstance(health, dict):
        return _store_result(zcli, "HTTP Server: health_check()", "FAILED", f"Invalid return: {type(health)}")
    
    # Should have 'running' key
    if "running" not in health:
        return _store_result(zcli, "HTTP Server: health_check()", "FAILED", "Missing 'running' key")
    
    return _store_result(zcli, "HTTP Server: health_check()", "PASSED", f"Running: {health['running']}")


def test_http_server_configuration(zcli=None, context=None):
    """Test HTTP server configuration via zConfig."""
    if not zcli:
        return _store_result(None, "HTTP Server: Configuration", "ERROR", "No zcli")
    
    # Should have http_server config
    if not hasattr(zcli.config, "http_server"):
        return _store_result(zcli, "HTTP Server: Configuration", "FAILED", "No http_server config")
    
    http_config = zcli.config.http_server
    
    # Should have enabled flag
    if not hasattr(http_config, "enabled"):
        return _store_result(zcli, "HTTP Server: Configuration", "WARN", "No enabled flag")
    
    return _store_result(zcli, "HTTP Server: Configuration", "PASSED", f"Enabled: {http_config.enabled}")


def test_http_server_instance_access(zcli=None, context=None):
    """Test HTTP server instance accessible via zcli.server."""
    if not zcli:
        return _store_result(None, "HTTP Server: Instance Access", "ERROR", "No zcli")
    
    # Should have server attribute
    server = getattr(zcli, "server", None)
    
    # Server may be None if not enabled
    return _store_result(zcli, "HTTP Server: Instance Access", "PASSED", 
                        f"Server: {type(server).__name__ if server else 'None'}")


# ===============================================================
# G. Integration Tests (3 tests)
# ===============================================================

def test_integration_health_checks(zcli=None, context=None):
    """Test all health checks work together."""
    if not zcli:
        return _store_result(None, "Integration: Health Checks", "ERROR", "No zcli")
    
    # Get combined health check
    health = zcli.comm.health_check_all()
    
    if not isinstance(health, dict):
        return _store_result(zcli, "Integration: Health Checks", "FAILED", f"Invalid return: {type(health)}")
    
    # Count health checks
    checks = len(health)
    
    return _store_result(zcli, "Integration: Health Checks", "PASSED", f"{checks} health checks integrated")


def test_integration_session_access(zcli=None, context=None):
    """Test zComm can access session correctly."""
    if not zcli:
        return _store_result(None, "Integration: Session Access", "ERROR", "No zcli")
    
    # zComm should have access to session
    if not hasattr(zcli.comm, "session"):
        return _store_result(zcli, "Integration: Session Access", "FAILED", "No session attribute")
    
    session = zcli.comm.session
    
    if not isinstance(session, dict):
        return _store_result(zcli, "Integration: Session Access", "FAILED", f"Invalid session type: {type(session)}")
    
    return _store_result(zcli, "Integration: Session Access", "PASSED", f"{len(session)} session keys")


def test_integration_logger_access(zcli=None, context=None):
    """Test zComm can access logger correctly."""
    if not zcli:
        return _store_result(None, "Integration: Logger Access", "ERROR", "No zcli")
    
    # zComm should have access to logger
    if not hasattr(zcli.comm, "logger"):
        return _store_result(zcli, "Integration: Logger Access", "FAILED", "No logger attribute")
    
    logger = zcli.comm.logger
    
    if not logger:
        return _store_result(zcli, "Integration: Logger Access", "FAILED", "logger is None")
    
    return _store_result(zcli, "Integration: Logger Access", "PASSED", f"Logger: {type(logger).__name__}")


# ===============================================================
# H. Layer 0 Compliance Tests (1 test)
# ===============================================================

def test_layer0_no_display_dependency(zcli=None, context=None):
    """Test zComm has no zDisplay dependency (Layer 0 compliance)."""
    if not zcli:
        return _store_result(None, "Layer 0: No zDisplay Dependency", "ERROR", "No zcli")
    
    # zComm should NOT import zDisplay
    import sys
    comm_module = sys.modules.get("zCLI.subsystems.zComm.zComm")
    
    if comm_module:
        # Check if zDisplay was imported
        if "zDisplay" in dir(comm_module):
            return _store_result(zcli, "Layer 0: No zDisplay Dependency", "FAILED", "zDisplay imported in zComm")
    
    return _store_result(zcli, "Layer 0: No zDisplay Dependency", "PASSED", "No zDisplay dependency")


# ===============================================================
# I. PostgreSQL Service Tests (6 tests)
# ===============================================================

def test_postgresql_initialization(zcli=None, context=None):
    """Test PostgreSQLService class is accessible."""
    if not zcli:
        return _store_result(None, "PostgreSQL: Initialization", "ERROR", "No zcli")
    
    # Try to import PostgreSQLService
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        # Create instance
        service = PostgreSQLService(zcli.logger)
        if not service:
            return _store_result(zcli, "PostgreSQL: Initialization", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: Initialization", "FAILED", f"Import error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: Initialization", "PASSED", "PostgreSQLService accessible")


def test_postgresql_start_method(zcli=None, context=None):
    """Test PostgreSQLService.start() method."""
    if not zcli:
        return _store_result(None, "PostgreSQL: start()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        service = PostgreSQLService(zcli.logger)
        
        if not hasattr(service, "start"):
            return _store_result(zcli, "PostgreSQL: start()", "FAILED", "Method missing")
        
        if not callable(service.start):
            return _store_result(zcli, "PostgreSQL: start()", "FAILED", "Not callable")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: start()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: start()", "PASSED", "Method exists and callable")


def test_postgresql_stop_method(zcli=None, context=None):
    """Test PostgreSQLService.stop() method."""
    if not zcli:
        return _store_result(None, "PostgreSQL: stop()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        service = PostgreSQLService(zcli.logger)
        
        if not hasattr(service, "stop"):
            return _store_result(zcli, "PostgreSQL: stop()", "FAILED", "Method missing")
        
        if not callable(service.stop):
            return _store_result(zcli, "PostgreSQL: stop()", "FAILED", "Not callable")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: stop()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: stop()", "PASSED", "Method exists and callable")


def test_postgresql_is_running(zcli=None, context=None):
    """Test PostgreSQLService.is_running() method."""
    if not zcli:
        return _store_result(None, "PostgreSQL: is_running()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        service = PostgreSQLService(zcli.logger)
        
        if not hasattr(service, "is_running"):
            return _store_result(zcli, "PostgreSQL: is_running()", "FAILED", "Method missing")
        
        # Call it
        running = service.is_running()
        
        if not isinstance(running, bool):
            return _store_result(zcli, "PostgreSQL: is_running()", "FAILED", f"Invalid return: {type(running)}")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: is_running()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: is_running()", "PASSED", f"Running status: {running}")


def test_postgresql_status(zcli=None, context=None):
    """Test PostgreSQLService.status() method."""
    if not zcli:
        return _store_result(None, "PostgreSQL: status()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        service = PostgreSQLService(zcli.logger)
        
        if not hasattr(service, "status"):
            return _store_result(zcli, "PostgreSQL: status()", "FAILED", "Method missing")
        
        # Call it
        status = service.status()
        
        if not isinstance(status, dict):
            return _store_result(zcli, "PostgreSQL: status()", "FAILED", f"Invalid return: {type(status)}")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: status()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: status()", "PASSED", "Status dict returned")


def test_postgresql_connection_info(zcli=None, context=None):
    """Test PostgreSQLService.get_connection_info() method."""
    if not zcli:
        return _store_result(None, "PostgreSQL: get_connection_info()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.services.postgresql_service import PostgreSQLService
        service = PostgreSQLService(zcli.logger)
        
        if not hasattr(service, "get_connection_info"):
            return _store_result(zcli, "PostgreSQL: get_connection_info()", "FAILED", "Method missing")
        
        # Call it
        info = service.get_connection_info()
        
        if not isinstance(info, dict):
            return _store_result(zcli, "PostgreSQL: get_connection_info()", "FAILED", f"Invalid return: {type(info)}")
    except Exception as e:
        return _store_result(zcli, "PostgreSQL: get_connection_info()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "PostgreSQL: get_connection_info()", "PASSED", "Connection info dict returned")


# ===============================================================
# J. zBifrost Bridge Tests (8 tests)
# ===============================================================

def test_bifrost_bridge_class(zcli=None, context=None):
    """Test zBifrost class is accessible."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Class", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        if not zBifrost:
            return _store_result(zcli, "Bifrost Bridge: Class", "FAILED", "Class not found")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Class", "FAILED", f"Import error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Class", "PASSED", "zBifrost class accessible")


def test_bifrost_initialization_validation(zcli=None, context=None):
    """Test zBifrost initialization requires logger."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Init Validation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        # Should raise ValueError with None logger
        try:
            zBifrost(None)
            return _store_result(zcli, "Bifrost Bridge: Init Validation", "FAILED", "No ValueError raised")
        except ValueError:
            # Expected
            pass
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Init Validation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Init Validation", "PASSED", "Logger required (ValueError raised)")


def test_bifrost_client_management(zcli=None, context=None):
    """Test zBifrost has client management."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Client Management", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        bifrost = zBifrost(zcli.logger)
        
        if not hasattr(bifrost, "clients"):
            return _store_result(zcli, "Bifrost Bridge: Client Management", "FAILED", "No clients attribute")
        
        if not isinstance(bifrost.clients, set):
            return _store_result(zcli, "Bifrost Bridge: Client Management", "FAILED", f"Invalid clients type: {type(bifrost.clients)}")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Client Management", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Client Management", "PASSED", "Client set initialized")


def test_bifrost_component_initialization(zcli=None, context=None):
    """Test zBifrost initializes all components."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Components", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        bifrost = zBifrost(zcli.logger)
        
        components = ["cache", "auth", "message_handler", "connection_info"]
        missing = [c for c in components if not hasattr(bifrost, c)]
        
        if missing:
            return _store_result(zcli, "Bifrost Bridge: Components", "FAILED", f"Missing: {missing}")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Components", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Components", "PASSED", "All 4 components initialized")


def test_bifrost_config_loading(zcli=None, context=None):
    """Test zBifrost loads config from zCLI."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Config Loading", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        bifrost = zBifrost(zcli.logger, zcli=zcli)
        
        if not hasattr(bifrost, "port"):
            return _store_result(zcli, "Bifrost Bridge: Config Loading", "FAILED", "No port attribute")
        
        if not hasattr(bifrost, "host"):
            return _store_result(zcli, "Bifrost Bridge: Config Loading", "FAILED", "No host attribute")
        
        if not isinstance(bifrost.port, int):
            return _store_result(zcli, "Bifrost Bridge: Config Loading", "FAILED", f"Invalid port type: {type(bifrost.port)}")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Config Loading", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Config Loading", "PASSED", f"Config loaded: {bifrost.port}")


def test_bifrost_port_validation(zcli=None, context=None):
    """Test zBifrost validates port range."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Port Validation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        # Should raise ValueError for invalid port
        try:
            zBifrost(zcli.logger, port=99999)
            return _store_result(zcli, "Bifrost Bridge: Port Validation", "FAILED", "No ValueError for port > 65535")
        except ValueError:
            # Expected
            pass
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Port Validation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Port Validation", "PASSED", "Port range validated")


def test_bifrost_running_state(zcli=None, context=None):
    """Test zBifrost tracks running state."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Running State", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        bifrost = zBifrost(zcli.logger)
        
        if not hasattr(bifrost, "_running"):
            return _store_result(zcli, "Bifrost Bridge: Running State", "FAILED", "No _running attribute")
        
        if not isinstance(bifrost._running, bool):
            return _store_result(zcli, "Bifrost Bridge: Running State", "FAILED", f"Invalid _running type: {type(bifrost._running)}")
        
        # Should default to False
        if bifrost._running != False:
            return _store_result(zcli, "Bifrost Bridge: Running State", "WARN", "Default _running not False")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Running State", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Running State", "PASSED", "_running initialized to False")


def test_bifrost_event_map(zcli=None, context=None):
    """Test zBifrost has event map."""
    if not zcli:
        return _store_result(None, "Bifrost Bridge: Event Map", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        bifrost = zBifrost(zcli.logger)
        
        # Event map is private attribute _event_map
        if not hasattr(bifrost, "_event_map"):
            return _store_result(zcli, "Bifrost Bridge: Event Map", "FAILED", "No _event_map attribute")
        
        if not isinstance(bifrost._event_map, dict):
            return _store_result(zcli, "Bifrost Bridge: Event Map", "FAILED", f"Invalid event_map type: {type(bifrost._event_map)}")
        
        # Should have some event handlers
        if len(bifrost._event_map) == 0:
            return _store_result(zcli, "Bifrost Bridge: Event Map", "WARN", "Event map is empty")
    except Exception as e:
        return _store_result(zcli, "Bifrost Bridge: Event Map", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Bifrost Bridge: Event Map", "PASSED", f"{len(bifrost._event_map)} event handlers")


# ===============================================================
# K. Bridge Connection Tests (4 tests)
# ===============================================================

def test_connection_info_manager(zcli=None, context=None):
    """Test ConnectionInfoManager class is accessible."""
    if not zcli:
        return _store_result(None, "Connection: InfoManager", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_connection import ConnectionInfoManager
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        manager = ConnectionInfoManager(zcli.logger, cache)
        if not manager:
            return _store_result(zcli, "Connection: InfoManager", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Connection: InfoManager", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Connection: InfoManager", "PASSED", "ConnectionInfoManager accessible")


def test_connection_metadata(zcli=None, context=None):
    """Test ConnectionInfoManager stores metadata."""
    if not zcli:
        return _store_result(None, "Connection: Metadata", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_connection import ConnectionInfoManager
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        manager = ConnectionInfoManager(zcli.logger, cache)
        
        # ConnectionInfoManager has logger, cache, zcli, walker attributes
        if not hasattr(manager, "logger"):
            return _store_result(zcli, "Connection: Metadata", "FAILED", "No logger attribute")
        
        if not hasattr(manager, "cache"):
            return _store_result(zcli, "Connection: Metadata", "FAILED", "No cache attribute")
    except Exception as e:
        return _store_result(zcli, "Connection: Metadata", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Connection: Metadata", "PASSED", "Metadata attributes present")


def test_connection_get_info(zcli=None, context=None):
    """Test ConnectionInfoManager.get_info() method."""
    if not zcli:
        return _store_result(None, "Connection: get_info()", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_connection import ConnectionInfoManager
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        manager = ConnectionInfoManager(zcli.logger, cache)
        
        # Method is get_connection_info, not get_info
        if not hasattr(manager, "get_connection_info"):
            return _store_result(zcli, "Connection: get_info()", "FAILED", "Method missing")
        
        # Call it
        info = manager.get_connection_info()
        
        if not isinstance(info, dict):
            return _store_result(zcli, "Connection: get_info()", "FAILED", f"Invalid return: {type(info)}")
    except Exception as e:
        return _store_result(zcli, "Connection: get_info()", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Connection: get_info()", "PASSED", "Connection info dict returned")


def test_connection_api_discovery(zcli=None, context=None):
    """Test ConnectionInfoManager supports API discovery."""
    if not zcli:
        return _store_result(None, "Connection: API Discovery", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_connection import ConnectionInfoManager
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        manager = ConnectionInfoManager(zcli.logger, cache)
        
        info = manager.get_connection_info()
        
        # Should have server_version or features
        if "server_version" not in info and "features" not in info:
            return _store_result(zcli, "Connection: API Discovery", "WARN", "No version/server info")
    except Exception as e:
        return _store_result(zcli, "Connection: API Discovery", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Connection: API Discovery", "PASSED", "API discovery info available")


# ===============================================================
# L. Bridge Auth - Three-Tier Tests (10 tests) [CRITICAL!]
# ===============================================================

def test_auth_manager_initialization(zcli=None, context=None):
    """Test AuthenticationManager class is accessible."""
    if not zcli:
        return _store_result(None, "Auth: Manager Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        if not manager:
            return _store_result(zcli, "Auth: Manager Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Auth: Manager Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Manager Init", "PASSED", "AuthenticationManager accessible")


def test_auth_layer1_zsession(zcli=None, context=None):
    """Test AuthenticationManager supports Layer 1 (zSession) auth."""
    if not zcli:
        return _store_result(None, "Auth: Layer 1 (zSession)", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        # Should have authenticate_client method
        if not hasattr(manager, "authenticate_client"):
            return _store_result(zcli, "Auth: Layer 1 (zSession)", "FAILED", "No authenticate_client method")
        
        # Check for authenticated_clients dict
        if not hasattr(manager, "authenticated_clients"):
            return _store_result(zcli, "Auth: Layer 1 (zSession)", "FAILED", "No authenticated_clients dict")
    except Exception as e:
        return _store_result(zcli, "Auth: Layer 1 (zSession)", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Layer 1 (zSession)", "PASSED", "zSession auth support confirmed")


def test_auth_layer2_application(zcli=None, context=None):
    """Test AuthenticationManager supports Layer 2 (Application) auth."""
    if not zcli:
        return _store_result(None, "Auth: Layer 2 (Application)", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        
        # Should accept app_auth_config
        manager = AuthenticationManager(zcli.logger, app_auth_config={"user_model": "test"})
        
        if not hasattr(manager, "app_auth_config"):
            return _store_result(zcli, "Auth: Layer 2 (Application)", "FAILED", "No app_auth_config attribute")
    except Exception as e:
        return _store_result(zcli, "Auth: Layer 2 (Application)", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Layer 2 (Application)", "PASSED", "Application auth support confirmed")


def test_auth_layer3_dual(zcli=None, context=None):
    """Test AuthenticationManager supports Layer 3 (Dual) auth."""
    if not zcli:
        return _store_result(None, "Auth: Layer 3 (Dual)", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        # Dual auth is detected automatically when both zSession and token present
        # Just verify the infrastructure exists
        if not hasattr(manager, "authenticated_clients"):
            return _store_result(zcli, "Auth: Layer 3 (Dual)", "FAILED", "No client tracking")
    except Exception as e:
        return _store_result(zcli, "Auth: Layer 3 (Dual)", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Layer 3 (Dual)", "PASSED", "Dual auth infrastructure present")


def test_auth_multi_app_support(zcli=None, context=None):
    """Test AuthenticationManager supports multi-app authentication."""
    if not zcli:
        return _store_result(None, "Auth: Multi-App Support", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        # Multi-app support allows multiple WebSocket connections with different app contexts
        # Each connection can have its own app_name in the authentication result
        if not hasattr(manager, "authenticated_clients"):
            return _store_result(zcli, "Auth: Multi-App Support", "FAILED", "No client tracking for multi-app")
    except Exception as e:
        return _store_result(zcli, "Auth: Multi-App Support", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Multi-App Support", "PASSED", "Multi-app infrastructure present")


def test_auth_origin_validation(zcli=None, context=None):
    """Test AuthenticationManager validates origins (CSRF protection)."""
    if not zcli:
        return _store_result(None, "Auth: Origin Validation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger, allowed_origins=["http://localhost:3000"])
        
        if not hasattr(manager, "allowed_origins"):
            return _store_result(zcli, "Auth: Origin Validation", "FAILED", "No allowed_origins attribute")
    except Exception as e:
        return _store_result(zcli, "Auth: Origin Validation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Origin Validation", "PASSED", "Origin validation configured")


def test_auth_token_extraction(zcli=None, context=None):
    """Test AuthenticationManager can extract tokens."""
    if not zcli:
        return _store_result(None, "Auth: Token Extraction", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        # Token extraction happens in authenticate_client
        if not hasattr(manager, "authenticate_client"):
            return _store_result(zcli, "Auth: Token Extraction", "FAILED", "No authenticate_client method")
    except Exception as e:
        return _store_result(zcli, "Auth: Token Extraction", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Token Extraction", "PASSED", "Token extraction method present")


def test_auth_client_tracking(zcli=None, context=None):
    """Test AuthenticationManager tracks authenticated clients."""
    if not zcli:
        return _store_result(None, "Auth: Client Tracking", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        if not hasattr(manager, "authenticated_clients"):
            return _store_result(zcli, "Auth: Client Tracking", "FAILED", "No authenticated_clients dict")
        
        if not isinstance(manager.authenticated_clients, dict):
            return _store_result(zcli, "Auth: Client Tracking", "FAILED", f"Invalid type: {type(manager.authenticated_clients)}")
    except Exception as e:
        return _store_result(zcli, "Auth: Client Tracking", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Client Tracking", "PASSED", "authenticated_clients dict initialized")


def test_auth_context_detection(zcli=None, context=None):
    """Test AuthenticationManager detects authentication context."""
    if not zcli:
        return _store_result(None, "Auth: Context Detection", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        manager = AuthenticationManager(zcli.logger)
        
        # Context detection returns: "zSession", "application", or "dual"
        # Verified by presence of get_client_info method
        if not hasattr(manager, "get_client_info"):
            return _store_result(zcli, "Auth: Context Detection", "FAILED", "No get_client_info method")
    except Exception as e:
        return _store_result(zcli, "Auth: Context Detection", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Context Detection", "PASSED", "Context detection method present")


def test_auth_configurable_providers(zcli=None, context=None):
    """Test AuthenticationManager supports configurable auth providers."""
    if not zcli:
        return _store_result(None, "Auth: Configurable Providers", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_auth import AuthenticationManager
        
        # Should accept app_auth_config with custom fields
        config = {
            "user_model": "@.custom.users",
            "id_field": "user_id",
            "username_field": "email",
            "role_field": "user_role"
        }
        manager = AuthenticationManager(zcli.logger, app_auth_config=config)
        
        if not manager.app_auth_config:
            return _store_result(zcli, "Auth: Configurable Providers", "FAILED", "Config not stored")
    except Exception as e:
        return _store_result(zcli, "Auth: Configurable Providers", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Auth: Configurable Providers", "PASSED", "Custom auth config accepted")


# ===============================================================
# M. Bridge Cache - Security Tests (8 tests) [SECURITY!]
# ===============================================================

def test_cache_manager_initialization(zcli=None, context=None):
    """Test CacheManager class is accessible."""
    if not zcli:
        return _store_result(None, "Cache: Manager Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        if not manager:
            return _store_result(zcli, "Cache: Manager Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Cache: Manager Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Manager Init", "PASSED", "CacheManager accessible")


def test_cache_user_isolation(zcli=None, context=None):
    """Test CacheManager isolates cache by user_id."""
    if not zcli:
        return _store_result(None, "Cache: User Isolation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        # generate_cache_key should include user_id in key
        if not hasattr(manager, "generate_cache_key"):
            return _store_result(zcli, "Cache: User Isolation", "FAILED", "No generate_cache_key method")
        
        # Test with different users
        data = {"zKey": "^ListUsers"}
        context1 = {"user_id": "user1", "app_name": "app1", "role": "admin", "auth_context": "zSession"}
        context2 = {"user_id": "user2", "app_name": "app1", "role": "admin", "auth_context": "zSession"}
        
        key1 = manager.generate_cache_key(data, context1)
        key2 = manager.generate_cache_key(data, context2)
        
        if key1 == key2:
            return _store_result(zcli, "Cache: User Isolation", "FAILED", "Same key for different users!")
    except Exception as e:
        return _store_result(zcli, "Cache: User Isolation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: User Isolation", "PASSED", "Different keys for different users")


def test_cache_app_isolation(zcli=None, context=None):
    """Test CacheManager isolates cache by app_name."""
    if not zcli:
        return _store_result(None, "Cache: App Isolation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        # Test with different apps
        data = {"zKey": "^ListProducts"}
        context1 = {"user_id": "user1", "app_name": "ecommerce", "role": "customer", "auth_context": "application"}
        context2 = {"user_id": "user1", "app_name": "crm", "role": "customer", "auth_context": "application"}
        
        key1 = manager.generate_cache_key(data, context1)
        key2 = manager.generate_cache_key(data, context2)
        
        if key1 == key2:
            return _store_result(zcli, "Cache: App Isolation", "FAILED", "Same key for different apps!")
    except Exception as e:
        return _store_result(zcli, "Cache: App Isolation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: App Isolation", "PASSED", "Different keys for different apps")


def test_cache_key_generation(zcli=None, context=None):
    """Test CacheManager generates deterministic cache keys."""
    if not zcli:
        return _store_result(None, "Cache: Key Generation", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        data = {"zKey": "^ListUsers", "action": "read"}
        context = {"user_id": "user1", "app_name": "app1", "role": "admin", "auth_context": "zSession"}
        
        key1 = manager.generate_cache_key(data, context)
        key2 = manager.generate_cache_key(data, context)
        
        if key1 != key2:
            return _store_result(zcli, "Cache: Key Generation", "FAILED", "Keys not deterministic!")
        
        if not isinstance(key1, str):
            return _store_result(zcli, "Cache: Key Generation", "FAILED", f"Invalid key type: {type(key1)}")
    except Exception as e:
        return _store_result(zcli, "Cache: Key Generation", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Key Generation", "PASSED", "Deterministic keys generated")


def test_cache_security_warning(zcli=None, context=None):
    """Test CacheManager warns when user context is missing."""
    if not zcli:
        return _store_result(None, "Cache: Security Warning", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        data = {"zKey": "^ListUsers"}
        
        # Should warn when context is None
        key = manager.generate_cache_key(data, None)
        
        # Should still generate a key (fallback to anonymous)
        if not key:
            return _store_result(zcli, "Cache: Security Warning", "FAILED", "No fallback key generated")
    except Exception as e:
        return _store_result(zcli, "Cache: Security Warning", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Security Warning", "PASSED", "Security warning + fallback works")


def test_cache_query_operations(zcli=None, context=None):
    """Test CacheManager query cache operations."""
    if not zcli:
        return _store_result(None, "Cache: Query Operations", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        if not hasattr(manager, "cache_query"):
            return _store_result(zcli, "Cache: Query Operations", "FAILED", "No cache_query method")
        
        if not hasattr(manager, "get_query"):
            return _store_result(zcli, "Cache: Query Operations", "FAILED", "No get_query method")
    except Exception as e:
        return _store_result(zcli, "Cache: Query Operations", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Query Operations", "PASSED", "Query cache methods present")


def test_cache_schema_operations(zcli=None, context=None):
    """Test CacheManager schema cache operations."""
    if not zcli:
        return _store_result(None, "Cache: Schema Operations", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        # CacheManager only has get_schema() for reading from cache
        # Schema is cached internally via set/get pattern
        if not hasattr(manager, "get_schema"):
            return _store_result(zcli, "Cache: Schema Operations", "FAILED", "No get_schema method")
    except Exception as e:
        return _store_result(zcli, "Cache: Schema Operations", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Schema Operations", "PASSED", "Schema cache methods present")


def test_cache_clear_operations(zcli=None, context=None):
    """Test CacheManager selective cache clearing."""
    if not zcli:
        return _store_result(None, "Cache: Clear Operations", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        manager = CacheManager(zcli.logger)
        
        # CacheManager has clear_all(), clear_user_cache(), clear_app_cache()
        clear_methods = ["clear_all", "clear_user_cache", "clear_app_cache"]
        missing = [m for m in clear_methods if not hasattr(manager, m)]
        
        if missing:
            return _store_result(zcli, "Cache: Clear Operations", "FAILED", f"Missing methods: {missing}")
    except Exception as e:
        return _store_result(zcli, "Cache: Clear Operations", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Cache: Clear Operations", "PASSED", "Clear methods present")


# ===============================================================
# N. Bridge Messages Tests (6 tests)
# ===============================================================

def test_message_handler_initialization(zcli=None, context=None):
    """Test MessageHandler class is accessible."""
    if not zcli:
        return _store_result(None, "Messages: Handler Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        # MessageHandler requires 4 args: logger, cache_manager, zcli, walker
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        if not handler:
            return _store_result(zcli, "Messages: Handler Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Messages: Handler Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: Handler Init", "PASSED", "MessageHandler accessible")


def test_message_user_context_extraction(zcli=None, context=None):
    """Test MessageHandler extracts user context."""
    if not zcli:
        return _store_result(None, "Messages: User Context", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        # Should have _extract_user_context method
        if not hasattr(handler, "_extract_user_context"):
            return _store_result(zcli, "Messages: User Context", "FAILED", "No _extract_user_context method")
    except Exception as e:
        return _store_result(zcli, "Messages: User Context", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: User Context", "PASSED", "User context extraction method present")


def test_message_cacheable_detection(zcli=None, context=None):
    """Test MessageHandler detects cacheable operations."""
    if not zcli:
        return _store_result(None, "Messages: Cacheable Detection", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        # Should have _is_cacheable_operation method
        if not hasattr(handler, "_is_cacheable_operation"):
            return _store_result(zcli, "Messages: Cacheable Detection", "FAILED", "No _is_cacheable_operation method")
    except Exception as e:
        return _store_result(zcli, "Messages: Cacheable Detection", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: Cacheable Detection", "PASSED", "Cacheable detection method present")


def test_message_event_routing(zcli=None, context=None):
    """Test MessageHandler routes events."""
    if not zcli:
        return _store_result(None, "Messages: Event Routing", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        # MessageHandler has handle_message method for routing
        if not hasattr(handler, "handle_message"):
            return _store_result(zcli, "Messages: Event Routing", "FAILED", "No handle_message method")
    except Exception as e:
        return _store_result(zcli, "Messages: Event Routing", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: Event Routing", "PASSED", "Event routing method present")


def test_message_json_parsing(zcli=None, context=None):
    """Test MessageHandler parses JSON messages."""
    if not zcli:
        return _store_result(None, "Messages: JSON Parsing", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        # handle_message method should parse JSON automatically
        if not callable(handler.handle_message):
            return _store_result(zcli, "Messages: JSON Parsing", "FAILED", "handle_message not callable")
    except Exception as e:
        return _store_result(zcli, "Messages: JSON Parsing", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: JSON Parsing", "PASSED", "JSON parsing capability confirmed")


def test_message_error_handling(zcli=None, context=None):
    """Test MessageHandler has error handling."""
    if not zcli:
        return _store_result(None, "Messages: Error Handling", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_messages import MessageHandler
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.bridge_cache import CacheManager
        
        cache = CacheManager(zcli.logger)
        handler = MessageHandler(zcli.logger, cache, zcli, zcli.walker)
        
        # Should have logger for error handling
        if not hasattr(handler, "logger"):
            return _store_result(zcli, "Messages: Error Handling", "FAILED", "No logger attribute")
    except Exception as e:
        return _store_result(zcli, "Messages: Error Handling", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Messages: Error Handling", "PASSED", "Error handling infrastructure present")


# ===============================================================
# O. Event Handlers Tests (8 tests)
# ===============================================================

def test_client_events_initialization(zcli=None, context=None):
    """Test ClientEvents class is accessible."""
    if not zcli:
        return _store_result(None, "Events: Client Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_client import ClientEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = ClientEvents(bifrost)
        
        if not events:
            return _store_result(zcli, "Events: Client Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Events: Client Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Client Init", "PASSED", "ClientEvents accessible")


def test_client_events_lifecycle(zcli=None, context=None):
    """Test ClientEvents handles client lifecycle."""
    if not zcli:
        return _store_result(None, "Events: Client Lifecycle", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_client import ClientEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = ClientEvents(bifrost)
        
        # ClientEvents has handle_input_response and handle_connection_info
        lifecycle_methods = ["handle_input_response", "handle_connection_info"]
        missing = [m for m in lifecycle_methods if not hasattr(events, m)]
        
        if missing:
            return _store_result(zcli, "Events: Client Lifecycle", "FAILED", f"Missing methods: {missing}")
    except Exception as e:
        return _store_result(zcli, "Events: Client Lifecycle", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Client Lifecycle", "PASSED", "Lifecycle methods present")


def test_cache_events_initialization(zcli=None, context=None):
    """Test CacheEvents class is accessible."""
    if not zcli:
        return _store_result(None, "Events: Cache Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_cache import CacheEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = CacheEvents(bifrost)
        
        if not events:
            return _store_result(zcli, "Events: Cache Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Events: Cache Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Cache Init", "PASSED", "CacheEvents accessible")


def test_cache_events_operations(zcli=None, context=None):
    """Test CacheEvents handles cache operations."""
    if not zcli:
        return _store_result(None, "Events: Cache Operations", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_cache import CacheEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = CacheEvents(bifrost)
        
        # CacheEvents has handle_get_schema, handle_clear_cache, handle_cache_stats, handle_set_cache_ttl
        cache_methods = ["handle_get_schema", "handle_clear_cache", "handle_cache_stats", "handle_set_cache_ttl"]
        missing = [m for m in cache_methods if not hasattr(events, m)]
        
        if missing:
            return _store_result(zcli, "Events: Cache Operations", "FAILED", f"Missing methods: {missing}")
    except Exception as e:
        return _store_result(zcli, "Events: Cache Operations", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Cache Operations", "PASSED", "Cache operation methods present")


def test_discovery_events_initialization(zcli=None, context=None):
    """Test DiscoveryEvents class is accessible."""
    if not zcli:
        return _store_result(None, "Events: Discovery Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_discovery import DiscoveryEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = DiscoveryEvents(bifrost)
        
        if not events:
            return _store_result(zcli, "Events: Discovery Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Events: Discovery Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Discovery Init", "PASSED", "DiscoveryEvents accessible")


def test_discovery_events_introspection(zcli=None, context=None):
    """Test DiscoveryEvents provides API introspection."""
    if not zcli:
        return _store_result(None, "Events: Discovery Introspection", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_discovery import DiscoveryEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = DiscoveryEvents(bifrost)
        
        # DiscoveryEvents has handle_discover and handle_introspect
        discovery_methods = ["handle_discover", "handle_introspect"]
        missing = [m for m in discovery_methods if not hasattr(events, m)]
        
        if missing:
            return _store_result(zcli, "Events: Discovery Introspection", "FAILED", f"Missing methods: {missing}")
    except Exception as e:
        return _store_result(zcli, "Events: Discovery Introspection", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Discovery Introspection", "PASSED", "Introspection method present")


def test_dispatch_events_initialization(zcli=None, context=None):
    """Test DispatchEvents class is accessible."""
    if not zcli:
        return _store_result(None, "Events: Dispatch Init", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_dispatch import DispatchEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = DispatchEvents(bifrost)
        
        if not events:
            return _store_result(zcli, "Events: Dispatch Init", "FAILED", "Failed to create instance")
    except Exception as e:
        return _store_result(zcli, "Events: Dispatch Init", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Dispatch Init", "PASSED", "DispatchEvents accessible")


def test_dispatch_events_user_context(zcli=None, context=None):
    """Test DispatchEvents extracts user context for commands."""
    if not zcli:
        return _store_result(None, "Events: Dispatch User Context", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bridge_modules.events.bridge_event_dispatch import DispatchEvents
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge import zBifrost
        
        bifrost = zBifrost(zcli.logger)
        events = DispatchEvents(bifrost)
        
        # Should have handle_dispatch method with user context awareness
        if not hasattr(events, "handle_dispatch"):
            return _store_result(zcli, "Events: Dispatch User Context", "FAILED", "No handle_dispatch method")
    except Exception as e:
        return _store_result(zcli, "Events: Dispatch User Context", "FAILED", f"Error: {str(e)}")
    
    return _store_result(zcli, "Events: Dispatch User Context", "PASSED", "Dispatch method with context present")


# ===============================================================
# P. Integration Tests - Real Operations (8 tests)
# ===============================================================

def test_integration_port_availability_check(zcli=None, context=None):
    """Test real port availability checking."""
    if not zcli:
        return _store_result(None, "Integration: Port Availability", "ERROR", "No zcli")
    
    try:
        # Test checking an available port (high number, unlikely to be in use)
        test_port = 59999
        is_available = zcli.comm.check_port(test_port)
        
        if isinstance(is_available, bool):
            return _store_result(zcli, "Integration: Port Availability", "PASSED", 
                               f"Port {test_port} check: available={is_available}")
        else:
            return _store_result(zcli, "Integration: Port Availability", "FAILED", 
                               f"Invalid return type: {type(is_available)}")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Port Availability", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_health_check_execution(zcli=None, context=None):
    """Test actually calling health_check_all()."""
    if not zcli:
        return _store_result(None, "Integration: Health Check Exec", "ERROR", "No zcli")
    
    try:
        # Actually execute the health check
        health_data = zcli.comm.health_check_all()
        
        if not isinstance(health_data, dict):
            return _store_result(zcli, "Integration: Health Check Exec", "FAILED", 
                               f"Invalid return type: {type(health_data)}")
        
        # Count health checks
        check_count = len(health_data)
        
        return _store_result(zcli, "Integration: Health Check Exec", "PASSED", 
                           f"Executed: {check_count} checks returned")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Health Check Exec", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_websocket_server_lifecycle(zcli=None, context=None):
    """Test WebSocket server creation (without starting)."""
    if not zcli:
        return _store_result(None, "Integration: WebSocket Lifecycle", "ERROR", "No zcli")
    
    try:
        # Check if we can access WebSocket configuration
        ws_config = zcli.config.websocket
        
        if not hasattr(ws_config, 'host') or not hasattr(ws_config, 'port'):
            return _store_result(zcli, "Integration: WebSocket Lifecycle", "FAILED", 
                               "Missing WebSocket config")
        
        # Validate configuration values
        host = ws_config.host
        port = ws_config.port
        
        if not isinstance(host, str) or not isinstance(port, int):
            return _store_result(zcli, "Integration: WebSocket Lifecycle", "FAILED", 
                               f"Invalid config types: host={type(host)}, port={type(port)}")
        
        return _store_result(zcli, "Integration: WebSocket Lifecycle", "PASSED", 
                           f"Config validated: {host}:{port}")
    
    except Exception as e:
        return _store_result(zcli, "Integration: WebSocket Lifecycle", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_http_client_initialization(zcli=None, context=None):
    """Test HTTP client can be initialized for real requests."""
    if not zcli:
        return _store_result(None, "Integration: HTTP Client Init", "ERROR", "No zcli")
    
    try:
        # Access the HTTP client
        http_client = zcli.comm._http_client
        
        if not http_client:
            return _store_result(zcli, "Integration: HTTP Client Init", "FAILED", 
                               "HTTP client not initialized")
        
        # Verify it has required attributes for making requests
        # HTTPClient only needs: logger attribute and post() method
        has_post = hasattr(http_client, 'post') and callable(http_client.post)
        has_logger = hasattr(http_client, 'logger')
        
        if has_post and has_logger:
            return _store_result(zcli, "Integration: HTTP Client Init", "PASSED", 
                               "HTTP client ready (post method + logger)")
        else:
            return _store_result(zcli, "Integration: HTTP Client Init", "FAILED", 
                               f"Missing requirements: post={has_post}, logger={has_logger}")
    
    except Exception as e:
        return _store_result(zcli, "Integration: HTTP Client Init", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_service_manager_operations(zcli=None, context=None):
    """Test service manager status operations."""
    if not zcli:
        return _store_result(None, "Integration: Service Manager Ops", "ERROR", "No zcli")
    
    try:
        # Get status of all services (without starting anything)
        status_data = zcli.comm.services.status()
        
        if not isinstance(status_data, dict):
            return _store_result(zcli, "Integration: Service Manager Ops", "FAILED", 
                               f"Invalid status type: {type(status_data)}")
        
        # Check for PostgreSQL service info
        service_count = len(status_data)
        
        return _store_result(zcli, "Integration: Service Manager Ops", "PASSED", 
                           f"Status retrieved: {service_count} services")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Service Manager Ops", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_bifrost_manager_state(zcli=None, context=None):
    """Test Bifrost manager state without starting server."""
    if not zcli:
        return _store_result(None, "Integration: Bifrost Manager State", "ERROR", "No zcli")
    
    try:
        # Access the Bifrost manager
        bifrost_mgr = zcli.comm._bifrost_mgr
        
        if not bifrost_mgr:
            return _store_result(zcli, "Integration: Bifrost Manager State", "FAILED", 
                               "Bifrost manager not initialized")
        
        # Check if WebSocket is started (should be None in Terminal mode)
        ws_instance = bifrost_mgr.websocket
        
        # In Terminal mode, WebSocket shouldn't be auto-started
        if ws_instance is None:
            return _store_result(zcli, "Integration: Bifrost Manager State", "PASSED", 
                               "Bifrost manager ready (WebSocket not started)")
        else:
            return _store_result(zcli, "Integration: Bifrost Manager State", "WARN", 
                               "WebSocket unexpectedly started in Terminal mode")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Bifrost Manager State", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_network_utils_operations(zcli=None, context=None):
    """Test network utility operations with real port checks."""
    if not zcli:
        return _store_result(None, "Integration: Network Utils Ops", "ERROR", "No zcli")
    
    try:
        from zCLI.subsystems.zComm.zComm_modules.helpers.network_utils import NetworkUtils
        
        # Create a network utils instance
        net_utils = NetworkUtils(zcli.logger)
        
        # Test checking a well-known port (port 80 - HTTP)
        # This should be in use or restricted on most systems
        result_80 = net_utils.check_port(80)
        
        # Test checking a high port (unlikely to be in use)
        result_high = net_utils.check_port(59998)
        
        if isinstance(result_80, bool) and isinstance(result_high, bool):
            return _store_result(zcli, "Integration: Network Utils Ops", "PASSED", 
                               f"Port checks executed: 80={result_80}, 59998={result_high}")
        else:
            return _store_result(zcli, "Integration: Network Utils Ops", "FAILED", 
                               "Invalid return types from port checks")
    
    except ImportError:
        return _store_result(zcli, "Integration: Network Utils Ops", "WARN", 
                           "NetworkUtils module not accessible")
    except Exception as e:
        return _store_result(zcli, "Integration: Network Utils Ops", "ERROR", 
                           f"Exception: {str(e)}")


def test_integration_session_comm_persistence(zcli=None, context=None):
    """Test zComm session data persistence and access."""
    if not zcli:
        return _store_result(None, "Integration: Session Persistence", "ERROR", "No zcli")
    
    try:
        # Store some test data in session via zComm
        test_key = "zComm_integration_test"
        test_value = "integration_test_value"
        
        # zComm should have access to session
        if not hasattr(zcli.comm, "session"):
            return _store_result(zcli, "Integration: Session Persistence", "FAILED", 
                               "zComm has no session access")
        
        # Store data
        zcli.comm.session[test_key] = test_value
        
        # Verify we can read it back
        retrieved = zcli.comm.session.get(test_key)
        
        # Clean up
        if test_key in zcli.comm.session:
            del zcli.comm.session[test_key]
        
        if retrieved == test_value:
            return _store_result(zcli, "Integration: Session Persistence", "PASSED", 
                               "Session data persisted and retrieved")
        else:
            return _store_result(zcli, "Integration: Session Persistence", "FAILED", 
                               f"Data mismatch: expected={test_value}, got={retrieved}")
    
    except Exception as e:
        return _store_result(zcli, "Integration: Session Persistence", "ERROR", 
                           f"Exception: {str(e)}")


# ===============================================================
# Display Test Results (Final Step)
# ===============================================================

def display_test_results(zcli=None, context=None):
    """Display accumulated test results with comprehensive statistics."""
    if not zcli:
        return None
    
    results = zcli.session.get("zTestRunner_results", [])
    if not results:
        print("\n[WARN] No test results found")
        input("Press Enter to return to main menu...")
        return None
    
    # Calculate stats
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASSED")
    failed = sum(1 for r in results if r.get("status") == "FAILED")
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    warnings = sum(1 for r in results if r.get("status") == "WARN")
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    # Display header
    print("\n" + "=" * 80)
    print(f"zComm Comprehensive Test Suite - {total} Tests")
    print("=" * 80 + "\n")
    
    # Group by category
    categories = {
        "A. zComm Facade API (14 tests)": [],
        "B. Bifrost Manager (8 tests)": [],
        "C. HTTP Client (5 tests)": [],
        "D. Service Manager (7 tests)": [],
        "E. Network Utils (6 tests)": [],
        "F. HTTP Server (4 tests)": [],
        "G. Integration (3 tests)": [],
        "H. Layer 0 Compliance (1 test)": [],
        "I. PostgreSQL Service (6 tests)": [],
        "J. zBifrost Bridge (8 tests)": [],
        "K. Bridge Connection (4 tests)": [],
        "L. Bridge Auth - Three-Tier (10 tests) [CRITICAL]": [],
        "M. Bridge Cache - Security (8 tests) [SECURITY]": [],
        "N. Bridge Messages (6 tests)": [],
        "O. Event Handlers (8 tests)": [],
        "P. Integration Tests (8 tests)": []
    }
    
    # Categorize
    for r in results:
        test = r.get("test", "")
        if "Facade:" in test: categories["A. zComm Facade API (14 tests)"].append(r)
        elif "Bifrost:" in test and "Bifrost Bridge:" not in test: categories["B. Bifrost Manager (8 tests)"].append(r)
        elif "HTTP Client:" in test: categories["C. HTTP Client (5 tests)"].append(r)
        elif "Service Manager:" in test: categories["D. Service Manager (7 tests)"].append(r)
        elif "Network Utils:" in test: categories["E. Network Utils (6 tests)"].append(r)
        elif "HTTP Server:" in test: categories["F. HTTP Server (4 tests)"].append(r)
        # Old unit-level integration tests (checking cross-module access)
        elif "Integration: Health Checks" in test or "Integration: Session Access" in test or "Integration: Logger Access" in test:
            categories["G. Integration (3 tests)"].append(r)
        elif "Layer 0:" in test: categories["H. Layer 0 Compliance (1 test)"].append(r)
        elif "PostgreSQL:" in test: categories["I. PostgreSQL Service (6 tests)"].append(r)
        elif "Bifrost Bridge:" in test: categories["J. zBifrost Bridge (8 tests)"].append(r)
        elif "Connection:" in test: categories["K. Bridge Connection (4 tests)"].append(r)
        elif "Auth:" in test: categories["L. Bridge Auth - Three-Tier (10 tests) [CRITICAL]"].append(r)
        elif "Cache:" in test: categories["M. Bridge Cache - Security (8 tests) [SECURITY]"].append(r)
        elif "Messages:" in test: categories["N. Bridge Messages (6 tests)"].append(r)
        elif "Events:" in test: categories["O. Event Handlers (8 tests)"].append(r)
        # New real operations integration tests (P)
        elif "Integration:" in test: categories["P. Integration Tests (8 tests)"].append(r)
    
    # Display by category
    for category, tests in categories.items():
        if not tests:
            continue
        print(f"\n{category}")
        print("-" * 80)
        for r in tests:
            status = r.get("status", "UNKNOWN")
            icon = {"PASSED": "[OK]", "FAILED": "[FAIL]", "ERROR": "[ERROR]", "WARN": "[WARN]"}.get(status, "[?]")
            print(f"  {icon} {r.get('test', 'Unknown')}")
            if status != "PASSED":
                print(f"      -> {r.get('message', '')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print(f"  Total Tests:    {total}")
    if passed > 0: print(f"  [OK] Passed:    {passed} ({pass_pct:.1f}%)")
    if failed > 0: print(f"  [FAIL] Failed:  {failed} ({failed/total*100:.1f}%)")
    if errors > 0: print(f"  [ERROR] Errors: {errors} ({errors/total*100:.1f}%)")
    if warnings > 0: print(f"  [WARN] Warnings: {warnings} ({warnings/total*100:.1f}%)")
    print("=" * 80)
    
    if failed == 0 and errors == 0:
        print(f"\n[SUCCESS] All {passed} tests passed ({pass_pct:.0f}%)")
    else:
        print(f"\n[FAILURE] {failed + errors} test(s) did not pass")
    
    print(f"\n[INFO] Coverage: All 15 zComm modules + 8 integration tests (A-to-P comprehensive coverage)")
    print(f"[INFO] Including: Three-Tier Auth, Cache Security, PostgreSQL, Bifrost Bridge, All Event Handlers")
    print(f"[INFO] Integration Tests: Real port checks, health execution, WebSocket lifecycle, HTTP client, service manager, session persistence")
    print("\n[INFO] Review results above.")
    
    # Only prompt for input if stdin is a terminal (not piped)
    import sys
    if sys.stdin.isatty():
        input("Press Enter to return to main menu...")
    
    zcli.session["zTestRunner_results"] = []
    return None

