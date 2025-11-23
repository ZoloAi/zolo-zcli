#!/usr/bin/env python3
"""
Level 2c: User Logger Methods - .dev() and .user()
===================================================

Goal:
    Show custom logger methods for application vs development logs.
    This is a micro step up from basic logger usage - distinguishing
    between development diagnostics and user-facing application logs.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_user_demo.py

Methods:
    z.logger.dev()  - Shows in INFO+, hidden in PROD (for dev diagnostics)
    z.logger.user() - Shows in ALL modes, even PROD (for app messages)

Key Point:
    Use .dev() for debugging/diagnostics during development.
    Use .user() for important application messages that should
    always be visible, even in production.
"""

from zCLI import zCLI


def run_demo():
    # Initialize with PROD level to show the difference
    z = zCLI({
        "logger": "PROD",  # Try changing to "INFO" to see .dev() messages
    })
    
    print("\n# Session configuration:")
    print(f"zLogger level : {z.session.get('zLogger')}")
    
    print("\n# Using custom logger methods:\n")
    
    # Development logs (hidden in PROD, shown in INFO+)
    z.logger.dev("Development diagnostic: Cache hit rate is 87%%")
    z.logger.dev("Debug: Database query took 23ms")
    z.logger.dev("Internal state: Queue has 42 pending items")
    
    print()  # Visual separator
    
    # User application logs (ALWAYS visible, even in PROD)
    z.logger.user("Application started successfully")
    z.logger.user("Loaded configuration from database")
    z.logger.user("Processing 1,247 user records...")
    z.logger.user("Application ready - listening on port 8080")
    
    print("\n# What you just saw:")
    print("  - In PROD mode: Only .user() messages shown (clean!)")
    print("  - .dev() messages are hidden in PROD")
    print("  - Change logger to 'INFO' to see both .dev() and .user()")
    print("\n  Perfect for production apps that need clean, focused logging!")


if __name__ == "__main__":
    run_demo()

