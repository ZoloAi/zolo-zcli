#!/usr/bin/env python3
"""
Level 2: Service Status Check
==============================

Goal:
    Check if PostgreSQL is running on your machine.
    - Shows z.comm.service_status() detection
    - Gets connection info if service is running
    - Safe to run even if PostgreSQL not installed
    - No manual port probing or OS commands

Run:
    python Demos/Layer_0/zComm_Demo/Level_2_Services/service_check.py
"""

from zCLI import zCLI

def run_demo():
    """Check if PostgreSQL service is running."""
    z = zCLI({"logger": "PROD"})

    service = "postgresql"
    
    print()
    print("=== Service Status Check ===")
    print()
    print(f"Checking {service}...")
    print()
    
    # Check service status
    status = z.comm.service_status(service)
    
    if status.get("running"):
        print(f"✓ {service.upper()} is running")
        print()
        
        # Get connection details
        info = z.comm.get_service_connection_info(service)
        if info:
            print("Connection info:")
            print(f"  Host: {info.get('host', 'unknown')}")
            print(f"  Port: {info.get('port', 'unknown')}")
            print()
            print("You can connect:")
            print(f"  psql -h {info['host']} -p {info['port']}")
        
    else:
        print(f"✗ {service.upper()} is not running")
        if status.get("error"):
            print(f"  Reason: {status['error']}")
    
    print()
    print("Tip: zComm detects services across macOS/Linux/Windows")
    print()

if __name__ == "__main__":
    run_demo()

