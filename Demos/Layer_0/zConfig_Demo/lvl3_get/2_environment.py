#!/usr/bin/env python3
"""Level 3: Get - Environment Configuration

Learn to read environment configuration values.
While zMachine identifies hardware, zEnvironment defines your working context:
deployment mode, logging levels, network settings, and more.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl3_get/2_environment.py

Key Discovery:
  - Access environment config with z.config.get_environment()
  - Deployment, logging, network, security, performance settings
  - Stored persistently across all projects
  - Copy-paste any accessor line you need
"""

from zCLI import zCLI


def run_demo():
    print("\n" + "="*60)
    print("  YOUR ENVIRONMENT CONFIGURATION")
    print("="*60)

    # Override environment defaults using zSpark (highest priority layer!)
    # This demonstrates the 5-layer configuration hierarchy:
    #   1. Defaults (lowest)
    #   2. System environment variables
    #   3. zConfig.environment.yaml
    #   4. Project .zEnv file
    #   5. zSpark (highest) ← WE ARE HERE!
    #
    # By setting deployment: "Production" in zSpark, we override
    # whatever is in zConfig.environment.yaml for THIS session only.
    
    zSpark = {
        "deployment": "Production",  # Override: Force Production mode for this demo
        "title": "environment-demo",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zCLI(zSpark)

    # Get all environment values at once (copy this pattern)
    env = z.config.get_environment()
    
    print("\n# zSpark Override in Action:")
    print(f"  deployment set to: {env.get('deployment')} (from zSpark, not environment.yaml)")
    print("  → This override only affects THIS session")
    print("  → Your zConfig.environment.yaml remains unchanged")

    print("\n# DEPLOYMENT:")
    print(f"  deployment        : {env.get('deployment')}")
    print(f"  role              : {env.get('role')}")

    print("\n# LOGGING:")
    logging_cfg = env.get("logging", {})
    print(f"  level             : {logging_cfg.get('level')}")
    print(f"  format            : {logging_cfg.get('format')}")
    print(f"  file_enabled      : {logging_cfg.get('file_enabled')}")

    print("\n# NETWORK:")
    network_cfg = env.get("network", {})
    print(f"  host              : {network_cfg.get('host')}")
    print(f"  port              : {network_cfg.get('port')}")
    print(f"  external_host     : {network_cfg.get('external_host')}")

    print("\n# SECURITY:")
    security_cfg = env.get("security", {})
    print(f"  require_auth      : {security_cfg.get('require_auth')}")
    print(f"  ssl_enabled       : {security_cfg.get('ssl_enabled')}")

    print("\n# PERFORMANCE:")
    performance_cfg = env.get("performance", {})
    print(f"  max_workers       : {performance_cfg.get('max_workers')}")
    print(f"  timeout           : {performance_cfg.get('timeout')}")

    print("\n# WEBSOCKET:")
    websocket_cfg = env.get("websocket", {})
    print(f"  host              : {websocket_cfg.get('host')}")
    print(f"  port              : {websocket_cfg.get('port')}")
    print(f"  require_auth      : {websocket_cfg.get('require_auth')}")

    print("\n# CUSTOM FIELDS:")
    print(f"  datacenter        : {env.get('datacenter')}")
    print(f"  cluster           : {env.get('cluster')}")
    
    print("\n# Nested Access Pattern (for complex settings):")
    print("  # Method 1: Step by step")
    logging_dict = env.get('logging', {})
    log_level = logging_dict.get('level')
    print(f"  logging_dict = env.get('logging', {{}})  → {logging_dict}")
    print(f"  log_level = logging_dict.get('level')    → {log_level}")
    
    print("\n  # Method 2: Chained access (one line)")
    log_level_direct = env.get('logging', {}).get('level')
    print(f"  log_level = env.get('logging', {{}}).get('level')  → {log_level_direct}")
    
    print("\n  # Both methods give the same result!")
    print(f"  Match: {log_level == log_level_direct} ✓")

    print("\n# What you discovered:")
    print("  ✓ zEnvironment defines your working context")
    print("  ✓ Deployment mode controls app behavior (Development/Testing/Production)")
    print("  ✓ 5-layer hierarchy: zSpark (highest) overrides environment.yaml")
    print("  ✓ Settings persist across all projects")
    print("  ✓ Grouped by category: deployment, logging, network, security, performance")
    print("  ✓ Custom fields supported (datacenter, cluster, etc.)")
    print("  ✓ Copy-paste any accessor line you need")
    print("  ✓ Per-project overrides covered in Level 4 (.zEnv files)")

    print("\n# Usage pattern:")
    print("  env = z.config.get_environment()      # Get all values")
    print("  deployment = env.get('deployment')    # Get single value")
    print("  # Or use nested access:")
    print("  logging = env.get('logging', {}).get('level')")

if __name__ == "__main__":
    run_demo()
