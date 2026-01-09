#!/usr/bin/env python3
"""Level 2: Logger PROD - Silent Production Logging

Discover the PROD logger level: a unique zCLI feature for production environments
that need complete console silence while capturing full debug logs to file.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_prod.py

Key Discovery:
  - PROD is NOT a standard log level (zCLI innovation)
  - Console: Completely silent (no output)
  - File: DEBUG level (captures everything)
  - Perfect for: APIs, daemons, background services
"""
from zKernel import zKernel


def run_demo():
    print("\n" + "="*60)
    print("  THE PROD LOGGER LEVEL")
    print("="*60)
    
    print("\n# Standard log levels (Python):")
    print("  DEBUG, INFO, WARNING, ERROR, CRITICAL")
    
    print("\n# zCLI adds a 6th level:")
    print("  PROD = Silent console + DEBUG file logging")
    
    print("\n" + "-"*60)
    print("  Running with logger: PROD")
    print("-"*60)

    zSpark = {
        "deployment": "Production",
        "title": "my-production-api",
        "logger": "PROD",  # The special 6th level!
        "logger_path": "./logs",
        "zTraceback": True,
    }
    z = zKernel(zSpark)
    
    print("\n# Notice: Console is SILENT below this line!")
    print("# (All logs go to file only)")
    print()
    
    # These will NOT show in console, but ARE in the log file
    z.logger.debug("DEBUG: Initializing cache...")
    z.logger.info("INFO: API server started on port 8000")
    z.logger.info("INFO: Database connection established")
    z.logger.warning("WARNING: Rate limit at 85%")
    z.logger.error("ERROR: External service timeout")
    z.logger.critical("CRITICAL: Database connection lost!")
    
    print("\n# Did you see any logs above? NO!")
    print("# But they're ALL in the log file at DEBUG level")
    
    print("\n# Use case:")
    print("  Production APIs/services that need:")
    print("  - Zero console noise (silent operation)")
    print("  - Full debug logs for troubleshooting")
    print("  - Perfect for: REST APIs, microservices, daemons")
    
    import os
    cwd = os.getcwd()
    print("\n# Check the log file:")
    print(f"  {cwd}/logs/my-production-api.log")
    print("  (All 6 log messages are there, even DEBUG!)")


if __name__ == "__main__":
    run_demo()

