## zComm Demo (Layer 0)

These examples showcase zComm's core communication features.

### Level 0: Hello

**`Level_0_Hello/hello_comm.py`**
- The simplest possible introduction to zComm
- Shows zComm auto-initializes with zCLI
- Checks if a port is available
- Zero configuration required

### Level 1: Network Basics

**`Level_1_Network/port_check.py`**
- Check multiple ports for availability
- Demonstrates iteration with `z.comm.check_port()`
- Common service ports (HTTP, PostgreSQL, Redis, etc.)
- Clean, scannable output

**`Level_1_Network/http_simple.py`**
- Make HTTP POST requests to public APIs
- Uses httpbin.org (no server setup needed)
- Demonstrates JSON request/response handling
- No `requests` library required

### Level 2: Services & Error Handling

**`Level_2_Services/service_check.py`**
- Detect if PostgreSQL is running
- Get service connection information
- Cross-platform service detection
- No manual port probing or OS commands

**`Level_2_Services/service_multi.py`**
- Check multiple services in one pass
- PostgreSQL, Redis, MongoDB detection
- Practical for development environment setup
- Clean, scannable output with summary

**`Level_2_Services/http_errors.py`**
- HTTP error handling (404, 500, timeouts)
- Invalid URLs and connection failures
- Safe error handling without crashes
- Always check for `None` responses

### Level 3: Service Lifecycle

**`Level_3_Lifecycle/service_start.py`**
- Programmatically start services
- Check status before/after operations
- Handle start failures gracefully
- Get connection info for started services
- Full lifecycle control from code

### Level 4+: Advanced Demos

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

