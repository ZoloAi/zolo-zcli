#!/usr/bin/env python3
"""
zComm Port Probe Demo

Goal:
    Illustrate zComm's `check_port` helper. We check a port, bind a temporary
    socket to occupy it, check again, then release it—all using zComm's API.

Usage:
    python Demos/Layer_0/zComm_Demo/port_probe_demo.py
"""

from __future__ import annotations

import socket
import time
from pathlib import Path
from types import SimpleNamespace

from zCLI.subsystems.zConfig import zConfig
from zCLI.subsystems.zComm import zComm


DEMO_ROOT = Path(__file__).resolve().parent
ZSPARK = {
    "zSpace": str(DEMO_ROOT),
    "env_file": str(DEMO_ROOT / ".zEnv"),
    "zMode": "Terminal",
}


class MinimalZCLI(SimpleNamespace):
    """Loads zConfig + zComm for network utilities."""

    def __init__(self) -> None:
        super().__init__()
        self.session = {}
        self.logger = None
        self.zspark_obj = ZSPARK
        self.config = zConfig(self, zSpark_obj=ZSPARK)
        self.comm = zComm(self)


def occupy_port(port: int) -> socket.socket:
    """Bind a socket to occupy the port (returns the socket for later close)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", port))
    sock.listen(1)
    return sock


def run_demo() -> None:
    app = MinimalZCLI()
    env = app.config.environment
    port = int(env.get_env_var("COMM_PORT_CHECK", "8765"))

    print("=== zComm Port Probe Demo ===")
    print(f"Target port: {port}")
    print()

    available_before = app.comm.check_port(port)
    print(f"Before binding socket  : {'available' if available_before else 'in use'}")

    try:
        sock = occupy_port(port)
    except OSError as exc:
        print(f"Failed to bind temporary socket on port {port}: {exc}")
        return

    try:
        available_during = app.comm.check_port(port)
        print(f"While socket is bound  : {'available' if available_during else 'in use'}")
    finally:
        sock.close()
        time.sleep(0.1)  # give OS a moment to release the port

    available_after = app.comm.check_port(port)
    print(f"After releasing socket : {'available' if available_after else 'in use'}")


if __name__ == "__main__":
    run_demo()

