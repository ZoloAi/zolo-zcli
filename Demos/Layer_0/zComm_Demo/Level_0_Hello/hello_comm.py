#!/usr/bin/env python3
"""
Level 0: Hello zComm
====================

Goal:
    The tiniest possible introduction to zComm.
    - Initialize zCLI (which auto-loads zComm)
    - Check if a port is available
    - Print it out with zero setup

Run:
    python Demos/Layer_0/zComm_Demo/Level_0_Hello/hello_comm.py
"""

from zCLI import zCLI

def run_demo():
    """Initialize zCLI and show the first bits of zComm capability."""
    z = zCLI({"logger": "PROD"})

    # Check if common web port is available
    port = 8080
    is_available = z.comm.check_port(port)
    
    print()
    print("=== Level 0: Hello zComm ===")
    print(f"Port {port} : {'available' if is_available else 'in use'}")
    print()
    print("Tip: zComm auto-initializes with zCLI - zero setup!")
    print()

if __name__ == "__main__":
    run_demo()

