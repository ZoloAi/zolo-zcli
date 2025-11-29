#!/usr/bin/env python3
"""Level 2: Logger Basics - Your First Logs

Learn to use the built-in logger. No configuration needed!

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py
"""
from zCLI import zCLI


def run_demo():
    print("\n" + "="*60)
    print("  YOUR FIRST LOGS")
    print("="*60)
    zSpark = {
        "deployment": "Production",   # Minimal (active)
        "logger": "INFO",           # But with DEBUG logging for troubleshooting
    }
    z = zCLI(zSpark)

    print("\n# Using z.logger in your code:")
    print("# Five log levels, from most to least verbose:\n")

    z.logger.debug("DEBUG: Detailed diagnostic information")
    z.logger.info("INFO: Application status update")
    z.logger.warning("WARNING: Something needs attention")
    z.logger.error("ERROR: Something failed")
    z.logger.critical("CRITICAL: System failure!")

    print("\n# What you just learned:")
    print("  ✓ z.logger is built-in, no imports needed")
    print("  ✓ Five log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    print("  ✓ In Development mode, INFO and above are shown")
    print("  ✓ Logs appear in console AND log file automatically")

    print("\n# Where are logs stored?")
    print("  Remember from Level 1? zCLI support folder:")
    print("  → macOS: ~/Library/Application Support/zolo-zcli/logs/")
    print("  → Your logs: zcli-app.log")
    print("  → Framework logs: zcli-framework.log (automatic)")

    print("\n# Next:")
    print("  Learn how deployment mode affects logging defaults!")


if __name__ == "__main__":
    run_demo()
