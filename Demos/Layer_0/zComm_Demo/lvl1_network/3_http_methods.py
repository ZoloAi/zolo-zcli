#!/usr/bin/env python3
"""Level 1: All HTTP Methods

Complete RESTful HTTP client - all 5 standard methods in one pattern.

Run:
    python Demos/Layer_0/zComm_Demo/lvl1_network/3_http_methods.py

Key Discovery:
  - All 5 HTTP methods: GET, POST, PUT, PATCH, DELETE
  - Consistent API across all methods
  - One simple pattern for all RESTful operations
"""

from zCLI import zCLI

def run_demo():
    """Showcase all 5 HTTP methods."""
    # Consistent zSpark pattern
    zSpark = {
        "deployment": "Production",
        "title": "http-methods",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zCLI(zSpark)

    # GET - Retrieve data
    response = z.comm.http_get("https://httpbin.org/get", params={"key": "value"})
    if response:
        print(f"GET:    ✓ {response.json()['args']}")

    # POST - Create resource
    response = z.comm.http_post("https://httpbin.org/post", data={"name": "Alice"})
    if response:
        print(f"POST:   ✓ {response.json()['json']}")

    # PUT - Update entire resource
    response = z.comm.http_put("https://httpbin.org/put", data={"name": "Alice", "role": "Developer"})
    if response:
        print(f"PUT:    ✓ {response.json()['json']}")

    # PATCH - Partial update
    response = z.comm.http_patch("https://httpbin.org/patch", data={"role": "Tech Lead"})
    if response:
        print(f"PATCH:  ✓ {response.json()['json']}")

    # DELETE - Remove resource
    response = z.comm.http_delete("https://httpbin.org/delete")
    if response:
        print(f"DELETE: ✓ Resource removed")

    print("\nFive methods, one simple pattern.\n")

if __name__ == "__main__":
    run_demo()
