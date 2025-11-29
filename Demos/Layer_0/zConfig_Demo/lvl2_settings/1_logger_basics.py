#!/usr/bin/env python3
"""Level 2: Logger Basics - Separation of Concerns

Use z.logger directly—no setup needed.
This demo shows deployment and logger are INDEPENDENT.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py

Key Discovery:
  - Production deployment (no banners)
  - BUT INFO logging (override default)
  - Proves: deployment ≠ logger verbosity
"""
from zCLI import zCLI


def run_demo():
    # Production deployment + INFO logging (override default)
    zSpark = {
        "deployment": "Production",  # No banners
        "logger": "INFO",            # But verbose logs (override default ERROR)
    }
    z = zCLI(zSpark)

    print("\n# Using the built-in logger in your code:")
    print("# (Watch both console AND log file output)")
    print()

    # Use the logger in your application code - no extra imports needed!
    z.logger.info("Starting application initialization...")
    z.logger.debug("Debug details: configuration loaded") #thi
    z.logger.info("Processing user data...")
    z.logger.warning("Rate limit approaching threshold")
    z.logger.error("Failed to connect to external API")
    z.logger.info("Application startup complete")

    print("\n# What you just discovered:")
    print("  - Production deployment = No banners ✓")
    print("  - Logger: INFO = Detailed logs ✓")
    print("  - They work TOGETHER but are INDEPENDENT")
    print("\n# Try this:")
    print("  - Remove 'logger': 'INFO' to see Production default (ERROR only)")
    print("  - Change to 'Development' deployment to see banners return")


if __name__ == "__main__":
    run_demo()
