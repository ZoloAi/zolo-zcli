#!/usr/bin/env python3
"""
Simple zConfig demo (#2):

Goal:
    Show how a tiny inventory script can read environment settings from a `.zEnv`
    file and machine information without pulling in any other zCLI subsystem.

Usage:
    python Demos/Layer_0/zConfig_Demo/simple_inventory_demo.py

What it demonstrates:
    - zConfig auto-detects machine info (hostname, OS, etc.)
    - zConfig loads `.zEnv` values (deployment mode, thresholds)
    - The script prints a human-readable summary
    - No persistence or advanced logic—just configuration consumption
"""

from __future__ import annotations

from pathlib import Path
from random import randint
from types import SimpleNamespace

from zCLI.subsystems.zConfig import zConfig


DEMO_ROOT = Path(__file__).resolve().parent
ZSPARK = {
    "zSpace": str(DEMO_ROOT),
    "env_file": str(DEMO_ROOT / ".zEnv"),
    "zMode": "Terminal",
}


class ConfigOnlyShell(SimpleNamespace):
    """The tiniest possible host object—only zConfig is loaded."""

    def __init__(self) -> None:
        super().__init__()
        self.session = {}
        self.logger = None
        self.zspark_obj = ZSPARK
        self.config = zConfig(self, zSpark_obj=ZSPARK)


def fake_inventory() -> list[dict[str, int | str]]:
    """Tiny in-memory inventory list for demonstration."""
    return [
        {"item": "markers", "quantity": randint(0, 10)},
        {"item": "erasers", "quantity": randint(0, 10)},
        {"item": "laptops", "quantity": randint(0, 10)},
    ]


def run_demo() -> None:
    shell = ConfigOnlyShell()
    machine = shell.config.get_machine()
    env_config = shell.config.environment

    deployment = env_config.get("deployment", "Debug")
    threshold = int(env_config.get_env_var("APP_THRESHOLD", "5"))

    print("=== zConfig Demo (Simple) ===")
    print(f"Machine hostname : {machine.get('hostname')}")
    print(f"Deployment mode  : {deployment}")
    print(f"Stock threshold  : {threshold}")
    print()

    items = fake_inventory()
    low_stock = [item for item in items if item["quantity"] <= threshold]

    print("Low stock items:")
    for item in low_stock:
        print(f"  - {item['item']}: {item['quantity']} remaining")

    if not low_stock:
        print("  All items are above threshold!")


if __name__ == "__main__":
    run_demo()

