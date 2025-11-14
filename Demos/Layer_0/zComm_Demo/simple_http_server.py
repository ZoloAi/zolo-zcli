#!/usr/bin/env python3
"""
Simple HTTP Server for zComm Demo

This is a minimal HTTP server that provides a test endpoint for the
zComm HTTP client demo. It's intentionally simple—just Python's built-in
http.server with a custom handler.

Run this first:
    python Demos/Layer_0/zComm_Demo/simple_http_server.py

Then in another terminal, run the client:
    python Demos/Layer_0/zComm_Demo/http_client_demo.py
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime


class SimpleAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that echoes POST data back."""

    def do_POST(self):
        """Handle POST requests - echo back the data with a timestamp."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            received_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            received_data = {"raw": post_data.decode('utf-8', errors='ignore')}
        
        # Echo back with server info
        response = {
            "status": "received",
            "timestamp": datetime.now().isoformat(),
            "server": "simple_http_server.py",
            "received_data": received_data,
            "message": f"Server received your message: {received_data.get('message', 'no message')}"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] POST received: {received_data}")

    def log_message(self, format, *args):
        """Suppress default server logs for cleaner output."""
        pass


def main():
    host = '127.0.0.1'
    port = 8000
    
    server = HTTPServer((host, port), SimpleAPIHandler)
    print(f"=== Simple HTTP Server ===")
    print(f"Listening on http://{host}:{port}")
    print(f"Ready to receive POST requests from zComm client demo")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[Server] Shutting down...")
        server.shutdown()
        print("[Server] Stopped")


if __name__ == "__main__":
    main()

