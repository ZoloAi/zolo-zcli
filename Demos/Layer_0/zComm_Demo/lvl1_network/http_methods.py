#!/usr/bin/env python3
"""
Level 1: HTTP Methods (GET, POST, PUT, PATCH, DELETE)
=======================================================

Goal:
    Complete RESTful HTTP client - one line per method.
    Declare what you want - zComm handles the rest.

Run:
    python3 Demos/Layer_0/zComm_Demo/lvl1_network/http_methods.py
"""

from zCLI import zCLI

def run_demo():
    """Declare HTTP requests - zComm executes."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== HTTP Methods Demo ===")
    print()
    
    # Declare: GET with query params
    print("GET - Retrieve data")
    response = z.comm.http_get("https://httpbin.org/get", params={"key": "value"})
    print(f"✓ {response.json()['args']}" if response else "✗ Failed")
    print()
    
    # Declare: POST with JSON data
    print("POST - Create resource")
    response = z.comm.http_post("https://httpbin.org/post", data={"name": "Alice"})
    print(f"✓ {response.json()['json']}" if response else "✗ Failed")
    print()
    
    # Declare: PUT entire resource
    print("PUT - Update entire resource")
    response = z.comm.http_put("https://httpbin.org/put", data={"name": "Alice", "role": "Developer"})
    print(f"✓ {response.json()['json']}" if response else "✗ Failed")
    print()
    
    # Declare: PATCH partial update
    print("PATCH - Partial update")
    response = z.comm.http_patch("https://httpbin.org/patch", data={"role": "Tech Lead"})
    print(f"✓ {response.json()['json']}" if response else "✗ Failed")
    print()
    
    # Declare: DELETE resource
    print("DELETE - Remove resource")
    response = z.comm.http_delete("https://httpbin.org/delete")
    print("✓ Deleted" if response else "✗ Failed")
    print()
    
    print("=" * 50)
    print("Five methods, one simple pattern")
    print()

if __name__ == "__main__":
    run_demo()

