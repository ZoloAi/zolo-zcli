## Level 2: Services & Error Handling

Learn how to detect and manage local development services, plus handle HTTP errors gracefully.

### What You'll Learn

- Detect if services (PostgreSQL, Redis, MongoDB) are running
- Get connection information automatically
- Cross-platform service detection (macOS/Linux/Windows)
- No manual port probing or OS-specific commands
- Uses PROD logger for clean output

### Installation Requirements

Service management features require optional dependencies:

```bash
# For PostgreSQL support
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git[postgresql]

# For multiple services
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git[postgresql,redis,mongodb]
```

See [Installation Guide](../../../Documentation/INSTALL.md) for complete setup instructions.

### Demos

#### **`service_check.py`** - Service Detection
- Check if PostgreSQL is running
- Get connection info (host, port)
- Safe to run even without PostgreSQL installed
- Works across different platforms

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_2_Services/service_check.py
```

**Expected Output (if PostgreSQL running):**
```
=== Service Status Check ===

Checking postgresql...

✓ POSTGRESQL is running

Connection info:
  Host: localhost
  Port: 5432

You can connect:
  psql -h localhost -p 5432

Tip: zComm detects services across macOS/Linux/Windows
```

**Expected Output (if PostgreSQL not running):**
```
=== Service Status Check ===

Checking postgresql...

✗ POSTGRESQL is not running

Tip: zComm detects services across macOS/Linux/Windows
```

#### **`service_multi.py`** - Multiple Service Detection
- Check PostgreSQL, Redis, and MongoDB
- Iterate through multiple services
- Get summary of development environment
- Practical for team setup scripts

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_2_Services/service_multi.py
```

**Expected Output:**
```
=== Multiple Service Detection ===

Checking development environment...

✓ PostgreSQL Database
  localhost:5432

✗ Redis Cache
  Not running

✗ MongoDB Database
  Not running

========================================
Summary: 1/3 services running

Tip: Check your entire dev stack with one script!
```

> **Note:** Redis and MongoDB are currently stubs in zComm. Only PostgreSQL has full service management implementation.

#### **`http_errors.py`** - HTTP Error Handling
- Test various HTTP error conditions
- 404 Not Found, 500 Server Error
- Invalid URLs and timeouts
- Demonstrates safe error handling (returns `None`)

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_2_Services/http_errors.py
```

**Expected Output:**
```
=== HTTP Error Handling Demo ===

1. Testing 404 Not Found...
   Status: 404 (Not Found)

2. Testing 500 Server Error...
   Status: 500 (Server Error)

3. Testing Invalid URL...
   ✓ Handled gracefully - returned None

4. Testing Timeout (10 second delay with 2s timeout)...
   ✓ Timeout handled gracefully - returned None

==================================================
All errors handled safely - no crashes!

Tip: zComm returns None on errors - always check!
```

### Key Takeaways

- **Service detection:** zComm automatically detects running services without manual configuration
- **Cross-platform:** Works on macOS (Homebrew), Linux (systemd/apt), and Windows services
- **Connection ready:** Get host/port information to connect immediately
- **Safe execution:** Won't fail if service isn't installed
- **Error handling:** HTTP errors return `None` instead of crashing - always check responses
- **Graceful failures:** Timeouts, invalid URLs, and HTTP errors handled safely

