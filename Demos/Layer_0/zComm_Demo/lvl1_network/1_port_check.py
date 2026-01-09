#!/usr/bin/env python3
"""Level 1: Check Multiple Ports

In Level 0, you checked port 8080. Now let's check multiple ports and
understand what ports are.

Run:
    python Demos/Layer_0/zComm_Demo/lvl1_network/1_port_check.py

Key Discovery:
  - Ports = unique numbers (1-65535) each service needs
  - Common ports: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL)
  - Check before starting servers (prevents conflicts)
"""

from zKernel import zKernel

def run_demo():
    """Check common ports for availability."""
    # Consistent zSpark pattern from zConfig
    zSpark = {
        "deployment": "Production",
        "title": "port-check",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zKernel(zSpark)
    
    print("\n" + "="*60)
    print("  NETWORK PORTS - AVAILABILITY CHECK")
    print("="*60)

    # Common ports and their services
    ports = {
        80: "HTTP",
        443: "HTTPS",
        8080: "Dev Server",
        3000: "Node/React",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        56891: "zBifrost"
    }
    
    print("\n# Checking common service ports:")
    
    # Check each port (copy this pattern)
    for port, service in ports.items():
        is_available = z.comm.check_port(port)
        status = "✓ available" if is_available else "✗ in use"
        print(f"  Port {port:5d} ({service:12s}): {status}")
    
    print("\n# What you discovered:")
    print("  ✓ Ports = apartment numbers in your computer (1-65535)")
    print("  ✓ Each service needs its own unique port")
    print("  ✓ Check BEFORE starting servers (prevents conflicts)")
    print("  ✓ One line: z.comm.check_port(8080)")
    
    print("\n# Usage pattern:")
    print("  is_free = z.comm.check_port(8080)")
    print("  # Returns True if available, False if in use\n")

if __name__ == "__main__":
    run_demo()

