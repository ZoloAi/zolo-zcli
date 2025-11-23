#!/usr/bin/env python3
"""
Level 2b: Using zCLI's Built-in Logger
=======================================

Goal:
    Show how to use z.logger in your own code. This is a micro step up from
    the zspark_demo - you learned to CONTROL the logger, now learn to USE it.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_demo.py

Key Point:
    No need to import logging, configure handlers, or set up formatters.
    zCLI's logger is already configured and ready to use.
"""

from zCLI import zCLI


def run_demo():
    # Initialize with INFO level (micro step up from PROD in zspark_demo)
    z = zCLI({
        "logger": "INFO",  # Try changing to "DEBUG" or "PROD" to see differences
    })

    print("\n# Session configuration:")
    print(f"zLogger level : {z.session.get('zLogger')}")

    print("\n# Using the built-in logger in your code:")
    print("# (Watch both console AND log file output)\n")

    # Use the logger in your application code - no extra imports needed!
    z.logger.info("Starting application initialization...")
    z.logger.debug("Debug details: configuration loaded")
    z.logger.info("Processing user data...")
    z.logger.warning("Rate limit approaching threshold")
    z.logger.error("Failed to connect to external API")
    z.logger.info("Application startup complete")

    print("\n# What you just saw:")
    print("  - All log levels work out of the box")
    print("  - Logs go to both console AND file")
    print("  - No logging.getLogger() or configuration needed")
    print("  - Try changing 'logger' to 'DEBUG' or 'PROD' and run again")


if __name__ == "__main__":
    run_demo()
