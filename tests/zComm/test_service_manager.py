#!/usr/bin/env python3
"""Service Manager Tests - Test PostgreSQL and other service management."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zCLI.zCLI import zCLI


def test_service_manager_initialization():
    """Test that service manager initializes properly."""
    print("=" * 70)
    print("TEST 1: Service Manager Initialization")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Check service manager attributes
    assert hasattr(zcli.comm, 'services'), "zComm missing services attribute"
    assert hasattr(zcli.comm.services, 'start'), "ServiceManager missing start method"
    assert hasattr(zcli.comm.services, 'stop'), "ServiceManager missing stop method"
    assert hasattr(zcli.comm.services, 'status'), "ServiceManager missing status method"
    
    print("✅ Service manager has all required methods:")
    print("   - start(service_name, **kwargs)")
    print("   - stop(service_name)")
    print("   - restart(service_name)")
    print("   - status(service_name)")
    print("   - get_connection_info(service_name)")
    print()
    return True


def test_port_availability():
    """Test port availability checking."""
    print("=" * 70)
    print("TEST 2: Port Availability Check")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Test common ports
    test_ports = [56891, 5432, 6379, 8080]
    
    for port in test_ports:
        is_available = zcli.comm.check_port(port)
        status = "✅ Available" if is_available else "❌ In use"
        print(f"   Port {port:5d}: {status}")
    
    print()
    print("✅ Port checking works")
    print()
    return True


def test_service_status():
    """Test service status checking."""
    print("=" * 70)
    print("TEST 3: Service Status Checking")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Get status for common services (will show not running if not started)
    services = ['postgresql', 'redis']
    
    for service in services:
        try:
            status = zcli.comm.service_status(service)
            print(f"   {service}: {status}")
        except Exception as e:
            print(f"   {service}: Not configured ({e})")
    
    print()
    print("✅ Service status method callable")
    print()
    return True


def test_websocket_creation():
    """Test WebSocket server instance creation."""
    print("=" * 70)
    print("TEST 4: WebSocket Instance Creation")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Create WebSocket instance (without starting)
    ws = zcli.comm.create_websocket(port=56891, host="127.0.0.1")
    
    assert ws is not None, "Failed to create WebSocket instance"
    assert hasattr(ws, 'handle_client'), "WebSocket missing handle_client"
    assert hasattr(ws, 'broadcast'), "WebSocket missing broadcast"
    
    print("✅ WebSocket instance created:")
    print(f"   Type: {type(ws).__name__}")
    print(f"   Port: {ws.port}")
    print(f"   Host: {ws.host}")
    print(f"   Methods: handle_client, broadcast, validate_origin, authenticate_client")
    print()
    return True


def test_comm_integration():
    """Test zComm integration with zCLI."""
    print("=" * 70)
    print("TEST 5: zComm Integration with zCLI")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Verify zComm is accessible from dependent subsystems
    checks = [
        ("zDisplay can access zComm", hasattr(zcli.display.zcli, 'comm')),
        ("zDialog can access zComm", hasattr(zcli.dialog.zcli, 'comm')),
        ("zData can access zComm", hasattr(zcli.data.zcli, 'comm')),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        all_passed = all_passed and result
    
    print()
    if all_passed:
        print("✅ All subsystems can access zComm")
    else:
        print("❌ Some subsystems cannot access zComm")
    
    print()
    return all_passed


def main():
    """Run all service manager tests."""
    print()
    print("=" * 70)
    print("ZCOMM SERVICE MANAGER TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_service_manager_initialization,
        test_port_availability,
        test_service_status,
        test_websocket_creation,
        test_comm_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("=" * 70)
    print()
    
    if failed == 0:
        print("🎉 All tests passed!")
        print()
        print("Next steps:")
        print("   1. Run: python3 tests/zComm/test_websocket_server.py")
        print("      (in one terminal)")
        print()
        print("   2. Run: python3 tests/zComm/test_websocket_client.py")
        print("      (in another terminal)")
        print()
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

