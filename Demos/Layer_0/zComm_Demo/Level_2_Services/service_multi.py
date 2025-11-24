#!/usr/bin/env python3
"""
Level 2: Multiple Service Detection
====================================

Goal:
    Check multiple services in one pass.
    - Shows iteration pattern with service_status()
    - Checks PostgreSQL, Redis, MongoDB
    - Practical for development environment setup
    - Clean, scannable output

Run:
    python3 Demos/Layer_0/zComm_Demo/Level_2_Services/service_multi.py
"""

from zCLI import zCLI

def run_demo():
    """Check multiple development services."""
    z = zCLI({"logger": "PROD"})

    # Services to check
    services = ["postgresql", "redis", "mongodb"]

    print()
    print("=== Multiple Service Detection ===")
    print()

    running = 0

    # Check each service - display as we go
    for service in services:
        status = z.comm.service_status(service)

        if status.get("running"):
            info = z.comm.get_service_connection_info(service)
            print(f"✓ {service.upper()}: {info['host']}:{info['port']}")
            running += 1
        else:
            print(f"✗ {service.upper()}: Not running")

    # Summary
    print()
    print(f"{'='*40}")
    print(f"Summary: {running}/{len(services)} services running")
    print()
    print("Tip: Check your entire dev stack with one script!")
    print()

if __name__ == "__main__":
    run_demo()

