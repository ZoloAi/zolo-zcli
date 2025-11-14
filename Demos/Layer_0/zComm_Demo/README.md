## zComm Demo (Layer 0)

These examples load **zConfig + zComm only** to showcase core communication features without the rest of zCLI.

### `simple_http_server.py`
- Minimal HTTP server (Python's built-in `http.server`) that provides a test endpoint.
- Run this **first** before running the HTTP client demo.
- Listens on `http://127.0.0.1:8000` and echoes POST data back.

### `http_client_demo.py`
- Uses zConfig to bootstrap configuration (workspace, `.zEnv`, logger).
- Calls the local HTTP server via `zComm.http_post`—no `requests` library needed.
- Demonstrates complete request/response cycle with status code and JSON response.
- **Requires `simple_http_server.py` to be running first.**

### `port_probe_demo.py`
- Uses `zComm.check_port` to inspect local port availability.
- Binds a temporary socket to illustrate the difference between "free" and "in use".
- Demonstrates network utility functions.

### `service_status_demo.py`
- Checks if local services (PostgreSQL) are running.
- Retrieves connection info if service is available.
- Demonstrates service detection without manual port probing or OS-specific commands.
- **Safe to run even if PostgreSQL is not installed** (reports "not running").

### Shared configuration
- `.zEnv` defines API base URL, endpoint, timeout, and the port to probe.

