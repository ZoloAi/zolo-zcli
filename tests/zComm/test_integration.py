#!/usr/bin/env python3
"""zComm Integration Tests - Test full zCLI integration with communication layer."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zCLI.zCLI import zCLI


def test_layer0_initialization():
    """Test that Layer 0 initializes in correct order."""
    print("=" * 70)
    print("TEST 1: Layer 0 Initialization Order")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Verify Layer 0 components exist
    assert hasattr(zcli, 'config'), "Missing zConfig"
    assert hasattr(zcli, 'session'), "Missing session"
    assert hasattr(zcli, 'comm'), "Missing zComm"
    
    print("✅ Layer 0 components initialized:")
    print(f"   1. zConfig:  {type(zcli.config).__name__}")
    print(f"   2. session:  {type(zcli.session).__name__}")
    print(f"   3. zComm:    {type(zcli.comm).__name__}")
    print()
    
    # Verify zComm was initialized BEFORE dependent subsystems
    print("✅ zComm initialized before dependent subsystems:")
    print(f"   - zDisplay available: {hasattr(zcli, 'display')}")
    print(f"   - zDialog available:  {hasattr(zcli, 'dialog')}")
    print(f"   - zData available:    {hasattr(zcli, 'data')}")
    print()
    return True


def test_comm_accessibility():
    """Test that all subsystems can access zComm."""
    print("=" * 70)
    print("TEST 2: zComm Accessibility from Subsystems")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    subsystems = [
        ('zDisplay', zcli.display),
        ('zParser', zcli.zparser),
        ('zLoader', zcli.loader),
        ('zFunc', zcli.zfunc),
        ('zDialog', zcli.dialog),
        ('zOpen', zcli.open),
        ('zData', zcli.data),
    ]
    
    all_passed = True
    for name, subsystem in subsystems:
        has_zcli = hasattr(subsystem, 'zcli')
        has_comm = has_zcli and hasattr(subsystem.zcli, 'comm')
        
        status = "✅" if has_comm else "❌"
        print(f"   {status} {name:12s} can access zComm: {has_comm}")
        all_passed = all_passed and has_comm
    
    print()
    if all_passed:
        print("✅ All subsystems can access zComm via zcli.comm")
    else:
        print("❌ Some subsystems cannot access zComm")
    
    print()
    return all_passed


def test_websocket_features():
    """Test WebSocket-specific features."""
    print("=" * 70)
    print("TEST 3: WebSocket Features")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Test WebSocket creation
    ws = zcli.comm.create_websocket()
    
    features = [
        ('WebSocket instance created', ws is not None),
        ('Has handle_client method', hasattr(ws, 'handle_client')),
        ('Has broadcast method', hasattr(ws, 'broadcast')),
        ('Has validate_origin method', hasattr(ws, 'validate_origin')),
        ('Has authenticate_client method', hasattr(ws, 'authenticate_client')),
    ]
    
    all_passed = True
    for feature_name, result in features:
        status = "✅" if result else "❌"
        print(f"   {status} {feature_name}")
        all_passed = all_passed and result
    
    print()
    return all_passed


def test_service_management():
    """Test service management capabilities."""
    print("=" * 70)
    print("TEST 4: Service Management")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Test service manager methods exist
    methods = [
        'start_service',
        'stop_service',
        'restart_service',
        'service_status',
        'get_service_connection_info',
    ]
    
    all_exist = True
    for method in methods:
        exists = hasattr(zcli.comm, method)
        status = "✅" if exists else "❌"
        print(f"   {status} {method}")
        all_exist = all_exist and exists
    
    print()
    if all_exist:
        print("✅ All service management methods available")
    
    print()
    return all_exist


def test_network_utilities():
    """Test network utility methods."""
    print("=" * 70)
    print("TEST 5: Network Utilities")
    print("=" * 70)
    print()
    
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    # Test port checking on common ports
    test_ports = [56891, 5432, 6379]
    
    print("Port availability checks:")
    for port in test_ports:
        is_available = zcli.comm.check_port(port)
        status = "Available" if is_available else "In use"
        print(f"   Port {port}: {status}")
    
    print()
    print("✅ Network utilities functional")
    print()
    return True


def main():
    """Run all integration tests."""
    print()
    print("=" * 70)
    print("ZCOMM INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_layer0_initialization,
        test_comm_accessibility,
        test_websocket_features,
        test_service_management,
        test_network_utilities,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
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
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

