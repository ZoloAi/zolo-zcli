# GitHub Issue: Add Full HTTP Method Support to zComm

**Title:**
```
Add GET, PUT, DELETE, and PATCH HTTP methods to zComm HTTP client
```

**Labels:** `enhancement`, `subsystem:zComm`, `http-client`

---

## Summary

zComm currently only implements `http_post()` for HTTP requests. To provide a complete HTTP client experience, we need to add support for GET, PUT, DELETE, and PATCH methods. This will enable users to interact with RESTful APIs without requiring the `requests` library.

## Current State

**Currently Implemented:**
- ✅ `z.comm.http_post(url, data={}, timeout=10)` - POST requests with JSON payload

**Missing Methods:**
- ❌ `http_get()` - Retrieve resources
- ❌ `http_put()` - Update/replace resources
- ❌ `http_delete()` - Remove resources
- ❌ `http_patch()` - Partial updates

## Proposed API

### GET Method
```python
response = z.comm.http_get(
    url="https://api.example.com/users/123",
    params={"include": "profile"},  # Query parameters
    headers={},                      # Optional custom headers
    timeout=10
)
```

**Returns:** Response object or `None` on failure

---

### PUT Method
```python
response = z.comm.http_put(
    url="https://api.example.com/users/123",
    data={"name": "John Doe", "email": "john@example.com"},
    headers={},
    timeout=10
)
```

**Returns:** Response object or `None` on failure

---

### DELETE Method
```python
response = z.comm.http_delete(
    url="https://api.example.com/users/123",
    headers={},
    timeout=10
)
```

**Returns:** Response object or `None` on failure

---

### PATCH Method
```python
response = z.comm.http_patch(
    url="https://api.example.com/users/123",
    data={"email": "newemail@example.com"},  # Partial update
    headers={},
    timeout=10
)
```

**Returns:** Response object or `None` on failure

---

## Implementation Requirements

### 1. **Consistent API Design**
All methods should follow the same pattern as `http_post()`:
- Accept `url` (required), `data` or `params` (optional), `headers` (optional), `timeout` (default: 10)
- Return Response object with `.status_code`, `.json()`, `.text` or `None` on failure
- Handle all error cases gracefully (timeouts, network errors, invalid URLs)
- Use PROD logger for clean output

### 2. **Error Handling**
Maintain current error handling strategy:
- Connection timeouts → `None`
- Invalid URLs/DNS failures → `None`
- Network errors → `None`
- HTTP error codes (404, 500, etc.) → Response object (user checks `.status_code`)

### 3. **Query Parameters (GET)**
GET requests should support query parameters:
```python
# Should translate to: https://api.example.com/search?q=python&limit=10
response = z.comm.http_get(
    "https://api.example.com/search",
    params={"q": "python", "limit": 10}
)
```

### 4. **Custom Headers**
All methods should support custom headers:
```python
response = z.comm.http_get(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token123"}
)
```

### 5. **Content-Type Handling**
- POST/PUT/PATCH should default to `Content-Type: application/json`
- Allow override via custom headers if needed
- GET/DELETE typically don't send body data

---

## Acceptance Criteria

- [ ] `http_get()` implemented with params support
- [ ] `http_put()` implemented with JSON data support
- [ ] `http_delete()` implemented
- [ ] `http_patch()` implemented with JSON data support
- [ ] All methods return Response object or `None` on failure
- [ ] Query parameters properly encoded in GET requests
- [ ] Custom headers supported across all methods
- [ ] Error handling consistent with `http_post()`
- [ ] Documentation updated in `zComm_GUIDE.md`
- [ ] Demo created: `http_methods.py` showing all HTTP verbs
- [ ] All methods tested with httpbin.org endpoints

---

## Demo Impact

### Before (Current State)
```python
# Only POST available
response = z.comm.http_post("https://httpbin.org/post", data={})
```

### After (Proposed)
```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# GET - Retrieve data
users = z.comm.http_get("https://api.example.com/users")

# POST - Create new resource
new_user = z.comm.http_post(
    "https://api.example.com/users",
    data={"name": "Alice"}
)

# PUT - Update entire resource
updated = z.comm.http_put(
    "https://api.example.com/users/123",
    data={"name": "Alice Updated", "email": "alice@example.com"}
)

# PATCH - Partial update
patched = z.comm.http_patch(
    "https://api.example.com/users/123",
    data={"email": "newemail@example.com"}
)

# DELETE - Remove resource
deleted = z.comm.http_delete("https://api.example.com/users/123")
```

---

## Implementation Notes

### File to Modify
- **`zCLI/subsystems/zComm/zComm_modules/comm_http.py`** - Add new methods to HTTPClient class
- **`zCLI/subsystems/zComm/zComm.py`** - Add facade methods to zComm class

### Method Delegation Pattern
```python
# In zComm.py facade
def http_get(self, url: str, params: Optional[Dict] = None, 
             headers: Optional[Dict] = None, timeout: int = 10):
    """GET request facade."""
    return self._http_client.get(url, params=params, headers=headers, timeout=timeout)
```

### Testing with httpbin.org
All methods can be tested against httpbin.org:
- `https://httpbin.org/get` - Test GET
- `https://httpbin.org/put` - Test PUT
- `https://httpbin.org/delete` - Test DELETE
- `https://httpbin.org/patch` - Test PATCH

---

## Priority

**Medium-High** - While POST covers many use cases, full RESTful API support is expected in a modern HTTP client. This is a logical completion of the HTTP client feature set.

---

## Related Files

- `zCLI/subsystems/zComm/zComm.py` (facade layer)
- `zCLI/subsystems/zComm/zComm_modules/comm_http.py` (implementation)
- `Documentation/zComm_GUIDE.md` (documentation)
- `Demos/Layer_0/zComm_Demo/Level_1_Network/http_simple.py` (example demo)

---

## Testing Checklist

- [ ] GET with query parameters
- [ ] GET with custom headers
- [ ] PUT with JSON body
- [ ] DELETE with authentication header
- [ ] PATCH with partial update
- [ ] All methods handle timeouts gracefully
- [ ] All methods handle invalid URLs gracefully
- [ ] All methods handle network errors gracefully
- [ ] Response objects have `.status_code`, `.json()`, `.text`
- [ ] Cross-platform compatibility (macOS, Linux, Windows)

