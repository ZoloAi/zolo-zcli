#!/usr/bin/env python3
"""Level 1: Simple HTTP GET

After checking ports, let's make HTTP requests - the foundation of API communication.

Run:
    python Demos/Layer_0/zComm_Demo/lvl1_network/2_http_get.py

Key Discovery:
  - Make HTTP GET requests with one line
  - No requests library needed
  - Built-in JSON parsing
  - Returns None on failure (no crashes)
"""

from zKernel import zKernel

def run_demo():
    """Make a simple GET request to a public API."""
    # Consistent zSpark pattern
    zSpark = {
        "deployment": "Production",
        "title": "http-get",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zKernel(zSpark)

    # Public API for testing (no auth needed)
    url = "https://httpbin.org/get"
    
    # Make GET request with query parameters
    response = z.comm.http_get(url, params={"message": "Hello from zComm!"})
    
    if response:
        data = response.json()
        print(f"\n✓ GET request successful!")
        print(f"  Status: {response.status_code}")
        print(f"  Echoed Response: {data.get('args')}\n")

if __name__ == "__main__":
    run_demo()

