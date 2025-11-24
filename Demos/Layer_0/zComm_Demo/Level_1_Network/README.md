## Level 1: Network Basics

Learn core zComm network utilities with simple, focused examples.

### What You'll Learn

- Check port availability across multiple ports
- Understand common service ports (HTTP, PostgreSQL, Redis, etc.)
- Use zComm's network utilities in iteration patterns
- Clean console output with PROD logger

### Demos

#### **`port_check.py`** - Port Availability
- Check 8 common service ports
- Display availability status for each
- Simple loop pattern for scalability

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_1_Network/port_check.py
```

**Expected Output:**
```
=== Port Availability Check ===

Port    80 (HTTP        ): ✓ available
Port   443 (HTTPS       ): ✓ available
Port  8080 (HTTP Alt    ): ✓ available
Port  3000 (Dev Server  ): ✓ available
Port  5432 (PostgreSQL  ): ✗ in use
Port  6379 (Redis       ): ✓ available
Port 27017 (MongoDB     ): ✓ available
Port 56891 (zBifrost    ): ✓ available

Tip: Use z.comm.check_port() before starting servers
```

---

#### **`http_simple.py`** - HTTP POST Request
- Make POST request to public API (httpbin.org)
- No local server setup required
- Demonstrates request/response handling
- Parse JSON responses

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_1_Network/http_simple.py
```

**Expected Output:**
```
=== Simple HTTP POST Demo ===

Sending POST to: https://httpbin.org/post
Payload: {
  "message": "Hello from zComm!",
  "framework": "zCLI",
  "demo": "http_simple"
}

✓ Response received!
  Status code: 200

Server echoed:
  URL: https://httpbin.org/post
  Method: {'demo': 'http_simple', 'framework': 'zCLI', 'message': 'Hello from zComm!'}

Tip: No 'requests' library needed - zComm handles it!
```

### Key Takeaways

- **Port checking:** zComm's `check_port()` works seamlessly in loops without managing socket objects
- **HTTP requests:** Built-in HTTP client eliminates the need for the `requests` library
- **Public APIs:** Use httpbin.org for testing without local server setup

