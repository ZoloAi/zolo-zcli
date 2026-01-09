#!/usr/bin/env python3
"""Level 3: Get - Workspace Variables (Dotenv)

Learn how zCLI automatically loads .env/.zEnv files from your workspace.
No python-dotenv import needed - it just works!

Run:
    cd Demos/Layer_0/zConfig_Demo/lvl3_get
    python3 3_dotenv.py

Key Discovery:
  - .env/.zEnv files auto-load from workspace (CS convention)
  - Access via z.config.environment.get_env_var()
  - Perfect for secrets, API keys, feature flags
  - Layer 4 of the configuration hierarchy
"""

from zKernel import zKernel
import os
from pathlib import Path


def run_demo():
    # Change to demo directory so .zEnv is found
    demo_dir = Path(__file__).parent
    original_dir = Path.cwd()
    os.chdir(demo_dir)
    print("\n" + "="*60)
    print("  WORKSPACE VARIABLES (.zEnv)")
    print("="*60)

    # Consistent zSpark pattern
    zSpark = {
        "deployment": "Production",
        "title": "dotenv-demo",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zKernel(zSpark)

    print("\n# Dotenv file location:")
    print("  This folder contains a .zEnv file")
    print("  zCLI found and loaded it automatically!")
    print("  (.zEnv is preferred, but .env also works)")

    print("\n# APPLICATION SETTINGS (from .zEnv):")
    # Get values with fallback defaults
    app_name = z.config.environment.get_env_var("APP_NAME", "Unknown")
    app_version = z.config.environment.get_env_var("APP_VERSION", "0.0.0")
    app_mode = z.config.environment.get_env_var("APP_MODE", "production")
    
    print(f"  APP_NAME      : {app_name}")
    print(f"  APP_VERSION   : {app_version}")
    print(f"  APP_MODE      : {app_mode}")

    print("\n# FEATURE FLAGS (from .zEnv):")
    # Boolean conversion for feature flags
    debug_mode = z.config.environment.get_env_var("FEATURE_DEBUG", "false").lower() == "true"
    verbose_mode = z.config.environment.get_env_var("FEATURE_VERBOSE", "false").lower() == "true"
    
    print(f"  FEATURE_DEBUG   : {debug_mode}")
    print(f"  FEATURE_VERBOSE : {verbose_mode}")

    print("\n# API SETTINGS (from .zEnv):")
    api_endpoint = z.config.environment.get_env_var("API_ENDPOINT", "https://default.com")
    api_timeout = int(z.config.environment.get_env_var("API_TIMEOUT", "10"))
    
    print(f"  API_ENDPOINT  : {api_endpoint}")
    print(f"  API_TIMEOUT   : {api_timeout} seconds")

    print("\n# MISSING KEY (not in .zEnv):")
    # This key doesn't exist, so we get the fallback
    missing_key = z.config.environment.get_env_var("DOES_NOT_EXIST", "fallback_value")
    print(f"  DOES_NOT_EXIST: {missing_key} (fallback)")

    print("\n# What you discovered:")
    print("  ✓ Dotenv convention (.env/.zEnv) auto-loads")
    print("  ✓ No python-dotenv import needed")
    print("  ✓ Access via get_env_var(key, default)")
    print("  ✓ Perfect for secrets (add to .gitignore!)")
    print("  ✓ Layer 4: Workspace-specific configuration")
    print("  ✓ Overrides global settings, overridden by zSpark")

    print("\n# Usage pattern:")
    print("  value = z.config.environment.get_env_var('KEY', 'default')")
    print("  # Returns the value from dotenv file or the default")

    print("\n# Try editing .zEnv:")
    print("  Change APP_NAME to your name and run again!")
    print("  (.env files work the same way)")

    # Restore original directory
    os.chdir(original_dir)


if __name__ == "__main__":
    run_demo()

