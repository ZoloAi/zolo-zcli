#!/usr/bin/env python3
"""
Level 0: Hello zConfig
======================

Goal:
    The tiniest possible introduction to zConfig.
    - Initialize zCLI (which auto-loads zConfig)
    - Read one machine value and one environment value
    - Print them out with zero setup

Run:
    python Demos/Layer_0/zConfig_Demo/Level_0_Hello/hello_config.py
"""

from zCLI import zCLI

def run_demo():
    """Initialize zCLI and show the first bits of config insight."""
    z = zCLI()

    hostname = z.config.get_machine("hostname")
    deployment = z.config.environment.get("deployment", "Debug")
    workspace_dir = z.config.sys_paths.workspace_dir
    
    print()
    print("=== Level 0: Hello zConfig ===")
    print(f"Hostname   : {hostname}")
    print(f"Deployment : {deployment}")
    print(f"Workspace  : {workspace_dir}")
    print()
    print("Tip: Everything above came from zConfig with zero setup.")
    print()

if __name__ == "__main__":
    run_demo()
