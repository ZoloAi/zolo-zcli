#!/usr/bin/env python3
"""Level 2: zTraceback - Automatic Exception Handling

Enable automatic exception handling with zTraceback: True
No try/except needed - errors launch an interactive menu automatically!

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/4_ztraceback.py

Key Discovery:
  - zTraceback: True intercepts unhandled exceptions
  - Launches interactive menu automatically
  - No try/except code needed in your application
  - Perfect for development and debugging
"""
from zKernel import zKernel


def run_demo():
    print("\n" + "="*60)
    print("  ZTRACEBACK: AUTOMATIC EXCEPTION HANDLING")
    print("="*60)
    
    # Enable automatic exception handling
    zSpark = {
        "deployment": "Production",  # zTraceback is for debugging
        "title": "my-production-api",
        "logger": "INFO",
        "logger_path": "./logs",
        "zTraceback": True,  # Enable automatic exception handling
    }
    z = zKernel(zSpark)
    
    print("\n# Configuration:")
    print("  deployment : Production (clean zTraceback UI)")
    print("  zTraceback : True (automatic exception handling)")
    
    print("\n# What zTraceback does:")
    print("  - Intercepts unhandled exceptions")
    print("  - Launches interactive menu")
    print("  - No try/except needed!")
    
    # Nested function calls to show traceback depth
    def level_3():
        """Innermost function - where error occurs."""
        z.logger.debug("level_3(): About to divide by zero...")
        result = 1 / 0  # This will trigger zTraceback
        return result
    
    def level_2():
        """Middle function."""
        z.logger.debug("level_2(): Calling level_3()...")
        return level_3()
    
    def level_1():
        """Outermost function."""
        z.logger.debug("level_1(): Calling level_2()...")
        return level_2()
    
    print("\n# Triggering error in nested calls:")
    print("  level_1() → level_2() → level_3() → ERROR")
    print("\n# Watch: zTraceback will intercept automatically!\n")
    
    # This will trigger the error and zTraceback menu
    level_1()


if __name__ == "__main__":
    run_demo()
