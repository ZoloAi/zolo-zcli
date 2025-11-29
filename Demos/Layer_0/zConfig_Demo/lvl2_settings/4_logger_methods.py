#!/usr/bin/env python3
"""Level 2: Logger Methods - Deployment-Aware Logging

Learn custom logger methods that respect deployment mode:
    z.logger.dev()  - Hidden in Production, shown in Debug/Info
    z.logger.user() - Always visible, even in Production

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/4_logger_methods.py

When to use:
    .dev()  - Development diagnostics, debug info, internal state
    .user() - Application events, user-facing messages, important logs

Key Point:
    These methods check DEPLOYMENT mode, not log level!
    Perfect for keeping production logs clean while showing details in development."""

from zCLI import zCLI


def run_demo():
    # Production deployment to demonstrate .dev() suppression
    z = zCLI({
        "deployment": "Production",  # Try changing to "Debug" to see .dev() messages
        # logger: "ERROR" is implicit in Production
    })
    
    print("\n# Session configuration:")
    print(f"Deployment    : {z.config.get_environment('deployment')}")
    print(f"zLogger level : {z.session.get('zLogger')}")
    
    print("\n# Using custom logger methods:\n")
    
    # Development logs (hidden in Production, shown in Debug/Info)
    z.logger.dev("Development diagnostic: Cache hit rate is 87%%")
    z.logger.dev("Debug: Database query took 23ms")
    z.logger.dev("Internal state: Queue has 42 pending items")
    
    print()  # Visual separator
    
    # User application logs (ALWAYS visible, even in Production)
    z.logger.user("Application started successfully")
    z.logger.user("Loaded configuration from database")
    z.logger.user("Processing 1,247 user records...")
    z.logger.user("Application ready - listening on port 8080")
    
    print("\n# What you just saw:")
    print("  - In Production: Only .user() messages shown (clean!)")
    print("  - .dev() messages are hidden in Production")
    print("  - Change deployment to 'Debug' to see both .dev() and .user()")
    print("\n  Perfect for production apps that need clean, focused logging!")


if __name__ == "__main__":
    run_demo()

