#!/usr/bin/env python3
"""Level 2: Logger Advanced - Full Control

Learn to customize everything: deployment, logger level, session title, and log path.
This demo shows the complete separation between deployment and logging.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/2_logger_advanced.py

Key Discovery:
  - Production deployment (no banners)
  - INFO logging (override default ERROR)
  - Custom session title (custom log filename)
  - Custom log path (save logs wherever you want)
"""
from zCLI import zCLI


def run_demo():
    print("\n" + "="*60)
    print("  ADVANCED LOGGER CONFIGURATION")
    print("="*60)

    # Full control via zSpark
    zSpark = {
        "deployment": "Production",  # No banners/sysmsg
        "title": "my-production-api",  # Filename: my-production-api.log
        "logger": "INFO",  # Override Production default (ERROR)
        "logger_path": "./logs",  # Directory: ./logs/
    }
    z = zCLI(zSpark)

    print("\n# Configuration:")
    print("  deployment  : Production")
    print("  logger      : INFO")
    print("  title       : my-production-api")
    print("  logger_path : ./logs")
    print("  → Result    : ./logs/my-production-api.log")

    print("\n# Application logs:")
    z.logger.debug("DEBUG: Cache initialization complete")
    z.logger.info("INFO: API server started on port 8000")
    z.logger.info("INFO: Connected to database successfully")
    z.logger.warning("WARNING: Rate limit at 80% capacity")
    z.logger.error("ERROR: Failed to connect to external service")

    print("\n# Key concepts:")
    print("  logger_path = WHERE (directory)")
    print("  title       = WHAT (filename)")
    print("  Result      = logger_path/title.log")
    
    import os
    print(f"\n# Check your logs:")
    print(f"  {os.getcwd()}/logs/my-production-api.log")

if __name__ == "__main__":
    run_demo()
