#!/usr/bin/env python3
"""
zComm HTTP Client Demo

Goal:
    Show how to call an HTTP endpoint without importing `requests`.
    We rely on zConfig for setup (workspace, .zEnv) and zComm for the HTTP client.

Setup:
    1. Start the test server:
       python Demos/Layer_0/zComm_Demo/simple_http_server.py
    
    2. Run this client (in another terminal):
       python Demos/Layer_0/zComm_Demo/http_client_demo.py
"""

from __future__ import annotations

from json import dumps
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
    """Small host object: load zConfig, then zComm."""

    def __init__(self) -> None:
        super().__init__()
        self.session = {}
        self.logger = None
        self.zspark_obj = ZSPARK
        self.config = zConfig(self, zSpark_obj=ZSPARK)
        self.comm = zComm(self)


def run_demo() -> None:
    app = MinimalZCLI()
    env = app.config.environment

    base_url = env.get_env_var("COMM_API_BASE", "https://httpbin.org").rstrip("/")
    endpoint = env.get_env_var("COMM_API_ENDPOINT", "/post")
    timeout = int(env.get_env_var("COMM_TIMEOUT", "5"))

    url = f"{base_url}{endpoint}"
    payload = {
        "message": "Hello from zComm",
        "deployment": env.get("deployment", "Debug"),
        "hostname": app.config.get_machine("hostname"),
    }

    print("=== zComm HTTP Client Demo ===")
    print(f"POST {url}")
    print(f"Payload: {payload}")
    print()

    response = app.comm.http_post(url, data=payload, timeout=timeout)
    if response is None:
        print("Request failed or returned no response.")
        return

    print(f"Status code: {response.status_code}")
    try:
        response_json = response.json()
    except ValueError:
        print("Response was not JSON. Raw text:")
        print(response.text)
        return

    # Show a small subset of the echoed JSON for readability.
    snippet = {
        "url": response_json.get("url"),
        "json": response_json.get("json"),
        "headers": {
            "Content-Type": response_json.get("headers", {}).get("Content-Type"),
        },
    }
    print("Response JSON snippet:")
    print(dumps(snippet, indent=2))


if __name__ == "__main__":
    run_demo()

