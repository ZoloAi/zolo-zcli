#!/usr/bin/env python3
"""
Level 3: Get - Environment Configuration
=========================================

Goal:
    Surface the entire environment configuration (zConfig.environment) via
    z.config.get_environment(), so you can copy/paste access lines for
    deployment, logging, network, and security settings.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl3_get/2_environment.py
"""

from zCLI import zCLI


def run_demo():
    """Display zEnvironment values with copy/paste-ready accessors."""
    z = zCLI()
    # (copy these lines as needed to fetch zEnvironment values)
    env = z.config.get_environment()

    logging_cfg = env.get("logging", {})
    network_cfg = env.get("network", {})
    security_cfg = env.get("security", {})
    performance_cfg = env.get("performance", {})
    websocket_cfg = env.get("websocket", {})

    print("\n# Direct zEnvironment accessors:")
    print(f"deployment        : {env.get('deployment')}")
    print(f"role              : {env.get('role')}")
    print(f"datacenter        : {env.get('datacenter')}")
    print(f"cluster           : {env.get('cluster')}")
    print(f"logging.level     : {logging_cfg.get('level')}")
    print(f"logging.format    : {logging_cfg.get('format')}")
    print(f"logging.file_path : {logging_cfg.get('file_path')}") #empty defaults to ~.zMachine.logs
    print(f"network.host      : {network_cfg.get('host')}")
    print(f"network.port      : {network_cfg.get('port')}")
    print(f"network.external  : {network_cfg.get('external_host')}")
    print(f"security.require_auth : {security_cfg.get('require_auth')}")
    print(f"security.ssl_enabled  : {security_cfg.get('ssl_enabled')}")
    print(f"performance.max_workers : {performance_cfg.get('max_workers')}")
    print(f"performance.timeout    : {performance_cfg.get('timeout')}")
    print(f"websocket.host    : {websocket_cfg.get('host')}")
    print(f"websocket.port    : {websocket_cfg.get('port')}")
    print(f"websocket.auth    : {websocket_cfg.get('require_auth')}")

if __name__ == "__main__":
    run_demo()
