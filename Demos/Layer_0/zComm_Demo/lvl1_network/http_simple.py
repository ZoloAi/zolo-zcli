#!/usr/bin/env python3
"""
Level 1: Simple HTTP POST
==========================

Goal:
    Make an HTTP POST request to a public API.
    - Shows z.comm.http_post() with real API
    - No local server setup needed (uses httpbin.org)
    - Demonstrates request/response handling
    - Clean JSON output

Run:
    python Demos/Layer_0/zComm_Demo/lvl1_network/http_simple.py
"""

from zCLI import zCLI
import json

def run_demo():
    """Make a simple POST request to httpbin.org."""
    z = zCLI({"logger": "PROD"})

    # Public API for testing HTTP requests
    url = "https://httpbin.org/post"
    
    # Sample data to send
    payload = {
        "message": "Hello from zComm!",
        "framework": "zCLI",
        "demo": "http_simple"
    }
    
    print()
    print("=== Simple HTTP POST Demo ===")
    print()
    print(f"Sending POST to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    # Make the POST request
    response = z.comm.http_post(url, data=payload, timeout=10)
    
    if response is None:
        print("❌ Request failed (no response)")
        return
    
    print(f"✓ Response received!")
    print(f"  Status code: {response.status_code}")
    print()
    
    # Parse JSON response
    try:
        data = response.json()
        
        # Show what httpbin.org echoed back
        print("Server echoed:")
        print(f"  URL: {data.get('url')}")
        print(f"  Method: {data.get('json', {})}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")
        return
    
    print("Tip: No 'requests' library needed - zComm handles it!")
    print()

if __name__ == "__main__":
    run_demo()

