# zAuth: The Authentication Subsystem

## **Overview**
- **zAuth** is **zCLI**'s session-only authentication subsystem
- Provides dual-mode authentication (Terminal/GUI), remote API integration, and session credential management
- Initializes after zDisplay, providing authentication services to all subsystems

## **Architecture**

### **Layer 1 Authentication Services**
**zAuth** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm, zDisplay)
- Provides authentication services to all other subsystems
- Depends on zDisplay for dual-mode I/O
- Establishes session-only authentication (no persistence)

### **Streamlined Design**
```
zAuth/
├── __init__.py                       # Module exports
└── zAuth.py                          # Self-contained authentication class
```

**Note:** All authentication logic is now contained within the `zAuth` class itself, eliminating the need for separate module files.

---

## **Core Features**

### **1. Session-Only Authentication**
- **No Persistence**: Credentials stored only in `session["zAuth"]` during runtime
- **Fresh Login**: Users authenticate each session
- **Clean Logout**: Session cleared on logout or exit

### **2. Dual-Mode I/O**
- **Terminal Mode**: Interactive prompts via `zDisplay.zEvents.zAuth`
- **GUI Mode**: WebSocket events via bifrost for frontend forms
- Automatic mode detection and seamless switching

### **3. Remote API Integration**
- **Environment-Based**: Enabled via `ZOLO_USE_REMOTE_API=true`
- **zComm Integration**: Uses zComm for HTTP communication
- **Flexible Endpoints**: Configurable server URL

---

## **Session Structure**

### **zAuth Session Data**
```python
session["zAuth"] = {
    "id": None,           # User ID (e.g., "zU_abc123")
    "username": None,     # Username
    "role": None,         # User role (e.g., "admin", "user")
    "API_Key": None       # API key for authenticated requests
}
```

### **Authentication States**
- **Not Authenticated**: All fields are `None`
- **Authenticated**: All fields populated after successful login
- **Logged Out**: All fields reset to `None`

---

## **API Reference**

### **Core Methods**

#### **`login(username=None, password=None, server_url=None)`**
Authenticate user for current session.

**Parameters:**
- `username` (str, optional): Username (prompts if not provided)
- `password` (str, optional): Password (prompts if not provided)
- `server_url` (str, optional): API server URL (uses env default if not provided)

**Returns:**
```python
{
    "status": "success" | "fail" | "pending",
    "credentials": {...},  # On success
    "reason": "..."        # On failure
}
```

**Example:**
```python
# Interactive login (prompts for credentials)
result = zcli.auth.login()

# Direct login
result = zcli.auth.login("alice", "secret123")
```

---

#### **`logout()`**
Clear session authentication.

**Returns:**
```python
{"status": "success"}
```

**Example:**
```python
zcli.auth.logout()
```

---

#### **`status()`**
Display current authentication status.

**Returns:**
```python
# When authenticated:
{
    "status": "authenticated",
    "user": {
        "id": "zU_abc123",
        "username": "alice",
        "role": "admin",
        "API_Key": "key_xyz..."
    }
}

# When not authenticated:
{"status": "not_authenticated"}
```

**Example:**
```python
status = zcli.auth.status()
if status["status"] == "authenticated":
    print(f"Logged in as: {status['user']['username']}")
```

---

#### **`is_authenticated()`**
Check if user is currently authenticated.

**Returns:** `bool`

**Example:**
```python
if zcli.auth.is_authenticated():
    # Proceed with authenticated action
    pass
else:
    # Prompt for login
    zcli.auth.login()
```

---

#### **`get_credentials()`**
Get current session credentials.

**Returns:** `dict` or `None`

**Example:**
```python
creds = zcli.auth.get_credentials()
if creds:
    api_key = creds["API_Key"]
    username = creds["username"]
```

---

## **Shell Commands**

### **Available Commands**
```bash
# Login (interactive)
auth login

# Login (with username)
auth login alice

# Logout
auth logout

# Show status
auth status
```

### **Command Flow**
```
User: "auth login"
  ↓
zParser → {"type": "auth", "action": "login"}
  ↓
zShell_executor → execute_auth()
  ↓
zAuth.login() → zDisplay.zEvents.zAuth.login_prompt()
  ↓
Terminal: Interactive prompts
GUI: WebSocket event to frontend
  ↓
Authentication → Session update
  ↓
Success/Failure display
```

---

## **Dual-Mode Events**

### **zDisplay.zEvents.zAuth Package**
zAuth uses dedicated display events for dual-mode I/O:

#### **`login_prompt(username, password)`**
- **Terminal**: Interactive prompts for credentials
- **GUI**: Sends `auth_login_prompt` event with form fields

#### **`login_success(user_data)`**
- **Terminal**: Formatted success message with user details
- **GUI**: Sends `auth_login_success` event with user data

#### **`login_failure(reason)`**
- **Terminal**: Error message with failure reason
- **GUI**: Sends `auth_login_failure` event with reason

#### **`logout_success()`**
- **Terminal**: Success confirmation
- **GUI**: Sends `auth_logout_success` event

#### **`logout_warning()`**
- **Terminal**: Warning when not logged in
- **GUI**: Sends `auth_logout_warning` event

#### **`status_display(auth_data)`**
- **Terminal**: Formatted table with auth details
- **GUI**: Sends `auth_status` event with structured data

#### **`status_not_authenticated()`**
- **Terminal**: Warning message
- **GUI**: Sends `auth_status` event (not authenticated)

---

## **GUI Integration**

### **Bifrost Events**
When in GUI mode, zAuth sends clean JSON events via bifrost:

```json
// Login prompt
{
  "event": "auth_login_prompt",
  "data": {
    "username": null,
    "password": null,
    "fields": ["username", "password"]
  }
}

// Login success
{
  "event": "auth_login_success",
  "data": {
    "username": "alice",
    "role": "admin",
    "user_id": "zU_abc123",
    "api_key": "key_xyz..."
  }
}

// Login failure
{
  "event": "auth_login_failure",
  "data": {
    "reason": "Invalid credentials"
  }
}

// Status display
{
  "event": "auth_status",
  "data": {
    "authenticated": true,
    "username": "alice",
    "role": "admin",
    "user_id": "zU_abc123",
    "api_key": "key_xyz..."
  }
}
```

### **Frontend Implementation**
The frontend receives these events and renders appropriate UI:
- Login form for `auth_login_prompt`
- Success notification for `auth_login_success`
- Error message for `auth_login_failure`
- Status display for `auth_status`

---

## **Remote Authentication**

### **Configuration**
```bash
# Enable remote API
export ZOLO_USE_REMOTE_API=true

# Set API URL (optional, defaults to http://localhost:5000)
export ZOLO_API_URL=https://api.example.com
```

### **API Endpoint**
Remote authentication expects a POST endpoint at `/auth/login`:

**Request:**
```json
{
  "username": "alice",
  "password": "secret123"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "credentials": {
    "username": "alice",
    "api_key": "key_xyz...",
    "role": "admin",
    "user_id": "zU_abc123"
  }
}
```

**Response (Failure):**
```json
{
  "status": "fail",
  "reason": "Invalid credentials"
}
```

---

## **Best Practices**

### **1. Check Authentication Before Protected Actions**
```python
if not zcli.auth.is_authenticated():
    zcli.display.warning("Authentication required")
    result = zcli.auth.login()
    if result["status"] != "success":
        return {"error": "Authentication failed"}

# Proceed with authenticated action
```

### **2. Use Session Credentials for API Calls**
```python
creds = zcli.auth.get_credentials()
if creds:
    headers = {"Authorization": f"Bearer {creds['API_Key']}"}
    # Make authenticated API call
```

### **3. Handle GUI Mode Gracefully**
```python
result = zcli.auth.login()
if result["status"] == "pending":
    # GUI mode - credentials will be sent via bifrost
    # Frontend will handle the response
    return
```

### **4. Clear Session on Exit**
```python
# In cleanup/exit handlers
zcli.auth.logout()
```

---

## **Testing**

### **Test Suite**
Run zAuth tests:
```bash
python3 zTestSuite/zAuth_Test.py
```

### **Test Coverage**
- **17 tests** covering:
  - Initialization and session structure
  - Session-only authentication
  - Login/logout workflows
  - Status display
  - Remote API integration
  - Dual-mode event integration

---

## **Migration Notes**

### **From Old zAuth**
The streamlined zAuth removes:
- ❌ **CredentialManager**: No persistence
- ❌ **local_auth**: Disabled local authentication
- ❌ **validate_api_key**: Removed validation method
- ❌ **zAuth_modules/**: All logic moved into main class
- ❌ **helpers.py**: Removed unused helper functions

All authentication is now:
- ✅ **Session-only**: No file-based persistence
- ✅ **Remote-first**: Uses remote API when enabled
- ✅ **Dual-mode**: Works in Terminal and GUI
- ✅ **Self-contained**: Single file architecture

### **Code Updates**
```python
# Old (deprecated)
zcli.display.handle({"event": "text", "content": "Login required"})
username = input("Username: ")

# New (streamlined)
result = zcli.auth.login()  # Uses zDisplay events automatically
```

---

## **Summary**

**zAuth** provides streamlined, session-only authentication with:
- **Dual-mode I/O** via zDisplay events (Terminal/GUI)
- **Remote API integration** via zComm
- **Clean session management** with no persistence
- **17 passing tests** ensuring reliability

For display integration details, see [zDisplay_GUIDE.md](zDisplay_GUIDE.md).
For configuration options, see [zConfig_GUIDE.md](zConfig_GUIDE.md).

