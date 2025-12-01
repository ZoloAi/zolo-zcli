#!/usr/bin/env python3
"""Level 0: Hello zComm

After mastering zConfig, explore zComm - the communication layer.
Same zSpark pattern, zero additional setup!

Run:
    python Demos/Layer_0/zComm_Demo/lvl0_hello/1_hello_comm.py

Key Discovery:
  - Watch subsystem initialization order (zConfig → zComm)
  - zComm auto-initializes immediately after zConfig
  - Both are Layer 0 subsystems (foundation)
"""

from zCLI import zCLI

def run_demo():
    """Initialize zCLI and observe zComm auto-initialization."""
    # Consistent zSpark pattern from zConfig
    zSpark = {
        "deployment": "Development",  # Show subsystem banners
        "title": "hello-comm",
        "logger": "PROD",             # Silent console, file-only logging
        "logger_path": "./logs",
    }
    
    print("\n" + "="*60)
    print("  HELLO ZCOMM")
    print("="*60)
    print("\nWatch the initialization order above...")
    print("Look for: [zConfig Ready] → [zComm Ready]\n")
    
    z = zCLI(zSpark)
    
    print("\n" + "="*60)
    print("# What you discovered:")
    print("="*60)
    print("  ✓ zConfig initializes first (Layer 0)")
    print("  ✓ zComm initializes immediately after")
    print("  ✓ Same zSpark pattern from zConfig demos")
    print("  ✓ Communication layer ready with zero config\n")

if __name__ == "__main__":
    run_demo()

