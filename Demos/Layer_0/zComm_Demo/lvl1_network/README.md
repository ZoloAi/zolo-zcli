## Level 1: Network Basics

Learn core zComm network utilities with simple, focused examples.

### What You'll Learn

- Check port availability across multiple ports
- Understand common service ports (HTTP, PostgreSQL, Redis, etc.)
- Use zComm's network utilities in iteration patterns
- Make HTTP requests with all RESTful methods (GET, POST, PUT, PATCH, DELETE)
- Clean console output with PROD logger

### Demos

#### **`port_check.py`** - Port Availability
- Check 8 common service ports
- Display availability status for each
- Simple loop pattern for scalability

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/lvl1_network/1_port_check.py
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
python Demos/Layer_0/zComm_Demo/lvl1_network/2_http_simple.py
```

**Expected Output:**
```
=== Simple HTTP POST Demo ===

Sending POST to: https://httpbin.org/post
Payload: {
  "message": "Hello from zComm!",
  "framework": "zKernel",
  "demo": "http_simple"
}

✓ Response received!
  Status code: 200

Server echoed:
  URL: https://httpbin.org/post
  Method: {'demo': 'http_simple', 'framework': 'zKernel', 'message': 'Hello from zComm!'}

Tip: No 'requests' library needed - zComm handles it!
```

---

#### **`http_methods.py`** - Complete RESTful HTTP Client
- All HTTP methods: GET, POST, PUT, PATCH, DELETE
- Query parameters for GET requests
- JSON payloads for POST/PUT/PATCH
- Complete API interaction workflow

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/lvl1_network/3_http_methods.py
```

**Expected Output:**
```
=== HTTP Methods Demo ===

GET - Retrieve data
✓ {'key': 'value'}

POST - Create resource
✓ {'name': 'Alice'}

PUT - Update entire resource
✓ {'name': 'Alice', 'role': 'Developer'}

PATCH - Partial update
✓ {'role': 'Tech Lead'}

DELETE - Remove resource
✓ Deleted

==================================================
Five methods, one simple pattern
```

### Key Takeaways

- **Port checking:** zComm's `check_port()` works seamlessly in loops without managing socket objects
- **Complete HTTP client:** All RESTful methods (GET, POST, PUT, PATCH, DELETE) available
- **No dependencies:** Built-in HTTP client eliminates the need for the `requests` library
- **Public APIs:** Use httpbin.org for testing without local server setup
- **RESTful workflows:** GET to retrieve, POST to create, PUT/PATCH to update, DELETE to remove

