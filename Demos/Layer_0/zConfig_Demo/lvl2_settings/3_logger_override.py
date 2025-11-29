#!/usr/bin/env python3
"""Level 2: Logger Override - Breaking Smart Defaults

Shows how to override smart defaults when you need different behavior.
Deployment and logger are INDEPENDENT - mix them however you need!

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_override.py

When to use this:
    - Troubleshooting production issues
    - Need detailed logs without changing deployment behavior
    - Want DEBUG logs but still minimal banners/output"""

from zCLI import zCLI

def run_demo():
    # Production deployment with DEBUG logging (explicit override)
    # Useful for troubleshooting production issues
    z = zCLI({
        "deployment": "Production",
        "logger": "DEBUG",  # Explicitly override default ERROR logging
    })
    session = z.session
    
    print("\n# Session state:")
    print(f"zMode           : {session.get('zMode')}")
    print(f"zSpace          : {session.get('zSpace')}")
    print(f"zLogger (level) : {session.get('zLogger')}")
    print(f"Deployment      : {z.config.get_environment('deployment')}")
    print(f"Is Production?  : {z.config.is_production()}")
    
    print("\n# Notice:")
    print("  - Still no 'Ready' banners (Production deployment)")
    print("  - But logger is set to DEBUG for troubleshooting")
    print("  - Explicit logger override works at ANY hierarchy level")
    print("  - Use this for debugging production issues!")

if __name__ == "__main__":
    run_demo()

