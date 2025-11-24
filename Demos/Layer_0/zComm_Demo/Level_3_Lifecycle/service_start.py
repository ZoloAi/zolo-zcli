#!/usr/bin/env python3
"""
Level 3: Service Lifecycle Management
======================================

Goal:
    Declare desired service state - zComm handles the rest.
    - Start service: z.comm.start_service()
    - Stop service: z.comm.stop_service()
    - Get connection: z.comm.get_service_connection_info()
    - No manual orchestration needed

Run:
    python3 Demos/Layer_0/zComm_Demo/Level_3_Lifecycle/service_start.py

Note:
    Requires PostgreSQL installed and system permissions.
    Install: pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git[postgresql]
"""

from zCLI import zCLI

def run_demo():
    """Declare: Start PostgreSQL and get connection."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Service Lifecycle ===")
    print()
    
    # Declare: I want PostgreSQL running
    print("Starting PostgreSQL...")
    success = z.comm.start_service("postgresql")
    
    if not success:
        print("✗ Failed to start")
        print()
        print("Requirements:")
        print("  brew install postgresql  (macOS)")
        print("  sudo apt-get install postgresql  (Linux)")
        print()
        return
    
    print("✓ Service started")
    print()
    
    # Declare: I want connection info
    info = z.comm.get_service_connection_info("postgresql")
    
    if info:
        print("Connection ready:")
        print(f"  {info['host']}:{info['port']}")
        print()
        print(f"Connect: psql -h {info['host']} -p {info['port']}")
    
    print()
    print("=" * 45)
    print("Stop: z.comm.stop_service('postgresql')")
    print()

if __name__ == "__main__":
    run_demo()

