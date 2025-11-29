#!/usr/bin/env python3
"""Level 1: Initialize - Deployment Modes

Goal:
    Learn about the three deployment modes and experience Testing mode.
    Testing mode gives you detailed logs without banner noise.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment_modes.py
"""

from zCLI import zCLI

def run_demo():
    # Three deployment modes available (uncomment to try each):
    # "Development" - Full output: banners + INFO logs (local dev)
    # "Testing"     - Clean logs only: no banners + INFO logs (staging/QA)
    # "Production"  - Minimal: no banners + ERROR logs (production)

    zSpark = {
        # "deployment": "Development",  # Full output
        #"deployment": "Testing",       # Clean logs (default for this demo)
        "deployment": "Production",   # Minimal output
    }
    z = zCLI(zSpark)

    print("\n# Session state:")
    print(f"Deployment      : {z.config.get_environment('deployment')}")
    print(f"Logger level    : {z.session.get('zLogger')}")
    print(f"Banners shown   : {z.logger.should_show_sysmsg()}")
    print(f"Is Production?  : {z.config.is_production()}")
    print(f"Is Testing?     : {z.config.environment.is_testing()}")

    print("\n# Notice:")
    print("  - No banners/sysmsg in Testing mode")
    print("  - Logger defaults to INFO (detailed logs)")
    print("  - Perfect for staging/QA environments")
    print("  - Try uncommenting other deployments to compare!")

    print("\n# Logger output example:")
    z.logger.info("INFO: Application started")
    z.logger.warning("WARNING: Rate limit high")
    z.logger.error("ERROR: Connection failed")


if __name__ == "__main__":
    run_demo()
