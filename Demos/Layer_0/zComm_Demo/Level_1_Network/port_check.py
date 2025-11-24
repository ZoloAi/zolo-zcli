#!/usr/bin/env python3
"""
Level 1: Port Availability Check
=================================

Goal:
    Check multiple ports to see which are available.
    - Shows z.comm.check_port() with multiple ports
    - Demonstrates simple iteration pattern
    - Clean, scannable output

Run:
    python Demos/Layer_0/zComm_Demo/Level_1_Network/port_check.py
"""

from zCLI import zCLI

def run_demo():
    """Check common ports for availability."""
    z = zCLI({"logger": "PROD"})

    # Common ports to check
    ports = {
        80: "HTTP",
        443: "HTTPS", 
        8080: "HTTP Alt",
        3000: "Dev Server",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        56891: "zBifrost"
    }
    
    print()
    print("=== Port Availability Check ===")
    print()
    
    # Check each port
    for port, service in ports.items():
        is_available = z.comm.check_port(port)
        status = "✓ available" if is_available else "✗ in use"
        print(f"Port {port:5d} ({service:12s}): {status}")
    
    print()
    print("Tip: Use z.comm.check_port() before starting servers")
    print()

if __name__ == "__main__":
    run_demo()

