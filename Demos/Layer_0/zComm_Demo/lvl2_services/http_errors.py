#!/usr/bin/env python3
"""
Level 2: HTTP Error Handling
=============================

Goal:
    Show how zComm handles various HTTP errors gracefully.
    - Connection timeouts
    - Invalid URLs
    - HTTP error codes (404, 500)
    - Safe error handling without crashes
    - Clean error reporting

Run:
    python3 Demos/Layer_0/zComm_Demo/lvl2_services/http_errors.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate HTTP error handling."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== HTTP Error Handling Demo ===")
    print()
    
    # Test cases with different error conditions
    tests = [
        ("https://httpbin.org/status/404", 5, "404 Not Found"),
        ("https://httpbin.org/status/500", 5, "500 Server Error"),
        ("https://invalid-domain-xyz.com/api", 3, "Invalid URL"),
        ("https://httpbin.org/delay/10", 2, "Timeout (2s limit)")
    ]
    
    for i, (url, timeout, description) in enumerate(tests, 1):
        print(f"{i}. Testing {description}...")
        response = z.comm.http_post(url, data={}, timeout=timeout)
        
        if response is None:
            print("   ✓ Handled gracefully - returned None")
        else:
            print(f"   Status: {response.status_code}")
        print()
    
    print("=" * 50)
    print("All errors handled safely - no crashes!")
    print()
    print("Tip: zComm returns None on errors - always check!")
    print()

if __name__ == "__main__":
    run_demo()

